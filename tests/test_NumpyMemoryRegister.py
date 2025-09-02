import numpy as np
import pytest
import rasterio
from numpy.typing import DTypeLike
from rasterio import windows
from rasterio.transform import from_origin

from kelp_o_matic.hann import BartlettHannKernel, Kernel, NumpyMemoryRegister


def create_dummy_tiff(
    filename: str,
    width: int = 512,
    height: int = 512,
    num_bands: int = 3,
    dtype: DTypeLike = np.uint8,
) -> None:
    """Create a dummy TIFF file for testing.

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
        rng = np.random.default_rng(0)
        # Write dummy data to each band
        for i in range(1, num_bands + 1):
            data = rng.uniform(0, 255, (height, width)).astype(dtype)
            dst.write(data, i)


@pytest.fixture
def memory_register() -> NumpyMemoryRegister:
    # Initialize NumpyMemoryRegister with the dummy image
    return NumpyMemoryRegister(
        image_width=1000,
        register_depth=2,
        window_size=256,
        kernel=BartlettHannKernel,
    )


@pytest.fixture
def small_img_memory_register() -> NumpyMemoryRegister:
    # Initialize NumpyMemoryRegister with the dummy image
    return NumpyMemoryRegister(
        image_width=200,
        register_depth=2,
        window_size=256,
        kernel=BartlettHannKernel,
    )


@pytest.fixture
def full_window_memory_register() -> NumpyMemoryRegister:
    # Initialize NumpyMemoryRegister with the dummy image
    return NumpyMemoryRegister(
        image_width=200,
        register_depth=2,
        window_size=200,
        kernel=BartlettHannKernel,
    )


@pytest.fixture
def odd_window_memory_register() -> NumpyMemoryRegister:
    # Initialize NumpyMemoryRegister with the dummy image
    return NumpyMemoryRegister(
        image_width=200,
        register_depth=2,
        window_size=125,
        kernel=BartlettHannKernel,
    )


def test_initialization(memory_register: NumpyMemoryRegister) -> None:
    assert memory_register.n == 2
    assert memory_register.ws == 256
    assert memory_register.hws == 256 // 2
    assert isinstance(memory_register.kernel, BartlettHannKernel)
    width = np.ceil(1000 / 256) * 256 + 128
    assert width == memory_register.width
    assert memory_register.register.shape == (2, 256, width)


def test_step_method(memory_register: NumpyMemoryRegister) -> None:
    # Test typical case
    rng = np.random.default_rng(0)
    new_logits = rng.uniform(size=(2, 256, 256))

    img_window = windows.Window(col_off=0, row_off=0, width=256, height=256)
    preds, preds_win = memory_register._step(
        new_logits,
        img_window,
        top=False,
        left=False,
        bottom=False,
        right=False,
    )

    assert preds.shape == (2, 128, 128)
    assert isinstance(preds_win, windows.Window)
    assert preds_win == windows.Window(col_off=0, row_off=0, width=128, height=128)

    img_window = windows.Window(col_off=768, row_off=0, width=232, height=256)
    preds, preds_win = memory_register._step(
        new_logits,
        img_window,
        top=False,
        left=False,
        bottom=False,
        right=False,
    )

    assert preds.shape == (2, 128, 128)
    assert isinstance(preds_win, windows.Window)
    assert preds_win == windows.Window(col_off=768, row_off=0, width=128, height=128)

    img_window = windows.Window(col_off=896, row_off=0, width=104, height=256)
    preds, preds_win = memory_register._step(
        new_logits,
        img_window,
        top=False,
        left=False,
        bottom=False,
        right=False,
    )

    assert preds.shape == (2, 128, 104)
    assert isinstance(preds_win, windows.Window)
    assert preds_win == windows.Window(col_off=896, row_off=0, width=104, height=128)


def test_small_img_edge_case(small_img_memory_register: NumpyMemoryRegister) -> None:
    # Test small image
    rng = np.random.default_rng(0)
    new_logits = rng.uniform(size=(2, 256, 256))

    img_window = windows.Window(col_off=0, row_off=0, width=200, height=200)
    preds, preds_win = small_img_memory_register._step(
        new_logits,
        img_window,
        top=False,
        left=False,
        bottom=False,
        right=False,
    )

    assert preds.shape == (2, 128, 128)
    assert isinstance(preds_win, windows.Window)
    assert preds_win == windows.Window(col_off=0, row_off=0, width=128, height=128)

    img_window = windows.Window(col_off=128, row_off=0, width=72, height=200)
    preds, preds_win = small_img_memory_register._step(
        new_logits,
        img_window,
        top=False,
        left=False,
        bottom=False,
        right=False,
    )

    assert preds.shape == (2, 128, 72)
    assert isinstance(preds_win, windows.Window)
    assert preds_win == windows.Window(col_off=128, row_off=0, width=72, height=128)

    img_window = windows.Window(col_off=0, row_off=128, width=128, height=72)
    preds, preds_win = small_img_memory_register._step(
        new_logits,
        img_window,
        top=False,
        left=False,
        bottom=False,
        right=False,
    )

    assert preds.shape == (2, 72, 128)
    assert isinstance(preds_win, windows.Window)
    assert preds_win == windows.Window(col_off=0, row_off=128, width=128, height=72)

    img_window = windows.Window(col_off=128, row_off=128, width=72, height=72)
    preds, preds_win = small_img_memory_register._step(
        new_logits,
        img_window,
        top=False,
        left=False,
        bottom=False,
        right=False,
    )

    assert preds.shape == (2, 72, 72)
    assert isinstance(preds_win, windows.Window)
    assert preds_win == windows.Window(col_off=128, row_off=128, width=72, height=72)


def test_full_window_sizes(full_window_memory_register: NumpyMemoryRegister) -> None:
    # Test case that image size is equal to the register window size
    rng = np.random.default_rng(0)
    new_logits = rng.uniform(size=(2, 200, 200))

    img_window = windows.Window(col_off=0, row_off=0, width=200, height=200)
    preds, preds_win = full_window_memory_register._step(
        new_logits,
        img_window,
        top=False,
        left=False,
        bottom=False,
        right=False,
    )

    assert preds.shape == (2, 100, 100)
    assert isinstance(preds_win, windows.Window)
    assert preds_win == windows.Window(col_off=0, row_off=0, width=100, height=100)

    img_window = windows.Window(col_off=100, row_off=0, width=100, height=200)
    preds, preds_win = full_window_memory_register._step(
        new_logits,
        img_window,
        top=False,
        left=False,
        bottom=False,
        right=False,
    )

    assert preds.shape == (2, 100, 100)
    assert isinstance(preds_win, windows.Window)
    assert preds_win == windows.Window(col_off=100, row_off=0, width=100, height=100)


def test_odd_window_size(odd_window_memory_register: NumpyMemoryRegister) -> None:
    # Test case where the register size is an odd number
    rng = np.random.default_rng(0)
    new_logits = rng.uniform(size=(2, 125, 125))

    assert odd_window_memory_register.hws == 62

    img_window = windows.Window(col_off=0, row_off=0, width=125, height=125)
    preds, preds_win = odd_window_memory_register._step(
        new_logits,
        img_window,
        top=False,
        left=False,
        bottom=False,
        right=False,
    )

    assert preds.shape == (2, 62, 62)
    assert isinstance(preds_win, windows.Window)
    assert preds_win == windows.Window(col_off=0, row_off=0, width=62, height=62)

    img_window = windows.Window(col_off=62, row_off=0, width=63, height=125)
    preds, preds_win = odd_window_memory_register._step(
        new_logits,
        img_window,
        top=False,
        left=False,
        bottom=False,
        right=False,
    )

    assert preds.shape == (2, 62, 62)
    assert isinstance(preds_win, windows.Window)
    assert preds_win == windows.Window(col_off=62, row_off=0, width=62, height=62)

    img_window = windows.Window(col_off=124, row_off=0, width=1, height=125)
    preds, preds_win = odd_window_memory_register._step(
        new_logits,
        img_window,
        top=False,
        left=False,
        bottom=False,
        right=False,
    )

    assert preds.shape == (2, 62, 1)
    assert isinstance(preds_win, windows.Window)
    assert preds_win == windows.Window(col_off=124, row_off=0, width=1, height=62)

    img_window = windows.Window(col_off=0, row_off=62, width=125, height=63)
    preds, preds_win = odd_window_memory_register._step(
        new_logits,
        img_window,
        top=False,
        left=False,
        bottom=False,
        right=False,
    )

    assert preds.shape == (2, 62, 62)
    assert isinstance(preds_win, windows.Window)
    assert preds_win == windows.Window(col_off=0, row_off=62, width=62, height=62)

    img_window = windows.Window(col_off=0, row_off=124, width=125, height=1)
    preds, preds_win = odd_window_memory_register._step(
        new_logits,
        img_window,
        top=False,
        left=False,
        bottom=False,
        right=False,
    )

    assert preds.shape == (2, 1, 62)
    assert isinstance(preds_win, windows.Window)
    assert preds_win == windows.Window(col_off=0, row_off=124, width=62, height=1)


def test_moving_window() -> None:
    class DummyKernel(Kernel):
        @staticmethod
        def _init_wi(size: int) -> np.ndarray:
            return np.ones(size)

    h, w, s = 4, 4, 2
    register = NumpyMemoryRegister(
        image_width=w,
        register_depth=1,
        window_size=s,
        kernel=DummyKernel,
    )
    output = np.zeros((1, h, w), dtype=np.float32)

    for row_off in range(0, h - s // 2, s // 2):
        for col_off in range(0, w - s // 2, s // 2):
            img_window = windows.Window(
                row_off=row_off,
                col_off=col_off,
                height=(min(s, h - row_off)),
                width=(min(s, w - col_off)),
            )
            istop = row_off == 0
            isleft = col_off == 0
            isbottom = row_off == (h - s)
            isright = col_off == (w - s)

            preds, win = register._step(
                np.ones((1, s, s), dtype=np.float32),
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

    a = output[0]

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


def test_kernel_sum() -> None:
    h, w, s = 600, 600, 20

    register = NumpyMemoryRegister(
        image_width=w,
        register_depth=1,
        window_size=s,
        kernel=BartlettHannKernel,
    )
    output = np.zeros((1, h, w), dtype=np.float32)

    for row_off in range(0, h - s // 2, s // 2):
        for col_off in range(0, w - s // 2, s // 2):
            img_window = windows.Window(
                row_off=row_off,
                col_off=col_off,
                height=(min(s, h - row_off)),
                width=(min(s, w - col_off)),
            )
            istop = row_off == 0
            isleft = col_off == 0
            isbottom = row_off == (h - s)
            isright = col_off == (w - s)

            preds, win = register._step(
                np.ones((1, s, s), dtype=np.float32),
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

    a = output[0]
    # Each output pixels should sum to 1
    assert np.allclose(a, 1.0)
