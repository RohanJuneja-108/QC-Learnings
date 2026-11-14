
import csv
from pathlib import Path

import psutil
import Resource_Monitor_V2 as monitor

# Experiment configuration
QUBITS = 18
START_LAYERS = 200
GROWTH_FACTOR = 1.5
MAX_LAYERS = 800

TIMEOUT_SECONDS = 20
MIN_START_RAM_MB = 1500

# Safety limits
monitor.TIMEOUT_SECONDS = TIMEOUT_SECONDS
monitor.MAX_TREE_RSS_MB = 512
monitor.MIN_FREE_RAM_MB = 800

results = []
layers = START_LAYERS

while layers <= MAX_LAYERS:

    free_ram_mb = (
        psutil.virtual_memory().available / 2**20
    )

    if free_ram_mb < MIN_START_RAM_MB:
        print("Low RAM. Stopping experiment.")
        break

    print(
        f"\nTesting {QUBITS} qubits, "
        f"{layers} layers"
    )

    result = monitor.benchmark(QUBITS, layers)

    result["actual_depth"] = 4 * layers + QUBITS - 3
    result["gate_count"] = layers * (3 * QUBITS - 1)

    results.append(result)

    print("Status:", result["status"])
    print("Actual depth:", result["actual_depth"])
    print("Gates:", result["gate_count"])
    print("Aer time:", result["aer_time_s"])
    print("Wall time:", result["wall_time_s"])
    print("Peak RSS:", result["peak_tree_rss_mb"])

    # Stop at first unsuccessful trial
    if result["status"] != "SUCCESS":
        print("\nBudget boundary encountered.")
        break

    # Increase depth by 50%
    next_layers = int(layers * GROWTH_FACTOR)
    layers = max(layers + 1, next_layers)

# Save even if interrupted by a resource boundary
if results:
    output = Path("adaptive_depth_results.csv")

    with output.open(
        "w", newline="", encoding="utf-8"
    ) as file:
        writer = csv.DictWriter(
            file, fieldnames=results[0].keys()
        )
        writer.writeheader()
        writer.writerows(results)

    successful = [
        row for row in results
        if row["status"] == "SUCCESS"
    ]

    if successful:
        best = max(
            successful,
            key=lambda row: row["actual_depth"]
        )

        print("\nLargest successful configuration:")
        print("Qubits:", best["qubits"])
        print("Layers:", best["layers"])
        print("Depth:", best["actual_depth"])
        print("Gates:", best["gate_count"])

    print("\nResults saved:", output.resolve())
