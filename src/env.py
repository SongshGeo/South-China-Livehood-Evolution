#!/usr/bin/env python 3.11.0
# -*-coding:utf-8 -*-
# @Author  : Shuang (Twist) Song
# @Contact   : SongshGeo@gmail.com
# GitHub   : https://github.com/SongshGeo
# Website: https://cv.songshgeo.com/

from __future__ import annotations

from typing import Optional

import numpy as np

from abses.nature import PatchCell

from .farmer import Farmer
from .hunter import Hunter


class CompetingCell(PatchCell):
    """狩猎采集者和农民竞争的舞台"""

    def __init__(self, pos=None, indices=None):
        super().__init__(pos, indices)
        # 1 亚热带常绿阔叶林类型=1042.57人/32.65百平方公里（31.93人/百平方公里）、海岸常绿阔叶林类型=2892.17人/72.72百平方公里（39.77人/百平方公里）（Binford 2001: 143）海岸地带可以参考即有考古发掘材料设置人口局限较高的地块；2 参考已有全球狩猎采集者人口上限计算结果（Tallavaara et al. 2017 及补充材料；
        self.lim_h: float = 1042.57 / 32.65
        self.slope: float = np.random.uniform(0, 40)
        self.elevation: float = np.random.uniform(0, 100)
        self.is_water: bool = np.random.choice([True, False], p=[0.05, 0.95])
        self.water_distance: Optional[float] = None

    @property
    def is_arable(self) -> bool:
        """综合:
        1 考古遗址分布推演出的分布特征（Wu et al. 2023 中农业相关遗址数据）
        2 发展农业所需的一般条件：坡度小于20，海拔、坡向……（Shelach, 1999; Qiao, 2010）；
        3 今天的农业用地分布特征？"""
        # TODO 这里是不还不确定
        return self.slope <= 20

    def convert(self, agent: Farmer | Hunter):
        """农民与狩猎采集者之间的互相转化"""
        if isinstance(agent, Farmer):
            converted = Hunter(size=agent.size)
            agent.die()
        elif isinstance(agent, Hunter):
            converted = Farmer(size=agent.size)
            agent.die()
        else:
            raise TypeError("Agent must be Farmer or Hunter.")
        converted.put_on(self)
        return converted


class Env:
    """
    环境类
    """

    def __init__(self):
        pass

    def __str__(self):
        pass

    def calculate_water_distance(self):
        """据大型水体（主要河流、海洋）距离 (km)"""

    def add_farmers(self):
        """
        添加从北方来的农民，根据全局变量的泊松分布模拟
        """
        farmers = None
        positions = None
        # TODO 农民迁移过来就直接定居吗
        # 根据适合居住的程度来确定概率？ （1）
        # ratio % <- 调参
        return farmers, positions

    def update_climate(self):
        """气候变化"""

    def update_map(self):
        """海陆变迁"""
