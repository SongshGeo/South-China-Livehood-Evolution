#!/usr/bin/env python 3.11.0
# -*-coding:utf-8 -*-
# @Author  : Shuang (Twist) Song
# @Contact   : SongshGeo@gmail.com
# GitHub   : https://github.com/SongshGeo
# Website: https://cv.songshgeo.com/

"""这个模块是基本的主体类，写了 Farmer 和 Hunter 类的某些共用方法，
根据不同具体类别的主体需求，部分功能也会被覆写。
"""

from numbers import Number
from typing import Optional, Self, Tuple

import numpy as np
import pandas as pd
from abses import Actor, alive_required
from abses.cells import PatchCell


class SiteGroup(Actor):
    """原始的聚落"""

    def __init__(self, *arg, **kwargs) -> None:
        super().__init__(*arg, **kwargs)
        self._min_size = self.params.get("min_size", 0.0)
        self._max_size = self.params.get("max_size", 0.0)
        self.size = kwargs.get("size", self.min_size)
        self.source = self.breed

    @property
    def size(self) -> int:
        """人口规模，转化成整数"""
        return np.ceil(self._size)

    @size.setter
    def size(self, size: Number) -> None:
        """人口规模有最大最小值限制"""
        if size < self.min_size:
            # 如果小于能够生存的最小情况，就死去
            self.die()
            return
        size = min(size, self.max_size)
        self._size = size

    @property
    def min_size(self) -> int:
        """最小的人数，转化成整数"""
        return np.ceil(self._min_size)

    @min_size.setter
    def min_size(self, value: Number) -> None:
        """调整最小值"""
        if not isinstance(value, Number):
            raise TypeError(f"Min size of {self.breed} {type(value)} not num.")
        self._min_size = value

    @property
    def max_size(self) -> int:
        """最大的人数，转化成整数"""
        return np.ceil(self._max_size)

    @max_size.setter
    def max_size(self, value: Number) -> None:
        """调整最大人数"""
        if not isinstance(value, Number):
            raise TypeError("Max size of {self.breed} {type(value)} not num.")
        self._max_size = value

    def random_size(
        self, min_size: Number | None, max_size: None | Number = None
    ) -> None:
        """在最小、最大值之间，随机选择一个值作为本主体的规模。"""
        if min_size is None:
            min_size = self.min_size
        min_size = max(min_size, self.min_size)
        if max_size is None:
            max_size = self.max_size
        self.size = self.random.randint(int(min_size), int(max_size))

    @alive_required
    def population_growth(self, growth_rate: Optional[float] = None) -> None:
        """人口增长"""
        if growth_rate is None:
            growth_rate = self.params.growth_rate
        self.size = self._size + self._size * growth_rate

    @alive_required
    def diffuse(self, group_range: Tuple[Number] | None = None) -> Self | None:
        """人口分散，采用均匀分布随机选择一个最小和最大的规模，分裂出去。
        如果分裂出新的小队之后，原有的主体数量小于最小阈值，则原有主体会死掉。

        Parameters:
            group_range:
                新小队的规模，分别是最小值和最大值。
                例如默认的（10，20）就代表新小队生成的规模可能在 [10~20) 之间（左闭右开区间）。

        Returns:
            如果产生了新的小队并找到了适合生存的位置，则返回新的主体。
            如果没产生新的小队，则返回 None。
            如果产生了新的小队，但走了很远也没找到适合生存的地方，也会返回 None。
        """
        # 获取分散小组的最小-最大人数.
        if group_range is None:
            group_range = self.params.get("new_group_size", (0, 0))
        s_min, s_max = group_range
        # 如果当前的人数还不足以产生一支最小的小队，则不会产生
        if self.size < s_min:
            return None
        # 随机大小的一个规模，用于创建新的小队
        random_size = self.random.randint(int(s_min), int(s_max))
        # 如果这个随机来的大小比原来主体拥有的人数还多，则将大小设置为之前主体的全部人口
        size = min(random_size, self.size)
        # 创建一个新的小队伍
        cls = self.__class__  # The same breed (hunter->hunter; farmer->farmer)
        new = self.model.agents.new(cls, singleton=True, size=size)
        # 记录当前的位置
        cell = self.at
        # 原有人口减少，这里会触发减少到人数不足最小值时，死去
        self.size -= size
        # 新的人在周围寻找一个可以去的格子，并试图移动到那里
        if new_cell := search_cell(new, cell=cell):
            new.move.to(new_cell)
            return new
        # 如果走了很远，没有符合要求的格子，主体就会死亡
        new.die()
        return "Died"

    def report(self) -> pd.Series:
        """汇报主体的属性。

        Returns:
            返回一个`pandas.Series`表格，汇报该主体的属性。
        """
        return pd.Series(
            {
                "unique_id": self.unique_id,
                "breed": self.breed,
                "size": self.size,
                "position": self.pos,
            }
        )

    def convert(self):
        """转化的行为。"""

    def step(self):
        """每一步的行为。"""
        self.population_growth()
        self.convert()
        self.diffuse()

    def loss_in_competition(self, at: Optional[PatchCell] = None) -> None:
        """在竞争中失败"""
        self.die()
        return at


def search_cell(
    agent: SiteGroup, cell: PatchCell, radius: int = 1, **kwargs
) -> PatchCell:
    """在周围寻找一个新的地方，能够让迁徙的人过去"""
    if cell is None:
        raise TypeError(f"Expect PatchCell, got {type(cell)}, r={radius}.")
    # 先找到周围的格子
    cells = cell.neighboring(
        radius=radius, moore=False, include_center=False, annular=True
    )
    # 检查周围的格子是否符合当前主体的停留要求
    accessibility = [cell.able_to_live(agent) for cell in cells]
    # 如果有符合要求的格子，随机选择一个符合要求的
    if any(accessibility):
        selected_cells = cells.select(accessibility)
        prob = [cell.suitable_level(agent) for cell in selected_cells]
        return selected_cells.random.choice(prob=prob)
    if radius < agent.params.max_travel_distance:
        return search_cell(agent, cell, radius=radius + 1, **kwargs)
    return None
