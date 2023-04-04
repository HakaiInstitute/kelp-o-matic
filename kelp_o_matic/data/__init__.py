from pkg_resources import resource_filename

lraspp_kelp_presence_onnx_path = resource_filename(
    __name__, "LRASPP_MobileNetV3_kelp_presence_jit_miou=0.8023.pt"
)
lraspp_kelp_species_onnx_path = resource_filename(
    __name__, "LRASPP_MobileNetV3_kelp_species_jit_miou=0.9634.pt"
)
lraspp_mussel_presence_onnx_path = resource_filename(
    __name__, "LRASPP_MobileNetV3_mussel_presence_jit_miou=0.8384.pt"
)
