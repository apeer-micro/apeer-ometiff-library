import itertools as it
import numpy as np

def apply2DTrafo(trafo2D, array5D, inputs):
    arrayOut5D = _init_output_array(array5D)

    for t, z, c in it.product(range(nT), range(nZ), range(nC)):
        arrayOut5D[t, z, c, :, :] = trafo2D(array5D[t, z, c, :, :], inputs)

    return arrayOut5D


def apply3DTrafo_ZStack(trafo3D, array5D, inputs):
    arrayOut5D = _init_output_array(array5D)

    for t, c in it.product(range(nT), range(nC)):
        arrayOut5D[t, :, c, :, :] = trafo3D(array5D[t, :, c, :, :], inputs)

    return arrayOut5D


def apply3DTrafo_RGB(trafo3D, array5D, inputs):
    arrayOut5D = _init_output_array(array5D)

    for t, z in it.product(range(nT), range(nZ)):
        arrayOut5D[t, z, :, :, :] = trafo3D(array5D[t, z, :, :, :], inputs)

    return arrayOut5D


def _init_output_array(input_array5D):
    arrayOut5D = np.zeros_like(array5D)
    nT, nZ, nC, nX, nY = np.shape(arrayOut5D)
    return arrayOut5D