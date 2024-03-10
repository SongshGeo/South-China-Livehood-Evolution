#!/usr/bin/env python 3.11.0
# -*-coding:utf-8 -*-
# @Author  : Shuang (Twist) Song
# @Contact   : SongshGeo@gmail.com
# GitHub   : https://github.com/SongshGeo
# Website: https://cv.songshgeo.com/

"""在基础主体之上，农民有以下不同：
1. 新属性：人口增长率，是可变的，会因为复杂化而下降。
"""

from __future__ import annotations

from numbers import Number
from typing import TYPE_CHECKING, Self, Tuple

import numpy as np

from .people import SiteGroup

if TYPE_CHECKING:
    from abses_sce.hunter import Hunter
    from abses_sce.rice_farmer import RiceFarmer


class Farmer(SiteGroup):
    """
    农民
    """

    def __init__(self, *arg, **kwargs) -> None:
        super().__init__(*arg, **kwargs)
        self._area = self.params.area
        self._growth_rate = self.params.growth_rate
        self.size = kwargs.get("size", self.min_size)

    @property
    def growth_rate(self) -> float:
        """人口增长率，默认值可以在配置文件里的`growth_rate`中调节，也可以因复杂化而下降。设置新的人口增长率时不能下降到负增长。"""
        return getattr(self, "_growth_rate", 0.0)

    @growth_rate.setter
    def growth_rate(self, growth_rate) -> None:
        """人口增长率变化"""
        growth_rate = max(growth_rate, 0.0)
        self._growth_rate = float(growth_rate)

    @property
    def area(self) -> float:
        """耕地面积。当发生复杂化时，理论上耕地面积会增加一块（2km * 2km）的土地，但这块土地会因为复杂化而变的略小。计算公式为：

        $area = init_area * (2 - complexity)$

        其中complexity为复杂化时的损失系数，应该在0-1之间。
        """
        return getattr(self, "_area", 0)

    @area.setter
    def area(self, area: float) -> None:
        """耕地面积变化，会不断增加"""
        area = max(self.area, area)
        self._area = float(area)

    @SiteGroup.size.setter
    def size(self, size: Number) -> None:
        """人口规模有最大最小值限制"""
        SiteGroup.size.fset(self, size)
        if size > self.max_size:
            self.complicate()

    @property
    def max_size(self) -> float:
        """最大人口数量

        Note:
            参考裴李岗时期（9000-7000 BP），人均耕地为0.008平方公里（乔玉 2010），
            结合华南气候条件下较高的生产力和更充沛的自然资源，将所需人均耕地设置为0.004平方公里，
            那么该单位人口上限即π * 2 * 2 / 0.004=3142人。
        """
        capital_area = self.params.get("capital_area")
        if not capital_area:
            raise ValueError("Capital area is not set in params.")
        max_size = np.pi * self.area**2 / capital_area
        return np.ceil(max_size)

    def _convert_to_hunter(self) -> Hunter | Self:
        # 如果人数大于不能转化的阈值，就直接返回自身
        cond1 = self.size <= self.params.convert_threshold.get("to_hunter")
        # 概率小于转化概率
        cond2 = self.random.random() < self.params.convert_prob.get("to_hunter", 0.0)
        # 满足上述两个条件就转化
        return self._cell.convert(self, to="Hunter") if cond1 & cond2 else self

    def _convert_to_rice(self) -> RiceFarmer | Self:
        """转化成"""
        # 人数大于水稻所需最小人数
        cond1 = self.size >= self.params.convert_threshold.get("to_rice", 0)
        # 概率小于转化概率
        cond2 = self.random.random() < self.params.convert_prob.get("to_rice", 0.0)
        # 所处地块适宜水稻生存
        cond3 = self._cell.is_rice_arable
        return (
            self._cell.convert(self, to="RiceFarmer") if cond1 & cond2 & cond3 else self
        )

    def convert(self) -> Self | Hunter | RiceFarmer:
        """转换，先判断是否转化成狩猎采集，如果不是，再看看是否转换成水稻农民"""
        agent = self._convert_to_hunter()
        return agent if agent is not self else self._convert_to_rice()

    def diffuse(
        self, group_range: Tuple[Number] | None = None, diffuse_prob: Number = None
    ) -> Self:
        """农民的分散。一旦随机数小于分散概率，则会分散出去。
        但不像狩猎采集者，农民如果分裂不出最小的一支队伍，就不会扩散出去。
        可以在配置文件里`diffuse_prob`参数调节分散概率。
        """
        # 检测概率是否够产生小队
        if diffuse_prob is None:
            diffuse_prob = self.params.get("diffuse_prob", 0.0)
        if self.random.random() < diffuse_prob:
            return super().diffuse(group_range=group_range)
        return None

    def complicate(self, complexity: float | None = None) -> Self:
        """农民的复杂化，耕地上限再增加耕地密度增加、人口增长率下降。人口增长率的下降比例也为复杂化系数的值。"""
        if complexity is None:
            complexity = self.params.get("complexity", 0.0)
        self.growth_rate *= 1 - complexity
        self.area += self.params.area * (1 - complexity)

    def loss(self) -> None:
        """农民的损失，人口增长率下降。"""
        if self.random.random() < self.params.loss.prob:
            self.size *= 1 - self.params.loss.rate
