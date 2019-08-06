from skimage.external import tifffile
import numpy as np
import xml.dom.minidom
from apeer_ometiff_library import omexmlClass


def read_ometiff(input_path):
    with tifffile.TiffFile(input_path) as tif:
        # Return image data from multiple TIFF pages as numpy array.
        array = tif.asarray()
        omexml_string = tif[0].image_description.decode("utf-8")

    # Turn Ome XML String to a Bioformats object for parsing
    metadata = omexmlClass.OMEXML(omexml_string)

    # Parse pixel sizes
    pixels = metadata.image(0).Pixels
    size_c = pixels.SizeC
    size_t = pixels.SizeT
    size_z = pixels.SizeZ
    size_x = pixels.SizeX
    size_y = pixels.SizeY

    # Expand image array to 5D of order (T, Z, C, X, Y)
    if size_c == 1:
        array = np.expand_dims(array, axis=-3)
    if size_z == 1:
        array = np.expand_dims(array, axis=-4)
    if size_t == 1:
        array = np.expand_dims(array, axis=-5)

    return array, omexml_string


def update_xml(omexml, Image_ID=None, Image_Name=None, Image_AcquisitionDate=None,
               DimensionOrder=None, dType=None, SizeT=None, SizeZ=None, SizeC=None, SizeX=None, SizeY=None,
                Channel_ID=None, Channel_Name=None, Channel_SamplesPerPixel=None):

    metadata = omexmlClass.OMEXML(omexml)

    if not Image_ID == None:
        metadata.image(0).Image.ID = Image_ID
    if not Image_Name == None:
        metadata.image(0).Name = Image_Name
    if not Image_AcquisitionDate == None:
        metadata.image(0).Image.AcquisitionDate = Image_AcquisitionDate

    if not DimensionOrder == None:
        metadata.image(0).Pixels.DimensionOrder = DimensionOrder
    if not dType == None:
        metadata.image(0).Pixels.PixelType = dType
    if not SizeT == None:
        metadata.image(0).Pixels.SizeT = SizeT
    if not SizeZ == None:
        metadata.image(0).Pixels.SizeZ = SizeZ
    if not SizeC == None:
        metadata.image(0).Pixels.SizeC = SizeC
    if not SizeX == None:
        metadata.image(0).Pixels.SizeX = SizeX
    if not SizeY == None:
        metadata.image(0).Pixels.SizeY = SizeY

    if not Channel_ID == None:
        metadata.image(0).Channel.ID = Channel_ID
    if not Channel_Name == None:
        metadata.image(0).Channel.Name = Channel_Name
    if not Channel_SamplesPerPixel == None:
        metadata.image(0).Channel.SamplesPerPixel = Channel_SamplesPerPixel

    metadata = metadata.to_xml(encoding='utf-8')
    return metadata.replace("<ome:", "<").replace("</ome:", "</")
    #omexmlString = xml.dom.minidom.parseString(metadata)
    #return omexmlString.toprettyxml()


def write_ometiff(output_path, array, omexml_string):
    tifffile.imsave(output_path, array, photometric='minisblack', description=omexml_string, metadata={'axes': 'TZCXY'})
