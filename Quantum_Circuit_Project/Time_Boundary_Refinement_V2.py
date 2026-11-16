
import csv
from pathlib import Path

import psutil
import Resource_Monitor_V2 as monitor

QUBITS = 20
LAYERS = [160, 170, 180]
REPETITIONS = 5

monitor.TIMEOUT_SECONDS = 20
monitor.MAX_TREE_RSS_MB = 512
monitor.MIN_FREE_RAM_MB = 800

MIN_START_RAM_MB = 1500

OUTPUT = Path("time_boundary_refinement_v2.csv")

FIELDS = [
    "qubits", "layers", "actual_depth",
    "gate_count", "repetition", "status",
    "wall_time_s", "aer_time_s",
    "peak_tree_rss_mb", "required_memory_mb",
    "method", "return_code", "error"
]

with OUTPUT.open("w", newline="") as f:
    csv.DictWriter(f, fieldnames=FIELDS).writeheader()

stop_all = False

for layers in LAYERS:
    print(f"\n--- {QUBITS} qubits, {layers} layers ---")

    for repeat in range(1, REPETITIONS + 1):

        available = psutil.virtual_memory().available / 2**20

        if available < MIN_START_RAM_MB:
            print("Insufficient available RAM.")
            stop_all = True
            break

        result = monitor.benchmark(QUBITS, layers)

        row = {
            **result,
            "repetition": repeat,
            "actual_depth": 4 * layers + QUBITS - 3,
            "gate_count": layers * (3 * QUBITS - 1)
        }

        with OUTPUT.open("a", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=FIELDS)
            writer.writerow(row)

        print(
            f"Run {repeat}: {row['status']} | "
            f"Wall: {row['wall_time_s']} s | "
            f"Aer: {row['aer_time_s']} s | "
            f"RSS: {row['peak_tree_rss_mb']} MiB"
        )

        if row["status"] in {
            "MEMORY_LIMIT",
            "LOW_SYSTEM_MEMORY",
            "FAILED",
            "INVALID_OUTPUT"
        }:
            stop_all = True
            break

    if stop_all:
        break

print("\nExperiment finished.")
print("Results:", OUTPUT.resolve())
