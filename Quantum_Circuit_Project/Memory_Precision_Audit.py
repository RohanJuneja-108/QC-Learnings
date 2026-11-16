
import time
import psutil

from qiskit.quantum_info import Pauli
from qiskit_aer import AerSimulator
from Circuit_Generator import generate_circuit


QUBITS = 18
LAYERS = 2
MIN_FREE_RAM_MB = 1500


for precision in ["single", "double"]:

    available_mb = (
        psutil.virtual_memory().available / (1024 ** 2)
    )

    if available_mb < MIN_FREE_RAM_MB:
        print("Insufficient free RAM. Stopping.", flush=True)
        break

    print(f"\n{'=' * 40}", flush=True)
    print(f"Precision: {precision}", flush=True)

    # STEP 1: Construct circuit
    print("Generating circuit...", flush=True)

    build_start = time.perf_counter()

    circuit = generate_circuit(
        num_qubits=QUBITS,
        num_layers=LAYERS,
        seed=42
    )

    circuit.save_expectation_value(
        Pauli("Z"),
        [0],
        label="z0"
    )

    build_time = time.perf_counter() - build_start

    print(f"Circuit generated in {build_time:.4f} s",
          flush=True)

    # STEP 2: Configure simulator
    simulator = AerSimulator(
        method="statevector",
        device="CPU",
        precision=precision,
        enable_truncation=False,
        max_memory_mb=256,
        max_parallel_threads=2,
        fusion_enable=False
    )

    # STEP 3: Start timer BEFORE simulation
    print("Starting simulation...", flush=True)

    start = time.perf_counter()

    result = simulator.run(
        circuit,
        shots=1
    ).result()

    elapsed = time.perf_counter() - start

    print(f"Simulation returned after {elapsed:.4f} s",
          flush=True)

    # STEP 4: Verify result
    print("Success:", result.success, flush=True)

    if not result.success:
        print("Status:", result.status, flush=True)
        continue

    metadata = result.results[0].metadata

    bytes_per_amplitude = (
        8 if precision == "single" else 16
    )

    theoretical_memory_mb = (
        (2 ** QUBITS) * bytes_per_amplitude
        / (1024 ** 2)
    )

    # STEP 5: Print results
    print("Method:", metadata.get("method"))
    print("Device:", metadata.get("device"))
    print("Simulated qubits:",
          metadata.get("num_qubits"))
    print("Required memory (MiB):",
          metadata.get("required_memory_mb"))
    print("Aer time (s):",
          metadata.get("time_taken"))
    print("Configured precision:",
          simulator.options.precision)
    print("Truncation enabled:",
          simulator.options.enable_truncation)
    print("Theoretical state memory (MiB):",
          theoretical_memory_mb)
    print("Expectation Z0:",
          result.data(0)["z0"])

    print("Experiment completed.", flush=True)
