#!/usr/bin/env python 3.11.0
# -*-coding:utf-8 -*-
# @Author  : Shuang (Twist) Song
# @Contact   : SongshGeo@gmail.com
# GitHub   : https://github.com/SongshGeo
# Website: https://cv.songshgeo.com/

import os
from typing import Self

import numpy as np
from hydra import compose, initialize

from src.people import SiteGroup

# 加载项目层面的配置
with initialize(version_base=None, config_path="../config"):
    cfg = compose(config_name="config")
os.chdir(cfg.root)

INIT_AREA = cfg.farmer.area


class Farmer(SiteGroup):
    """
    农民
    """

    def __init__(self, *arg, **kwargs) -> None:
        self._area = INIT_AREA
        super().__init__(*arg, **kwargs)
        self._growth_rate = self.params.growth_rate

    @property
    def growth_rate(self) -> float:
        """人口增长率，默认值可以在配置文件里的`growth_rate`中调节，也可以因复杂化而下降。设置新的人口增长率时不能下降到负增长。"""
        return self._growth_rate

    @growth_rate.setter
    def growth_rate(self, growth_rate) -> None:
        """人口增长率变化"""
        growth_rate = max(growth_rate, 0)
        self._growth_rate = float(growth_rate)

    @property
    def area(self) -> float:
        """耕地面积。当发生复杂化时，理论上耕地面积会增加一块（2km * 2km）的土地，但这块土地会因为复杂化而变的略小。计算公式为：

        $area = init_area * (2 - complexity)$

        其中complexity为复杂化时的损失系数，应该在0-1之间。
        """
        return self._area

    @area.setter
    def area(self, area: float) -> None:
        """耕地面积变化，会不断增加"""
        area = max(self.area, area)
        self._area = float(area)

    @property
    def size(self) -> int:
        """农民的人口规模和狩猎采集者有些区别，当人口规模小于最小值时，农民会死亡（见不到独居的农民）。
        此外，一旦新的人口规模大于当前的最大值，则会复杂化。
        """
        return self._size

    @size.setter
    def size(self, size):
        """人口规模有最大最小值限制"""
        if size < self.params.min_size:
            # * 这里是不是少于就死了
            self.die()
        elif size > self.max_size:
            self.complicate()
        self._size = int(size)

    @property
    def max_size(self) -> float:
        """最大人口数量

        > 参考对裴李岗时期（9000-7000 BP）人均所需耕地为0.008平方公里的数据（乔玉 2010），结合华南气候条件下较高的生产力和更充沛的自然资源，将所需人均耕地设置为0.004平方公里，那么该单位人口上限即π2*2/0.004=3142人
        """
        return self.area * np.pi**2 * 2 / 0.004

    def diffuse(self) -> Self:
        """农民的分散。一旦随机数小于分散概率，则会分散出去。可以在配置文件里`diffuse_prob`参数调节分散概率。"""
        # cond1 = self.size >= self.loc("lim_h")
        if self.random.random() < self.params.diffuse_prob:
            # if cond1 and cond2:
            return super().diffuse()

    def complicate(self) -> Self:
        """农民的复杂化，耕地上限再增加耕地密度增加、人口增长率下降。人口增长率的下降比例也为复杂化系数的值。"""
        self.growth_rate *= 1 - self.params.complexity
        self.area += INIT_AREA * (1 - self.params.complexity)
