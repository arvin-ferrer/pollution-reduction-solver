import numpy as numpy
import pandas as pd

def simplex(tableau, is_max=True):
    tableau = tableau.astype(float)
    n, m = tableau.shape
    
    while np.min(tableau[-1, :-1]) < 0:
        pivot_col = np.argmin(tableau[-1, :-1])
        ratios = np.array([
            tableau[i, -1] / tableau[i, pivot_col] if tableau[i, pivot_col] > 0 else np.inf
            for i in range(n - 1)
        ])
        pivot_row = np.argmin(ratios)
        tableau[pivot_row, :] /= tableau[pivot_row, pivot_col]
        for i in range(n):
            if i != pivot_row:
                tableau[i, :] -= tableau[i, pivot_col] * tableau[pivot_row, :]
    
    # Extract basic variables
    solution = np.zeros(m - 1)
    for i in range(m - 1):
        col = tableau[:, i]
        if (col == 1).sum() == 1 and (col == 0).sum() == n - 1:
            solution[i] = tableau[np.where(col == 1)[0][0], -1]
    
    return solution, tableau[-1, -1], tableau