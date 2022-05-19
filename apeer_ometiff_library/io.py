from pathlib import Path
from types import TracebackType
from typing import Union, Optional, Type, Tuple, List

import tifffile
import numpy as np
import sys
from apeer_ometiff_library import omexmlClass

PathLike = Union[str, Path]


class OmeTiffFile:
    def __init__(self, path: PathLike):
        self._path = path
        self._tiff_file = tifffile.TiffFile(self._path)

    def __enter__(self) -> "OmeTiffFile":
        return self

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> bool:
        self.close()
        return False

    def close(self) -> None:
        self._tiff_file.close()

    @property
    def is_multi_series(self):
        return omexmlClass.OMEXML(self._tiff_file.ome_metadata).image_count > 1

    def read(self) -> Tuple[np.ndarray, str]:
        omexml_string = self._tiff_file.ome_metadata
        array = _ensure_correct_dimensions(self._tiff_file.asarray(), omexml_string)
        return array, omexml_string

    def read_multi_series(self) -> Tuple[List[np.ndarray], str]:
        omexml_string = self._tiff_file.ome_metadata
        arrays = [
            _ensure_correct_dimensions(
                self._tiff_file.asarray(series=series), omexml_string
            )
            for series in range(
                omexmlClass.OMEXML(self._tiff_file.ome_metadata).image_count
            )
        ]
        return arrays, omexml_string


def read_ometiff(input_path):
    with tifffile.TiffFile(input_path) as tif:
        array = tif.asarray()
        omexml_string = tif.ome_metadata

    array = _ensure_correct_dimensions(array, omexml_string)

    return array, omexml_string


def _ensure_correct_dimensions(array, omexml_string):
    # Turn Ome XML String to an Bioformats object for parsing
    metadata = omexmlClass.OMEXML(omexml_string)

    # Parse pixel sizes
    pixels = metadata.image(0).Pixels
    size_c = pixels.SizeC
    size_t = pixels.SizeT
    size_z = pixels.SizeZ
    size_x = pixels.SizeX
    size_y = pixels.SizeY
    # Expand image array to 5D and make sure to return the array in (T, Z, C, X, Y) order
    dim_format = pixels.DimensionOrder
    if dim_format == "XYCZT":
        if size_c == 1:
            array = np.expand_dims(array, axis=-3)
        if size_z == 1:
            array = np.expand_dims(array, axis=-4)
        if size_t == 1:
            array = np.expand_dims(array, axis=-5)
    elif dim_format == "XYZCT":
        if size_z == 1:
            array = np.expand_dims(array, axis=-3)
        if size_c == 1:
            array = np.expand_dims(array, axis=-4)
        if size_t == 1:
            array = np.expand_dims(array, axis=-5)
        array = np.moveaxis(array, 1, 2)
    elif dim_format == "XYCTZ":
        if size_c == 1:
            array = np.expand_dims(array, axis=-3)
        if size_t == 1:
            array = np.expand_dims(array, axis=-4)
        if size_z == 1:
            array = np.expand_dims(array, axis=-5)
        array = np.moveaxis(array, 0, 1)
    elif dim_format == "XYZTC":
        if size_z == 1:
            array = np.expand_dims(array, axis=-3)
        if size_t == 1:
            array = np.expand_dims(array, axis=-4)
        if size_c == 1:
            array = np.expand_dims(array, axis=-5)
        array = np.moveaxis(array, 0, 2)
    elif dim_format == "XYTZC":
        if size_t == 1:
            array = np.expand_dims(array, axis=-3)
        if size_z == 1:
            array = np.expand_dims(array, axis=-4)
        if size_c == 1:
            array = np.expand_dims(array, axis=-5)
        array = np.moveaxis(array, 0, 2)
        array = np.moveaxis(array, 0, 1)
    elif dim_format == "XYTCZ":
        if size_t == 1:
            array = np.expand_dims(array, axis=-3)
        if size_c == 1:
            array = np.expand_dims(array, axis=-4)
        if size_z == 1:
            array = np.expand_dims(array, axis=-5)
        array = np.moveaxis(array, 1, 2)
        array = np.moveaxis(array, 0, 1)
    else:
        print(array.shape)
        raise Exception("Unknow dimension format")
    return array


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



def write_ometiff(output_path, array, omexml_string = None, compression=None):
    """
    Write the given 5D array as an ome.tiff

    Parameters
    ----------
    output_path : str
        Path where to save the ome.tiff
    array : np.ndarray
        5D array containing ome.tiff data, order should be TZCYX
    omexml_string : Optional[encoded xml]
        encoded XML Metadata, will be generated if not provided.
    compression : str
        possible values listed here:
        https://github.com/cgohlke/tifffile/blob/f55fc8a49c2ad30697a6b1760d5a325533574ad8/tifffile/tifffile.py#L12131
    """
    if omexml_string is None:
        omexml_string = gen_xml(array)

    if sys.version < "3.7":
        tifffile.imwrite(output_path, array,  photometric = "minisblack", description=omexml_string, metadata=None,
                         compress=compression)
    else:
        tifffile.imwrite(output_path, array,  photometric = "minisblack", description=omexml_string, metadata=None,
                         compression=compression)
