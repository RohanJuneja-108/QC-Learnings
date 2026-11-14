
import csv
from pathlib import Path

import psutil
import Resource_Monitor_V2 as monitor

QUBITS = 18
LAYER_COUNTS = [700, 750, 800]

REPETITIONS = 2

monitor.TIMEOUT_SECONDS = 20
monitor.MAX_TREE_RSS_MB = 512
monitor.MIN_FREE_RAM_MB = 800

MIN_START_RAM_MB = 1500

results = []
stop = False

output = Path("depth_boundary_results_it2.csv")

for layers in LAYER_COUNTS:
    for repetition in range(1, REPETITIONS + 1):

        available = (
            psutil.virtual_memory().available / 2**20
        )

        if available < MIN_START_RAM_MB:
            print("Insufficient available RAM. Stopping.")
            stop = True
            break

        print(
            f"\nTesting {QUBITS} qubits | "
            f"{layers} layers | run {repetition}"
        )

        row = monitor.benchmark(QUBITS, layers)

        row["repetition"] = repetition
        row["actual_depth"] = 4 * layers + QUBITS - 3
        row["gate_count"] = layers * (3 * QUBITS - 1)

        results.append(row)

        print("Status:", row["status"])
        print("Depth:", row["actual_depth"])
        print("Gates:", row["gate_count"])
        print("Aer time:", row["aer_time_s"])
        print("Wall time:", row["wall_time_s"])
        print("Peak RSS:", row["peak_tree_rss_mb"])

        # Save after every trial
        with output.open(
            "w", newline="", encoding="utf-8"
        ) as file:
            writer = csv.DictWriter(
                file, fieldnames=results[0].keys()
            )
            writer.writeheader()
            writer.writerows(results)

        if row["status"] != "SUCCESS":
            print("Unsuccessful trial. Stopping search.")
            stop = True
            break

    if stop:
        break

print("\nBoundary refinement finished.")

successful = [
    row for row in results
    if row["status"] == "SUCCESS"
]

if successful:
    best = max(
        successful,
        key=lambda x: x["actual_depth"]
    )
    print("Largest successful tested depth:",
          best["actual_depth"])

print("Results saved:", output.resolve())
