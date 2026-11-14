
import csv
import time
from pathlib import Path

from qiskit.quantum_info import Pauli
from qiskit_aer import AerSimulator

from Circuit_Generator import generate_circuit


# Small, safe experiments for our first benchmark
QUBIT_COUNTS = [3, 5, 10]
LAYER_COUNTS = [5, 50, 200]
REPETITIONS = 3

simulator = AerSimulator(
    method="statevector",
    device="CPU",
    max_memory_mb=512,
    max_parallel_threads=2,
    fusion_enable=False
)

results = []

# Warm up the simulator
warmup = generate_circuit(2, 2)
warmup.save_expectation_value(
    Pauli("Z"), [0], label="z0"
)
simulator.run(warmup, shots=1).result()

for n in QUBIT_COUNTS:
    for layers in LAYER_COUNTS:

        print(f"\nTesting {n} qubits, {layers} layers")

        # Measure circuit construction separately
        build_start = time.perf_counter()

        circuit = generate_circuit(
            num_qubits=n,
            num_layers=layers,
            seed=42
        )

        # Save a scalar observable instead of
        # returning the full statevector
        circuit.save_expectation_value(
            Pauli("Z"), [0], label="z0"
        )

        build_time = time.perf_counter() - build_start

        for repeat in range(1, REPETITIONS + 1):
            start = time.perf_counter()

            try:
                result = simulator.run(
                    circuit, shots=1
                ).result()

                elapsed = time.perf_counter() - start

                if not result.success:
                    raise RuntimeError(str(result.status))

                expectation = float(
                    result.data(0)["z0"]
                )

                status = "SUCCESS"
                error = ""

            except Exception as exc:
                elapsed = time.perf_counter() - start
                expectation = ""
                status = "FAILED"
                error = str(exc)

            row = {
                "qubits": n,
                "layers": layers,
                "depth": circuit.depth(),
                "gates": circuit.size(),
                "repeat": repeat,
                "build_time_s": build_time,
                "simulation_time_s": elapsed,
                "expectation_z0": expectation,
                "status": status,
                "error": error
            }

            results.append(row)

            print(
                f"  Run {repeat}: "
                f"{status} | {elapsed:.6f} s"
            )

# Save benchmark results
output = Path("benchmark_results.csv")

with output.open("w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(
        f, fieldnames=results[0].keys()
    )
    writer.writeheader()
    writer.writerows(results)

print(f"\nResults saved to: {output.resolve()}")
