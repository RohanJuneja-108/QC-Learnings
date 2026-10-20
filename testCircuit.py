from qiskit import QuantumCircuit
import qiskit

print(f"Qiskit version installed: {qiskit.__version__}")

# Create a simple 2-qubit circuit
qc = QuantumCircuit(2)
qc.h(0) # Add a Hadamard gate to qubit 0
qc.cx(0, 1) # Add a CNOT gate

# Draw the circuit
print("Here is your quantum circuit:")
print(qc.draw(output='text'))