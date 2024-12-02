import numpy as np
import pytest
import rasterio
import torch
from rasterio.transform import from_origin
from rasterio.windows import Window

from kelp_o_matic.hann import BartlettHannKernel, Kernel, TorchMemoryRegister


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
    # Initialize TorchMemoryRegister with the dummy image
    return TorchMemoryRegister(
        image_width=1000,
        register_depth=2,
        window_size=256,
        kernel=BartlettHannKernel,
        device=torch.device("cpu"),
    )


@pytest.fixture
def small_img_memory_register():
    # Initialize TorchMemoryRegister with the dummy image
    return TorchMemoryRegister(
        image_width=200,
        register_depth=2,
        window_size=256,
        kernel=BartlettHannKernel,
        device=torch.device("cpu"),
    )


@pytest.fixture
def full_window_memory_register():
    # Initialize TorchMemoryRegister with the dummy image
    return TorchMemoryRegister(
        image_width=200,
        register_depth=2,
        window_size=200,
        kernel=BartlettHannKernel,
        device=torch.device("cpu"),
    )


@pytest.fixture
def odd_window_memory_register():
    # Initialize TorchMemoryRegister with the dummy image
    return TorchMemoryRegister(
        image_width=200,
        register_depth=2,
        window_size=125,
        kernel=BartlettHannKernel,
        device=torch.device("cpu"),
    )


def test_initialization(memory_register):
    assert memory_register.n == 2
    assert memory_register.ws == 256
    assert memory_register.hws == 256 // 2
    assert isinstance(memory_register.kernel, BartlettHannKernel)
    width = np.ceil(1000 / 256) * 256 + 128
    assert width == memory_register.width
    assert memory_register.register.shape == (2, 256, width)
    assert memory_register.register.device == torch.device("cpu")


def test_step_method(memory_register):
    # Test typical case
    new_logits = torch.rand((2, 256, 256))

    img_window = rasterio.windows.Window(0, 0, 256, 256)
    preds, preds_win = memory_register.step(
        new_logits, img_window, top=False, left=False, bottom=False, right=False
    )

    assert preds.shape == (2, 128, 128)
    assert isinstance(preds_win, rasterio.windows.Window)
    assert preds_win == rasterio.windows.Window(0, 0, 128, 128)

    img_window = rasterio.windows.Window(768, 0, 232, 256)
    preds, preds_win = memory_register.step(
        new_logits, img_window, top=False, left=False, bottom=False, right=False
    )

    assert preds.shape == (2, 128, 128)
    assert isinstance(preds_win, rasterio.windows.Window)
    assert preds_win == rasterio.windows.Window(768, 0, 128, 128)

    img_window = rasterio.windows.Window(896, 0, 104, 256)
    preds, preds_win = memory_register.step(
        new_logits, img_window, top=False, left=False, bottom=False, right=False
    )

    assert preds.shape == (2, 128, 104)
    assert isinstance(preds_win, rasterio.windows.Window)
    assert preds_win == rasterio.windows.Window(896, 0, 104, 128)


def test_small_img_edge_case(small_img_memory_register):
    # Test small image
    new_logits = torch.rand((2, 256, 256))

    img_window = rasterio.windows.Window(0, 0, 200, 200)
    preds, preds_win = small_img_memory_register.step(
        new_logits, img_window, top=False, left=False, bottom=False, right=False
    )

    assert preds.shape == (2, 128, 128)
    assert isinstance(preds_win, rasterio.windows.Window)
    assert preds_win == rasterio.windows.Window(0, 0, 128, 128)

    img_window = rasterio.windows.Window(128, 0, 72, 200)
    preds, preds_win = small_img_memory_register.step(
        new_logits, img_window, top=False, left=False, bottom=False, right=False
    )

    assert preds.shape == (2, 128, 72)
    assert isinstance(preds_win, rasterio.windows.Window)
    assert preds_win == rasterio.windows.Window(128, 0, 72, 128)

    img_window = rasterio.windows.Window(0, 128, 128, 72)
    preds, preds_win = small_img_memory_register.step(
        new_logits, img_window, top=False, left=False, bottom=False, right=False
    )

    assert preds.shape == (2, 72, 128)
    assert isinstance(preds_win, rasterio.windows.Window)
    assert preds_win == rasterio.windows.Window(0, 128, 128, 72)

    img_window = rasterio.windows.Window(128, 128, 72, 72)
    preds, preds_win = small_img_memory_register.step(
        new_logits, img_window, top=False, left=False, bottom=False, right=False
    )

    assert preds.shape == (2, 72, 72)
    assert isinstance(preds_win, rasterio.windows.Window)
    assert preds_win == rasterio.windows.Window(128, 128, 72, 72)


def test_full_window_sizes(full_window_memory_register):
    # Test case that image size is equal to the register window size
    new_logits = torch.rand((2, 200, 200))

    img_window = rasterio.windows.Window(0, 0, 200, 200)
    preds, preds_win = full_window_memory_register.step(
        new_logits, img_window, top=False, left=False, bottom=False, right=False
    )

    assert preds.shape == (2, 100, 100)
    assert isinstance(preds_win, rasterio.windows.Window)
    assert preds_win == rasterio.windows.Window(0, 0, 100, 100)

    img_window = rasterio.windows.Window(100, 0, 100, 200)
    preds, preds_win = full_window_memory_register.step(
        new_logits, img_window, top=False, left=False, bottom=False, right=False
    )

    assert preds.shape == (2, 100, 100)
    assert isinstance(preds_win, rasterio.windows.Window)
    assert preds_win == rasterio.windows.Window(100, 0, 100, 100)


def test_odd_window_size(odd_window_memory_register):
    # Test case where the register size is an odd number
    new_logits = torch.rand((2, 125, 125))

    assert odd_window_memory_register.hws == 62

    img_window = rasterio.windows.Window(0, 0, 125, 125)
    preds, preds_win = odd_window_memory_register.step(
        new_logits, img_window, top=False, left=False, bottom=False, right=False
    )

    assert preds.shape == (2, 62, 62)
    assert isinstance(preds_win, rasterio.windows.Window)
    assert preds_win == rasterio.windows.Window(0, 0, 62, 62)

    img_window = rasterio.windows.Window(62, 0, 63, 125)
    preds, preds_win = odd_window_memory_register.step(
        new_logits, img_window, top=False, left=False, bottom=False, right=False
    )

    assert preds.shape == (2, 62, 62)
    assert isinstance(preds_win, rasterio.windows.Window)
    assert preds_win == rasterio.windows.Window(62, 0, 62, 62)

    img_window = rasterio.windows.Window(124, 0, 1, 125)
    preds, preds_win = odd_window_memory_register.step(
        new_logits, img_window, top=False, left=False, bottom=False, right=False
    )

    assert preds.shape == (2, 62, 1)
    assert isinstance(preds_win, rasterio.windows.Window)
    assert preds_win == rasterio.windows.Window(124, 0, 1, 62)

    img_window = rasterio.windows.Window(0, 62, 125, 63)
    preds, preds_win = odd_window_memory_register.step(
        new_logits, img_window, top=False, left=False, bottom=False, right=False
    )

    assert preds.shape == (2, 62, 62)
    assert isinstance(preds_win, rasterio.windows.Window)
    assert preds_win == rasterio.windows.Window(0, 62, 62, 62)

    img_window = rasterio.windows.Window(0, 124, 125, 1)
    preds, preds_win = odd_window_memory_register.step(
        new_logits, img_window, top=False, left=False, bottom=False, right=False
    )

    assert preds.shape == (2, 1, 62)
    assert isinstance(preds_win, rasterio.windows.Window)
    assert preds_win == rasterio.windows.Window(0, 124, 62, 1)


def test_moving_window():
    class DummyKernel(Kernel):
        @staticmethod
        def _init_wi(size: int, device: torch.device.type) -> torch.Tensor:
            return torch.ones(size, device=device)

    h, w, s = 4, 4, 2
    register = TorchMemoryRegister(
        image_width=w,
        register_depth=1,
        window_size=s,
        kernel=DummyKernel,
        device=torch.device("cpu"),
    )
    output = torch.zeros((1, h, w), dtype=torch.float32)

    for row_off in range(0, h - s // 2, s // 2):
        for col_off in range(0, w - s // 2, s // 2):
            img_window = Window(
                row_off=row_off,
                col_off=col_off,
                height=(min(s, h - row_off)),
                width=(min(s, w - col_off)),
            )
            istop = row_off == 0
            isleft = col_off == 0
            isbottom = row_off == (h - s)
            isright = col_off == (w - s)

            preds, win = register.step(
                torch.ones((1, s, s), dtype=torch.float32),
                img_window,
                top=istop,
                left=isleft,
                bottom=isbottom,
                right=isright,
            )

            if istop:
                assert win.row_off == 0
                assert win.height == s // 2
            if isleft:
                assert win.col_off == 0
                assert win.width == s // 2
            if isbottom:
                assert win.row_off == h - s
                assert win.height == s
            if isright:
                assert win.col_off == w - s
                assert win.width == s

            output[
                :,
                win.row_off : win.row_off + win.height,
                win.col_off : win.col_off + win.width,
            ] += preds

    a = output[0].numpy()

    # Each corner should have been visited once
    assert np.allclose(a[0, 0], 1.0)
    assert np.allclose(a[0, w - 1], 1.0)
    assert np.allclose(a[h - 1, 0], 1.0)
    assert np.allclose(a[h - 1, w - 1], 1.0)

    # Edges not including corners should have been visited twice
    assert np.allclose(a[0, 1 : w - 1], 2.0)
    assert np.allclose(a[h - 1, 1 : w - 1], 2.0)
    assert np.allclose(a[1 : h - 1, 0], 2.0)
    assert np.allclose(a[1 : h - 1, w - 1], 2.0)

    # Center should have been visited four times
    assert np.allclose(a[1 : h - 1, 1 : w - 1], 4.0)


def test_kernel_sum():
    h, w, s = 600, 600, 20

    register = TorchMemoryRegister(
        image_width=w,
        register_depth=1,
        window_size=s,
        kernel=BartlettHannKernel,
        device=torch.device("cpu"),
    )
    output = torch.zeros((1, h, w), dtype=torch.float32)

    for row_off in range(0, h - s // 2, s // 2):
        for col_off in range(0, w - s // 2, s // 2):
            img_window = Window(
                row_off=row_off,
                col_off=col_off,
                height=(min(s, h - row_off)),
                width=(min(s, w - col_off)),
            )
            istop = row_off == 0
            isleft = col_off == 0
            isbottom = row_off == (h - s)
            isright = col_off == (w - s)

            preds, win = register.step(
                torch.ones((1, s, s), dtype=torch.float32),
                img_window,
                top=istop,
                left=isleft,
                bottom=isbottom,
                right=isright,
            )

            if istop:
                assert win.row_off == 0
                assert win.height == s // 2
            if isleft:
                assert win.col_off == 0
                assert win.width == s // 2
            if isbottom:
                assert win.row_off == h - s
                assert win.height == s
            if isright:
                assert win.col_off == w - s
                assert win.width == s

            output[
                :,
                win.row_off : win.row_off + win.height,
                win.col_off : win.col_off + win.width,
            ] += preds

    a = output[0].numpy()
    # Each output pixels should sum to 1
    assert np.allclose(a, 1.0)
