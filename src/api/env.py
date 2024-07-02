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
from typing import Optional

import numpy as np
import rasterio
from abses import ActorsList
from abses.cells import raster_attribute
from abses.nature import BaseNature, PatchCell
from hydra import compose, initialize

from src.api.farmer import Farmer
from src.api.hunter import Hunter
from src.api.people import SiteGroup
from src.api.rice_farmer import RiceFarmer

# 加载项目层面的配置
with initialize(version_base=None, config_path="../../config"):
    cfg = compose(config_name="config")
os.chdir(cfg.root)


class CompetingCell(PatchCell):
    """狩猎采集者和农民竞争的舞台"""

    max_agents = 1

    def __init__(self, pos=None, indices=None):
        super().__init__(pos, indices)
        self.lim_h: float = cfg.env.lim_h
        self.lim_g: float = cfg.env.lim_g
        self.slope: float = np.random.uniform(0, 30)
        self.elevation: float = np.random.uniform(0, 300)
        self._is_water: Optional[bool] = None

    def _count(self, breed: str) -> int:
        """统计此处的农民或者狩猎采集者的数量"""
        return self.agents(breed).get("size", how="item", default=0)

    @raster_attribute
    def farmers(self) -> int:
        """这里的农民有多少（size）"""
        return self._count("Farmer")

    @raster_attribute
    def hunters(self) -> int:
        """这里的农民有多少（size）"""
        return self._count("Hunter")

    @raster_attribute
    def rice_farmers(self) -> int:
        """这里的农民有多少（size）"""
        return self._count("RiceFarmer")

    @raster_attribute
    def is_water(self) -> bool:
        """是否是水体"""
        if self._is_water is None:
            return self.elevation <= 0 or np.isnan(self.elevation)
        return self._is_water

    @is_water.setter
    def is_water(self, value: bool) -> None:
        if not isinstance(value, bool):
            raise TypeError(f"Can only be bool type, got {type(value)}.")
        self._is_water = value

    @raster_attribute
    def is_arable(self) -> bool:
        """是否是可耕地，只有同时满足以下条件，才能成为一个可耕地:
        1. 坡度小于10度。
        2. 海拔高度小于200m。
        3. 不是水体。

        >  1. 考古遗址分布推演出的分布特征（Wu et al. 2023 中农业相关遗址数据）
        > 2 发展农业所需的一般条件：坡度小于20，海拔、坡向……（Shelach, 1999; Qiao, 2010）；
        > 3 今天的农业用地分布特征？

        returns:
            是否是耕地，是则返回 True，否则返回 False。
        """

        # 坡度小于10度
        cond1 = self.slope <= 10
        # 海拔高度小于200m
        cond2 = (self.elevation < 200) and (self.elevation > 0)
        # 不是水体
        cond3 = not self.is_water
        # 条件都满足才是可耕地
        return cond1 and cond2 and cond3

    @raster_attribute
    def dem_suitable(self) -> int:
        """海拔高度的适宜程度"""
        # 0-100: 2
        # 100-200: 1
        # 200+: 0
        dem = self.elevation
        if dem < 100:
            return 2
        return 1 if dem < 200 else 0

    @raster_attribute
    def slope_suitable(self) -> int:
        """坡度的适宜程度"""
        # 0-2: 5
        # 2-4: 4
        # 4-6: 3
        # 6-8: 2
        # 8-10: 1
        # 10+: 0
        if self.slope < 2:
            return 5
        if self.slope < 4:
            return 4
        if self.slope < 6:
            return 3
        if self.slope < 8:
            return 2
        return 1 if self.slope < 10 else 0

    @raster_attribute
    def is_rice_arable(self) -> bool:
        """是否是水稻的可耕地"""
        # 坡度小于等于0.5
        cond1 = self.slope <= 0.5
        # 海拔高度小于200m
        cond2 = (self.elevation < 200) and (self.elevation > 0)
        # 不是水体
        cond3 = not self.is_water
        return cond1 and cond2 and cond3

    def able_to_live(self, agent: SiteGroup) -> None:
        """检查该主体能否能到特定的地方:
        1. 对狩猎采集者而言，只要不是水域
        2. 对农民而言，需要是可耕地

        Args:
            agent (SiteGroup): 狩猎采集者或者农民，需要被检查的主体。

        Returns:
            如果被检查的主体能够在此处存活，返回True；否则返回False。
        """
        if agent.breed == "Hunter":
            return not self.is_water
        no_agent_here = self.agents.has() == 0
        if agent.breed == "RiceFarmer":
            return self.is_rice_arable & no_agent_here
        if agent.breed == "Farmer":
            return self.is_arable & no_agent_here
        if agent.breed == "SiteGroup":
            return True
        raise TypeError("Agent must be a valid People.")

    def suitable_level(self, agent: SiteGroup) -> float:
        """根据此处的主体类型，返回一个适宜其停留的水平值。

        Args:
            agent (Farmer | Hunter): 狩猎采集者或者农民。

        Returns:
            适合该类主体停留此处的适宜度。

        Raises:
            TypeError: 如果输入的主体不是狩猎采集者或者农民，则会抛出TypeError异常。
        """
        if agent.breed == "Hunter":
            return 1.0
        if agent.breed == "RiceFarmer":
            return self.dem_suitable
        if agent.breed == "Farmer":
            return self.dem_suitable * 0.5 + self.slope_suitable * 0.2
        if agent.breed == "SiteGroup":
            return 1.0
        raise TypeError("Agent must be Farmer or Hunter.")

    def convert(self, agent: Farmer | Hunter, to: str) -> SiteGroup:
        """让此处的农民与狩猎采集者之间互相转化。

        Args:
            agent (Farmer | Hunter): 狩猎采集者或者农民，需要被转化的主体。
            convert_to (Farmer | Hunter): 转化成什么类型。

        Returns:
            被转化的主体。输入农民，则转化为一个狩猎采集者；输入狩猎采集者，则转化为一个农民。

        Raises:
            TypeError: 如果输入的主体不是狩猎采集者或者农民，
            或者想转化成的类型不从基础主体继承而来，
            则会抛出TypeError异常。
        """
        to = {"Farmer": Farmer, "RiceFarmer": RiceFarmer, "Hunter": Hunter}.get(to)
        if not isinstance(agent, SiteGroup):
            raise TypeError(f"Agent must be inherited from SiteGroup, not {agent}.")
        if to is None:
            raise TypeError("Agent must be inherited from SiteGroup.")
        # 创建一个新的主体
        # print(f"Going to create size {agent.size} {convert_to}")
        converted = self.layer.model.agents.new(to, size=agent.size, singleton=True)
        converted.source = agent.source  # 记录原来是什么主体
        agent.die()  # 旧的主体死亡
        converted.move.to(self)
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
            apply_raster=True,
        )
        arr = self._open_rasterio(cfg.db.slo)
        self.dem.apply_raster(arr, attr_name="slope")
        arr = self._open_rasterio(cfg.db.lim_h)
        self.dem.apply_raster(arr, attr_name="lim_h")

    def _open_rasterio(self, source: str) -> np.ndarray:
        with rasterio.open(source) as dataset:
            arr = dataset.read(1)
            arr = np.where(arr < 0, np.nan, arr)
        return arr.reshape((1, arr.shape[0], arr.shape[1]))

    def add_hunters(self, ratio: Optional[float] = 0.05):
        """
        添加初始的狩猎采集者，随机抽取一些斑块，将初始的狩猎采集者放上去
        """
        available_cells = self.cells.select({"is_water": False})
        num = int(len(available_cells) * ratio)
        hunters = available_cells.random.new(Hunter, size=num)
        init_min, init_max = cfg.hunter.init_size
        hunters.apply(lambda h: h.random_size(init_min, init_max))

    def add_farmers(self, farmer_cls: type = Farmer):
        """
        添加从北方来的农民，根据全局变量的泊松分布模拟。关于泊松分布的介绍可以看[这个链接](https://zhuanlan.zhihu.com/p/373751245)。当泊松分布生成的农民被创建时，将其放置在地图上任意一个可耕地。

        Returns:
            本次新添加的农民列表。
        """
        lam_key = f"lam_{farmer_cls.breed}".lower()
        tick_key = f"tick_{farmer_cls.breed}".lower()
        if self.time.tick < self.params.get(tick_key, 0):
            farmers_num = 0
        else:
            farmers_num = np.random.poisson(self.params.get(lam_key, 0))
        # create farmers
        farmers = self.model.agents.new(farmer_cls, num=farmers_num)
        arable = self.dem.get_raster("is_arable").reshape(self.dem.shape2d)
        arable_cells = self.dem.array_cells[arable.astype(bool)]
        for farmer in farmers:
            min_size, max_size = farmer.params.new_group_size
            farmer.size = farmer.random.randint(int(min_size), int(max_size))
        # 从可耕地、没有主体的里面选
        arable_cells = ActorsList(self.model, arable_cells)
        agents_num = arable_cells.apply(lambda c: c.agents.has())
        valid_cells = arable_cells.select(agents_num == 0)
        chosen_cells = valid_cells.random.choice(
            size=farmers_num, replace=False, as_list=True
        )
        for farmer, cell in zip(farmers, chosen_cells):
            if not cell:
                raise ValueError(f"arable_cells {cell} is None")
            farmer.move.to(cell)
        return farmers
