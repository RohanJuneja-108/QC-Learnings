
from qiskit import QuantumCircuit
import numpy as np


def generate_circuit(
    num_qubits: int,
    num_layers: int,
    seed: int = 42
) -> QuantumCircuit:

    if num_qubits < 1:
        raise ValueError("num_qubits must be >= 1")

    if num_layers < 0:
        raise ValueError("num_layers must be >= 0")

    rng = np.random.default_rng(seed)

    qc = QuantumCircuit(num_qubits)

    for layer in range(num_layers):

        # Single-qubit rotations
        for qubit in range(num_qubits):
            theta = rng.uniform(0, 2 * np.pi)
            phi = rng.uniform(0, 2 * np.pi)

            qc.rx(theta, qubit)
            qc.rz(phi, qubit)

        # Nearest-neighbour entanglement
        for qubit in range(num_qubits - 1):
            qc.cx(qubit, qubit + 1)

    return qc


if __name__ == "__main__":

    circuit = generate_circuit(
        num_qubits=3,
        num_layers=5
    )

    print("Qubits:", circuit.num_qubits)
    print("Requested layers:", 5)
    print("Actual depth:", circuit.depth())
    print("Total operations:", circuit.size())
    print("Gate distribution:", circuit.count_ops())

    print(circuit.draw(output="text"))
