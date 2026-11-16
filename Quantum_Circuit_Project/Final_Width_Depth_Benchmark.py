
import csv
from pathlib import Path

import psutil
import Resource_Monitor_V2 as monitor

# =====================================
# FINAL EXPERIMENT CONFIGURATION
# =====================================

WIDTHS = [16, 18, 20, 22, 23]

TIME_BUDGET_S = 60
STATE_MEMORY_BUDGET_MIB = 128

MAX_LAYERS = 4096
START_LAYERS = 20
LAYER_RESOLUTION = 10

VALIDATION_RUNS = 3

MIN_START_RAM_MIB = 1500

monitor.TIMEOUT_SECONDS = TIME_BUDGET_S
monitor.MAX_TREE_RSS_MB = 512
monitor.MIN_FREE_RAM_MB = 800

RAW_FILE = Path("final_boundary_raw.csv")
SUMMARY_FILE = Path("final_boundary_summary.csv")

raw_rows = []
summary_rows = []


def state_memory_mib(n):
    return 16 * 2**n / 2**20


def actual_depth(n, layers):
    # Valid for our fixed RX-RZ-CNOT
    # chain circuit, n >= 3.
    return 4 * layers + n - 3


def save_csv(path, rows):
    if not rows:
        return

    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=rows[0].keys()
        )
        writer.writeheader()
        writer.writerows(rows)


def run_trial(n, layers, trial):
    available = psutil.virtual_memory().available / 2**20

    if available < MIN_START_RAM_MIB:
        raise RuntimeError(
            "Insufficient free system RAM to continue safely."
        )

    result = monitor.benchmark(n, layers)

    status = result.get("status", "UNKNOWN")
    error = str(result.get("error") or "")

    # Recognize Aer memory-budget rejection.
    if (
        "Insufficient memory to run circuit" in error
        or status == "SIMULATOR_MEMORY_REJECTED"
    ):
        status = "SIMULATOR_MEMORY_REJECTED"

    row = {
        "qubits": n,
        "layers": layers,
        "actual_depth": actual_depth(n, layers),
        "trial": trial,
        "status": status,
        "wall_time_s": result.get("wall_time_s"),
        "peak_tree_rss_mb": result.get(
            "peak_tree_rss_mb"
        ),
        "required_memory_mb": result.get(
            "required_memory_mb"
        ),
        "simulated_qubits": result.get(
            "simulated_qubits"
        ),
        "error": error[-300:]
    }

    raw_rows.append(row)
    save_csv(RAW_FILE, raw_rows)

    print(
        f"  n={n}, layers={layers}, trial={trial}"
        f" -> {status}, "
        f"time={row['wall_time_s']}s",
        flush=True
    )

    return status


def check_point(n, layers, repeats=1):
    statuses = [
        run_trial(n, layers, i + 1)
        for i in range(repeats)
    ]

    allowed = {"SUCCESS", "TIMEOUT"}

    if any(s not in allowed for s in statuses):
        raise RuntimeError(
            f"Unexpected result at n={n}, layers={layers}: "
            f"{statuses}. Check final_boundary_raw.csv"
        )

    # All repeated trials must succeed
    # for a configuration to be validated.
    return all(s == "SUCCESS" for s in statuses)


def search_width(n):
    print(
        f"\n{'=' * 48}\n"
        f"SEARCHING {n} QUBITS\n"
        f"{'=' * 48}",
        flush=True
    )

    required = state_memory_mib(n)

    if required > STATE_MEMORY_BUDGET_MIB:
        print("Skipping: exceeds state-memory budget.")

        return {
            "qubits": n,
            "memory_mib": required,
            "largest_validated_layers": None,
            "largest_validated_depth": None,
            "first_timeout_layers": None,
            "boundary_state": "MEMORY_BUDGET_EXCEEDED"
        }

    low = 0
    high = None
    layers = START_LAYERS

    # PHASE A: Find initial success / timeout bracket.
    while layers <= MAX_LAYERS:
        success = check_point(n, layers)

        if success:
            low = layers
            layers *= 2
        else:
            high = layers
            break

    # PHASE B: Refine the bracket.
    if high is not None:
        while high - low > LAYER_RESOLUTION:
            midpoint = (low + high) // 2

            # Round down to a multiple of 10.
            midpoint = (
                midpoint // LAYER_RESOLUTION
            ) * LAYER_RESOLUTION

            if midpoint <= low:
                break

            if check_point(n, midpoint):
                low = midpoint
            else:
                high = midpoint

    # PHASE C: Validate final candidate.
    if low > 0:
        validated = check_point(
            n, low, repeats=VALIDATION_RUNS
        )

        if not validated:
            print(
                "Validation was inconsistent; "
                "the boundary remains uncertain."
            )

            return {
                "qubits": n,
                "memory_mib": required,
                "largest_validated_layers": None,
                "largest_validated_depth": None,
                "first_timeout_layers": high,
                "boundary_state": "UNCERTAIN"
            }

    if high is None:
        state = "NOT_REACHED_WITHIN_LAYER_CAP"
    else:
        state = "BRACKETED"

    return {
        "qubits": n,
        "memory_mib": required,
        "largest_validated_layers": low or None,
        "largest_validated_depth": (
            actual_depth(n, low) if low else None
        ),
        "first_timeout_layers": high,
        "boundary_state": state
    }


if __name__ == "__main__":
    try:
        for width in WIDTHS:
            summary = search_width(width)

            summary_rows.append(summary)
            save_csv(SUMMARY_FILE, summary_rows)

            print("\nCURRENT SUMMARY")
            print(summary, flush=True)

    except (KeyboardInterrupt, RuntimeError) as exc:
        print("\nBenchmark stopped:", exc, flush=True)

    finally:
        save_csv(RAW_FILE, raw_rows)
        save_csv(SUMMARY_FILE, summary_rows)

        print("\nPartial/final results saved.")
        print("Raw:", RAW_FILE.resolve())
        print("Summary:", SUMMARY_FILE.resolve())
