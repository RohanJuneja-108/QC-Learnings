
import csv
import time
from pathlib import Path

import psutil
import Resource_Monitor_V2 as monitor


# ------------------------------------
# Experiment configuration
# ------------------------------------

QUBIT_COUNTS = [12, 16, 18, 20]
LAYER_COUNTS = [20, 50, 100]

REPETITIONS = 1

monitor.TIMEOUT_SECONDS = 20
monitor.MAX_TREE_RSS_MB = 512
monitor.MIN_FREE_RAM_MB = 800

MIN_START_RAM_MB = 1500

OUTPUT = Path("qubit_depth_results.csv")

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


# ------------------------------------
# Prepare CSV
# ------------------------------------

with OUTPUT.open(
    "w",
    newline="",
    encoding="utf-8"
) as file:

    writer = csv.DictWriter(
        file,
        fieldnames=FIELDNAMES
    )
    writer.writeheader()


# ------------------------------------
# Execute experiment grid
# ------------------------------------

stop_all = False

for n in QUBIT_COUNTS:

    for layers in LAYER_COUNTS:

        for repetition in range(1, REPETITIONS + 1):

            available_ram = (
                psutil.virtual_memory().available
                / (1024 ** 2)
            )

            if available_ram < MIN_START_RAM_MB:
                print(
                    "\nLow available RAM. "
                    "Stopping all experiments."
                )
                stop_all = True
                break

            print(
                f"\nTesting {n} qubits | "
                f"{layers} layers | "
                f"Run {repetition}"
            )

            result = monitor.benchmark(n, layers)

            # Valid for our particular
            # RX-RZ-CX-chain generator
            if n >= 3:
                actual_depth = 4 * layers + n - 3
            else:
                actual_depth = None

            gate_count = layers * (3 * n - 1)

            row = {
                "qubits": n,
                "layers": layers,
                "actual_depth": actual_depth,
                "gate_count": gate_count,
                "repetition": repetition,
                "status": result["status"],
                "wall_time_s": result["wall_time_s"],
                "aer_time_s": result["aer_time_s"],
                "peak_tree_rss_mb":
                    result["peak_tree_rss_mb"],
                "required_memory_mb":
                    result["required_memory_mb"],
                "method": result["method"],
                "return_code": result["return_code"],
                "error": result["error"]
            }

            # Save each trial immediately
            with OUTPUT.open(
                "a",
                newline="",
                encoding="utf-8"
            ) as file:

                writer = csv.DictWriter(
                    file,
                    fieldnames=FIELDNAMES
                )

                writer.writerow(row)

            print("Status:", row["status"])
            print("Depth:", row["actual_depth"])
            print("Gates:", row["gate_count"])
            print("Wall time:", row["wall_time_s"])
            print("Aer time:", row["aer_time_s"])
            print(
                "Peak RSS:",
                row["peak_tree_rss_mb"]
            )

            if row["status"] in {
                "LOW_SYSTEM_MEMORY",
                "MEMORY_LIMIT",
                "FAILED",
                "INVALID_OUTPUT"
            }:
                stop_all = True
                break

            if row["status"] == "TIMEOUT":
                print(
                    "Time budget exceeded; "
                    "skipping deeper circuits "
                    "at this qubit count."
                )
                break

            time.sleep(0.5)

        if stop_all:
            break

    if stop_all:
        break


print("\nBenchmark experiment completed.")
print("Results:", OUTPUT.resolve())
