import numpy as np
import pandas as pd
class SimplexSolver:
    def __init__(self):
        pass
    def extract_basic_solution(self, tableau, numVars):
        n, m = tableau.shape
        n -= 1  # number of constraint rows
        sol = np.zeros(m - 1)

        for j in range(m - 1):
            col = tableau[:n, j]  # only constraint rows
            if np.sum(col == 1) == 1 and np.sum(col == 0) == (n - 1):
                row_index = np.where(col == 1)[0][0]
                sol[j] = tableau[row_index, -1]  # RHS value
        Z = tableau[n, -1]
        finalSol = np.append(sol, Z)
        return finalSol

    def solve(self, tableau, numVars, costVectorC):
        tableau = tableau.copy()
        n, m = tableau.shape # get the number of rows and cols of the tableau
        n -= 1  
        # setting up the solutions 
        final = {} 
        tableauList = []
        objectiveRowList = []
        basicSolutions = [] 
        
        maxIter = 1000
        iteration = 0
        # gaussian to solve for the minimization  
        while tableau[n, :m-1].min() < 0 and iteration < maxIter:
            # append the tableau and objective row per iteration
            tableauList.append(tableau.copy())
            objectiveRowList.append(tableau[n, :].copy())
            
            # basicSolutions.append(tableau[n, :].copy()) 
            basicSolutions.append(self.extract_basic_solution(tableau, numVars))

            iteration += 1
            # getting the pivot column
            PC = np.argmin(tableau[n, :m-1]) 
            ratios = np.full(n, np.inf)
            # normalize
            for i in range(n):
                if tableau[i, PC] > 0:
                    ratios[i] = tableau[i, -1] / tableau[i, PC]
            # check if infeasible if there division by zero if there's a inf value
            if np.all(np.isinf(ratios)):
                final['status'] = 'Infeasible'
                final['finalTableau'] = tableau
                final['basicSolution'] = tableau[n, :]
                final['Z'] = np.inf
                final['tableauList'] = tableauList
                final['objectiveRowList'] = objectiveRowList 
                final['basicSolutions'] = basicSolutions
                return final
            # getting the pivot row
            PR = np.argmin(ratios) 
            # normalize
            tableau[PR, :] /= tableau[PR, PC]
            for i in range(n + 1):
                if i != PR:
                    tableau[i, :] -= tableau[i, PC] * tableau[PR, :]
        # adding the latest tableau and objective row
        tableauList.append(tableau.copy())
        objectiveRowList.append(tableau[n, :].copy())
        
        # store the basic solutions
        basicSolutions.append(tableau[n, :].copy()) 
        
        # for the solution table 
        slack_start_col = m - 2 - numVars
        finalSol = tableau[n, slack_start_col : m-2]
        # final cost
        Z = tableau[n, -1]  

        final['tableauList'] = tableauList
        final['objectiveRowList'] = objectiveRowList
        final['basicSolutions'] = basicSolutions 
        final['finalTableau'] = tableau
        final['basicSolution'] = finalSol #for the charts
        final['Z'] = Z
        final['status'] = 'Optimal'

        return final