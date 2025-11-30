# City Pollution Reduction Solver

> **CMSC 150: Numerical & Symbolic Computation**  
> **Final Project – Optimization Decision Support System**

This project is an interactive Linear Programming (LP) solver designed to help city planners of Greenvale determine the most cost-effective combination of mitigation projects to meet strict environmental pollution targets.

It features a fully custom **Simplex Algorithm** implementation written in Python, integrated into a modern **Streamlit** dashboard with real-time visualization.

---

## Usage Guide

- 1. **Select Projects** - Choose which mitigation projects to include using the sidebar. Use Select All to simulate full-budget planning.
- 2. **Inspect Data** - 
- 3. **Click Solve** - The system constructs and iterates through the Simplex tableau.
- 4. **4. Analyze Results** 
- Optimal Solution: Minimum cost, chosen project units, pollutant reduction charts.
- Simplex Iterations: Step through every tableau iteration using a slider.
- Input Data: Inspect raw CSV tables used as the model’s basis.

---
## Problem Statement

The system models the optimization task as a **Minimization Linear Programming** problem.

### 1. Mathematical Formulation

- **Decision Variables:**
  $x_j$: number of units allocated to mitigation project $j$

- **Parameters:**
  $C_j$: cost per unit of project $j$
  $a_{ij}$: reduction of pollutant $i$ by project $j$
  $b_i$: minimum required reduction of pollutant $i$

### Objective Function

Minimize total cost:

$$
\text{Minimize } Z = \sum_{j=1}^{30} C_j x_j
$$

### Constraints

1. **Pollutant Reduction Requirements ($\ge$)**

$$
\sum_{j=1}^{30} a_{ij} x_j \ge b_i \quad \text{for } i = 1, \dots, 10
$$

2. **Project Capacity Limits**

$$
0 \le x_j \le 20 \quad \text{for } j = 1, \dots, 30
$$

---

## Installation & Setup

Follow these steps to run the project locally:

### 1. Prerequisites
- **Python 3.8+** 
- **pip**
installed on your system.

### 2. Clone the Repository

```bash
git clone git@github.com:arvin-ferrer/Project150.git
cd Project150
```
### 3. Set up a Virtual Environment (Recommended but optional)

``` 
# Windows
python -m venv venv
.\venv\Scripts\activate
# Linux
python3 -m venv venv
source venv/bin/activate
```
# Install dependencies
```
pip install -r requirements.txt
```
# Run the app
```
streamlit run main.py
```

The dashboard should automatically open in your browser at:
http://localhost:8501

## Technology Stack
```
Python: Core logic and numerical computation
NumPy: Efficient matrix operations and Simplex processing
Pandas: Data management
Streamlit: Interactive visualization dashboard
Altair: Data visualization
```