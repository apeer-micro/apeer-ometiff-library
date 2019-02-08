import itertools as it
import numpy as np

def apply2DTrafo(trafo2D, array5D, parameterDict):
    arrayOut5D = np.zeros_like(array5D)
    nT, nZ, nC, nX, nY = np.shape(arrayOut5D)

    for t, z, c in it.product(range(nT), range(nZ), range(nC)):
        arrayOut5D[t, z, c, :, :] = trafo2D(array5D[t, z, c, :, :], parameterDict)

    return arrayOut5D