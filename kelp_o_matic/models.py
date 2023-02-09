import gc
from abc import ABC, ABCMeta, abstractmethod

import torch

from kelp_o_matic.data import (
    lraspp_kelp_presence_torchscript_path,
    lraspp_kelp_species_torchscript_path,
    lraspp_mussel_presence_torchscript_path,
)


class _Model(ABC):
    def __init__(self, use_gpu: bool = True):
        self.device = (
            torch.device("cuda")
            if torch.cuda.is_available() and use_gpu
            else torch.device("cpu")
        )
        self.model = self.load_model()

    @property
    @abstractmethod
    def torchscript_path(self):
        raise NotImplementedError

    def load_model(self) -> "torch.nn.Module":
        model = torch.jit.load(self.torchscript_path, map_location=self.device)
        model.eval()
        return model

    def reload(self):
        del self.model
        gc.collect()
        self.model = self.load_model()

    def __call__(self, batch: "torch.Tensor") -> "torch.Tensor":
        with torch.no_grad():
            return torch.argmax(self.model.forward(batch.to(self.device)), dim=1)


class KelpPresenceSegmentationModel(_Model):
    torchscript_path = lraspp_kelp_presence_torchscript_path


class KelpSpeciesSegmentationModel(_Model):
    torchscript_path = lraspp_kelp_species_torchscript_path

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.presence_model = KelpPresenceSegmentationModel(*args, **kwargs)

    def __call__(self, batch: "torch.Tensor") -> "torch.Tensor":
        with torch.no_grad():
            batch = batch.to(self.device)
            presence = self.presence_model(batch)  # 0: bg, 1: kelp
            species = torch.argmax(self.model.forward(batch), dim=1)  # 0: macro, 1: nereo

            return torch.mul(presence, torch.add(species, 2))  # 0: bg, 2: macro, 3: nereo


class MusselPresenceSegmentationModel(_Model):
    torchscript_path = lraspp_mussel_presence_torchscript_path
