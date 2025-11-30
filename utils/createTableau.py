import numpy as np
import pandas as pd

def createTableau(costVectorC, pollutantMatrixApoll, targetVectorBpoll):
    # get the number of projects 
    numProjects = len(costVectorC)
    # get the number of pollutants
    numPollutants = len(targetVectorBpoll)
    # pollutant coeff matrix
    pollMatrix = pollutantMatrixApoll
    # the pollutant vector to target
    pollVector = targetVectorBpoll.reshape(-1, 1)
    # project limits x >= 20 transformed to -x <= -20
    limitsA = np.eye(numProjects) * -1
    # limit value 20 projects
    limitsB = np.full((numProjects, 1), -20.0)
    # stacking the pollutant matrix and the limits
    matrixLimits = np.vstack([pollMatrix, limitsA])
    # same with matrixLimits
    matrixLimitsB = np.vstack([pollVector, limitsB])
     # objective function (costs)
    costConstraint = costVectorC.reshape(1, -1)
    # transposing the matrix
    matrixLimitsT = matrixLimits.T
    costConstraintT = costConstraint.T
    negVer = -matrixLimitsB.T
    
    # adding the slack variables
    numDualVars = matrixLimitsT.shape[1] # 23 (pollutants + limits (constraints))
    numSlacks = matrixLimitsT.shape[0]   # 13 (one per project)
    
    rows = numSlacks + 1
    cols = numDualVars + numSlacks + 2
    tableau = np.zeros((rows, cols))
    # fill coefficients
    tableau[:numSlacks, :numDualVars] = matrixLimitsT
    tableau[:numSlacks, numDualVars : numDualVars + numSlacks] = np.eye(numSlacks)
    # fill rhs
    tableau[:numSlacks, -1] = costConstraintT.flatten()
    # fill objective row
    tableau[-1, :numDualVars] = negVer
    
    # fill Z column
    tableau[-1, -2] = 1.0
    return tableau
