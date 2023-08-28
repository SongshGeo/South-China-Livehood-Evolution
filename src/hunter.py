#!/usr/bin/env python 3.11.0
# -*-coding:utf-8 -*-
# @Author  : Shuang (Twist) Song
# @Contact   : SongshGeo@gmail.com
# GitHub   : https://github.com/SongshGeo
# Website: https://cv.songshgeo.com/

from typing import Optional

from abses import Actor

from src.const import INTENSIFIED, LOSS
from src.farmer import Farmer
from src.people import Person


class Hunter(Actor):
    """狩猎采集者"""

    def setup(self):
        super().setup()
        self._move: Optional[bool] = None

    def move_to(self, *args, **kwargs):
        """有移动能力才能移动"""
        if self._move:
            # TODO 怎么移动？如何随机？
            super().move_to(*args, **kwargs)

    def convert(self, sphere: int = 1):
        region = self.buffer(sphere)
        # TODO 范围内若有其它农民，就转换？那有点容易啊
        if self.model.select(region):
            farmer = Farmer(location=self.loc)
            self.die()
            return farmer

    def compete(self, other: Person):
        # TODO: 如何选择竞争对象？什么时候发生竞争？同一个地块？
        if other.breed == "Farmer":
            if self.size * INTENSIFIED > other.size:
                other.die()
            elif self.size * INTENSIFIED < other.size:
                self.size *= LOSS
                self.move_to()
        elif other.breed == "Hunter":
            if self.size > other.size:
                other.move_to()
            elif self.size < other.size:
                self.move_to()
            # TODO: 相等的时候怎么办？
