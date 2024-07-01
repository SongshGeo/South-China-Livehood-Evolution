#!/usr/bin/env python 3.11.0
# -*-coding:utf-8 -*-
# @Author  : Shuang (Twist) Song
# @Contact   : SongshGeo@gmail.com
# GitHub   : https://github.com/SongshGeo
# Website: https://cv.songshgeo.com/

from typing import Self

from .farmer import Farmer


class RiceFarmer(Farmer):
    """种植水稻的农民"""

    def convert(self) -> Farmer | Self:
        """可以转化会种植普通水稻的农民"""
        cond1 = self.size < self.params.convert_threshold.get("to_farmer")
        cond2 = self.random.random() < self.params.convert_prob.get("to_farmer", 0.0)
        return self._cell.convert(self, to="Farmer") if cond1 & cond2 else self
