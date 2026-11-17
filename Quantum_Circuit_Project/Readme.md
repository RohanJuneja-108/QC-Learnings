# How Big a Quantum Circuit Can My Laptop Simulate?

### A beginner-friendly project using Python and Qiskit Aer Statevector Simulation

**In one sentence:** This project builds the **same type of quantum circuit** at different sizes, runs it on a normal laptop, and checks how many **qubits** and **layers** can finish within a chosen time and memory budget.

> **Quick result:** Under our tested settings, we successfully validated circuits ranging from **16 qubits / 4,096 layers** to **23 qubits / 40 layers**. These are tested successful configurations, **not absolute limits of the laptop**.

## 1. What problem are we trying to solve?

A quantum circuit is a sequence of operations on qubits. We can simulate such circuits on an ordinary computer, but bigger circuits take more time and memory.

Two ways to make a circuit bigger are:

- **Width:** the number of qubits (for example, 16 vs. 20 qubits).
- **Depth:** how many steps of gate operations happen in sequence. In our code, we control the number of **repeated layers**; the *actual* circuit depth is calculated separately.

**Our question:** *For one fixed circuit design, which combinations of width and layers can this laptop simulate in 60 seconds, without crossing our chosen memory safeguards?*

This project does **not** run on quantum hardware. We use **Qiskit Aer**, which simulates quantum states on the laptop's classical **CPU**.

## 2. Which circuit did we choose, and why?

Each repeated layer follows the same pattern:

1. Apply an **RX rotation** to each qubit.
2. Apply an **RZ rotation** to each qubit.
3. Apply **CNOT gates** between neighbouring qubits in a chain.

We repeat the pattern `L` times on `n` qubits. Rotation angles are generated using a fixed random seed (`42`) to make the experiment reproducible.

**Why this particular circuit?** It is easy to generate at different sizes, includes both single-qubit and two-qubit operations, and lets us vary just **two inputs**: `n` (qubits) and `L` (layers). It is a **test circuit for benchmarking**, not a particular real-world quantum algorithm or a benchmark of every possible circuit.

For this specific, untranspiled circuit generator (when `n >= 3`):

- **Number of gates:** `G(n, L) = L × (3n − 1)`
- **Actual circuit depth:** `D(n, L) = 4L + n − 3`

For example, at **20 qubits and 370 layers**, the circuit has **21,830 gates** and **actual depth 1,497**. These formulas should be checked again if the generator is changed.

## 3. How does the project work?

```text
Choose width (n) and repeated layers (L)
                  |
                  v
        Generate the circuit
         Circuit_Generator.py
                  |
                  v
    Run CPU statevector simulation
    through Resource_Monitor_V2.py
                  |
                  v
  Record wall time, memory, and status
                  |
                  v
  Try larger/smaller layer counts to
       locate a practical boundary
                  |
                  v
      Repeat important trials
                  |
                  v
       Save CSVs and make plots
```

The main statuses mean:

- **SUCCESS:** the simulation finished within the allowed time and resources.
- **TIMEOUT:** it did not finish before the deadline; it might succeed if given more time.
- **SIMULATOR_MEMORY_REJECTED:** Aer refused the run because its estimated quantum-state memory exceeded the configured limit.
- **MEMORY_LIMIT / LOW_SYSTEM_MEMORY:** the monitor stopped the worker to protect the laptop.
- **FAILED:** another program or simulation error; it must be investigated rather than treated as proof of a hardware limit.

## 4. What settings did we use?

| Setting | Value | What it means |
|---|---|---|
| Simulator | Qiskit Aer `statevector` | Stores and updates the quantum state |
| Device | CPU | Runs on the laptop processor |
| Precision | Double | 16 bytes per complex state amplitude |
| Truncation | Disabled | Do not quietly reduce the simulated qubit count |
| Max CPU threads | 2 | Fixed simulator thread setting |
| Gate fusion | Disabled | Keeps a fixed simulation configuration |
| Time budget | **60 seconds per trial** | Deadline for the whole monitored worker run |
| Aer state-memory budget | **128 MiB** | Limit on quantum-state storage, not all program memory |
| Process-tree RSS safeguard | **512 MiB** | Separate stop threshold for monitored process RAM |
| Minimum available system RAM | **800 MiB** | During-run safety threshold |
| Minimum RAM before starting | **1,500 MiB** | Do not start when system RAM is too low |
| Repeat checks | 3 trials | Check that selected successful points are repeatable |

**Why 60 seconds?** It is a practical experimental deadline we chose. It is **not** a scientific law or a built-in limit of the laptop. Changing the deadline, computer, or simulator settings may change the results.

## 5. What did we find?

The table shows our **conservatively validated successful configurations**. “Validated” means we observed at least three successful trials under the tested conditions.

| Qubits | Repeated layers | Actual depth | Mean wall time | Successful trials |
|---:|---:|---:|---:|---:|
| 16 | 4,096 | 16,397 | 28.87 s | 3/3 |
| 18 | 1,920 | 7,695 | 51.61 s | 3/3 |
| 20 | 370 | 1,497 | 52.14 s | 4/4 |
| 22 | 60 | 259 | 38.14 s | 3/3 |
| 23 | 40 | 180 | 56.16 s | 4/4 |

**How to read this:** As width increased, we generally had to use fewer layers to get repeatable success under the 60-second deadline. This makes sense because a statevector gets much larger when we add qubits.

**Important exceptions and cautions:**

- **16 qubits:** 4,096 layers passed, but we stopped at our planned search cap. We **did not find a time limit** at this width.
- **18 qubits:** larger layer counts sometimes passed and sometimes timed out. The table shows a safer, repeatably successful point.
- **20 qubits:** 370 layers passed repeatedly; one tested 380-layer run timed out.
- **22 qubits:** 80 layers had mixed results, so we conservatively report 60 layers.
- **23 qubits:** 40 layers passed repeatedly; the tested 50-layer run timed out.

**These are not the proven maximum depths.** They are the largest configurations we chose to report after our repeat checks. Read [`FINAL_ANALYSIS.md`](FINAL_ANALYSIS.md) for the full interpretation.

## 6. Why do qubits affect memory so much?

In double-precision statevector simulation, the raw quantum-state storage is:

```text
State memory (bytes) = 16 × 2^(number of qubits)
```

| Qubits | Raw statevector memory |
|---:|---:|
| 16 | 1 MiB |
| 18 | 4 MiB |
| 20 | 16 MiB |
| 22 | 64 MiB |
| 23 | 128 MiB |
| 24 | 256 MiB |

**One extra qubit doubles the statevector storage.** Four extra qubits multiply it by 16.

However, the **whole program** needs more RAM than the statevector alone. For example, at **16 qubits and 4,096 layers**, the largest recorded process-tree RAM usage in the successful validation trials was about **450 MiB**, even though the raw statevector is only **1 MiB**. That additional memory may include Python, circuit instructions, and simulator overhead; we did not measure each contribution separately.

Our separate 128 MiB Aer memory-limit test rejected a 24-qubit circuit because its statevector needed 256 MiB. That is a **configured-budget rejection**, not proof that the laptop could never simulate 24 qubits.

## 7. See the results visually

**Largest validated depth at each tested width**

![Validated circuit depth by width](01_validated_depth_by_width.png)

**How measured execution time changes with layers**

![Wall time versus layers](02_wall_time_vs_layers.png)

**How monitored program memory changes with layers**

![Process-tree memory versus layers](03_process_memory_vs_layers.png)

**Which measured configurations succeeded or timed out**

![Measured feasibility points](04_measured_feasibility_points.png)

The last plot shows **measured points only**. Blank areas are *untested*, not automatically successful or unsuccessful.

## 8. Files and folders

**Python scripts from the original working project** (add these to this folder to make the archive runnable):

| Script | Purpose |
|---|---|
| `Circuit_Generator.py` | Builds the chosen circuit at a requested width and number of layers |
| `Resource_Monitor_V2.py` | Runs simulations in a worker process and monitors time and memory |
| `Final_Width_Depth_Benchmark.py` | Searches for successful and timed-out layer counts |
| `Final_Boundary_Validation.py` | Repeats selected configurations to check reliability |

**Results included in this folder:**

| File | Purpose |
|---|---|
| `final_boundary_raw.csv` | Every trial from the main boundary search |
| `final_boundary_summary.csv` | Original *pre-validation* search summary; keep for reference |
| `final_validation_results.csv` | Follow-up repeated trials |
| `consolidated_validated_results.csv` | Updated, final validated results table |
| `FINAL_ANALYSIS.md` | Plain-language explanation of the results and limitations |
| `01_...png` to `04_...png` | Four final figures |

> **Note:** This results package contains the documents, CSVs, and figures, but **does not yet include the four original Python source files**. Copy those from your original project directory before describing this folder as a fully runnable repository.

## 9. How can someone run it?

**Before starting:** Install Python, Qiskit, Qiskit Aer, and `psutil` in a suitable environment. On the original Windows machine, the working Conda environment is named `Circuit_Compute`.

Place the four original Python scripts in the same project folder, and check that `Resource_Monitor_V2.py` still uses the settings shown above. Avoid raising RAM limits without checking available memory.

In PowerShell:

```powershell
conda activate Circuit_Compute
python -u .\Final_Width_Depth_Benchmark.py
python -u .\Final_Boundary_Validation.py
```

The scripts write CSV results. **They can execute many trials, each with up to a 60-second deadline**, so this is not an instant smoke test. You can first test the monitor on a small circuit:

```powershell
python -c "import Resource_Monitor_V2 as m; print(m.benchmark(16, 20))"
```

If you are using a different computer, verify the limits and start conservatively. The results are **machine- and configuration-dependent**.

### Record the machine details

To make a future GitHub repository reproducible, add a `SYSTEM_INFO.md` containing your CPU, RAM, Python/Qiskit/Aer versions and power settings. On Windows:

```powershell
python --version
python -m pip show qiskit qiskit-aer psutil
Get-CimInstance Win32_Processor | Select-Object Name
Get-CimInstance Win32_ComputerSystem | Select-Object TotalPhysicalMemory
powercfg /getactivescheme
```

## 10. Takeaway

We learned how to **build a repeatable quantum circuit, simulate it with Qiskit Aer, monitor the laptop's resource usage, search for practical time limits, and explain the results using real measurements**.

**Bottom line:** The project maps *what worked within our chosen limits* for **one fixed circuit family on one laptop**. It does not claim to find the absolute maximum circuit size for every quantum circuit or computer.
