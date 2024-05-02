import numpy as np
import rasterio
from rasterio.profiles import DefaultGTiffProfile
from rasterio.windows import Window

from kelp_o_matic.geotiff_io import GeotiffReader


def _create_simple_1band_img(tmpdir):
    simple_img = np.array([[1, 2], [3, 4]])

    p = str(tmpdir.join("simple_img.tif"))
    height, width = simple_img.shape

    with rasterio.open(
        p,
        "w",
        **DefaultGTiffProfile(
            height=height,
            width=width,
            count=1,
            crs="+proj=latlong",
            transform=rasterio.Affine.identity(),
        ),
    ) as dst:
        dst.write(simple_img.astype(rasterio.uint8), 1)

    return p


def _create_simple_3band_img(tmpdir):
    simple_img = np.array(
        [[[11, 112, 213], [221, 22, 123]], [[131, 232, 33], [41, 142, 243]]]
    )

    p = str(tmpdir.join("threeband_img.tif"))
    height, width, _ = simple_img.shape

    with rasterio.open(
        p,
        "w",
        **DefaultGTiffProfile(
            height=height,
            width=width,
            count=3,
            crs="+proj=latlong",
            transform=rasterio.Affine.identity(),
        ),
    ) as dst:
        for b in range(simple_img.shape[-1]):
            dst.write(simple_img[:, :, b].astype(rasterio.uint8), b + 1)

    return p


def test_simple_crop(tmpdir):
    p = _create_simple_1band_img(tmpdir)

    ds = GeotiffReader(p, crop_size=1)
    c, w = ds[0]
    assert c == np.array([[1]])
    assert w == Window(row_off=0, col_off=0, height=1, width=1)

    c, w = ds[1]
    assert c == np.array([[2]])
    assert w == Window(row_off=0, col_off=1, height=1, width=1)

    c, w = ds[2]
    assert c == np.array([[3]])
    assert w == Window(row_off=1, col_off=0, height=1, width=1)

    c, w = ds[3]
    assert c == np.array([[4]])
    assert w == Window(row_off=1, col_off=1, height=1, width=1)

    ds = GeotiffReader(p, crop_size=2)
    assert np.all(ds[0][0] == np.expand_dims(np.array([[1, 2], [3, 4]]), 2))


def test_stride(tmpdir):
    p = _create_simple_1band_img(tmpdir)
    ds = GeotiffReader(p, crop_size=2, stride=1)
    c, w = ds[0]
    assert np.all(c == np.expand_dims(np.array([[1, 2], [3, 4]]), 2))
    assert w == Window(row_off=0, col_off=0, height=2, width=2)

    c, w = ds[1]
    assert np.all(c == np.expand_dims(np.array([[2], [4]]), 2))
    assert w == Window(row_off=0, col_off=1, height=2, width=1)


def test_len(tmpdir):
    p = _create_simple_3band_img(tmpdir)
    ds = GeotiffReader(p, crop_size=1)
    assert len(ds) == 4

    ds = GeotiffReader(p, crop_size=2)
    assert len(ds) == 1


def test_y0x0_getters(tmpdir):
    p = _create_simple_3band_img(tmpdir)
    ds = GeotiffReader(p, crop_size=1)
    assert ds.y0 == [0, 1]
    assert ds.x0 == [0, 1]
