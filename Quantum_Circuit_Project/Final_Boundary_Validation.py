
import csv
from pathlib import Path

import psutil
import Resource_Monitor_V2 as monitor

monitor.TIMEOUT_SECONDS = 60
monitor.MAX_TREE_RSS_MB = 512
monitor.MIN_FREE_RAM_MB = 800

MIN_START_RAM_MB = 1500
REPEATS = 3

OUTPUT = Path("final_validation_results.csv")

# Candidate widths and depths.
# Each fallback is used only if the first
# candidate does not pass all three trials.
TESTS = {
    16: [4096],
    18: [1920, 1600],
    22: [80, 60],
}

rows = []


def save_results():
    if not rows:
        return

    with OUTPUT.open(
        "w", newline="", encoding="utf-8"
    ) as file:
        writer = csv.DictWriter(
            file, fieldnames=rows[0].keys()
        )
        writer.writeheader()
        writer.writerows(rows)


def run_candidate(qubits, layers):
    successes = 0

    for trial in range(1, REPEATS + 1):
        available = (
            psutil.virtual_memory().available / 2**20
        )

        if available < MIN_START_RAM_MB:
            raise RuntimeError(
                "Available RAM below safety threshold."
            )

        result = monitor.benchmark(qubits, layers)
        status = result["status"]

        row = {
            "qubits": qubits,
            "layers": layers,
            "actual_depth": 4 * layers + qubits - 3,
            "trial": trial,
            "status": status,
            "wall_time_s": result.get("wall_time_s"),
            "peak_tree_rss_mb": result.get(
                "peak_tree_rss_mb"
            ),
            "error": result.get("error", "")[-300:],
        }

        rows.append(row)
        save_results()

        print(
            f"{qubits} qubits | "
            f"{layers} layers | "
            f"Trial {trial}/{REPEATS} | "
            f"{status} | "
            f"{row['wall_time_s']}s",
            flush=True,
        )

        if status == "SUCCESS":
            successes += 1

        elif status != "TIMEOUT":
            raise RuntimeError(
                f"Unexpected failure: {status}. "
                "Inspect final_validation_results.csv"
            )

    return successes


def main():
    for qubits, candidates in TESTS.items():
        print(f"\n{'=' * 42}")
        print(f"VALIDATING {qubits} QUBITS")
        print("=" * 42, flush=True)

        for layers in candidates:
            successes = run_candidate(qubits, layers)

            print(
                f"Result: {successes}/{REPEATS} "
                f"successful runs",
                flush=True,
            )

            if successes == REPEATS:
                print(
                    f"Validated candidate: "
                    f"{qubits} qubits, {layers} layers"
                )
                break
        else:
            print(
                f"No additional candidate validated "
                f"for {qubits} qubits."
            )


if __name__ == "__main__":
    try:
        main()
    except (RuntimeError, KeyboardInterrupt) as error:
        print("\nExperiment stopped:", error)
    finally:
        save_results()
        print("\nResults saved:", OUTPUT.resolve())
