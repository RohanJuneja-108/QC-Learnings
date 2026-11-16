
import csv
from pathlib import Path

import psutil
import Resource_Monitor_V2 as monitor

QUBITS = [18, 20, 22]
LAYERS = 2

monitor.TIMEOUT_SECONDS = 20
monitor.MAX_TREE_RSS_MB = 512
monitor.MIN_FREE_RAM_MB = 800

MIN_START_RAM_MB = 1500

results = []
output = Path("double_precision_memory_audit.csv")

for n in QUBITS:

    available_mb = (
        psutil.virtual_memory().available / 2**20
    )

    if available_mb < MIN_START_RAM_MB:
        print("Low available RAM. Stopping.")
        break

    print(f"\nTesting {n} qubits", flush=True)

    result = monitor.benchmark(n, LAYERS)

    theoretical_mb = (
        (2 ** n) * 16 / (1024 ** 2)
    )

    result["theoretical_memory_mb"] = theoretical_mb

    results.append(result)

    print("Status:", result["status"])
    print("Requested qubits:", n)
    print(
        "Simulated qubits:",
        result["simulated_qubits"]
    )
    print(
        "Theoretical memory:",
        theoretical_mb, "MiB"
    )
    print(
        "Aer required memory:",
        result["required_memory_mb"], "MiB"
    )
    print(
        "Observed peak RSS:",
        result["peak_tree_rss_mb"], "MiB"
    )
    print(
        "Aer execution time:",
        result["aer_time_s"]
    )

    with output.open(
        "w", newline="", encoding="utf-8"
    ) as file:
        writer = csv.DictWriter(
            file, fieldnames=results[0].keys()
        )
        writer.writeheader()
        writer.writerows(results)

    if result["status"] != "SUCCESS":
        print("Stopping after unsuccessful trial.")
        break

print("\nAudit finished.")
print("Results:", output.resolve())
