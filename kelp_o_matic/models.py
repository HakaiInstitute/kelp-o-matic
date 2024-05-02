import gc
from abc import ABC, abstractmethod, ABCMeta
from typing import Union, Type

import numpy as np
import torch
import torchvision.transforms.functional as f
from PIL.Image import Image

from kelp_o_matic.utils import lazy_load_params


class _Model(ABC):
    register_depth = 2

    @staticmethod
    def transform(x: Union[np.ndarray, Image]) -> torch.Tensor:
        x = f.to_tensor(x)[:3, :, :].to(torch.float)
        x = f.normalize(x, mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        return x

    def __init__(self, use_gpu: bool = True):
        is_cuda = torch.cuda.is_available() and use_gpu
        self.device = torch.device("cuda") if is_cuda else torch.device("cpu")
        self.model = self.load_model()

    @property
    @abstractmethod
    def torchscript_path(self) -> str:
        raise NotImplementedError

    def load_model(self) -> "torch.nn.Module":
        params_file = lazy_load_params(self.torchscript_path)
        model = torch.jit.load(params_file, map_location=self.device)
        model.eval()
        return model

    def reload(self):
        del self.model
        gc.collect()
        self.model = self.load_model()

    def __call__(self, x: "torch.Tensor") -> "torch.Tensor":
        with torch.no_grad():
            return self.model.forward(x.to(self.device))

    def post_process(self, x: "torch.Tensor") -> "np.ndarray":
        return x.argmax(dim=0).detach().cpu().numpy()

    def shortcut(self, crop_size: int):
        """Shortcut prediction for when we know a cropped section is background.
        Prevent unnecessary forward passes through model."""
        logits = torch.zeros(
            (self.register_depth, crop_size, crop_size), device=self.device
        )
        logits[0] = 1
        return logits


class _SpeciesSegmentationModel(_Model, metaclass=ABCMeta):
    register_depth = 4

    @property
    @abstractmethod
    def presence_model_class(self) -> Type["_Model"]:
        raise NotImplementedError

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.presence_model = self.presence_model_class(*args, **kwargs)

    def __call__(self, x: "torch.Tensor") -> "torch.Tensor":
        with torch.no_grad():
            x = x.to(self.device)
            presence_logits = self.presence_model(x)  # 0: bg, 1: kelp
            species_logits = self.model.forward(x)  # 0: macro, 1: nerea
            logits = torch.concat((presence_logits, species_logits), dim=1)

        return logits  # [[0: bg, 1: kelp], [0: macro, 1: nereo]]

    def post_process(self, x: "torch.Tensor") -> "np.ndarray":
        with torch.no_grad():
            presence = torch.argmax(x[:2], dim=0)  # 0: bg, 1: kelp
            species = torch.argmax(x[2:], dim=0) + 2  # 2: macro, 3: nereo
            label = torch.mul(presence, species)  # 0: bg, 2: macro, 3: nereo

        return label.detach().cpu().numpy()


class KelpRGBPresenceSegmentationModel(_Model):
    torchscript_path = "LRASPP_MobileNetV3_kelp_presence_rgb_jit_miou=0.8023.pt"


class KelpRGBSpeciesSegmentationModel(_SpeciesSegmentationModel):
    torchscript_path = "LRASPP_MobileNetV3_kelp_species_rgb_jit_miou=0.9634.pt"
    presence_model_class = KelpRGBPresenceSegmentationModel


class MusselRGBPresenceSegmentationModel(_Model):
    register_depth = 1
    torchscript_path = (
        "UNetPlusPlus_EfficientNetB4_mussel_presence_rgb_jit_dice=0.9269.pt"
    )

    def post_process(self, x: "torch.Tensor") -> "np.ndarray":
        with torch.no_grad():
            label = (torch.sigmoid(x) > 0.5).to(torch.uint8)[0]

        return label.detach().cpu().numpy()


def _rgbi_kelp_transform(x: Union[np.ndarray, Image]) -> torch.Tensor:
    # to float
    x = f.to_tensor(x)[:4, :, :].to(torch.float)
    # min-max scale
    x_unique = x.flatten().unique()
    min_ = x_unique[0]
    if len(x_unique) > 1:
        min_, _ = torch.kthvalue(x_unique, 2)
    max_ = x.flatten().max()
    return torch.clamp((x - min_) / (max_ - min_ + 1e-8), 0, 1)


class KelpRGBIPresenceSegmentationModel(_Model):
    torchscript_path = (
        "UNetPlusPlus_EfficientNetB4_kelp_presence_rgbi_jit_miou=0.8785.pt"
    )

    @staticmethod
    def transform(x: Union[np.ndarray, Image]) -> torch.Tensor:
        return _rgbi_kelp_transform(x)


class KelpRGBISpeciesSegmentationModel(_SpeciesSegmentationModel):
    torchscript_path = (
        "UNetPlusPlus_EfficientNetB4_kelp_species_rgbi_jit_miou=0.8432.pt"
    )
    presence_model_class = KelpRGBIPresenceSegmentationModel

    @staticmethod
    def transform(x: Union[np.ndarray, Image]) -> torch.Tensor:
        return _rgbi_kelp_transform(x)
