
import pandas as pd
import matplotlib.pyplot as plt

# Load benchmark results
df = pd.read_csv("benchmark_results.csv")

# Keep successful simulations
success = df[df["status"] == "SUCCESS"].copy()

# Convert seconds to milliseconds
success["simulation_time_ms"] = (
    success["simulation_time_s"] * 1000
)

# Group repeated experiments
summary = (
    success.groupby(["qubits", "layers"])
    .agg(
        depth=("depth", "first"),
        gates=("gates", "first"),
        median_time_ms=("simulation_time_ms", "median"),
        mean_time_ms=("simulation_time_ms", "mean"),
        std_time_ms=("simulation_time_ms", "std"),
        repetitions=("simulation_time_ms", "count")
    )
    .reset_index()
)

print("\nBenchmark Summary:")
print(summary.to_string(index=False))

# Plot 1: Simulation time vs layers
plt.figure(figsize=(9, 5))

for n, group in summary.groupby("qubits"):
    group = group.sort_values("layers")

    plt.plot(
        group["layers"],
        group["median_time_ms"],
        marker="o",
        label=f"{n} qubits"
    )

plt.xlabel("Requested circuit layers")
plt.ylabel("Median simulation time (ms)")
plt.title("Quantum Circuit Depth Scaling")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig("depth_scaling.png", dpi=200)
plt.show()

# Plot 2: Simulation time vs qubits
plt.figure(figsize=(9, 5))

for layers, group in summary.groupby("layers"):
    group = group.sort_values("qubits")

    plt.plot(
        group["qubits"],
        group["median_time_ms"],
        marker="o",
        label=f"{layers} layers"
    )

plt.xlabel("Number of qubits")
plt.ylabel("Median simulation time (ms)")
plt.title("Quantum Circuit Width Scaling")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig("qubit_scaling.png", dpi=200)
plt.show()

# Save aggregated results
summary.to_csv("benchmark_summary.csv", index=False)

print("\nAnalysis complete.")
