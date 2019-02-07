from skimage.external import tifffile
import numpy as np
import numpy as np
import itertools as it

from apeer_ometiff_library import omexmlClass

def readOmeTiff(input_path):
    with tifffile.TiffFile(input_path) as tif:
        array = tif.asarray()
        omexmlString = tif[0].image_description.decode("utf-8")

    # Turn Ome XML String to an Bioformats object for parsing
    metadata = omexmlClass.OMEXML(omexmlString)

    # Parse pixel sizes
    pixels = metadata.image(0).Pixels
    SizeC = pixels.SizeC
    SizeT = pixels.SizeT
    SizeZ = pixels.SizeZ
    SizeX = pixels.SizeX
    SizeY = pixels.SizeY
    pixels.DimensionOrder

    # Expand image array to 5D of order (T, Z, C, X, Y)
    if SizeC == 1:
        array = np.expand_dims(array, axis=-3)
    if SizeZ == 1:
        array = np.expand_dims(array, axis=-4)
    if SizeT == 1:
        array = np.expand_dims(array, axis=-5)

    return (array, omexmlString)

def writeOmeTiff(outputPath, array, omexmlString):
    tifffile.imsave(outputPath, array, description=omexmlString, metadata={'axes': 'TZCXY'})

def apply2DTrafo(trafo2D, array5D, parameterDict):
    arrayOut5D = np.zeros_like(array5D)
    nT, nZ, nC, nX, nY = np.shape(arrayOut5D)

    for t, z, c in it.product(range(nT), range(nZ), range(nC)):
        arrayOut5D[t, z, c, :, :] = trafo2D(array5D[t, z, c, :, :], parameterDict)

    return arrayOut5D
