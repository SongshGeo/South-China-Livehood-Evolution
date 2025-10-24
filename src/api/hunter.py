#!/usr/bin/env python 3.11.0
# -*-coding:utf-8 -*-
# @Author  : Shuang (Twist) Song
# @Contact   : SongshGeo@gmail.com
# GitHub   : https://github.com/SongshGeo
# Website: https://cv.songshgeo.com/

"""狩猎采集者的。"""
from __future__ import annotations

from numbers import Number
from typing import Optional, Self, Tuple

import numpy as np
from abses import PatchCell, alive_required

from src.api.farmer import Farmer
from src.api.people import SiteGroup, search_cell
from src.api.rice_farmer import RiceFarmer


class Hunter(SiteGroup):
    """狩猎采集者"""

    @property
    def max_size(self) -> int:
        """单位主体人口最大值：普通情况100，临近水体500"""
        if not self.on_earth:
            return 100_000_000

        # 检查是否临近水体
        if self.is_near_water():
            return self.params.max_size_water
        return self.params.max_size

    def is_near_water(self) -> bool:
        """检查是否临近水体（当前格子 water_type = 1）

        Returns:
            如果当前格子的 water_type = 1（近水陆地），返回 True，否则返回 False
        """
        if not self.on_earth:
            return False
        return self.at.is_near_water

    @property
    def is_complex(self) -> bool:
        """超过定居规模的阈值，会变成复杂狩猎采集者。参数配置文件里的`is_complex`可以调节该阈值。

        returns:
            是否是复杂狩猎采集者
        """
        return self.size > self.params.is_complex if self.on_earth else False

    @alive_required
    def merge(self, other_hunter: Hunter) -> bool:
        """狩猎采集者合并，保证人口守恒并检查全局人口上限。

        Parameters:
            other_hunter: 另一个狩猎采集者。

        Returns:
            是否被合并了。
        """
        # 计算合并后的人口
        merged_size = other_hunter.size + self.size

        # 检查全局人口上限
        try:
            env = self.model.nature
            if hasattr(env, "can_hunters_grow") and hasattr(env, "global_hunter_limit"):
                current_total = env.get_total_hunter_population()
                if merged_size > current_total:  # 合并会增加总人口
                    additional_population = merged_size - current_total
                    if not env.can_hunters_grow(additional_population):
                        # 如果超过全局上限，不进行合并
                        return False
        except (AttributeError, TypeError):
            pass  # 如果环境还没初始化，跳过检查

        # 进行正常合并（确保人口守恒）
        other_hunter.size = merged_size
        self.die()
        return True

    def diffuse(self, group_range: Tuple[Number] | None = None) -> Self:
        """如果人口大于一定规模，狩猎采集者分散出去

        Args:
            group_range (Tuple[Number, Number] | None):
                新主体的规模范围（最小值，最大值），默认为当前主体的规模参数。

        returns:
            分散后的结果。
            - 如果成功分散，返回分散出的新主体。
            - 当无法成功分散时，返回空值。
        """
        if self.size >= self.max_size:
            # 扩散不会增加总人口，所以不需要检查全局上限
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
        cond1 = any(cells.apply(lambda c: c.agents.has(Farmer)))
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
        cond1 = any(cells.apply(lambda c: c.agents.has(RiceFarmer)))
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

    def loss(self) -> None:
        """狩猎采集者的损失，按概率减少人口。"""
        if self.random.random() < self.params.loss.prob:
            self.size *= 1 - self.params.loss.rate

    @alive_required
    def population_growth(self, growth_rate: Optional[float] = None) -> None:
        """人口增长，检查全局人口上限"""
        if growth_rate is None:
            growth_rate = self.params.growth_rate

        # 计算增长后的人口
        new_size = self._size + self._size * growth_rate
        growth_amount = int(new_size - self._size)

        # 检查全局人口上限
        if growth_amount > 0:
            try:
                env = self.model.nature
                if hasattr(env, "can_hunters_grow") and hasattr(
                    env, "global_hunter_limit"
                ):
                    if not env.can_hunters_grow(growth_amount):
                        # 如果超过全局上限，不进行增长
                        return
            except (AttributeError, TypeError):
                pass  # 如果环境还没初始化，跳过检查

        # 进行正常增长
        self.size = new_size

    def step(self):
        """step of a hunter."""
        super().step()
        self.loss()
        self.move_one()
