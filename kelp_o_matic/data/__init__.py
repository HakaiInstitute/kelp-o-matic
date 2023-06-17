import importlib.resources as importlib_resources
c
_base = importlib_resources.files(__name__)

lraspp_kelp_presence_torchscript_path = (
    _base / "LRASPP_MobileNetV3_kelp_presence_jit_miou=0.8023.pt"
)
lraspp_kelp_species_torchscript_path = (
    _base / "LRASPP_MobileNetV3_kelp_species_jit_miou=0.9634.pt"
)
lraspp_mussel_presence_torchscript_path = (
    _base / "LRASPP_MobileNetV3_mussel_presence_jit_miou=0.8384.pt"
)
