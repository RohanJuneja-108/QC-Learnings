
import csv
import subprocess
import sys
import time
from pathlib import Path

import psutil


QUBIT_COUNTS = [10, 15, 20, 22, 24]
LAYERS = 50

TIMEOUT_SECONDS = 30
MAX_SIMULATOR_MEMORY_MB = 512

# Conservative starting safeguards
MIN_AVAILABLE_RAM_MB = 1024
MAX_WORKER_RSS_MB = 1024

OUTPUT_FILE = Path("resource_results.csv")


def run_worker(n, layers):
    from qiskit.quantum_info import Pauli
    from qiskit_aer import AerSimulator
    from Circuit_Generator import generate_circuit

    circuit = generate_circuit(n, layers, seed=42)

    circuit.save_expectation_value(
        Pauli("Z"), [0], label="z0"
    )

    simulator = AerSimulator(
        method="statevector",
        device="CPU",
        max_memory_mb=MAX_SIMULATOR_MEMORY_MB,
        max_parallel_threads=2,
        fusion_enable=False
    )

    result = simulator.run(circuit, shots=1).result()

    if not result.success:
        raise RuntimeError(str(result.status))

    print("SUCCESS", flush=True)


def run_supervised(n, layers):
    command = [
        sys.executable,
        str(Path(__file__).resolve()),
        "--worker",
        str(n),
        str(layers)
    ]

    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    monitor = psutil.Process(process.pid)

    start = time.perf_counter()
    peak_rss_mb = 0.0
    status = None

    while process.poll() is None:
        elapsed = time.perf_counter() - start

        try:
            rss_mb = (
                monitor.memory_info().rss / (1024 ** 2)
            )
            peak_rss_mb = max(peak_rss_mb, rss_mb)
        except psutil.NoSuchProcess:
            break

        available_mb = (
            psutil.virtual_memory().available / (1024 ** 2)
        )

        if elapsed >= TIMEOUT_SECONDS:
            status = "TIMEOUT"

        elif rss_mb > MAX_WORKER_RSS_MB:
            status = "PROCESS_MEMORY_LIMIT"

        elif available_mb < MIN_AVAILABLE_RAM_MB:
            status = "LOW_SYSTEM_MEMORY"

        if status is not None:
            process.kill()
            break

        time.sleep(0.05)

    stdout, stderr = process.communicate()
    elapsed = time.perf_counter() - start

    if status is None:
        if process.returncode == 0 and "SUCCESS" in stdout:
            status = "SUCCESS"
        else:
            status = "FAILED"

    return {
        "qubits": n,
        "layers": layers,
        "elapsed_s": round(elapsed, 5),
        "peak_observed_rss_mb": round(peak_rss_mb, 2),
        "status": status,
        "return_code": process.returncode,
        "error": stderr.strip()[-500:]
    }


def main():
    results = []

    for n in QUBIT_COUNTS:
        available_mb = (
            psutil.virtual_memory().available / (1024 ** 2)
        )

        if available_mb < 1536:
            print("Insufficient available RAM. Stopping.")
            break

        print(f"Testing {n} qubits, {LAYERS} layers")

        row = run_supervised(n, LAYERS)
        results.append(row)

        print(
            f"  {row['status']} | "
            f"{row['elapsed_s']} s | "
            f"observed peak RSS: "
            f"{row['peak_observed_rss_mb']} MiB"
        )

        if row["status"] in {
            "TIMEOUT",
            "PROCESS_MEMORY_LIMIT",
            "LOW_SYSTEM_MEMORY"
        }:
            print("Resource limit reached. Stopping.")
            break

    if results:
        with OUTPUT_FILE.open(
            "w", newline="", encoding="utf-8"
        ) as file:
            writer = csv.DictWriter(
                file, fieldnames=results[0].keys()
            )
            writer.writeheader()
            writer.writerows(results)

        print(f"\nSaved results to {OUTPUT_FILE}")


if __name__ == "__main__":
    if len(sys.argv) == 4 and sys.argv[1] == "--worker":
        run_worker(
            int(sys.argv[2]),
            int(sys.argv[3])
        )
    else:
        main()
