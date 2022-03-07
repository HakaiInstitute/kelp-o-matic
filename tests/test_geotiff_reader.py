import numpy as np
import rasterio
import torch
from rasterio.profiles import DefaultGTiffProfile
from torchvision import transforms

from hakai_segmentation.geotiff_io import GeotiffReader


def _create_simple_1band_img(tmpdir):
    simple_img = np.array([
        [1, 2],
        [3, 4]
    ])

    p = str(tmpdir.join("simple_img.tif"))
    height, width = simple_img.shape

    with rasterio.open(
            p,
            'w',
            **DefaultGTiffProfile(
                height=height,
                width=width,
                count=1,
                crs='+proj=latlong',
                transform=rasterio.Affine.identity()
            )) as dst:
        dst.write(simple_img.astype(rasterio.uint8), 1)

    return p


def _create_simple_3band_img(tmpdir):
    simple_img = np.array([[
        [11, 112, 213],
        [221, 22, 123]
    ], [
        [131, 232, 33],
        [41, 142, 243]
    ]])

    p = str(tmpdir.join("threeband_img.tif"))
    height, width, _ = simple_img.shape

    with rasterio.open(
            p,
            'w',
            **DefaultGTiffProfile(
                height=height,
                width=width,
                count=3,
                crs='+proj=latlong',
                transform=rasterio.Affine.identity()
            )) as dst:
        for b in range(simple_img.shape[-1]):
            dst.write(simple_img[:, :, b].astype(rasterio.uint8), b + 1)

    return p


def test_simple_crop(tmpdir):
    p = _create_simple_1band_img(tmpdir)

    ds = GeotiffReader(p, crop_size=1)
    assert ds[0] == np.array([[1]])
    assert ds[1] == np.array([[2]])
    assert ds[2] == np.array([[3]])
    assert ds[3] == np.array([[4]])

    ds = GeotiffReader(p, crop_size=2)
    assert np.all(ds[0] == np.array([[1, 2], [3, 4]]))


def test_padding(tmpdir):
    p = _create_simple_1band_img(tmpdir)
    ds = GeotiffReader(p, crop_size=1, padding=1, fill_value=0)
    assert np.all(ds[0] == np.array([[0, 0, 0], [0, 1, 2], [0, 3, 4]]))
    assert np.all(ds[1] == np.array([[0, 0, 0], [1, 2, 0], [3, 4, 0]]))
    assert np.all(ds[2] == np.array([[0, 1, 2], [0, 3, 4], [0, 0, 0]]))
    assert np.all(ds[3] == np.array([[1, 2, 0], [3, 4, 0], [0, 0, 0]]))

    ds = GeotiffReader(p, crop_size=2, padding=1, fill_value=0)
    assert np.all(ds[0] == np.array([[0, 0, 0, 0],
                                     [0, 1, 2, 0],
                                     [0, 3, 4, 0],
                                     [0, 0, 0, 0]
                                     ]))

    ds = GeotiffReader(p, crop_size=2, padding=2, fill_value=8)
    assert np.all(ds[0] == np.array([
        [8, 8, 8, 8, 8, 8],
        [8, 8, 8, 8, 8, 8],
        [8, 8, 1, 2, 8, 8],
        [8, 8, 3, 4, 8, 8],
        [8, 8, 8, 8, 8, 8],
        [8, 8, 8, 8, 8, 8],
    ]))


def test_fill_values(tmpdir):
    p = _create_simple_1band_img(tmpdir)
    ds = GeotiffReader(p, crop_size=2, padding=2)
    # Should default to 0
    assert ds.nodata == 0.0
    assert np.all(ds[0] == np.array([
        [0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0],
        [0, 0, 1, 2, 0, 0],
        [0, 0, 3, 4, 0, 0],
        [0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0],
    ]))

    # Should use raster nodata if available
    simple_img = np.array([
        [1, 2],
        [3, 4]
    ])

    p = str(tmpdir.mkdir("nodata").join("simple_img.tif"))
    height, width = simple_img.shape

    with rasterio.open(
            p,
            'w',
            **DefaultGTiffProfile(
                count=1,
                height=height,
                width=width,
                nodata=9,
                crs='+proj=latlong',
                transform=rasterio.Affine.identity()
            )) as dst:
        dst.write(simple_img.astype(rasterio.uint8), 1)

    ds = GeotiffReader(p, crop_size=2, padding=2)
    assert ds.nodata == 9
    assert np.all(ds[0] == np.array([
        [9, 9, 9, 9, 9, 9],
        [9, 9, 9, 9, 9, 9],
        [9, 9, 1, 2, 9, 9],
        [9, 9, 3, 4, 9, 9],
        [9, 9, 9, 9, 9, 9],
        [9, 9, 9, 9, 9, 9],
    ]))

    ds = GeotiffReader(p, crop_size=2, padding=2, fill_value=7)
    # Should use value defined at class instantiation
    assert ds.nodata == 9
    assert np.all(ds[0] == np.array([
        [7, 7, 7, 7, 7, 7],
        [7, 7, 7, 7, 7, 7],
        [7, 7, 1, 2, 7, 7],
        [7, 7, 3, 4, 7, 7],
        [7, 7, 7, 7, 7, 7],
        [7, 7, 7, 7, 7, 7],
    ]))


def test_transforms(tmpdir):
    p = _create_simple_1band_img(tmpdir)
    ds = GeotiffReader(p, crop_size=2, transform=transforms.ToTensor())
    it = (ds[0] * 255).to(torch.long)
    gt = torch.tensor([[1, 2], [3, 4]])

    assert torch.allclose(it, gt)


def test_band_ordering(tmpdir):
    p = _create_simple_3band_img(tmpdir)
    ds = GeotiffReader(p, crop_size=2, transform=transforms.ToTensor())
    it = (ds[0] * 255).to(torch.long)
    gt = torch.tensor([[
        [11, 112, 213],
        [221, 22, 123]
    ], [
        [131, 232, 33],
        [41, 142, 243]
    ]]).permute(2, 0, 1)  # Rearrange to (C, H, W)

    assert it.shape == torch.Size([3, 2, 2])
    assert torch.allclose(it, gt)


def test_len(tmpdir):
    p = _create_simple_3band_img(tmpdir)
    ds = GeotiffReader(p, crop_size=1)
    assert len(ds) == 4

    ds = GeotiffReader(p, crop_size=2)
    assert len(ds) == 1


def test_y0x0_getters(tmpdir):
    p = _create_simple_3band_img(tmpdir)
    ds = GeotiffReader(p, crop_size=1)
    assert ds.y0 == [0, 0, 1, 1]
    assert ds.x0 == [0, 1, 0, 1]


def test_filter(tmpdir):
    p = _create_simple_1band_img(tmpdir)
    ds = GeotiffReader(p, crop_size=1, padding=0, filter_=lambda img: np.all((img == 2)))
    crop, idx = next(iter(ds))
    assert crop == np.array([[2]])
    assert idx == 1

    q = _create_simple_3band_img(tmpdir)
    ds = GeotiffReader(q, crop_size=1, padding=0, filter_=lambda img: np.any((img == 22)))
    crop, idx = next(iter(ds))
    assert np.all(crop == np.array([[[221, 22, 123]]]))
    assert idx == 1

    ds = GeotiffReader(q, crop_size=1, padding=1, filter_=lambda img: np.any((img == 33)))
    crop, idx = next(iter(ds))

    assert np.all(crop == np.array([
        [[0, 0, 0], [11, 112, 213], [221, 22, 123]],
        [[0, 0, 0], [131, 232, 33], [41, 142, 243]],
        [[0, 0, 0], [0, 0, 0], [0, 0, 0]]
    ]))
    assert idx == 2
