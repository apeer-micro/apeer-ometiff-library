import numpy as np
import itertools as it

def apply_2d_trafo(trafo_2d, array_5d, **kwargs):
    n_t, n_z, n_c, n_x, n_y = np.shape(array_5d)
    array_out_5d = None
    firstIteration = True

    for t, z, c in it.product(range(n_t), range(n_z), range(n_c)):
        result = trafo_2d(array_5d[t, z, c, :, :], **kwargs)
        if firstIteration:
            array_out_5d = np.zeros_like(array_5d, result.dtype)
            firstIteration = False
        array_out_5d[t, z, c, :, :] = result

    return array_out_5d


def apply_3d_trafo_zstack(trafo_3d, array_5d, **kwargs):
    n_t, n_z, n_c, n_x, n_y = np.shape(array_5d)
    array_out_5d = None
    firstIteration = True

    for t, c in it.product(range(n_t), range(n_c)):
        result = trafo_3d(array_5d[t, :, c, :, :], **kwargs)
        if firstIteration:
            array_out_5d = np.zeros_like(array_5d, dtype=array_5d.dtype)
        firstIteration = False
        array_out_5d[t, :, c, :, :] = result

    return array_out_5d


def apply_3d_trafo_rgb(trafo_3d, array_5d, **kwargs):
    n_t, n_z, n_c, n_x, n_y = array_5d.shape
    array_out_5d = np.zeros_like(array5d, **kwargs)
    firstIteration = True

    for t, z in it.product(range(n_t), range(n_z)):
        result = trafo_3d(array_5d[t, z, :, :, :], **kwargs)
        if firstIteration:
            array_out_5d = array_out_5d.astype(result.dtype)
        firstIteration = False
        array_out_5d[t, z, :, :, :] = result

    return array_out_5d
