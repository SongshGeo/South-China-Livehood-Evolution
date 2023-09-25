#!/usr/bin/env python 3.11.0
# -*-coding:utf-8 -*-
# @Author  : Shuang (Twist) Song
# @Contact   : SongshGeo@gmail.com
# GitHub   : https://github.com/SongshGeo
# Website: https://cv.songshgeo.com/

from abc import abstractmethod
from typing import Optional, Self

import numpy as np
from abses import Actor

from src.const import MAX_SIZE, MIN_SIZE, SCALE


class Person(Actor):
    pass

    def setup(self):
        super().setup()
        self._size: Optional[int] = MIN_SIZE

    @property
    def size(self) -> int:
        return self._size

    @size.setter
    def size(self, size):
        """人口规模有最大最小值限制"""
        if size < MIN_SIZE:
            size = MIN_SIZE
        elif size > MAX_SIZE:
            size = MAX_SIZE
        self._size = int(size)

    def population_growth(self, growth_rate: float) -> None:
        """人口增长"""
        self.size += self.size * growth_rate

    def diffusion(self, threshold: int, possibility: float) -> Self:
        """人口分散"""
        # 如果人口大于一定规模
        cond1 = self.size >= threshold  # SCALE[1] * 2
        # TODO 狩猎采集者只有条件一
        # 如果随机数小于概率
        cond2 = np.random.random() < possibility
        if cond1 and cond2:
            scale = np.arange(SCALE[0], SCALE[1])
            size = np.random.choice(scale)
            self.size -= size
            # TODO: 扩散到队伍到哪里？周围格子随机(r=1,2,3...)
            # self.__class__(size=size)
            return
        else:
            return None

    def convert(self, sphere: int = 1):
        region = self.buffer(sphere)
        # TODO 范围内若有其它农民，就转换？ + rate %
        # TODO 也在适宜耕种的地方
        # 有一定
        if self.model.select(region):
            # farmer = Farmer(location=self.loc)
            self.die()
            return
        self.move_to("到一个可以耕种的格子")

    @abstractmethod
    def able_to_go(self, pos) -> None:
        """能否到 pos 的地方"""
        # 是否是随机到pos，如果不行怎么办？
