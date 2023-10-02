#!/usr/bin/env python 3.11.0
# -*-coding:utf-8 -*-
# @Author  : Shuang (Twist) Song
# @Contact   : SongshGeo@gmail.com
# GitHub   : https://github.com/SongshGeo
# Website: https://cv.songshgeo.com/

from typing import Self

from abses import PatchCell

from src.farmer import Farmer
from src.people import SiteGroup, search_a_new_place


class Hunter(SiteGroup):
    """狩猎采集者"""

    @property
    def is_complex(self) -> bool:
        """关于移动力大小的讨论尺度都太小，或许可以简化为1次移动1格，把差异落在狩猎采集者是否定居，即丧失移动力。后者可大致设定为size_h大于100（Kelly 2013: 171）"""
        return self.size > self.params.settle_size

    def put_on(self, cell: PatchCell | None = None) -> None:
        super().put_on(cell)
        if cell is not None and cell.has_agent("Farmer"):
            farmers = cell.agents.select("Farmer")
            if len(farmers) > 1:
                raise ValueError("Hunter put on more than one farmer")
            farmer = farmers[0]
            self.compete(farmer)

    def diffuse(self, force: bool = False) -> Self:
        """如果人口大于一定规模，狩猎采集者分散出去"""
        if force:
            return super().diffuse()
        if self.size >= self.loc("lim_h"):
            return super().diffuse()

    def convert(self):
        """周围有其他农民"""
        # 周围有农民
        cells = self._cell.get_neighboring_cells(radius=1, moore=False)
        cond1 = any(cells.trigger("has_agent", breed="Farmer"))
        # 且目前的土地是可耕地
        cond2 = self._cell.is_arable
        # 同时满足上述条件，狩猎采集者转化为农民
        return super().convert() if cond1 and cond2 else self

    def move(self):
        """有移动能力才能移动，在周围随机选取一个格子移动"""
        if not self.is_complex:
            if cell := search_a_new_place(self, self._cell, radius=1):
                self.put_on(cell)

    def _loss_competition(self, loser: SiteGroup):
        """失败者"""
        loss = self.model.params.loss_rate
        if loser.breed == "Farmer":
            loser.die()
        elif loser.breed == "Hunter":
            # * 这里我进行了一些修改，算是逃跑一只，大部队消灭
            loser.size *= loss
            if _ := loser.diffuse(force=True):
                loser.die()
        else:
            raise TypeError("Agent must be Farmer or Hunter.")

    def _compete_with_hunter(self, hunter: Self) -> bool:
        """与其它狩猎采集者竞争"""
        if self.size >= hunter.size:
            self._loss_competition(hunter)
            return True
        self._loss_competition(self)
        return False

    def _compete_with_farmer(self, farmer: Farmer) -> bool:
        """与其它农民竞争"""
        power = self.size * self.params.intensified_coefficient
        if power >= farmer.size:
            self._loss_competition(farmer)
            return True
        self._loss_competition(self)
        return False

    def compete(self, other: SiteGroup) -> bool:
        """与其它主体竞争
        other: 竞争者
        return: True or False，竞争成功或失败
        """
        if other.breed == "Farmer":
            return self._compete_with_farmer(other)
        elif other.breed == "Hunter":
            return self._compete_with_hunter(other)
        raise TypeError("Agent must be Farmer or Hunter.")
