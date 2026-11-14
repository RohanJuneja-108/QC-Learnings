
import os
import sys
import time
import subprocess

import psutil


# Conservative diagnostic configuration
QUBITS = 20
LAYERS = 20

TIMEOUT_SECONDS = 45
MAX_TREE_RSS_MB = 768
MIN_FREE_RAM_MB = 768

SAMPLE_INTERVAL = 0.05


def worker():
    from qiskit.quantum_info import Pauli
    from qiskit_aer import AerSimulator
    from Circuit_Generator import generate_circuit

    print(f"WORKER_PID={os.getpid()}", flush=True)

    qc = generate_circuit(QUBITS, LAYERS, seed=42)
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

    result = simulator.run(qc, shots=1).result()

    if not result.success:
        raise RuntimeError(str(result.status))

    metadata = result.results[0].metadata

    print("METHOD:", metadata.get("method"), flush=True)
    print("DEVICE:", metadata.get("device"), flush=True)
    print(
        "AER_TIME:",
        metadata.get("time_taken"),
        flush=True
    )
    print(
        "REQUIRED_MEMORY_MB:",
        metadata.get("required_memory_mb"),
        flush=True
    )
    print("SUCCESS", flush=True)


def process_tree(root):
    try:
        children = root.children(recursive=True)
        return [root] + children
    except psutil.Error:
        return [root]


def tree_rss_mb(root):
    processes = process_tree(root)
    total = 0.0
    details = []

    for proc in processes:
        try:
            rss = proc.memory_info().rss / (1024 ** 2)
            total += rss
            details.append((proc.pid, proc.name(), rss))
        except psutil.Error:
            continue

    return total, details


def terminate_tree(root):
    processes = process_tree(root)

    # Stop children first
    for proc in reversed(processes):
        try:
            proc.kill()
        except psutil.Error:
            pass

    psutil.wait_procs(processes, timeout=5)


def supervisor():
    available = (
        psutil.virtual_memory().available / (1024 ** 2)
    )

    print(f"Initial available RAM: {available:.2f} MiB")

    if available < MIN_FREE_RAM_MB + 768:
        print("Not enough free RAM for this diagnostic.")
        return

    process = subprocess.Popen(
        [sys.executable, os.path.abspath(__file__), "--worker"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    root = psutil.Process(process.pid)

    start = time.perf_counter()
    peak_tree_rss = 0.0
    status = None
    observed_pids = set()

    while process.poll() is None:
        elapsed = time.perf_counter() - start

        rss, details = tree_rss_mb(root)

        peak_tree_rss = max(peak_tree_rss, rss)

        for pid, name, memory in details:
            if pid not in observed_pids:
                observed_pids.add(pid)
                print(
                    f"Detected PID={pid}, "
                    f"name={name}, RSS={memory:.2f} MiB"
                )

        available = (
            psutil.virtual_memory().available / (1024 ** 2)
        )

        if elapsed > TIMEOUT_SECONDS:
            status = "TIMEOUT"
        elif rss > MAX_TREE_RSS_MB:
            status = "PROCESS_MEMORY_LIMIT"
        elif available < MIN_FREE_RAM_MB:
            status = "LOW_SYSTEM_MEMORY"

        if status:
            terminate_tree(root)
            break

        time.sleep(SAMPLE_INTERVAL)

    stdout, stderr = process.communicate()
    elapsed = time.perf_counter() - start

    if status is None:
        if process.returncode == 0 and "SUCCESS" in stdout.splitlines():
            status = "SUCCESS"
        else:
            status = "FAILED"

    print("\n--- DIAGNOSTIC RESULT ---")
    print("Status:", status)
    print("Supervisor PID:", os.getpid())
    print("Launched PID:", process.pid)
    print("Observed PIDs:", sorted(observed_pids))
    print("Peak observed tree RSS:", round(peak_tree_rss, 2), "MiB")
    print("Elapsed time:", round(elapsed, 4), "s")
    print("Return code:", process.returncode)

    print("\n--- WORKER OUTPUT ---")
    print(stdout)

    if stderr:
        print("\n--- WORKER ERRORS ---")
        print(stderr[-2000:])


if __name__ == "__main__":
    if "--worker" in sys.argv:
        worker()
    else:
        supervisor()
