import atexit
from contextlib import ExitStack
from importlib import resources

_file_manager = ExitStack()
atexit.register(_file_manager.close)

_base = resources.files(__name__)

lraspp_kelp_presence_torchscript_path = _file_manager.enter_context(
    resources.as_file(_base / "LRASPP_MobileNetV3_kelp_presence_jit_miou=0.8023.pt")
)
lraspp_kelp_species_torchscript_path = _file_manager.enter_context(
    resources.as_file(_base / "LRASPP_MobileNetV3_kelp_species_jit_miou=0.9634.pt")
)
lraspp_mussel_presence_torchscript_path = _file_manager.enter_context(
    resources.as_file(_base / "LRASPP_MobileNetV3_mussel_presence_jit_miou=0.8384.pt")
)
