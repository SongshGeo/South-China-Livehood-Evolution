#!/usr/bin/env python 3.11.0
# -*-coding:utf-8 -*-
# @Author  : Shuang (Twist) Song
# @Contact   : SongshGeo@gmail.com
# GitHub   : https://github.com/SongshGeo
# Website: https://cv.songshgeo.com/

"""狩猎采集者的。
"""
from __future__ import annotations

from numbers import Number
from typing import Optional, Self, Tuple

import numpy as np
from abses import PatchCell, alive_required

from abses_sce.farmer import Farmer
from abses_sce.people import SiteGroup, search_cell
from abses_sce.rice_farmer import RiceFarmer


class Hunter(SiteGroup):
    """狩猎采集者"""

    @property
    def max_size(self) -> int:
        return np.ceil(self.get("lim_h")) if self.on_earth else 100_000_000

    @property
    def is_complex(self) -> bool:
        """超过定居规模的阈值，会变成复杂狩猎采集者。参数配置文件里的`settle_size`可以调节该阈值。

        returns:
            是否是复杂狩猎采集者
        """
        return self.size > self.params.is_complex if self.on_earth else False

    @alive_required
    def moving(self, cell: PatchCell) -> None:
        """狩猎采集者要去的格子如果已经有了一个主体，就会与他竞争

        Args:
            cell (PatchCell | None): 狩猎采集者放到的格子。
        """
        other = cell.agents.item("item")
        if other is None:
            return True
        while other.alive and self.alive:
            result = self.compete(other)
        return result

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
        return None

    @alive_required
    def convert(self, radius: int = 1, moore: bool = False) -> Self:
        """狩猎采集者向农民转化：
        1. 优先转化成普通农民
        2. 其次考虑转化为水稻农民
        """
        agent = self._convert_to_farmer(radius=radius, moore=moore)
        # agent 不是自己说明转化成功
        if agent is not self:
            return agent
        # 没成功再看转化水稻农民的结果
        return self._convert_to_rice(radius=radius, moore=moore)

    def _convert_to_farmer(self, radius: int = 1, moore: bool = False) -> Self | Farmer:
        """狩猎采集者可能转化为农民，需要满足以下条件：
        1. 周围有农民
        2. 目前的土地是可耕地
        3. 转化概率小于阈值

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
        cells = self.at.neighboring(radius=radius, moore=moore)
        cond1 = any(cells.apply(lambda c: c.agents.has("Farmer")))
        # 且目前的土地是可耕地
        cond2 = self.at.is_arable
        # 转化概率小于阈值
        convert_prob = self.params.convert_prob.get("to_farmer", 0.0)
        cond3 = self.random.random() < convert_prob
        # 同时满足上述条件，狩猎采集者转化为农民
        return self.at.convert(self, "Farmer") if cond1 and cond2 and cond3 else self

    def _convert_to_rice(
        self, radius: int = 1, moore: bool = False
    ) -> Self | RiceFarmer:
        """狩猎采集者可能转化为水稻农民，需要满足以下条件：
        1. 周围有水稻农民
        2. 目前的土地是满足水稻生长条件的可耕地
        3. 转化概率小于阈值

        Args:
            radius (int): 搜索的半径范围，默认为周围一格。
            moore (bool): 是否使用Moore邻域进行搜索，
            即搜索8临域，包括对角线的四个格子。
            默认不启用（即仅计算上下左右四个格子）。

        returns:
            如果没有转化，返回自身。
            如果成功转化，返回转化后的主体。
        """
        # 周围有水稻农民
        cells = self.at.neighboring(radius=radius, moore=moore)
        cond1 = any(cells.apply(lambda c: c.agents.has("RiceFarmer")))
        # 且目前的土地是可耕地
        cond2 = self.at.is_rice_arable
        # 转化概率小于阈值
        convert_prob = self.params.convert_prob.get("to_rice", 0.0)
        cond3 = self.random.random() < convert_prob
        # 同时满足上述条件，狩猎采集者转化为农民
        return (
            self.at.convert(self, "RiceFarmer") if cond1 and cond2 and cond3 else self
        )

    @alive_required
    def move_one(self, radius: int = 1, cell_now: Optional[PatchCell] = None) -> None:
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
        if self.is_complex:
            return False
        # 如果没有指定当前的格子，就使用当前的格子
        if cell_now is None:
            cell_now = self.at
        if new_cell := search_cell(self, cell_now, radius=radius):
            self.move.to(new_cell)
            return True
        return False

    @alive_required
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
        power = self.size
        if isinstance(other, (Farmer, RiceFarmer)):
            power *= self.params.intensified_coefficient
        if power >= other.size:
            other.loss_in_competition(at=other.at)
            return True
        self.loss_in_competition(at=other.at)
        return False

    def loss_in_competition(self, at: Optional[PatchCell] = None) -> None:
        """在竞争中失败"""
        if self.is_complex:
            return self.die()
        self.size *= self.model.params.loss_rate
        # 没打过就继续跑吧
        self.move_one(cell_now=at)
        return None

    def step(self):
        """step of a hunter."""
        super().step()
        self.move_one()
