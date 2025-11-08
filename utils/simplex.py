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
        
        # list to store iteration
        tableauList = []
        objectiveRowList = []
        
        iteration = 0
        
        while tableau[n, :m-1].min() < -tol:
            tableauList.append(tableau.copy())
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
                return final

            PR = np.argmin(ratios) # pivot Row

            tableau[PR, :] /= tableau[PR, PC] # normalize

            for i in range(n + 1):
                if i != PR:
                    tableau[i, :] -= tableau[i, PC] * tableau[PR, :]
        
        # add the final optimal tableau
        tableauList.append(tableau.copy())
        objectiveRowList.append(tableau[n, :].copy())
        
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
        final['objectiveRowList'] = objectiveRowList
        final['finalTableau'] = tableau
        final['basicSolution'] = basicSolution
        final['Z'] = Z
        final['status'] = 'Optimal'

        return final

# if __name__ == "__main__":
#     np.set_printoptions(precision=6, suppress=True, linewidth=150)

#     try:
#         projectsMatrixDf = pd.read_csv('../data/projects_matrix.csv')
#         pollutantTargetsDf = pd.read_csv('../data/pollutant_targets.csv')
#     except FileNotFoundError:
#         print("Test failed: Data files not found in ../data/")
#         exit()
        
#     selectedProjectNames = [
#         "Boiler Retrofit", "Traffic Signal/Flow Upgrade", "Low-Emission Stove Program",
#         "Industrial Scrubbers", "Reforestation (acre-package)", "Agricultural Methane Reduction",
#         "Clean Cookstove & Fuel Switching", "Biochar for soils (per project unit)", "Industrial VOC",
#         "Wetlands restoration", "Household LPG conversion program", "Industrial process change",
#         "Behavioral demand-reduction program"
#     ]

#     filteredProjectsDf = projectsMatrixDf[projectsMatrixDf['Project Name'].isin(selectedProjectNames)].copy()
#     filteredProjectsDf['Project Name'] = pd.Categorical(filteredProjectsDf['Project Name'], categories=selectedProjectNames, ordered=True)
#     filteredProjectsDf = filteredProjectsDf.sort_values('Project Name')

#     costVectorC = filteredProjectsDf['Costs'].values
#     pollutantColumns = ['CO2', 'NOx', 'SO2', 'PM2.5', 'CH4', 'VOC', 'CO', 'NH3', 'BC', 'N2O']
#     pollutantMatrixApoll_raw = filteredProjectsDf[pollutantColumns].values
#     targetVectorBpoll = pollutantTargetsDf.set_index('Pollutant').loc[pollutantColumns, 'Target'].values

#     tableau = createBigMTableau(costVectorC, pollutantMatrixApoll_raw.T, targetVectorBpoll)
    
#     solver = SimplexSolver()
#     num_decision_vars = len(costVectorC)
#     result = solver.solve(tableau, numVars=num_decision_vars, costVectorC=costVectorC)

#     print(f"--- Feasible Test Case ---")
    
#     if result['status'] == 'Infeasible/Unbounded':
#         print("The problem was found to be infeasible.")
#     else:
#         print(f"Total Iterations: {len(result['tableauList']) - 1}")
            
#         print("\n--- FINAL RESULT ---")
#         print(f"Status: {result['status']}")
#         print(f"Optimal Z (Calculated): {result['Z']}")
#         print("Decision variables: ", result['basicSolution'])