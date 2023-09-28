#!/usr/bin/env python 3.11.0
# -*-coding:utf-8 -*-
# @Author  : Shuang (Twist) Song
# @Contact   : SongshGeo@gmail.com
# GitHub   : https://github.com/SongshGeo
# Website: https://cv.songshgeo.com/

from typing import Self

import numpy as np

from src.people import SiteGroup


class Farmer(SiteGroup):
    """
    农民类
    """

    @property
    def size(self) -> int:
        return self._size

    @size.setter
    def size(self, size):
        """人口规模有最大最小值限制"""
        if size < self.params.min_size:
            self.die()
        elif size > self.max_size:
            self.complicate()
        self._size = int(size)

    @property
    def max_size(self) -> float:
        """最大人口数量"""
        return self.params.area * np.pi**2 * 2 / 0.005

    def diffuse(self) -> Self:
        """农民的分散"""
        cond1 = self.size >= self.loc("lim_h")
        cond2 = np.random.random() < self.params.diffuse_prob
        if cond1 and cond2:
            super().diffuse()

    def complicate(self) -> Self:
        """农民的复杂化"""
        # 耕地上限再增加耕地密度增加、人口增长率下降
        self.max_size *= self.params.complexity
        # sub_group = None
        # return sub_group
