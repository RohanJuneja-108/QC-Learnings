
import os
import time
import psutil
import numpy as np

from qiskit.quantum_info import Pauli
from qiskit_aer import AerSimulator
from Circuit_Generator import generate_circuit

process = psutil.Process(os.getpid())

def report_memory(stage):
    mem = process.memory_info()
    available = psutil.virtual_memory().available

    print(f"\n{stage}")
    print(f"PID: {process.pid}")
    print(f"RSS: {mem.rss / 2**20:.2f} MiB")
    print(f"VMS: {mem.vms / 2**20:.2f} MiB")
    print(f"Available system RAM: "
          f"{available / 2**20:.2f} MiB")

    if hasattr(mem, "peak_wset"):
        print(f"Peak working set: "
              f"{mem.peak_wset / 2**20:.2f} MiB")
    elif hasattr(mem, "peak_rss"):
        print(f"Peak RSS: "
              f"{mem.peak_rss / 2**20:.2f} MiB")


# Test A: Known memory allocation
report_memory("A1: Before allocation")

# Allocate and touch 128 MiB of data.
data = np.ones(16_777_216, dtype=np.float64)

report_memory("A2: After 128 MiB allocation")

time.sleep(2)

del data

report_memory("A3: After releasing array")


# Test B: Quantum simulation
n = 20
layers = 50

qc = generate_circuit(n, layers, seed=42)
qc.save_expectation_value(
    Pauli("Z"), [0], label="z0"
)

simulator = AerSimulator(
    method="statevector",
    device="CPU",
    max_memory_mb=512,
    max_parallel_threads=2,
    fusion_enable=False
)

report_memory("B1: Before simulation")

start = time.perf_counter()
result = simulator.run(qc, shots=1).result()
elapsed = time.perf_counter() - start

report_memory("B2: After simulation")

print("\nSimulation success:", result.success)
print("Simulation wall time:", round(elapsed, 4), "s")

if result.success:
    print("Expectation Z0:", result.data(0)["z0"])
    print("Simulator metadata:", result.results[0].metadata)
else:
    print("Simulator status:", result.status)
