#!/usr/bin/env python 3.11.0
# -*-coding:utf-8 -*-
# @Author  : Shuang (Twist) Song
# @Contact   : SongshGeo@gmail.com
# GitHub   : https://github.com/SongshGeo
# Website: https://cv.songshgeo.com/

"""狩猎采集者的。
"""

from numbers import Number
from typing import Self, Tuple

import numpy as np
from abses import PatchCell

from src.farmer import Farmer
from src.people import SiteGroup, search_a_new_place


class Hunter(SiteGroup):
    """狩猎采集者"""

    @SiteGroup.size.setter
    def size(self, size: Number) -> None:
        if size < self.min_size:
            SiteGroup.size.fset(self, size)
        else:
            self._size = size

    @property
    def max_size(self) -> int:
        if not self.on_earth:
            return 100_000_000
        return np.ceil(self.loc("lim_h"))

    @property
    def is_complex(self) -> bool:
        """超过定居规模的阈值，会变成复杂狩猎采集者。参数配置文件里的`settle_size`可以调节该阈值。

        returns:
            是否是复杂狩猎采集者
        """
        return self.size > self.max_size

    def put_on(self, cell: PatchCell | None = None) -> None:
        """将狩猎采集者放到某个格子。狩猎采集者放到的格子如果已经有了一个主体，就会与他竞争（触发竞争方法）。

        Args:
            cell (PatchCell | None): 狩猎采集者放到的格子。
        """
        # 如果没有目标格子（死亡）
        if cell is None:
            super().put_on()
            return
        existing_agent = cell.agents[0] if cell.has_agent() else None
        super().put_on(cell)
        if existing_agent:
            self.compete(existing_agent)
        # 每到一个格子，重新设置大小，因为人口上限发生改变
        self.size = self.size

    def diffuse(self, group_range: Tuple[Number] | None = None) -> Self:
        """如果人口大于一定规模，狩猎采集者分散出去

        Args:
            force (bool): 是否强制触发该方法

        returns:
            分散后的结果。
            - 如果成功分散，返回分散出的新主体。
            - 当无法成功分散时，返回空值。
        """
        if self.size >= self.max_size:
            return super().diffuse(group_range=group_range)

    def convert(
        self, convert_prob: float | None = None, radius: int = 1, moore: bool = False
    ) -> Self:
        """狩猎采集者可能转化为农民，需要满足以下条件：
        1. 周围有农民
        2. 目前的土地是可耕地

        Args:
            radius (int): 搜索的半径范围，默认为周围一格。
            moore (bool): 是否使用Moore邻域进行搜索，
            即搜索8临域，包括对角线的四个格子。
            默认不启用（即仅计算上下左右四个格子）。

        returns:
            如果没有转化，返回自身。
            如果成功转化，返回转化后的主体。
        """
        # 周围有农民
        cells = self._cell.get_neighboring_cells(radius=radius, moore=moore)
        cond1 = any(cells.trigger("has_agent", breed="Farmer"))
        # 且目前的土地是可耕地
        cond2 = self._cell.is_arable
        # 同时满足上述条件，狩猎采集者转化为农民
        return super().convert(convert_prob) if cond1 and cond2 else self

    def move(self, radius: int = 1) -> None:
        """有移动能力才能移动，在周围随机选取一个格子移动。

        Note:
            *关于移动力大小的讨论尺度都太小，或许可以简化为1次移动1格。
            把差异落在狩猎采集者是否定居，即丧失移动力。
            后者可大致设定为size_h大于100（Kelly 2013: 171）。*

        Args:
            radius (int): 搜索的半径范围，在周围一格

        returns:
            如果成功移动，返回 `True`，否则返回 `False`。
        """
        # self._check_moves()
        if not self.is_complex:
            if cell := search_a_new_place(self, self._cell, radius=radius):
                self.put_on(cell)
                return True
        return False

    def _loss_competition(self, loser: SiteGroup):
        """失败者"""
        loss = self.model.params.loss_rate
        if loser.breed == "Farmer":
            loser.die()
        elif loser.breed == "Hunter":
            loser.size *= loss
            # 如果损失人口之后还在世界上，就溜了
            if loser.on_earth:
                loser.move()
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
        """与其它主体竞争，根据竞争对象有着不同的竞争规则：
        1. 与狩猎采集者竞争时，比较两者的人口规模。输了的一方将人口减半并进行一次移动。
        2. 与农民竞争时，狩猎采集者会具备一定强化系数，通过配置文件里的 `intensified_coefficient` 参数进行调节。
        输了的一方如果是农民，则直接被狩猎采集者消灭；
        如果是狩猎采集者，则将人口减半并进行一次移动。

        Args:
            other: 与该主体竞争的另一个主体。

        returns:
            竞争成功则返回 `True`，否则返回 `False`。
        """
        if other.breed == "Farmer":
            return self._compete_with_farmer(other)
        if other.breed == "Hunter":
            return self._compete_with_hunter(other)
        raise TypeError("Agent must be Farmer or Hunter.")
