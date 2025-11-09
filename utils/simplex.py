import numpy as np
import pandas as pd

class SimplexSolver:
    def __init__(self):
        pass
    def solve(self, tableau, numVars, costVectorC, tol=1e-9):

        tableau = tableau.copy()
        n, m = tableau.shape
        n -= 1  # last row is objective function

        final = {} # dictionary to store results
        
        # list to store each iteration
        tableauList = []
        objectiveRowList = []
        basicSolutions = []
        
        iteration = 0
        
        while tableau[n, :m-1].min() < -tol:
            # Store the objective row *before* pivoting
            objectiveRowList.append(tableau[n, :].copy())
            iteration += 1
            
            PC = np.argmin(tableau[n, :m-1]) # pivot Column
            
            ratios = np.full(n, np.inf)
            for i in range(n):
                if tableau[i, PC] > tol:
                    ratios[i] = tableau[i, -1] / tableau[i, PC]

            if np.all(np.isinf(ratios)):
                final['status'] = 'Infeasible'
                final['finalTableau'] = tableau
                final['basicSolution'] = np.zeros(numVars)
                final['Z'] = np.inf
                final['tableauList'] = tableauList
                final['objectiveRowList'] = objectiveRowList 
                final['basicSolutions'] = basicSolutions # add the new list
                return final

            PR = np.argmin(ratios) # pivot Row

            tableau[PR, :] /= tableau[PR, PC] # normalize

            for i in range(n + 1):
                if i != PR:
                    tableau[i, :] -= tableau[i, PC] * tableau[PR, :]
            
            
            tableauList.append(tableau.copy())
            basicSolutions.append(tableau[n, :].copy()) # Store last row


        # add the final optimal tableau
        tableauList.append(tableau.copy())
        objectiveRowList.append(tableau[n, :].copy())
        
        # add the final objective row to the basicSolutions list
        basicSolutions.append(tableau[n, :].copy())
        
        # extracting the final solution 
        basicSolution = np.zeros(numVars)
        for j in range(numVars):
            col = tableau[:n, j]
            ones = np.isclose(col, 1, atol=tol)
            zeros = np.isclose(col, 0, atol=tol)
            if ones.sum() == 1 and zeros.sum() == n - 1:
                rowIdx = np.where(ones)[0][0]
                basicSolution[j] = tableau[rowIdx, -1]
        
        # calculate Z from the original costs
        Z = np.dot(basicSolution, costVectorC)

        final['tableauList'] = tableauList
        final['basicSolutions'] = basicSolutions 
        final['finalTableau'] = tableau
        final['basicSolution'] = basicSolution
        final['Z'] = Z
        final['status'] = 'Optimal'

        return final 

