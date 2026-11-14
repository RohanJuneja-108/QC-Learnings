
import csv
from pathlib import Path

import Resource_Monitor_V2 as monitor

# Fixed circuit width
NUM_QUBITS = 18

# Increasing depth workload
LAYER_COUNTS = [10, 20, 50, 100, 200]

# Conservative resource settings
monitor.TIMEOUT_SECONDS = 20
monitor.MAX_TREE_RSS_MB = 512
monitor.MIN_FREE_RAM_MB = 800

MIN_START_RAM_MB = 1500

results = []

for layers in LAYER_COUNTS:

    free_mb = (
        monitor.psutil.virtual_memory().available
        / (1024 ** 2)
    )

    if free_mb < MIN_START_RAM_MB:
        print("Insufficient free RAM. Stopping.")
        break

    print(
        f"\nTesting {NUM_QUBITS} qubits, "
        f"{layers} layers"
    )

    row = monitor.benchmark(
        NUM_QUBITS,
        layers
    )

    results.append(row)

    print("Status:", row["status"])
    print("Wall time:", row["wall_time_s"], "s")
    print("Aer time:", row["aer_time_s"], "s")
    print(
        "Peak RSS:",
        row["peak_tree_rss_mb"], "MiB"
    )

    if row["status"] != "SUCCESS":
        print("Stopping at resource boundary.")
        break


if results:
    output = Path("depth_stress_results.csv")

    with output.open(
        "w", newline="", encoding="utf-8"
    ) as file:
        writer = csv.DictWriter(
            file, fieldnames=results[0].keys()
        )

        writer.writeheader()
        writer.writerows(results)

    print("\nResults saved to:", output.resolve())
