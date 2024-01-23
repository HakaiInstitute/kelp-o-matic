from pathlib import Path

import numpy as np
import pytest
import rasterio
import torch
from rasterio.transform import from_origin

from kelp_o_matic.hann import TorchMemoryRegister


def create_dummy_tiff(
    filename, width=512, height=512, num_bands=3, dtype=rasterio.uint8
):
    """
    Create a dummy TIFF file for testing.

    :param filename: Path to the file to be created.
    :param width: Width of the image.
    :param height: Height of the image.
    :param num_bands: Number of bands (channels) in the image.
    :param dtype: Data type of the image.
    """
    # Define the transform to position the image in space
    transform = from_origin(0, 0, 1, 1)

    # Create a new dataset with given parameters
    with rasterio.open(
        filename,
        "w",
        driver="GTiff",
        height=height,
        width=width,
        count=num_bands,
        dtype=dtype,
        crs="+proj=latlong",
        transform=transform,
    ) as dst:
        # Write dummy data to each band
        for i in range(1, num_bands + 1):
            data = np.random.randint(0, 255, (height, width)).astype(dtype)
            dst.write(data, i)


@pytest.fixture
def memory_register(tmp_path):
    # Create a dummy image file for testing
    dummy_image_path = tmp_path / "dummy_image.tif"
    create_dummy_tiff(dummy_image_path, width=1000, height=1000, num_bands=3)

    # Initialize TorchMemoryRegister with the dummy image
    return TorchMemoryRegister(
        image_path=dummy_image_path,
        reg_depth=2,
        window_size=256,
        device=torch.device("cpu"),
    )


@pytest.fixture
def small_dummy_image_path(tmp_path):
    # Create a dummy image file for testing
    small_dummy_image_path = tmp_path / "small_dummy_image.tif"
    create_dummy_tiff(small_dummy_image_path, width=200, height=200, num_bands=3)

    return small_dummy_image_path


@pytest.fixture
def small_img_memory_register(small_dummy_image_path):
    # Initialize TorchMemoryRegister with the dummy image
    return TorchMemoryRegister(
        image_path=small_dummy_image_path,
        reg_depth=2,
        window_size=256,
        device=torch.device("cpu"),
    )


@pytest.fixture
def full_window_memory_register(small_dummy_image_path):
    # Initialize TorchMemoryRegister with the dummy image
    return TorchMemoryRegister(
        image_path=small_dummy_image_path,
        reg_depth=2,
        window_size=200,
        device=torch.device("cpu"),
    )


@pytest.fixture
def odd_window_memory_register(small_dummy_image_path):
    # Initialize TorchMemoryRegister with the dummy image
    return TorchMemoryRegister(
        image_path=small_dummy_image_path,
        reg_depth=2,
        window_size=125,
        device=torch.device("cpu"),
    )


def test_initialization(memory_register):
    assert memory_register.n == 2
    assert memory_register.ws == 256
    assert memory_register.hws == 256 // 2
    assert isinstance(memory_register.image_path, Path)
    width = np.ceil(1000 / 256) * 256 + 128
    assert width == memory_register.width
    assert memory_register.register.shape == (2, 256, width)
    assert memory_register.register.device == torch.device("cpu")


def test_step_method(memory_register):
    # Test typical case
    new_logits = torch.rand((2, 256, 256))

    img_window = rasterio.windows.Window(0, 0, 256, 256)
    preds, preds_win = memory_register.step(new_logits, img_window)

    assert preds.shape == (2, 128, 128)
    assert isinstance(preds_win, rasterio.windows.Window)
    assert preds_win == rasterio.windows.Window(0, 0, 128, 128)

    img_window = rasterio.windows.Window(768, 0, 232, 256)
    preds, preds_win = memory_register.step(new_logits, img_window)

    assert preds.shape == (2, 128, 128)
    assert isinstance(preds_win, rasterio.windows.Window)
    assert preds_win == rasterio.windows.Window(768, 0, 128, 128)

    img_window = rasterio.windows.Window(896, 0, 104, 256)
    preds, preds_win = memory_register.step(new_logits, img_window)

    assert preds.shape == (2, 128, 104)
    assert isinstance(preds_win, rasterio.windows.Window)
    assert preds_win == rasterio.windows.Window(896, 0, 104, 128)


def test_small_img_edge_case(small_img_memory_register):
    # Test small image
    new_logits = torch.rand((2, 256, 256))

    img_window = rasterio.windows.Window(0, 0, 200, 200)
    preds, preds_win = small_img_memory_register.step(new_logits, img_window)

    assert preds.shape == (2, 128, 128)
    assert isinstance(preds_win, rasterio.windows.Window)
    assert preds_win == rasterio.windows.Window(0, 0, 128, 128)

    img_window = rasterio.windows.Window(128, 0, 72, 200)
    preds, preds_win = small_img_memory_register.step(new_logits, img_window)

    assert preds.shape == (2, 128, 72)
    assert isinstance(preds_win, rasterio.windows.Window)
    assert preds_win == rasterio.windows.Window(128, 0, 72, 128)

    img_window = rasterio.windows.Window(0, 128, 128, 72)
    preds, preds_win = small_img_memory_register.step(new_logits, img_window)

    assert preds.shape == (2, 72, 128)
    assert isinstance(preds_win, rasterio.windows.Window)
    assert preds_win == rasterio.windows.Window(0, 128, 128, 72)

    img_window = rasterio.windows.Window(128, 128, 72, 72)
    preds, preds_win = small_img_memory_register.step(new_logits, img_window)

    assert preds.shape == (2, 72, 72)
    assert isinstance(preds_win, rasterio.windows.Window)
    assert preds_win == rasterio.windows.Window(128, 128, 72, 72)


def test_full_window_sizes(full_window_memory_register):
    # Test case that image size is equal to the register window size
    new_logits = torch.rand((2, 200, 200))

    img_window = rasterio.windows.Window(0, 0, 200, 200)
    preds, preds_win = full_window_memory_register.step(new_logits, img_window)

    assert preds.shape == (2, 100, 100)
    assert isinstance(preds_win, rasterio.windows.Window)
    assert preds_win == rasterio.windows.Window(0, 0, 100, 100)

    img_window = rasterio.windows.Window(100, 0, 100, 200)
    preds, preds_win = full_window_memory_register.step(new_logits, img_window)

    assert preds.shape == (2, 100, 100)
    assert isinstance(preds_win, rasterio.windows.Window)
    assert preds_win == rasterio.windows.Window(100, 0, 100, 100)


def test_odd_window_size(odd_window_memory_register):
    # Test case where the register size is an odd number
    new_logits = torch.rand((2, 125, 125))

    assert odd_window_memory_register.hws == 62

    img_window = rasterio.windows.Window(0, 0, 125, 125)
    preds, preds_win = odd_window_memory_register.step(new_logits, img_window)

    assert preds.shape == (2, 62, 62)
    assert isinstance(preds_win, rasterio.windows.Window)
    assert preds_win == rasterio.windows.Window(0, 0, 62, 62)

    img_window = rasterio.windows.Window(62, 0, 63, 125)
    preds, preds_win = odd_window_memory_register.step(new_logits, img_window)

    assert preds.shape == (2, 62, 62)
    assert isinstance(preds_win, rasterio.windows.Window)
    assert preds_win == rasterio.windows.Window(62, 0, 62, 62)

    img_window = rasterio.windows.Window(124, 0, 1, 125)
    preds, preds_win = odd_window_memory_register.step(new_logits, img_window)

    assert preds.shape == (2, 62, 1)
    assert isinstance(preds_win, rasterio.windows.Window)
    assert preds_win == rasterio.windows.Window(124, 0, 1, 62)

    img_window = rasterio.windows.Window(0, 62, 125, 63)
    preds, preds_win = odd_window_memory_register.step(new_logits, img_window)

    assert preds.shape == (2, 62, 62)
    assert isinstance(preds_win, rasterio.windows.Window)
    assert preds_win == rasterio.windows.Window(0, 62, 62, 62)

    img_window = rasterio.windows.Window(0, 124, 125, 1)
    preds, preds_win = odd_window_memory_register.step(new_logits, img_window)

    assert preds.shape == (2, 1, 62)
    assert isinstance(preds_win, rasterio.windows.Window)
    assert preds_win == rasterio.windows.Window(0, 124, 62, 1)
