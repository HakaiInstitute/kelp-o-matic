import math
from abc import ABCMeta, abstractmethod
from pathlib import Path
from typing import Union

import numpy as np
import rasterio
import torch
from rasterio.windows import Window


# Implementation of paper:
# https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0229839#pone.0229839.ref007


class Kernel(torch.nn.Module, metaclass=ABCMeta):
    def __init__(
        self, size: int = 512, device: torch.device.type = torch.device("cpu")
    ):
        super().__init__()
        self.size = size
        self.wi = self._init_wi(size, device)
        self.wj = self.wi.clone()

    @staticmethod
    @abstractmethod
    def _init_wi(size: int, device: torch.device.type) -> torch.Tensor:
        raise NotImplementedError

    def get_kernel(
        self,
        top: bool = False,
        bottom: bool = False,
        left: bool = False,
        right: bool = False,
    ) -> torch.Tensor:
        wi, wj = self.wi.clone(), self.wj.clone()

        if top:
            wi[: self.size // 2] = 1
        if bottom:
            wi[self.size // 2 :] = 1

        if left:
            wj[: self.size // 2] = 1
        if right:
            wj[self.size // 2 :] = 1

        return wi.unsqueeze(1) @ wj.unsqueeze(0)

    def forward(
        self,
        x: torch.Tensor,
        top: bool = False,
        bottom: bool = False,
        left: bool = False,
        right: bool = False,
    ) -> torch.Tensor:
        kernel = self.get_kernel(top=top, bottom=bottom, left=left, right=right)
        return torch.mul(x, kernel)


class HannKernel(Kernel):
    @staticmethod
    def _init_wi(size: int, device: torch.device.type) -> torch.Tensor:
        i = torch.arange(0, size, device=device)
        return (1 - ((2 * np.pi * i) / (size - 1)).cos()) / 2


class BartlettHannKernel(Kernel):
    @staticmethod
    def _init_wi(size: int, device: torch.device.type) -> torch.Tensor:
        # Follows original paper:
        # Ha YH, Pearce JA. A new window and comparison to standard windows.
        # IEEE Transactions on Acoustics, Speech, and Signal Processing.
        # 1989;37(2):298–301.
        i = torch.arange(0, size, device=device)
        return (
            0.62
            - 0.48 * (i / size - 1 / 2).abs()
            + 0.38 * (2 * np.pi * (i / size - 1 / 2).abs()).cos()
        )


class TriangularKernel(Kernel):
    @staticmethod
    def _init_wi(size: int, device: torch.device.type) -> torch.Tensor:
        i = torch.arange(0, size, device=device)
        return 1 - (2 * i / size - 1).abs()


class BlackmanKernel(Kernel):
    @staticmethod
    def _init_wi(size: int, device: torch.device.type) -> torch.Tensor:
        i = torch.arange(0, size, device=device)
        return (
            0.42
            - 0.5 * (2 * np.pi * i / size).cos()
            + 0.08 * (4 * np.pi * i / size).cos()
        )


class TorchMemoryRegister(object):
    def __init__(
        self,
        image_path: Union[str, Path],
        reg_depth: int,
        window_size: int,
        device: torch.device.type,
    ):
        super().__init__()
        self.image_path = Path(image_path)
        self.n = reg_depth
        self.ws = window_size
        self.hws = window_size // 2
        self.device = device

        # Copy metadata from img
        with rasterio.open(str(image_path), "r") as src:
            src_width = src.width

        self.height = self.ws
        self.width = (math.ceil(src_width / self.ws) * self.ws) + self.hws
        self.register = torch.zeros(
            (self.n, self.height, self.width), device=self.device
        )

    @property
    def _zero_chip(self):
        return torch.zeros(
            (self.n, self.hws, self.hws), dtype=torch.float, device=self.device
        )

    def step(self, new_logits: torch.Tensor, img_window: Window):
        # 1. Read data from the registry to update with the new logits
        # |a|b| |
        # |c|d| |
        with torch.no_grad():
            logits_abcd = self.register[
                :, :, img_window.col_off : img_window.col_off + self.ws
            ].clone()
            logits_abcd += new_logits

        # Update the registry and pop information-complete data
        # |c|b| | + pop a
        # |0|d| |
        logits_a = logits_abcd[:, : self.hws, : self.hws]
        logits_c = logits_abcd[:, self.hws :, : self.hws]
        logits_c0 = torch.concat([logits_c, self._zero_chip], dim=1)
        logits_bd = logits_abcd[:, :, self.hws :]

        # write c0
        self.register[
            :, :, img_window.col_off : img_window.col_off + self.hws
        ] = logits_c0

        # write bd
        col_off_bd = img_window.col_off + self.hws
        self.register[:, :, col_off_bd : col_off_bd + (self.ws - self.hws)] = logits_bd

        # Return the information-complete predictions
        preds_win = Window(
            col_off=img_window.col_off,
            row_off=img_window.row_off,
            height=min(self.hws, img_window.height),
            width=min(self.hws, img_window.width),
        )
        preds = logits_a[:, : img_window.height, : img_window.width].softmax(axis=0)

        return preds, preds_win
