"""Supervised Qiskit Aer statevector benchmark for Windows.

Imported interface: benchmark(n, layers) and the configurable safety constants.
Direct execution: run a short width sweep.
"""

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

# This limits Aer quantum-state storage, NOT the total process RSS.
AER_STATE_MEMORY_MB = 128
OUTPUT = Path("resource_results_v2.csv")


def worker(n, layers):
    """Execute one simulation in an isolated child process."""
    from qiskit_aer import AerSimulator
    from qiskit.quantum_info import Pauli
    from Circuit_Generator import generate_circuit

    circuit = generate_circuit(n, layers, seed=42)
    circuit.save_expectation_value(Pauli("Z"), [0], label="z0")

    simulator = AerSimulator(
        method="statevector",
        device="CPU",
        precision="double",
        enable_truncation=False,
        max_memory_mb=AER_STATE_MEMORY_MB,
        max_parallel_threads=2,
        fusion_enable=False,
    )

    result = simulator.run(circuit, shots=1).result()
    if not result.success:
        raise RuntimeError(str(result.status))

    meta = result.results[0].metadata
    print(json.dumps({
        "aer_time_s": meta.get("time_taken"),
        "required_memory_mb": meta.get("required_memory_mb"),
        "simulated_qubits": meta.get("num_qubits"),
        "active_input_qubits": meta.get("active_input_qubits"),
        "method": meta.get("method"),
        "device": meta.get("device"),
        "precision": simulator.options.precision,
        "truncation": simulator.options.enable_truncation,
    }), flush=True)


def processes_in_tree(root):
    try:
        return [root] + root.children(recursive=True)
    except psutil.Error:
        return [root]


def measure_tree(root):
    total = 0
    for process in processes_in_tree(root):
        try:
            total += process.memory_info().rss
        except psutil.Error:
            pass
    return total / 2**20


def stop_tree(root):
    """Stop a worker and its descendants on Windows."""
    if os.name == "nt":
        subprocess.run(
            ["taskkill", "/PID", str(root.pid), "/T", "/F"],
            capture_output=True,
            text=True,
            check=False,
        )
    else:
        for process in reversed(processes_in_tree(root)):
            try:
                process.kill()
            except psutil.Error:
                pass


def benchmark(n, layers):
    """Return one measured result with safety limits and error classification."""
    n, layers = int(n), int(layers)
    if n < 1 or layers < 1:
        raise ValueError("n and layers must be positive integers")

    if psutil.virtual_memory().available / 2**20 < MIN_START_RAM_MB:
        raise RuntimeError("Not enough free RAM to start a benchmark safely")

    command = [
        sys.executable,
        "-u",
        str(Path(__file__).resolve()),
        "--worker",
        str(n),
        str(layers),
        str(AER_STATE_MEMORY_MB),
    ]
    start = time.perf_counter()
    proc = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    root = psutil.Process(proc.pid)
    peak_rss = 0.0
    status = None

    while proc.poll() is None:
        elapsed = time.perf_counter() - start
        peak_rss = max(peak_rss, measure_tree(root))
        free_ram_mb = psutil.virtual_memory().available / 2**20

        if elapsed >= TIMEOUT_SECONDS:
            status = "TIMEOUT"
        elif peak_rss >= MAX_TREE_RSS_MB:
            status = "MEMORY_LIMIT"
        elif free_ram_mb < MIN_FREE_RAM_MB:
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
            if "Insufficient memory to run circuit" in (stderr + stdout):
                status = "SIMULATOR_MEMORY_REJECTED"

    return {
        "qubits": n,
        "layers": layers,
        "status": status,
        "wall_time_s": round(elapsed, 4),
        "peak_tree_rss_mb": round(peak_rss, 2),
        "aer_time_s": meta.get("aer_time_s"),
        "required_memory_mb": meta.get("required_memory_mb"),
        "method": meta.get("method"),
        "return_code": proc.returncode,
        "error": (stderr or stdout)[-1000:] if status != "SUCCESS" else "",
        "simulated_qubits": meta.get("simulated_qubits"),
        "active_input_qubits": str(meta.get("active_input_qubits")),
        "precision": meta.get("precision"),
        "truncation": meta.get("truncation"),
    }


def main():
    rows = []
    for n in QUBITS:
        if psutil.virtual_memory().available / 2**20 < MIN_START_RAM_MB:
            print("Insufficient free RAM. Stopping.")
            break

        print(f"\nTesting {n} qubits...", flush=True)
        row = benchmark(n, LAYERS)
        rows.append(row)
        print("Status:", row["status"])
        print("Wall time:", row["wall_time_s"], "s")
        print("Peak tree RSS:", row["peak_tree_rss_mb"], "MiB")
        print("Aer time:", row["aer_time_s"])
        if row["status"] != "SUCCESS":
            print("Stopping after unsuccessful trial.")
            break

    if rows:
        with OUTPUT.open("w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=rows[0].keys())
            writer.writeheader()
            writer.writerows(rows)
        print("\nResults saved:", OUTPUT.resolve())


if __name__ == "__main__":
    if len(sys.argv) == 5 and sys.argv[1] == "--worker":
        AER_STATE_MEMORY_MB = int(sys.argv[4])
        worker(int(sys.argv[2]), int(sys.argv[3]))
    else:
        main()
