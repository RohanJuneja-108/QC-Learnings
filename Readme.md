# Quantum Computing & AI Exploration Lab

Welcome to my development repository! This project serves as my foundational sandbox for a long journey into Problem Solving, Backend APIs, Machine Learning, Deep Learning, Generative AI, AI Agents, and Quantum Computing (Qiskit, PennyLane, QuTiP).

## 🛠️ Environment Setup

To ensure stability and prevent dependency conflicts across different projects, this repository uses isolated virtual environments.

*   **OS:** Windows (PowerShell)
*   **IDE:** Visual Studio Code (VS Code)
*   **Python Version:** 3.13.3 (Selected globally and locally)
*   **Virtual Environment:** `Exploratory1_QC`

### Core VS Code Extensions Installed
*   **Python** (Microsoft) - For language support and IntelliSense (Pylance).
*   **Jupyter** (Microsoft) - For running interactive `.ipynb` notebooks natively inside VS Code.

## 📦 Installed Packages (Quantum Toolbox)

The `Exploratory1_QC` environment was created specifically to isolate our quantum computing tools. The following packages were installed:
*   `qiskit` (Core quantum SDK)
*   `qiskit[visualization]` (Matplotlib and dependencies for drawing circuits)
*   `qiskit-aer` (High-performance local quantum simulator)
*   `qiskit-ibm-runtime` (Client for connecting to real IBM Quantum computers)
*   `qiskit-optimization` (For solving QUBO and optimization problems)
*   `jupyter` (Execution engine for notebooks)

## 🚀 How to Run the Code

### 1. Activate the Environment
Before running any code, always ensure the virtual environment is activated in your terminal:
```powershell
.\Exploratory1_QC\Scripts\activate


```
# 🧠 Why VS Code is the Most Balanced Choice for This Long Journey

- **Lightweight and fast:** VS Code uses a fraction of the RAM and starts in
  seconds, which matters when you are running heavy ML models or quantum
  simulations locally.

- **Genuinely open-source and GitHub-native:** Git is built into the interface,
  making commit, push, and pull workflows seamless for your public repositories.

- **Excellent Jupyter and notebook support:** Critical for ML/DL
  experimentation, data exploration, and Generative AI prototyping.

- **Rich quantum ecosystem:** Extensions and community tools exist for Qiskit,
  PennyLane, Cirq, and QuTiP—including circuit visualization and syntax
  highlighting. You can also install the official Qiskit Code Assistant
  extension.

- **Polyglot flexibility:** You will eventually mix Python with shell scripts,
  Dockerfiles, YAML, and possibly JavaScript for agent interfaces; VS Code
  handles all of these natively.

- **Remote and Dev Containers:** Later, when you need to train models on a GPU
  server or run quantum simulations on a cluster, VS Code's Remote-SSH and
  Dev Containers keep your local setup light.


  ## 01 · Python 3.10 or Newer

Check what you already have before installing anything. Run this command to
see your current version:

```bash
python --version
```

If the command prints 3.10 or higher, you are done with this step.
Note: Qiskit raises its minimum Python version over time, so if you are
installing fresh, take the current version rather than an old one


# Set Up a Python Environment for Qiskit

## 1. Create the virtual environment

```bash
python -m venv .venv
```

## 2. Activate it in Windows PowerShell

```powershell
.\.venv\Scripts\Activate.ps1
```

You should see `(.venv)` appear in green at the start of your terminal prompt.

## 3. Install Qiskit

```bash
pip install --upgrade pip
pip install qiskit[visualization] qiskit-aer qiskit-ibm-runtime
```

## 4. Test that Qiskit works

Create a new file called `qiskit_test.py`, paste this code inside, and run it.

```python
import qiskit

print("Qiskit version:", qiskit.__version__)
```

If it prints the version without errors, you have successfully set up a professional Python environment for Quantum Computing. Welcome to the journey!


# Why Do We Need a Virtual Environment in Python?

**A virtual environment is a separate, isolated toolbox for each project.**

If you don't use one, you will eventually run into massive headaches, especially with Machine Learning, AI, and Quantum Computing. Here is exactly why it is needed for your long journey.

## 1. The "Dependency Hell" Problem

Imagine you are working on two different projects:

- **Project A (Quantum):** Requires `Qiskit version 1.0` and `NumPy version 1.2`.
- **Project B (Machine Learning):** Requires `PyTorch` and `NumPy version 2.0`.

If you install everything into your **Global System Python** (the 3.13.3 you just downloaded), Project A and Project B will fight over `NumPy`. One of your projects may break because of incompatible dependencies. Python cannot have two versions of the same library installed in the same global environment at the same time.

With a **Virtual Environment**, Project A gets its own folder with its own `NumPy` version, and Project B gets a different folder with its own `NumPy` version. They remain isolated from each other, and your main Windows Python installation stays clean.

## 2. GitHub and Sharing Your Work

You mentioned earlier that you want to push and pull code on GitHub.

If you install 50 heavy AI/Quantum libraries globally, how will someone else know which versions you used to run your code?

With a virtual environment, you can generate a text file called `requirements.txt`. Anyone who downloads your GitHub repository can install the listed dependencies to recreate a similar environment.

For example:

```bash
pip freeze > requirements.txt
```

Another developer can install the dependencies using:

```bash
pip install -r requirements.txt
```

**Important:** A virtual environment helps isolate dependencies, while `requirements.txt` records package versions. For truly reproducible setups, you may also need to specify the Python version and account for operating-system-specific dependencies.

## 3. The Libraries You Are Using Are HUGE

Quantum simulators such as Qiskit Aer, deep learning frameworks such as PyTorch, and AI agent frameworks can install many supporting packages.

Virtual environments keep project dependencies separate, making projects easier to manage and reducing conflicts between them.

However, they do not necessarily make your base Python installation faster or reduce the total disk space used. Each environment can consume additional disk space.

## 4. It Helps Prevent Dependency-Related Errors

If your global Python environment contains old packages, installing new ones may fail because of version conflicts.

A fresh virtual environment gives you a clean starting point for installing project-specific packages.

It does not guarantee that every installation will succeed, but it makes dependency conflicts easier to isolate and troubleshoot.

## Final takeaway

**Global Python** is your main Python installation.

**Virtual environment (`.venv`)** is an isolated workspace for a particular project.

**`requirements.txt`** records the Python packages and versions needed by your project.

For your Quantum Computing, Machine Learning, and AI projects, creating a separate virtual environment for each project is a good habit to develop from the beginning.



# 1. Create the Environment

```bash
python -m venv Exploratory1_QC
```

*(When you press Enter, look at the left sidebar in VS Code. You will see a new folder named `Exploratory1_QC` appear!)*

## 2. Activate It Manually (Just to See How It Works)

Because you changed the name, the activation command changes too:

```powershell
.\Exploratory1_QC\Scripts\Activate.ps1
```
or if above shows the error Try 
```powershell
.\Exploratory1_QC\Scripts\activate
```
You will now see `(Exploratory1_QC)` in green at the start of your terminal line.

## 3. Tell VS Code to Use It

Just like before, press `Ctrl + Shift + P`, type `Python: Select Interpreter`, and choose the one that says:

```text
Python 3.13.3 ('Exploratory1_QC': venv)

```
Look at the list. You should now see an option that says Python 3.13.3 ('Exploratory1_QC': venv). Click it.

## 💡 Quick Tip for the Future

Most Python developers stick to naming their virtual environment `.venv` (with the dot). Why? Because if you upload this project to GitHub, `.venv` is a common name that Git tools and project templates can be configured to ignore, and VS Code recognizes it as a virtual environment.

**Important:** Make sure your `.gitignore` file contains:

```gitignore
.venv/
Exploratory1_QC/
```

This prevents your virtual environment files from being uploaded to GitHub.


# 📁 Where to Create the File

Create it in your current folder (`Hackathons`), **NOT inside the `Exploratory1_QC` folder.**

Here is the golden rule of virtual environments:

- `Exploratory1_QC` is your **Toolbox** (it holds Python, the Qiskit libraries, and internal system files). You almost never put your own code inside this folder.

- `Hackathons` is your **Workspace** (this is where your actual projects, scripts, and notebooks live).

## Example Folder Structure

```text
Hackathons/
│
├── Exploratory1_QC/       # Virtual environment (Toolbox)
│   ├── Scripts/
│   ├── Lib/
│   └── pyvenv.cfg
│
├── qiskit_test.py         # Your Python code
├── main.py                # Your project code
└── .gitignore             # Files Git should ignore
```

**Remember:** Activate the virtual environment, but create and run your Python files from your `Hackathons` workspace. This keeps your project code separate from the environment's internal files.


Once you have created test_qiskit.py, paste this code into it and save (Ctrl+S):

```python
from qiskit import QuantumCircuit
import qiskit

print(f"Qiskit version installed: {qiskit.__version__}")

# Create a simple 2-qubit circuit
qc = QuantumCircuit(2)

qc.h(0)       # Add a Hadamard gate to qubit 0
qc.cx(0, 1)   # Add a CNOT gate

# Draw the circuit
print("Here is your quantum circuit:")
print(qc.draw(output='text'))
```


## To Run It

You have two options. Both are completely safe because we have already pointed VS Code to your new environment.

- **Option A:** Click the **Play button (▶)** in the top-right corner of the editor.

- **Option B:** Go to your terminal (where `(Exploratory1_QC)` is active) and type:

```powershell
python test_qiskit.py
```

## Your Three Python Toolboxes

- **Toolbox 1 (`Exploratory1_QC`):** Has Qiskit, Aer, and IBM Runtime. It's your Quantum Computing toolbox.

- **Toolbox 2 (to be created later):** Will have PyTorch, TensorFlow, and Transformers for your Machine Learning and Generative AI work.

- **Toolbox 3 (to be created later):** Will have FastAPI and Uvicorn for your Backend API work.

They all live on the same computer, but their Python packages remain isolated from one another.

If Qiskit needs an older version of a math library, it can use the version installed in its own environment without interfering with your ML project, which might need a newer version.

**This is exactly why professionals use virtual environments:** to keep project dependencies separate, reduce version conflicts, and make projects easier to maintain.

# Setting Up Jupyter Notebooks in VS Code for Quantum Computing

This guide will walk you through installing Jupyter, setting it up in VS Code, and running a final test to prove that VS Code, Jupyter, and your `Exploratory1_QC` environment are all communicating perfectly.

## 1. Installation and Setup

### Step 1: Install Jupyter in Your Existing Toolbox
You don't need to create anything new. Simply run this command inside your activated `Exploratory1_QC` environment. This adds Jupyter's core engine to your quantum toolbox.

```powershell
pip install jupyter
```

# Setting Up Jupyter Notebooks in VS Code for Quantum Computing

This guide walks you through installing Jupyter, setting it up in VS Code, and running a final test to prove that VS Code, Jupyter, and your `Exploratory1_QC` environment are all communicating properly.

## 1. Installation and Setup

### Step 1: Install Jupyter in Your Existing Environment

You don't need to create anything new. Run this command inside your activated `Exploratory1_QC` environment. It adds Jupyter's core engine to your quantum toolbox.

```powershell
pip install jupyter
```

### Step 2: Install the VS Code Extension

In VS Code, open the Extensions view (`Ctrl+Shift+X`) and install the **Jupyter** extension by Microsoft.

> **Note:** The Jupyter (Microsoft) extension lets VS Code open `.ipynb` files, connect to your `Exploratory1_QC` kernel, and run cells. This is what turns VS Code into a powerful notebook editor.

### Step 3: Create Your First Notebook

In your `Hackathons` folder, create a new file ending in `.ipynb` (e.g., `first_quantum_notebook.ipynb`). VS Code will automatically open it in its notebook interface.

In the top-right corner, select your `Exploratory1_QC` environment as the **Kernel**.

---

### Why you still need `pip install jupyter` if you are using VS Code

You might be thinking: *"I have VS Code, why install Jupyter?"*

VS Code is just an editor. By itself, it doesn't know how to execute `.ipynb` files. When you run `pip install jupyter` inside your `Exploratory1_QC` environment, you install the **Jupyter kernel** (the execution engine).

Then you install the **Jupyter extension** in VS Code. This allows VS Code to use the engine you just installed to run the notebook *without ever opening a web browser*, which keeps your workspace clean.

---

## 2. The Final Test

This test proves that everything is working.

### 1. Create a Notebook File

1. In VS Code, look at the left sidebar (Explorer) in the `Hackathons` folder.
2. Click the **New File** icon (the little paper with a `+`).
3. Name the file **`test_notebook.ipynb`**. The `.ipynb` extension is crucial: it tells VS Code this is a Jupyter Notebook.
4. When it opens, you will see an empty cell waiting for code.

### 2. Connect the Environment (Select Kernel)

Look at the **top-right corner** of the notebook editor. You will see a button that says **Select Kernel** (or it may say something like "Python 3.13.3").

1. Click it.
2. A dropdown appears at the top of the screen. Choose **Python Environments** (or **Jupyter Kernel**).
3. Select **`Exploratory1_QC`**.

### 3. Paste and Run the Code

Click inside the empty cell and paste this code:

```python
import qiskit
from qiskit import QuantumCircuit

# Create a simple quantum circuit
qc = QuantumCircuit(2)
qc.h(0)
qc.cx(0, 1)

print(f"Qiskit version: {qiskit.__version__}")
print("Jupyter Notebook is working perfectly!")
```

### 4. Execute the Cell

Look at the **left side of the code cell**. You will see a small **Play icon (▷)** next to the line numbers. Click it, or press **`Shift + Enter`**.

### 5. The Output Test

Once you run the cell, a spinning circle appears while it executes, then the output appears directly underneath the code.

Now let's test visualization. Click the **`+ Code`** button at the top of the notebook to add a new cell below the first one. Paste this and run it:

```python
# Draw the circuit visually using matplotlib
qc.draw('mpl')
```

Because you installed `qiskit[visualization]`, this should render a colorful diagram of the circuit right inside your notebook.

If you see both the text output and the circuit diagram, **your setup is working.**