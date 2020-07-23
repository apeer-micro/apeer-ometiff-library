import tifffile
import numpy as np
from apeer_ometiff_library import omexmlClass


def read_ometiff(input_path):
    with tifffile.TiffFile(input_path) as tif:
        array = tif.asarray()
        omexml_string = tif.ome_metadata

    # Turn Ome XML String to an Bioformats object for parsing
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

    if Image_ID:
        metadata.image().set_ID(Image_ID)
    if Image_Name:
        metadata.image().set_Name(Image_Name)
    if Image_AcquisitionDate:
        metadata.image().Image.AcquisitionDate = Image_AcquisitionDate

    if DimensionOrder:
        metadata.image().Pixels.DimensionOrder = DimensionOrder
    if dType:
        metadata.image().Pixels.PixelType = dType
    if SizeT:
        metadata.image().Pixels.set_SizeT(SizeT)
    if SizeZ:
        metadata.image().Pixels.set_SizeZ(SizeZ)
    if SizeC:
        metadata.image().Pixels.set_SizeC(SizeC)
    if SizeX:
        metadata.image().Pixels.set_SizeX(SizeX)
    if SizeY:
        metadata.image().Pixels.set_SizeY(SizeY)

    if Channel_ID:
        metadata.image().Channel.ID = Channel_ID
    if Channel_Name:
        metadata.image().Channel.Name = Channel_Name
    if Channel_SamplesPerPixel:
        metadata.image().Channel.SamplesPerPixel = Channel_SamplesPerPixel
    
    metadata = metadata.to_xml().encode()
    
    return metadata


def gen_xml(array):
    
    #Dimension order is assumed to be TZCYX
    dim_order = "TZCYX"
    
    metadata = omexmlClass.OMEXML()
    shape = array.shape
    assert ( len(shape) == 5), "Expected array of 5 dimensions"
    
    metadata.image().set_Name("IMAGE")
    metadata.image().set_ID("0")
    
    pixels = metadata.image().Pixels
    pixels.ome_uuid = metadata.uuidStr
    pixels.set_ID("0")
    
    pixels.channel_count = shape[2]
    
    pixels.set_SizeT(shape[0])
    pixels.set_SizeZ(shape[1])
    pixels.set_SizeC(shape[2])
    pixels.set_SizeY(shape[3])
    pixels.set_SizeX(shape[4])
    
    pixels.set_DimensionOrder(dim_order[::-1])
    
    pixels.set_PixelType(omexmlClass.get_pixel_type(array.dtype))
    
    for i in range(pixels.SizeC):
        pixels.Channel(i).set_ID("Channel:0:" + str(i))
        pixels.Channel(i).set_Name("C:" + str(i))
    
    for i in range(pixels.SizeC):
        pixels.Channel(i).set_SamplesPerPixel(1)
        
    pixels.populate_TiffData()
    
    return metadata.to_xml().encode()
    


def write_ometiff(output_path, array, omexml_string = None):
    
    if omexml_string is None:
        omexml_string = gen_xml(array)
        
    tifffile.imwrite(output_path, array,  photometric = "minisblack", description=omexml_string, metadata = None)
    
