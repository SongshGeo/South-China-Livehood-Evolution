#!/usr/bin/env python 3.11.0
# -*-coding:utf-8 -*-
# @Author  : Shuang (Twist) Song
# @Contact   : SongshGeo@gmail.com
# GitHub   : https://github.com/SongshGeo
# Website: https://cv.songshgeo.com/

from __future__ import annotations

import os
from typing import Optional

import numpy as np
from hydra import compose, initialize

from abses.nature import BaseNature, PatchCell

from .farmer import Farmer
from .hunter import Hunter
from .people import SiteGroup

# 加载项目层面的配置
with initialize(version_base=None, config_path="../config"):
    cfg = compose(config_name="config")
os.chdir(cfg.root)


class CompetingCell(PatchCell):
    """狩猎采集者和农民竞争的舞台"""

    def __init__(self, pos=None, indices=None):
        super().__init__(pos, indices)
        # 1 亚热带常绿阔叶林类型=1042.57人/32.65百平方公里（31.93人/百平方公里）、海岸常绿阔叶林类型=2892.17人/72.72百平方公里（39.77人/百平方公里）（Binford 2001: 143）海岸地带可以参考即有考古发掘材料设置人口局限较高的地块；2 参考已有全球狩猎采集者人口上限计算结果（Tallavaara et al. 2017 及补充材料；
        self.lim_h: float = 1042.57 / 32.65
        self.slope: float = np.random.uniform(0, 40)
        self.aspect: float = np.random.uniform(0, 360)
        self.elevation: float = np.random.uniform(0, 100)
        self.is_water: bool = np.random.choice([True, False], p=[0.05, 0.95])
        self.water_distance: Optional[float] = None

    @property
    def is_arable(self) -> bool:
        """综合:
        1 考古遗址分布推演出的分布特征（Wu et al. 2023 中农业相关遗址数据）
        2 发展农业所需的一般条件：坡度小于20，海拔、坡向……（Shelach, 1999; Qiao, 2010）；
        3 今天的农业用地分布特征？"""
        # 坡度小于10度
        cond1 = self.slope <= 10
        # 如果是0-45度或315-360度，意味着朝北的，不利于种植
        cond2 = self.aspect < 315 or self.aspect > 45
        # 海拔高度小于200m
        cond3 = self.elevation < 200
        # 三个条件都满足才是可耕地
        return cond1 & cond2 & cond3

    def able_to_live(self, agent: SiteGroup) -> None:
        """检查该主体能否能到特定的地方:
        1. 对狩猎采集者而言，只要不是水域
        2. 对农民而言，需要是可耕地
        """
        if isinstance(agent, Hunter):
            return not self.is_water
        if isinstance(agent, Farmer):
            return self.is_arable
        else:
            raise TypeError("Agent must be Farmer or Hunter.")

    def convert(self, agent: Farmer | Hunter):
        """农民与狩猎采集者之间的互相转化"""
        if isinstance(agent, Farmer):
            convert_to = Hunter
        elif isinstance(agent, Hunter):
            convert_to = Farmer
        else:
            raise TypeError("Agent must be Farmer or Hunter.")
        # 创建一个新的主体
        converted = self.model.agents.create(
            convert_to, size=agent.size, singleton=True
        )
        agent.die()  # 旧的主体死亡
        converted.put_on(self)
        return converted


class Env(BaseNature):
    """
    环境类
    """

    def __init__(self, model, name="nature"):
        super().__init__(model, name)
        self.dem = self.create_module(
            how="from_file",
            raster_file=cfg.db.dem,
            cell_cls=CompetingCell,
            attr_name="dem",
        )

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
