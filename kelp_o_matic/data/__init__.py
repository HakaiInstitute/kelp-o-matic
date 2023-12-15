import importlib.resources as importlib_resources

_base = importlib_resources.files(__name__)

rgb_kelp_presence_torchscript_path = (
    _base / "LRASPP_MobileNetV3_kelp_presence_rgb_jit_miou=0.8023.pt"
)
rgbi_kelp_presence_torchscript_path = (
    _base / "UNetPlusPlus_EfficientNetB4_kelp_presence_rgbi_jit_miou=0.8785.pt"
)
rgb_kelp_species_torchscript_path = (
    _base / "LRASPP_MobileNetV3_kelp_species_rgb_jit_miou=0.9634.pt"
)
rgbi_kelp_species_torchscript_path = (
    _base / "UNetPlusPlus_EfficientNetB4_kelp_species_rgbi_jit_miou=0.8432.pt"
)
rgb_mussel_presence_torchscript_path = (
    _base / "LRASPP_MobileNetV3_mussel_presence_rgb_jit_miou=0.8745.pt"
)
