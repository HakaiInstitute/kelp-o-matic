import math
from abc import ABCMeta, abstractmethod
from typing import Annotated, Type

import numpy as np
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
        image_width: Annotated[int, "Width of the image in pixels"],
        register_depth: Annotated[int, "Generally equal to the number of classes"],
        window_size: Annotated[int, "Moving window size"],
        kernel: Type[Kernel],
        device: torch.device.type,
    ):
        super().__init__()
        self.n = register_depth
        self.ws = window_size
        self.hws = window_size // 2
        self.kernel = kernel(size=window_size, device=device)
        self.device = device

        self.height = self.ws
        self.width = (math.ceil(image_width / self.ws) * self.ws) + self.hws
        self.register = torch.zeros(
            (self.n, self.height, self.width), device=self.device
        )

    @property
    def _zero_chip(self):
        return torch.zeros(
            (self.n, self.hws, self.hws), dtype=torch.float, device=self.device
        )

    def step(
        self,
        new_logits: torch.Tensor,
        img_window: Window,
        *,
        top: bool,
        bottom: bool,
        left: bool,
        right: bool,
    ):
        # Read data from the registry to update with the new logits
        # |a|b| |
        # |c|d| |
        with torch.no_grad():
            logits_abcd = self.register[
                :, :, img_window.col_off : img_window.col_off + self.ws
            ].clone()
            logits_abcd += self.kernel(
                new_logits, top=top, bottom=bottom, left=left, right=right
            )

        if right and bottom:
            # Need to return entire window
            logits_win = img_window
            logits = logits_abcd[:, : img_window.height, : img_window.width]

        elif right:
            # Need to return a and b sections

            # Update the registry and pop information-complete data
            # |c|d| | + pop a+b
            # |0|0| |
            logits_ab = logits_abcd[:, : self.hws, :]
            logits_cd = logits_abcd[:, self.hws :, :]
            logits_00 = torch.concat([self._zero_chip, self._zero_chip], dim=2)

            # write cd and 00
            self.register[
                :, : self.hws, img_window.col_off : img_window.col_off + self.ws
            ] = logits_cd
            self.register[
                :, self.hws :, img_window.col_off : img_window.col_off + self.ws
            ] = logits_00

            logits_win = Window(
                col_off=img_window.col_off,
                row_off=img_window.row_off,
                height=min(self.hws, img_window.height),
                width=min(self.ws, img_window.width),
            )
            logits = logits_ab[:, : logits_win.height, : logits_win.width]
        elif bottom:
            # Need to return a and c sections only

            # Update the registry and pop information-complete data
            # |0|b| | + pop a+c
            # |0|d| |
            logits_ac = logits_abcd[:, :, : self.hws]
            logits_00 = torch.concat([self._zero_chip, self._zero_chip], dim=1)
            logits_bd = logits_abcd[:, :, self.hws :]

            # write 00 and bd
            self.register[:, :, img_window.col_off : img_window.col_off + self.hws] = (
                logits_00  # Not really necessary since this is the last row
            )
            self.register[
                :, :, img_window.col_off + self.hws : img_window.col_off + self.ws
            ] = logits_bd

            logits_win = Window(
                col_off=img_window.col_off,
                row_off=img_window.row_off,
                height=min(self.ws, img_window.height),
                width=min(self.hws, img_window.width),
            )
            logits = logits_ac[:, : img_window.height, : img_window.width]
        else:
            # Need to return "a" section only

            # Update the registry and pop information-complete data
            # |c|b| | + pop a
            # |0|d| |
            logits_a = logits_abcd[:, : self.hws, : self.hws]
            logits_c = logits_abcd[:, self.hws :, : self.hws]
            logits_c0 = torch.concat([logits_c, self._zero_chip], dim=1)
            logits_bd = logits_abcd[:, :, self.hws :]

            # write c0
            self.register[:, :, img_window.col_off : img_window.col_off + self.hws] = (
                logits_c0
            )

            # write bd
            col_off_bd = img_window.col_off + self.hws
            self.register[:, :, col_off_bd : col_off_bd + (self.ws - self.hws)] = (
                logits_bd
            )

            logits_win = Window(
                col_off=img_window.col_off,
                row_off=img_window.row_off,
                height=min(self.hws, img_window.height),
                width=min(self.hws, img_window.width),
            )
            logits = logits_a[:, : img_window.height, : img_window.width]

        return logits, logits_win
