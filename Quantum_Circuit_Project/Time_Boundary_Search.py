
import csv
from pathlib import Path

import psutil
import Resource_Monitor_V2 as monitor

# Experiment setup
QUBITS = 20
LAYER_COUNTS = [120, 140, 160]
REPETITIONS = 2

# Safety settings
monitor.TIMEOUT_SECONDS = 20
monitor.MAX_TREE_RSS_MB = 512
monitor.MIN_FREE_RAM_MB = 800

MIN_START_RAM_MB = 1500

OUTPUT = Path("time_boundary_results.csv")

FIELDNAMES = [
    "qubits",
    "layers",
    "actual_depth",
    "gate_count",
    "repetition",
    "status",
    "wall_time_s",
    "aer_time_s",
    "peak_tree_rss_mb",
    "required_memory_mb",
    "method",
    "return_code",
    "error"
]

results = []

with OUTPUT.open("w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
    writer.writeheader()

stop_search = False

for layers in LAYER_COUNTS:
    for repetition in range(1, REPETITIONS + 1):

        free_ram = (
            psutil.virtual_memory().available / 2**20
        )

        if free_ram < MIN_START_RAM_MB:
            print("Insufficient free RAM. Stopping.")
            stop_search = True
            break

        print(
            f"\nTesting {QUBITS} qubits, "
            f"{layers} layers, run {repetition}"
        )

        result = monitor.benchmark(QUBITS, layers)

        row = {
            **result,
            "repetition": repetition,
            "actual_depth": 4 * layers + QUBITS - 3,
            "gate_count": layers * (3 * QUBITS - 1)
        }

        results.append(row)

        with OUTPUT.open(
            "a", newline="", encoding="utf-8"
        ) as f:
            writer = csv.DictWriter(
                f, fieldnames=FIELDNAMES
            )
            writer.writerow(row)

        print("Status:", row["status"])
        print("Depth:", row["actual_depth"])
        print("Gates:", row["gate_count"])
        print("Wall time:", row["wall_time_s"])
        print("Aer time:", row["aer_time_s"])
        print("Peak RSS:", row["peak_tree_rss_mb"])

        if row["status"] != "SUCCESS":
            print("Trial unsuccessful. Stopping search.")
            stop_search = True
            break

    if stop_search:
        break

print("\nSearch completed.")

successful = [
    row for row in results
    if row["status"] == "SUCCESS"
]

if successful:
    largest = max(
        successful,
        key=lambda r: r["actual_depth"]
    )

    print(
        "Largest successful tested depth:",
        largest["actual_depth"]
    )

print("Results saved:", OUTPUT.resolve())
