#!/usr/bin/env python 3.11.0
# -*-coding:utf-8 -*-
# @Author  : Shuang (Twist) Song
# @Contact   : SongshGeo@gmail.com
# GitHub   : https://github.com/SongshGeo
# Website: https://cv.songshgeo.com/

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
        # TODO: 应当尽量减少农民主体和狩猎采集者之间的不同，分化和扩散可以写成一个方法吗？
        # 如果人口大于一定规模
        cond1 = self.size >= threshold
        # 如果随机数小于概率
        cond2 = np.random.random() < possibility
        if cond1 and cond2:
            # TODO 确认一下是否能这样表示30～60人规模队伍
            scale = np.arange(SCALE[0], SCALE[1])
            size = np.random.choice(scale)
            self.size -= size
            # TODO: 扩散到队伍到哪里？
            return self.__class__(size=size)
        else:
            return None
