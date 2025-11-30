import numpy as np
import pandas as pd

def createTableau(costVectorC, pollutantMatrixApoll, targetVectorBpoll):
    # get the number of projects 
    numProjects = len(costVectorC)
    # get the number of pollutants
    numPollutants = len(targetVectorBpoll)
    # pollutant coeff matrix
    A_poll = pollutantMatrixApoll
    # the pollutant vector to target
    b_poll = targetVectorBpoll.reshape(-1, 1)
    # project limits x >= 20 transformed to -x <= -20
    A_limits = np.eye(numProjects) * -1
    # limit value 20 projects
    b_limits = np.full((numProjects, 1), -20.0)
    # stacking the pollutant matrix and the limits
    A_total = np.vstack([A_poll, A_limits])
    # same with A_total
    b_total = np.vstack([b_poll, b_limits])
     # objective function (costs)
    c_total = costVectorC.reshape(1, -1)
    # transposing the matrix
    A_dual = A_total.T
    b_dual = c_total.T
    c_dual = -b_total.T
    
    # adding the slack variables
    numDualVars = A_dual.shape[1] # 23 (pollutants + limits (constraints))
    numSlacks = A_dual.shape[0]   # 13 (one per project)
    
    rows = numSlacks + 1
    cols = numDualVars + numSlacks + 2
    tableau = np.zeros((rows, cols))
    # fill coefficients
    tableau[:numSlacks, :numDualVars] = A_dual
    tableau[:numSlacks, numDualVars : numDualVars + numSlacks] = np.eye(numSlacks)
    # fill rhs
    tableau[:numSlacks, -1] = b_dual.flatten()
    # fill objective row
    tableau[-1, :numDualVars] = c_dual
    
    # fill Z column
    tableau[-1, -2] = 1.0
    return tableau
