#!/usr/bin/env python 3.11.0
# -*-coding:utf-8 -*-
# @Author  : Shuang (Twist) Song
# @Contact   : SongshGeo@gmail.com
# GitHub   : https://github.com/SongshGeo
# Website: https://cv.songshgeo.com/

"""环境类
"""

from __future__ import annotations

import os

import numpy as np
import rasterio
from abses import ActorsList
from abses.cells import raster_attribute
from abses.nature import BaseNature, PatchCell
from hydra import compose, initialize

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
        self.lim_h: float = cfg.env.lim_h
        self.lim_g: float = cfg.env.lim_g
        self.slope: float = np.random.uniform(0, 30)
        self.aspect: float = np.random.uniform(0, 360)
        self.elevation: float = np.random.uniform(0, 300)
        self._is_water: bool = np.random.choice([True, False], p=[0.05, 0.95])
        # arable level for farmers.
        self.arable_level: float = np.random.uniform(0.0, 3.0)

    @raster_attribute
    def farmers(self) -> int:
        """这里的农民有多少（size）"""
        if len(self.agents) > 1:
            raise ValueError("More than one agent locates here.")
        if self.has_agent("Farmer"):
            return self.linked_attr("size")
        return 0

    @raster_attribute
    def hunters(self) -> int:
        """这里的农民有多少（size）"""
        if len(self.agents) > 1:
            raise ValueError("More than one agent locates here.")
        if self.has_agent("Hunter"):
            return self.linked_attr("size")
        return 0

    @raster_attribute
    def is_water(self) -> bool:
        """是否是水体"""
        return self._is_water or self.elevation <= 0

    @is_water.setter
    def is_water(self, value: bool) -> None:
        """设置是否水体"""
        if not isinstance(value, bool):
            raise TypeError(f"Should be bool, got {type(value)} instead.")
        self._is_water = value

    @raster_attribute
    def is_arable(self) -> bool:
        """是否是可耕地，只有同时满足以下条件，才能成为一个可耕地:
        1. 坡度小于10度。
        2. 坡向不是朝北的（如果是0-45度或315-360度，意味着朝北的，不利于种植）。
        3. 海拔高度小于200m。
        4. 不是水体。

        >  1. 考古遗址分布推演出的分布特征（Wu et al. 2023 中农业相关遗址数据）
        > 2 发展农业所需的一般条件：坡度小于20，海拔、坡向……（Shelach, 1999; Qiao, 2010）；
        > 3 今天的农业用地分布特征？

        returns:
            是否是耕地，是则返回 True，否则返回 False。
        """

        # 坡度小于10度
        cond1 = self.slope <= 10
        # 如果是0-45度或315-360度，意味着朝北的，不利于种植
        cond2 = self.aspect < 315 and self.aspect > 45
        # 海拔高度小于200m
        cond3 = (self.elevation < 200) and (self.elevation > 0)
        # 三个条件都满足才是可耕地
        cond4 = not self.is_water
        return cond1 and cond2 and cond3 and cond4

    def able_to_live(self, agent: SiteGroup) -> None:
        """检查该主体能否能到特定的地方:
        1. 对狩猎采集者而言，只要不是水域
        2. 对农民而言，需要是可耕地

        Args:
            agent (SiteGroup): 狩猎采集者或者农民，需要被检查的主体。

        Returns:
            如果被检查的主体能够在此处存活，返回True；否则返回False。
        """
        if isinstance(agent, Hunter):
            return not self.is_water
        if isinstance(agent, Farmer):
            cond1 = not self.has_agent()
            return self.is_arable & cond1
        if isinstance(agent, SiteGroup):
            return True
        raise TypeError("Agent must be People, Farmer or Hunter.")

    def suitable_level(self, agent: Farmer | Hunter) -> float:
        """根据此处的主体类型，返回一个适宜其停留的水平值。

        Args:
            agent (Farmer | Hunter): 狩猎采集者或者农民。

        Returns:
            适合该类主体停留此处的适宜度。

        Raises:
            TypeError: 如果输入的主体不是狩猎采集者或者农民，则会抛出TypeError异常。
        """
        if isinstance(agent, Hunter):
            return 1.0
        if isinstance(agent, Farmer):
            return self.arable_level
        if isinstance(agent, SiteGroup):
            return 1.0
        raise TypeError("Agent must be Farmer or Hunter.")

    def convert(self, agent: Farmer | Hunter):
        """让此处的农民与狩猎采集者之间互相转化。

        Args:
            agent (Farmer | Hunter): 狩猎采集者或者农民，需要被转化的主体。

        Returns:
            被转化的主体。输入农民，则转化为一个狩猎采集者；输入狩猎采集者，则转化为一个农民。

        Raises:
            TypeError: 如果输入的主体不是狩猎采集者或者农民，则会抛出TypeError异常。
        """
        if isinstance(agent, Farmer):
            convert_to = Hunter
        elif isinstance(agent, Hunter):
            convert_to = Farmer
        else:
            raise TypeError("Agent must be Farmer or Hunter.")
        # 创建一个新的主体
        # print(f"Going to create size {agent.size} {convert_to}")
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

    def __init__(self, model, name="env"):
        super().__init__(model, name)
        self.dem = self.create_module(
            how="from_file",
            raster_file=cfg.db.dem,
            cell_cls=CompetingCell,
            attr_name="elevation",
        )
        arr = self._open_rasterio(cfg.db.slo)
        self.dem.apply_raster(arr, attr_name="slope")
        arr = self._open_rasterio(cfg.db.asp)
        self.dem.apply_raster(arr, attr_name="aspect")
        arr = self._open_rasterio(cfg.db.farmland)
        self.dem.apply_raster(arr, attr_name="arable_level")
        arr = self._open_rasterio(cfg.db.lim_h)
        self.dem.apply_raster(arr, attr_name="lim_h")

    def _open_rasterio(self, source: str) -> np.ndarray:
        with rasterio.open(source) as dataset:
            arr = dataset.read(1)
            arr = np.where(arr < 0, np.nan, arr)
        return arr.reshape((1, arr.shape[0], arr.shape[1]))

    def add_hunters(self, ratio: float | None = 0.05):
        """
        添加初始的狩猎采集者，随机抽取一些斑块，将初始的狩猎采集者放上去
        """
        not_water = ~self.dem.get_raster(attr_name="is_water").astype(bool)
        not_water = not_water.reshape(self.dem.shape2d)
        not_water_cells = self.dem.array_cells[not_water]
        num = int(self.params.get("init_hunters", ratio) * not_water.sum())
        hunters = self.model.agents.create(Hunter, num=num)
        cells = np.random.choice(not_water_cells, size=num, replace=False)
        init_min, init_max = cfg.hunter.init_size
        for hunter, cell in zip(hunters, cells):
            hunter.put_on(cell)
            hunter.random_size(init_min, init_max)

    def add_farmers(self):
        """
        添加从北方来的农民，根据全局变量的泊松分布模拟。关于泊松分布的介绍可以看[这个链接](https://zhuanlan.zhihu.com/p/373751245)。当泊松分布生成的农民被创建时，将其放置在地图上任意一个可耕地。

        Returns:
            本次新添加的农民列表。
        """
        farmers_num = np.random.poisson(self.params.lam)
        farmers = self.model.agents.create(Farmer, num=farmers_num)
        arable = self.dem.get_raster("is_arable").reshape(self.dem.shape2d)
        arable_cells = self.dem.array_cells[arable.astype(bool)]
        for farmer in farmers:
            min_size, max_size = farmer.params.new_group_size
            farmer.size = farmer.random.randint(min_size, max_size)
        # 从可耕地、没有主体的里面选
        arable_cells = ActorsList(self.model, arable_cells)
        valid_cells = arable_cells.select(
            ~arable_cells.trigger("has_agent")
        ).random_choose(size=farmers_num, replace=False, as_list=True)
        for farmer, cell in zip(farmers, valid_cells):
            if not cell:
                raise ValueError(f"arable_cells {cell} is None")
            farmer.put_on(cell)
        return farmers
