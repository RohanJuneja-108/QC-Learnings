
import os
import sys
import subprocess
import time

from pathlib import Path


TIMEOUT_SECONDS = 10


def worker(n, precision):
    from qiskit_aer import AerSimulator
    from qiskit.quantum_info import Pauli
    from Circuit_Generator import generate_circuit

    print("Worker PID:", os.getpid(), flush=True)

    qc = generate_circuit(n, 2, seed=42)
    qc.save_expectation_value(
        Pauli("Z"), [0], label="z0"
    )

    simulator = AerSimulator(
        method="statevector",
        device="CPU",
        precision=precision,
        enable_truncation=True,
        max_memory_mb=256,
        max_parallel_threads=1,
        fusion_enable=False
    )

    print("Starting Aer...", flush=True)
    start = time.perf_counter()

    result = simulator.run(qc, shots=1).result()

    print("Elapsed:", time.perf_counter() - start)
    print("Success:", result.success)

    if result.success:
        metadata = result.results[0].metadata
        print("Required memory:",
              metadata.get("required_memory_mb"))
        print("Simulated qubits:",
              metadata.get("num_qubits"))
        print("Expectation:",
              result.data(0)["z0"])


def run_test(n, precision):
    cmd = [
        sys.executable, "-u",
        str(Path(__file__).resolve()),
        "--worker", str(n), precision
    ]

    print(f"\nTEST: {n} qubits, {precision}")

    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    try:
        stdout, stderr = process.communicate(
            timeout=TIMEOUT_SECONDS
        )

        print(stdout)
        if stderr:
            print("STDERR:", stderr[-1500:])

        print("Return code:", process.returncode)

    except subprocess.TimeoutExpired:
        print("TIMEOUT: Terminating worker tree.")

        subprocess.run(
            [
                "taskkill",
                "/PID", str(process.pid),
                "/T", "/F"
            ],
            capture_output=True,
            check=False
        )

        try:
            stdout, stderr = process.communicate(
                timeout=5
            )
            print(stdout)
            if stderr:
                print("STDERR:", stderr[-1500:])
        except subprocess.TimeoutExpired:
            print("Worker cleanup needs investigation.")


if __name__ == "__main__":
    if len(sys.argv) == 4 and sys.argv[1] == "--worker":
        worker(int(sys.argv[2]), sys.argv[3])
    else:
        for n in [3, 10]:
            for precision in ["double", "single"]:
                run_test(n, precision)
