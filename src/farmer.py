#!/usr/bin/env python 3.11.0
# -*-coding:utf-8 -*-
# @Author  : Shuang (Twist) Song
# @Contact   : SongshGeo@gmail.com
# GitHub   : https://github.com/SongshGeo
# Website: https://cv.songshgeo.com/

from typing import Optional, Self

from const import MIN_SIZE
from src.const import AFFILIATED, COMPLEXITY, MAX_SIZE
from src.people import Person


class Farmer(Person):
    """
    农民类
    """

    def setup(self):
        super().setup()
        self._max_size: Optional[int] = MAX_SIZE

    @property
    def size(self) -> int:
        return self._size

    @size.setter
    def size(self, size):
        """人口规模有最大最小值限制"""
        if size < MIN_SIZE:
            size = MIN_SIZE
        elif size > self._max_size:
            # NOTE: 在这里设置条件，达到人口上限就复杂化
            self.complicate()
        # NOTE: 转化成整数
        self._size = int(size)

    def complicate(self) -> Self:
        """农民的复杂化"""
        # TODO 初始的规模是多少？
        sub_group = Farmer(size=0, max_size=MAX_SIZE * AFFILIATED)
        # TODO 这里有一个问题是，复杂化出来的上限很低，所以很容易进一步复杂化
        self._max_size *= COMPLEXITY
        return sub_group
