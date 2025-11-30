import numpy as np
import pandas as pd
class SimplexSolver:
    def __init__(self):
        pass

    def solve(self, tableau, numVars, costVectorC):
        tableau = tableau.copy()
        n, m = tableau.shape # get the number of rows and cols of the tableau
        n -= 1  

        final = {} 
        
        tableauList = []
        objectiveRowList = []
        basicSolutions = [] 
        
        max_iter = 1000
        iteration = 0
        
        while tableau[n, :m-1].min() < 0 and iteration < max_iter:
            
            tableauList.append(tableau.copy())
            objectiveRowList.append(tableau[n, :].copy())
            
         
            basicSolutions.append(tableau[n, :].copy()) 
         
            iteration += 1
            
            PC = np.argmin(tableau[n, :m-1]) 
            
            ratios = np.full(n, np.inf)
            for i in range(n):
                if tableau[i, PC] > 0:
                    ratios[i] = tableau[i, -1] / tableau[i, PC]

            if np.all(np.isinf(ratios)):
                final['status'] = 'Infeasible'
                final['finalTableau'] = tableau
                final['basicSolution'] = tableau[n, :]
                final['Z'] = np.inf
                final['tableauList'] = tableauList
                final['objectiveRowList'] = objectiveRowList 
                final['basicSolutions'] = basicSolutions
                return final

            PR = np.argmin(ratios) 

            tableau[PR, :] /= tableau[PR, PC]

            for i in range(n + 1):
                if i != PR:
                    tableau[i, :] -= tableau[i, PC] * tableau[PR, :]
        
        tableauList.append(tableau.copy())
        objectiveRowList.append(tableau[n, :].copy())
        
        # store the final full row
        basicSolutions.append(tableau[n, :].copy()) 
        
        # for the solution table 
        slack_start_col = m - 2 - numVars
        final_primal_solution = tableau[n, slack_start_col : m-2]
        
        Z = tableau[n, -1]

        final['tableauList'] = tableauList
        final['objectiveRowList'] = objectiveRowList
        final['basicSolutions'] = basicSolutions 
        final['finalTableau'] = tableau
        final['basicSolution'] = final_primal_solution #for the charts
        final['Z'] = Z
        final['status'] = 'Optimal'

        return final