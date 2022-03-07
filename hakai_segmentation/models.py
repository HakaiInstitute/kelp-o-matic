from abc import ABC, ABCMeta, abstractmethod

import torch

from hakai_segmentation.data import lraspp_kelp_presence_torchscript_path, lraspp_mussel_presence_torchscript_path


class _Model(ABC):
    def __init__(self, no_gpu: bool = False):
        self.device = torch.device('cuda') if torch.cuda.is_available() and not no_gpu else torch.device('cpu')
        self.model = self.load_model()

    @abstractmethod
    def load_model(self) -> 'torch.nn.Module':
        raise NotImplementedError

    def __call__(self, batch: 'torch.Tensor') -> 'torch.Tensor':
        return self.model.forward(batch.to(self.device))


class _JITModel(_Model, metaclass=ABCMeta):
    @property
    @abstractmethod
    def torchscript_path(self):
        raise NotImplementedError

    def load_model(self) -> 'torch.nn.Module':
        model = torch.jit.load(self.torchscript_path, map_location=self.device)
        model.eval()
        return model


class KelpPresenceSegmentationModel(_JITModel):
    torchscript_path = lraspp_kelp_presence_torchscript_path


class MusselPresenceSegmentationModel(_JITModel):
    torchscript_path = lraspp_mussel_presence_torchscript_path
