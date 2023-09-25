#!/usr/bin/env python 3.11.0
# -*-coding:utf-8 -*-
# @Author  : Shuang (Twist) Song
# @Contact   : SongshGeo@gmail.com
# GitHub   : https://github.com/SongshGeo
# Website: https://cv.songshgeo.com/

from typing import Self

import numpy as np

from src.const import COMPLEXITY, GROWTH_RATE_FARMER, MIN_SIZE
from src.model import Model
from src.people import Person


class Farmer(Person):
    """
    农民类
    """

    def setup(self):
        super().setup()
        self.model = Model()
        self.growth_rate = GROWTH_RATE_FARMER

    @property
    def size(self) -> int:
        return self._size

    @size.setter
    def size(self, size):
        """人口规模有最大最小值限制"""
        if size < MIN_SIZE:
            self.die()
        elif size > self.max_size:
            self.complicate()
        self._size = int(size)

    @property
    def max_size(self) -> float:
        """最大人口数量"""
        return self.params.area * np.pi**2 * 2 / 0.005

    def complicate(self) -> Self:
        """农民的复杂化"""
        # 耕地上限再增加耕地密度增加、人口增长率下降
        self.max_size *= COMPLEXITY
        sub_group = None
        return sub_group
