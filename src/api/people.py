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
from abses import Actor, PatchCell, alive_required


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

        Note:
            人口并不严格守恒。分裂出新小队后，母体的剩余人口若低于 `min_size`，
            母体会死亡，那部分残余不会转移给任何主体，直接从系统里消失。上界是每次
            `min_size - 1` 人，且只可能发生在农业主体上：狩猎采集者要到 `max_size`
            才分裂，而新小队最大只有 `new_group_size` 的上限，残余必然远高于
            `min_size`。详见 issue #32。

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
        # 确保不超过当前人口
        size = min(random_size, self.size)

        # 先检查是否有可用的格子可以移动
        available_cell = self._search_cell_from_position(self.at)
        if available_cell is None:
            # 如果没有可用的格子，diffuse 不发生
            return None

        # 创建一个新的小队伍（先创建，确保即使原主体死亡，新主体也存在）
        cls = self.__class__  # The same breed (hunter->hunter; farmer->farmer)
        new = self.model.agents.new(cls, singleton=True, size=size)

        # 减少原有人口。注意这里会触发 size setter 的死亡检查：残余低于 min_size
        # 时母体死亡，残余人口随之消失（见 docstring 的 Note）
        self.size -= size

        # 新的人移动到找到的格子
        new.move.to(available_cell)
        return new

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

    def loss(self) -> None:
        """通用的损失方法，按概率减少人口。"""
        loss_params = self.params.get("loss", {})
        if not loss_params:
            return  # 如果没有损失参数，跳过

        prob = loss_params.get("prob", 0.0)
        rate = loss_params.get("rate", 0.0)

        if prob > 0 and rate > 0 and self.random.random() < prob:
            self.size *= 1 - rate

    def search_cell(self, radius: int = 1) -> Optional[PatchCell]:
        """在周围寻找一个新的地方，能够让迁徙的人过去

        简化版本：没有竞争机制，只需要检查：
        1. 格子是否适合该主体生存
        2. 格子是否为空（没有其他主体）
        """
        if self.at is None:
            raise TypeError(f"Agent {self} is not at any cell.")

        # 找到周围的格子
        cells = self.at.neighboring(
            radius=radius, moore=False, include_center=False, annular=True
        )

        # 简单筛选：只检查能否生存且为空
        available_cells = cells.select(lambda c: c.able_to_live(self))

        # 如果有可用格子，随机选择一个
        if len(available_cells) > 0:
            return available_cells.random.choice()

        # 扩大搜索范围
        max_distance = self.params.get("max_travel_distance", 5)
        if radius < max_distance:
            return self.search_cell(radius=radius + 1)

        return None

    def _search_cell_from_position(
        self, start_cell: PatchCell, radius: int = 1
    ) -> Optional[PatchCell]:
        """从指定位置搜索可用的格子（用于 diffuse 方法）"""
        if start_cell is None:
            return None

        # 找到周围的格子
        cells = start_cell.neighboring(
            radius=radius, moore=False, include_center=False, annular=True
        )

        # 简单筛选：只检查能否生存且为空
        available_cells = cells.select(lambda c: c.able_to_live(self))

        # 如果有可用格子，随机选择一个
        if len(available_cells) > 0:
            return available_cells.random.choice()

        # 扩大搜索范围
        max_distance = self.params.get("max_travel_distance", 5)
        if radius < max_distance:
            return self._search_cell_from_position(start_cell, radius=radius + 1)

        return None

    def step(self):
        """每一步的行为。"""
        self.population_growth()
        self.convert()
        self.diffuse()
        self.loss()
