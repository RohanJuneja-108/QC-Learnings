
import csv
from pathlib import Path

import psutil
import Resource_Monitor_V2 as monitor

QUBIT_COUNTS = [20, 22, 24]
LAYERS = 2

STATE_MEMORY_BUDGET_MB = 128
MIN_START_RAM_MB = 1500

monitor.TIMEOUT_SECONDS = 20
monitor.MAX_TREE_RSS_MB = 512
monitor.MIN_FREE_RAM_MB = 800

OUTPUT = Path("memory_boundary_results.csv")

results = []

for n in QUBIT_COUNTS:

    available_mb = (
        psutil.virtual_memory().available / 2**20
    )

    if available_mb < MIN_START_RAM_MB:
        print("Low free RAM. Stopping.")
        break

    theoretical_mb = 16 * (2**n) / (1024**2)

    print(f"\nTesting {n} qubits")
    print("Theoretical state memory:",
          theoretical_mb, "MiB")
    print("Configured budget:",
          STATE_MEMORY_BUDGET_MB, "MiB")

    result = monitor.benchmark(n, LAYERS)

    result["theoretical_memory_mb"] = theoretical_mb
    result["state_budget_mb"] = STATE_MEMORY_BUDGET_MB

    results.append(result)

    print("Status:", result["status"])
    print("Wall time:", result["wall_time_s"])
    print("Peak RSS:", result["peak_tree_rss_mb"])
    print("Return code:", result["return_code"])

    if result["status"] != "SUCCESS":
        print("Worker error:", result["error"])

    with OUTPUT.open(
        "w", newline="", encoding="utf-8"
    ) as file:
        writer = csv.DictWriter(
            file, fieldnames=results[0].keys()
        )
        writer.writeheader()
        writer.writerows(results)

    if result["status"] in {
        "TIMEOUT",
        "MEMORY_LIMIT",
        "LOW_SYSTEM_MEMORY"
    }:
        print("Safety limit reached. Stopping.")
        break

print("\nMemory-budget experiment completed.")
print("Results:", OUTPUT.resolve())
