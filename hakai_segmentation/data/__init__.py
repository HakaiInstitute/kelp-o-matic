from pkg_resources import resource_filename

lraspp_kelp_presence_torchscript_path = resource_filename(
    __name__, 'LRASPP_MobileNetV3_kelp_presence_jit.pt')
lraspp_mussel_presence_torchscript_path = resource_filename(
    __name__, 'LRASPP_MobileNetV3_mussel_presence_jit.pt')
