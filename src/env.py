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
import rasterio
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
        self.slope: float = np.random.uniform(0, 30)
        self.aspect: float = np.random.uniform(0, 360)
        self.elevation: float = np.random.uniform(0, 300)
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
        converted = self.layer.model.agents.create(
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
        arr = self._open_rasterio(cfg.db.slo)
        self.dem.apply_raster(arr, attr_name="slope")
        arr = self._open_rasterio(cfg.db.asp)
        self.dem.apply_raster(arr, attr_name="aspect")

    def _open_rasterio(self, source: str) -> np.ndarray:
        with rasterio.open(source) as dataset:
            arr = dataset.read(1)
            arr = np.where(arr < 0, np.nan, arr)
            return arr.reshape((1, arr.shape[0], arr.shape[1]))

    def initialize(self):
        is_arable = np.vectorize(lambda x: x.is_arable)(self.dem.array_cells)
        self.dem.apply_raster(is_arable.reshape(self.dem.shape3d), attr_name="arable")

    def calculate_water_distance(self):
        """据大型水体（主要河流、海洋）距离 (km)"""

    def add_farmers(self):
        """
        添加从北方来的农民，根据全局变量的泊松分布模拟
        """
        farmers_num = np.random.poisson()
        farmers = self.model.agents.create(Farmer, num=farmers_num)
        arable = self.dem.get_raster("arable").reshape(self.dem.shape2d)
        arable_cells = self.dem.array_cells[arable.astype(bool)]
        for farmer in farmers:
            min_size, max_size = farmer.params.new_group_size
            farmer.size = farmer.random.uniform(min_size, max_size)
        arable_cells = np.random.choice(arable_cells, size=farmers_num, replace=False)
        for farmer, cell in zip(farmers, arable_cells):
            if not cell:
                raise ValueError(f"arable_cells {cell} is None")
            farmer.put_on(cell)
        return farmers

    def update_climate(self):
        """气候变化"""

    def update_map(self):
        """海陆变迁"""
