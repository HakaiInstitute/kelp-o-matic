import gc
import importlib.resources as importlib_resources
from abc import ABC, abstractmethod
from typing import Union

import numpy as np
import torch
import torchvision.transforms.functional as f
from PIL.Image import Image

from kelp_o_matic.data import (
    rgb_kelp_presence_torchscript_path,
    rgb_kelp_species_torchscript_path,
    rgb_mussel_presence_torchscript_path,
)


class _Model(ABC):
    register_depth = 2

    @staticmethod
    def transform(x: Union[np.ndarray, Image]) -> torch.Tensor:
        x = f.to_tensor(x)[:3, :, :]
        x = f.normalize(x, mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        return x

    def __init__(self, use_gpu: bool = True):
        is_cuda = torch.cuda.is_available() and use_gpu
        self.device = torch.device("cuda") if is_cuda else torch.device("cpu")
        self.model = self.load_model()

    @property
    @abstractmethod
    def torchscript_path(self):
        raise NotImplementedError

    def load_model(self) -> "torch.nn.Module":
        with importlib_resources.as_file(self.torchscript_path) as ts:
            model = torch.jit.load(ts, map_location=self.device)
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


class KelpPresenceSegmentationModel(_Model):
    torchscript_path = rgb_kelp_presence_torchscript_path


class KelpSpeciesSegmentationModel(_Model):
    torchscript_path = rgb_kelp_species_torchscript_path
    register_depth = 4

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.presence_model = KelpPresenceSegmentationModel(*args, **kwargs)

    def __call__(self, x: "torch.Tensor") -> "torch.Tensor":
        with torch.no_grad():
            x = x.to(self.device)
            presence_logits = self.presence_model(x)  # 0: bg, 1: kelp
            species_logits = self.model.forward(x)  # 0: macro, 1: nerea
            logits = torch.concat((presence_logits, species_logits), dim=1)

        return logits  # 0: bg, 1: kelp, 2: macro, 3: nereo

    def post_process(self, x: "torch.Tensor") -> "np.ndarray":
        with torch.no_grad():
            presence = torch.argmax(x[:2], dim=0)  # 0: bg, 1: kelp
            species = torch.argmax(x[2:], dim=0) + 2  # 2: macro, 3: nereo
            label = torch.mul(presence, species)  # 0: bg, 2: macro, 3: nereo

        return label.detach().cpu().numpy()


class MusselPresenceSegmentationModel(_Model):
    torchscript_path = rgb_mussel_presence_torchscript_path
