
import csv
import json
import os
import subprocess
import sys
import time
from pathlib import Path

import psutil

QUBITS = [10, 15, 18, 20, 22]
LAYERS = 20

TIMEOUT_SECONDS = 20
MAX_TREE_RSS_MB = 512
MIN_FREE_RAM_MB = 800
MIN_START_RAM_MB = 1500

OUTPUT = Path("resource_results_v2.csv")


def worker(n, layers):
    from qiskit_aer import AerSimulator
    from qiskit.quantum_info import Pauli
    from Circuit_Generator import generate_circuit

    circuit = generate_circuit(n, layers, seed=42)
    circuit.save_expectation_value(
        Pauli("Z"), [0], label="z0"
    )

    simulator = AerSimulator(
        method="statevector",
        device="CPU",
        max_memory_mb=256,
        max_parallel_threads=2,
        fusion_enable=False
    )

    result = simulator.run(circuit, shots=1).result()

    if not result.success:
        raise RuntimeError(str(result.status))

    meta = result.results[0].metadata

    print(json.dumps({
        "aer_time_s": meta.get("time_taken"),
        "required_memory_mb": meta.get("required_memory_mb"),
        "method": meta.get("method"),
        "device": meta.get("device")
    }), flush=True)


def processes_in_tree(root):
    try:
        return [root] + root.children(recursive=True)
    except psutil.Error:
        return [root]


def measure_tree(root):
    total = 0

    for proc in processes_in_tree(root):
        try:
            total += proc.memory_info().rss
        except psutil.Error:
            pass

    return total / (1024 ** 2)


def stop_tree(root):
    # Windows: terminate the launcher and descendants.
    subprocess.run(
        ["taskkill", "/PID", str(root.pid), "/T", "/F"],
        capture_output=True,
        text=True,
        check=False
    )


def benchmark(n, layers):
    command = [
        sys.executable,
        str(Path(__file__).resolve()),
        "--worker",
        str(n),
        str(layers)
    ]

    proc = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    root = psutil.Process(proc.pid)

    start = time.perf_counter()
    peak_rss = 0.0
    status = None

    while proc.poll() is None:
        elapsed = time.perf_counter() - start
        rss = measure_tree(root)
        peak_rss = max(peak_rss, rss)

        free_ram = (
            psutil.virtual_memory().available / 2**20
        )

        if elapsed >= TIMEOUT_SECONDS:
            status = "TIMEOUT"

        elif rss >= MAX_TREE_RSS_MB:
            status = "MEMORY_LIMIT"

        elif free_ram < MIN_FREE_RAM_MB:
            status = "LOW_SYSTEM_MEMORY"

        if status is not None:
            stop_tree(root)
            break

        time.sleep(0.05)

    stdout, stderr = proc.communicate()
    elapsed = time.perf_counter() - start

    meta = {}

    if status is None:
        if proc.returncode == 0:
            try:
                meta = json.loads(stdout.strip())
                status = "SUCCESS"
            except json.JSONDecodeError:
                status = "INVALID_OUTPUT"
        else:
            status = "FAILED"

    return {
        "qubits": n,
        "layers": layers,
        "status": status,
        "wall_time_s": round(elapsed, 4),
        "peak_tree_rss_mb": round(peak_rss, 2),
        "aer_time_s": meta.get("aer_time_s"),
        "required_memory_mb": meta.get(
            "required_memory_mb"
        ),
        "method": meta.get("method"),
        "return_code": proc.returncode,
        "error": stderr[-300:]
    }


def main():
    rows = []

    for n in QUBITS:
        free_ram = (
            psutil.virtual_memory().available / 2**20
        )

        if free_ram < MIN_START_RAM_MB:
            print("Insufficient free RAM. Stopping.")
            break

        print(f"\nTesting {n} qubits...")

        row = benchmark(n, LAYERS)
        rows.append(row)

        print("Status:", row["status"])
        print("Wall time:", row["wall_time_s"], "s")
        print("Peak tree RSS:",
              row["peak_tree_rss_mb"], "MiB")
        print("Aer time:", row["aer_time_s"])

        if row["status"] != "SUCCESS":
            print("Stopping after unsuccessful trial.")
            break

    if rows:
        with OUTPUT.open(
            "w", newline="", encoding="utf-8"
        ) as file:
            writer = csv.DictWriter(
                file, fieldnames=rows[0].keys()
            )
            writer.writeheader()
            writer.writerows(rows)

        print("\nResults saved:", OUTPUT.resolve())


if __name__ == "__main__":
    if len(sys.argv) == 4 and sys.argv[1] == "--worker":
        worker(int(sys.argv[2]), int(sys.argv[3]))
    else:
        main()
