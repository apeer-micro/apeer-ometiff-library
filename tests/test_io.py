import os
import unittest
from pathlib import Path

import numpy as np
import tifffile

from apeer_ometiff_library.io import OmeTiffFile, write_ometiff


class TestOmeTiffFile(unittest.TestCase):
    def setUp(self):
        self._set_up_ometiff()
        self._set_up_multi_series_ometiff()

    def _set_up_ometiff(self):
        self.ometiff_path = Path("tmp.ome.tiff")
        self.ometiff_path.touch()
        self.ome_tiff_metadata = """<?xml version='1.0' encoding='utf-8'?>
        <OME xmlns="http://www.openmicroscopy.org/Schemas/OME/2016-06" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
             xsi:schemaLocation="http://www.openmicroscopy.org/Schemas/OME/2016-06 http://www.openmicroscopy.org/Schemas/OME/2016-06/ome.xsd"
             UUID="urn:uuid:11227ecd-e960-42e4-95c8-39e6cec94150">
            <Image ID="0" Name="IMAGE0">
                <AcquisitionDate>2022-05-13T11:25:25.212054</AcquisitionDate>
                <Pixels DimensionOrder="XYCZT" ID="0" SizeC="2" SizeT="3" SizeX="64" SizeY="32" SizeZ="4" Type="uint8"
                        BigEndian="true">
                    <Channel ID="Channel:0:0" SamplesPerPixel="1" Name="C:0">
                        <LightPath/>
                    </Channel>
                    <TiffData FirstT="0" FirstZ="0" FirstC="0" IFD="0" PlaneCount="1"/>
                </Pixels>
            </Image>
        </OME>""".encode()
        self.ometiff_array = 255 * np.ones((2, 3, 4, 32, 64), np.uint8)
        with tifffile.TiffWriter(self.ometiff_path) as tiff_writer:
            tiff_writer.save(
                self.ometiff_array,
                photometric="minisblack",
                description=self.ome_tiff_metadata,
                metadata={},
            )

    def _set_up_multi_series_ometiff(self):
        self.multi_series_ometiff_path = Path("multi_series_tmp.ome.tiff")
        self.multi_series_ometiff_path.touch()
        self.multi_series_metadata = """<?xml version='1.0' encoding='utf-8'?>
        <OME xmlns="http://www.openmicroscopy.org/Schemas/OME/2016-06" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
             xsi:schemaLocation="http://www.openmicroscopy.org/Schemas/OME/2016-06 http://www.openmicroscopy.org/Schemas/OME/2016-06/ome.xsd"
             UUID="urn:uuid:11227ecd-e960-42e4-95c8-39e6cec94150">
            <Image ID="0" Name="IMAGE0">
                <AcquisitionDate>2022-05-13T11:25:25.212054</AcquisitionDate>
                <Pixels DimensionOrder="XYCZT" ID="0" SizeC="1" SizeT="1" SizeX="64" SizeY="32" SizeZ="1" Type="uint8"
                        BigEndian="true">
                    <Channel ID="Channel:0:0" SamplesPerPixel="1" Name="C:0">
                        <LightPath/>
                    </Channel>
                    <TiffData FirstT="0" FirstZ="0" FirstC="0" IFD="0" PlaneCount="1"/>
                </Pixels>
            </Image>
            <Image ID="1" Name="IMAGE1">
                <AcquisitionDate>2022-05-13T11:25:25.212054</AcquisitionDate>
                <Pixels DimensionOrder="XYCZT" ID="0" SizeC="1" SizeT="1" SizeX="32" SizeY="64" SizeZ="1" Type="uint8"
                        BigEndian="true">
                    <Channel ID="Channel:0:0" SamplesPerPixel="1" Name="C:0">
                        <LightPath/>
                    </Channel>
                    <TiffData FirstT="0" FirstZ="0" FirstC="0" IFD="0" PlaneCount="1"/>
                </Pixels>
            </Image>
        </OME>""".encode()
        self.multi_series_ometiff_array0 = 255 * np.ones((1, 1, 1, 32, 64), np.uint8)
        self.multi_series_ometiff_array1 = np.zeros((1, 1, 1, 64, 32), np.uint8)
        with tifffile.TiffWriter(self.multi_series_ometiff_path) as tiff_writer:
            tiff_writer.save(
                self.multi_series_ometiff_array0,
                photometric="minisblack",
                metadata={},
            )
            tiff_writer.save(
                self.multi_series_ometiff_array1,
                photometric="minisblack",
                description=self.multi_series_metadata,
                metadata={},
            )

    def tearDown(self) -> None:
        self.ometiff_path.unlink()
        self.multi_series_ometiff_path.unlink()

    def test_is_multi_series(self):
        with OmeTiffFile(self.ometiff_path) as ome_tiff_file:
            self.assertFalse(ome_tiff_file.is_multi_series)

        with OmeTiffFile(self.multi_series_ometiff_path) as ome_tiff_file:
            self.assertTrue(ome_tiff_file.is_multi_series)

    def test_read(self):
        with OmeTiffFile(self.ometiff_path) as ome_tiff_file:
            array, omexml_string = ome_tiff_file.read()
            np.testing.assert_equal(array, self.ometiff_array)

    def test_read_multi_series(self):
        with OmeTiffFile(self.multi_series_ometiff_path) as ome_tiff_file:
            arrays, omexml_string = ome_tiff_file.read_multi_series()
            np.testing.assert_equal(
                arrays,
                [self.multi_series_ometiff_array0, self.multi_series_ometiff_array1],
            )

class TestOmeTiffWrite(unittest.TestCase):
    def setUp(self) -> None:
        self._test_array = np.ones((1, 7, 2, 256, 256))
        self._output_path = 'test.ome.tiff'

    def test_write(self):
        write_ometiff(output_path=self._output_path, array=self._test_array)

        with OmeTiffFile(self._output_path) as ome_tiff_file:
            array, omexml_string = ome_tiff_file.read()
            np.testing.assert_equal(array, self._test_array)

    def test_write_compress(self):
        write_ometiff(output_path=self._output_path, array=self._test_array, compression="adobe_deflate")

        with OmeTiffFile(self._output_path) as ome_tiff_file:
            array, omexml_string = ome_tiff_file.read()
            np.testing.assert_equal(array, self._test_array)
            os.remove(self._output_path)