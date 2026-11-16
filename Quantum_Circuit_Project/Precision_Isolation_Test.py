
import subprocess
import sys
import time
from pathlib import Path


TIMEOUT = 10


def worker(mode):
    from qiskit import QuantumCircuit
    from qiskit_aer import AerSimulator
    from qiskit.quantum_info import Pauli

    qc = QuantumCircuit(3)
    qc.h(0)
    qc.cx(0, 1)
    qc.rx(0.42, 2)

    if mode == "expectation":
        qc.save_expectation_value(
            Pauli("Z"), [0], label="z0"
        )
    else:
        qc.measure_all()

    simulator = AerSimulator(
        method="statevector",
        device="CPU",
        precision="single",
        max_parallel_threads=1,
        fusion_enable=False
    )

    print("Mode:", mode, flush=True)
    print("Starting simulation...", flush=True)

    result = simulator.run(
        qc, shots=100
    ).result()

    print("Success:", result.success, flush=True)

    if result.success:
        print(
            "Metadata:",
            result.results[0].metadata,
            flush=True
        )


def main():
    for mode in ["measurement", "expectation"]:

        print(f"\nTesting: {mode}", flush=True)

        command = [
            sys.executable,
            "-u",
            str(Path(__file__).resolve()),
            "--worker",
            mode
        ]

        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        try:
            out, err = process.communicate(
                timeout=TIMEOUT
            )
        except subprocess.TimeoutExpired:
            subprocess.run(
                [
                    "taskkill",
                    "/PID", str(process.pid),
                    "/T", "/F"
                ],
                capture_output=True,
                check=False
            )
            out, err = process.communicate()
            print("TIMEOUT")

        print(out)

        if err:
            print("ERROR:", err[-1000:])

        print("Return code:", process.returncode)


if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "--worker":
        worker(sys.argv[2])
    else:
        main()
