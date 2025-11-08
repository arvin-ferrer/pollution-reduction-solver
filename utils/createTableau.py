from utils.simplex import SimplexSolver

import numpy as np
import pandas as pd

def createTableau(costVectorC, pollutantMatrixApoll, targetVectorBpoll):
    M = 1e9
    numProjects = len(costVectorC)
    numPollutants = len(targetVectorBpoll)
    numConstraints = numPollutants + numProjects

    numVars = numProjects
    numSurplus = numPollutants
    numSlack = numProjects
    numArtificial = numPollutants

    numCols = numVars + numSurplus + numSlack + numArtificial + 2
    numRows = numConstraints + 1
    tableau = np.zeros((numRows, numCols))

    # pollutant constraints
    tableau[:numPollutants, :numProjects] = pollutantMatrixApoll
    for i in range(numPollutants):
        tableau[i, numProjects + i] = -1.0          
        tableau[i, numProjects + numSurplus + numSlack + i] = 1.0  
    tableau[:numPollutants, -1] = targetVectorBpoll

    # constraints
    for i in range(numProjects):
        rowIdx = numPollutants + i
        tableau[rowIdx, i] = 1.0
        tableau[rowIdx, numProjects + numSurplus + i] = 1.0 # slack
    tableau[numPollutants:numConstraints, -1] = 20.0 


    zRowIdx = numConstraints
    
    tableau[zRowIdx, :numProjects] = costVectorC
    
    for i in range(numArtificial):
        colIdx = numVars + numSurplus + numSlack + i
        tableau[zRowIdx, colIdx] = M
        
    tableau[zRowIdx, -2] = 1.0 # the Z' column

    for i in range(numPollutants):
        tableau[zRowIdx, :] -= M * tableau[i, :]
    # print(tableau)
    return tableau