#!/usr/bin/env python 3.11.0
# -*-coding:utf-8 -*-
# @Author  : Shuang (Twist) Song
# @Contact   : SongshGeo@gmail.com
# GitHub   : https://github.com/SongshGeo
# Website: https://cv.songshgeo.com/

from typing import Optional, Self

import numpy as np
import pandas as pd
from abses import Actor
from abses.nature import PatchCell


class SiteGroup(Actor):
    """原始的聚落"""

    def __init__(self, *arg, **kwargs) -> None:
        super().__init__(*arg, **kwargs)
        min_size = self.params.min_size
        self._size: Optional[int] = min_size
        self.size = kwargs.get("size", min_size)

    @property
    def size(self) -> int:
        """人口规模"""
        return self._size

    @size.setter
    def size(self, size):
        """人口规模有最大最小值限制"""
        if size < self.params.min_size:
            size = self.params.min_size
        elif size > self.params.max_size:
            size = self.params.max_size
        self._size = int(size)

    def population_growth(self, growth_rate: Optional[float] = None) -> None:
        """人口增长"""
        if not growth_rate:
            growth_rate = self.params.growth_rate
        self.size += self.size * growth_rate

    def diffuse(self) -> Self:
        """人口分散，随机选择一个最小和最大的规模，分裂出去"""
        s_min, s_max = self.params.new_group_size
        cell = self._cell
        # 随机大小的一个规模
        size = np.random.uniform(s_min, s_max)
        if size > self.size:
            self.die()
            return
        self.size -= size
        # 创建一个新的小队伍
        new = self.model.agents.create(self.__class__, singleton=True, size=size)
        # 在周围寻找一个可以去的格子
        # 试图移动到那里
        # 如果走了很远，没有符合要求的格子，主体就会死亡
        if new_cell := search_a_new_place(new, cell=cell):
            new.put_on(new_cell)
            return new
        new.die()

    def convert(self) -> Self:
        """当小于一定概率时，农民与狩猎采集者可能发生相互转化"""
        if self.random.random() < self.params.convert_prob:
            return self._cell.convert(self)
        return self

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


def search_a_new_place(
    agent: SiteGroup, cell: PatchCell, radius: int = 1, **kwargs
) -> PatchCell:
    """在周围寻找一个新的地方，能够让迁徙的人过去"""
    if not cell:
        raise TypeError(f"Cell must be PatchCell, rather than None, radius: {radius}.")
    # 先找到周围的格子
    cells = cell.get_neighboring_cells(
        radius=radius, moore=False, include_center=False, annular=True
    )
    # 检查周围的格子是否符合当前主体的停留要求
    accessibility = [cell.able_to_live(agent) for cell in cells]
    # 如果有符合要求的格子，随机选择一个符合要求的
    if any(accessibility):
        selected_cells = cells.select(accessibility)
        prob = [cell.suitable_level(agent) for cell in selected_cells]
        return selected_cells.random_choose(prob=prob)
    if radius < agent.params.max_travel_distance:
        return search_a_new_place(agent, cell, radius=radius + 1, **kwargs)
    return None
