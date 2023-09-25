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
from abses.nature import PatchCell
from src.const import MAX_SIZE, MIN_SIZE


def search_a_new_place(cell: PatchCell) -> PatchCell:
    """在周围寻找一个新的地方，能够让迁徙的人过去"""
    # TODO finish this
    # TODO: 扩散到队伍到哪里？周围格子随机(r=1,2,3...)
    return cell


class SiteGroup(Actor):
    """原始的聚落"""

    def __init__(self, *arg, **kwargs) -> None:
        super().__init__(*arg, **kwargs)
        self._size: Optional[int] = self.params.min_size

    @property
    def size(self) -> int:
        """人口规模"""
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

    def diffuse(self) -> Self:
        """人口分散，随机选择一个最小和最大的规模，分裂出去"""
        s_min, s_max = self.params.new_group_size
        size = np.random.choice(np.arange(s_min, s_max))
        self.size -= size
        new_group = self.__class__(model=self.model, size=size)
        new_group.put_on(search_a_new_place(self._cell))

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
