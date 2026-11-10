
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator
import time

# Parameters we can change
NUM_QUBITS = 3
NUM_LAYERS = 5
SHOTS = 1024

# Circuit construction
qc = QuantumCircuit(NUM_QUBITS)

for layer in range(NUM_LAYERS):
    for qubit in range(NUM_QUBITS):
        qc.h(qubit)

    for qubit in range(NUM_QUBITS - 1):
        qc.cx(qubit, qubit + 1)

qc.measure_all()

# Inspect circuit
print("Number of qubits:", qc.num_qubits)
print("Requested layers:", NUM_LAYERS)
print("Actual circuit depth:", qc.depth())
print("Total operations:", qc.size())
print("Gate distribution:", qc.count_ops())

# Run simulation
simulator = AerSimulator(
    method="statevector",
    device="CPU",
    max_memory_mb=512,
    max_parallel_threads=2
)

start = time.perf_counter()
result = simulator.run(qc, shots=SHOTS).result()
elapsed = time.perf_counter() - start

print("Simulation successful:", result.success)
print("Execution time:", round(elapsed, 6), "seconds")

if result.success:
    print("Measurement results:", result.get_counts())
