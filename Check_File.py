from qiskit_optimization import QuadraticProgram
from qiskit_optimization.translators import from_docplex_mp
from docplex.mp.model import Model

# Step 1: Initialize a classical optimization model using Docplex
mdl = Model(name="Noida_Traffic_Optimization")

# Step 2: Define binary variables (0 or 1)
x1 = mdl.binary_var(name="road_1")
x2 = mdl.binary_var(name="road_2")

# Step 3: Define the objective function (The QUBO math)
mdl.minimize(-x1 - x2 + 2*x1*x2)

# Step 4: Convert it directly into a Qiskit Quadratic Program
qp = QuadraticProgram()
qp = from_docplex_mp(mdl)

print("Your QUBO is ready for a Quantum Computer:")
print(qp.prettyprint())

# Step 5: Convert the QUBO into an operator (Hamiltonian matrix) for QAOA
operator, offset = qp.to_ising()
print("\nThis translates to the following Pauli Matrix Operators:")
print(operator)
