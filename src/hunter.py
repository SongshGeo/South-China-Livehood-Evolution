#!/usr/bin/env python 3.11.0
# -*-coding:utf-8 -*-
# @Author  : Shuang (Twist) Song
# @Contact   : SongshGeo@gmail.com
# GitHub   : https://github.com/SongshGeo
# Website: https://cv.songshgeo.com/

from typing import Optional

from abses import Actor

from src.const import INTENSIFIED, LOSS
from src.people import Person


class Hunter(Actor):
    """狩猎采集者"""

    def setup(self):
        super().setup()
        self._move: Optional[bool] = None

    def move_to(self, *args, **kwargs):
        """有移动能力才能移动"""
        if self._move:
            # TODO 怎么移动？周围随机 r=1,2,3,..
            super().move_to(*args, **kwargs)

    def compete(self, other: Person):
        if other.breed == "Farmer":
            if self.size * INTENSIFIED > other.size:
                other.die()
            elif self.size * INTENSIFIED < other.size:
                self.size *= LOSS
                self.move_to()
        elif other.breed == "Hunter":
            if self.size >= other.size:
                other.move_to()
            elif self.size < other.size:
                self.move_to()
        # 如果农民在这可以加入农民
