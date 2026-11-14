
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("qubit_depth_results.csv")

# Keep successful measurements
success = df[df["status"] == "SUCCESS"].copy()

if success.empty:
    raise RuntimeError("No successful results to plot.")

# Median Aer execution time
matrix = success.pivot_table(
    index="layers",
    columns="qubits",
    values="aer_time_s",
    aggfunc="median"
)

matrix = matrix.sort_index(
    axis=0
).sort_index(axis=1)

fig, ax = plt.subplots(figsize=(9, 6))

heatmap = ax.imshow(
    matrix.to_numpy(),
    aspect="auto",
    interpolation="nearest"
)

ax.set_xticks(np.arange(len(matrix.columns)))
ax.set_yticks(np.arange(len(matrix.index)))

ax.set_xticklabels(matrix.columns)
ax.set_yticklabels(matrix.index)

ax.set_xlabel("Number of qubits")
ax.set_ylabel("Requested circuit layers")
ax.set_title("Quantum Circuit Simulation Time")

# Annotate each measured configuration
for i in range(len(matrix.index)):
    for j in range(len(matrix.columns)):
        value = matrix.iloc[i, j]

        if pd.notna(value):
            ax.text(
                j, i,
                f"{value:.2f}s",
                ha="center",
                va="center"
            )

fig.colorbar(
    heatmap,
    ax=ax,
    label="Median Aer execution time (seconds)"
)

plt.tight_layout()
plt.savefig(
    "qubit_depth_heatmap.png",
    dpi=200
)

plt.show()
