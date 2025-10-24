#!/usr/bin/env python 3.11.0
# -*-coding:utf-8 -*-
# @Author  : Shuang (Twist) Song
# @Contact   : SongshGeo@gmail.com
# GitHub   : https://github.com/SongshGeo
# Website: https://cv.songshgeo.com/

"""环境类"""

from __future__ import annotations

from typing import Optional

import numpy as np
import rasterio
from abses import ActorsList, BaseNature, PatchCell, raster_attribute

from src.api.farmer import Farmer
from src.api.hunter import Hunter
from src.api.people import SiteGroup
from src.api.rice_farmer import RiceFarmer


class CompetingCell(PatchCell):
    """狩猎采集者和农民竞争的舞台"""

    max_agents = 1  # 一个斑块上最多有多少个主体

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.slope: float = np.random.uniform(0, 30)
        self.elevation: float = np.random.uniform(0, 300)
        self.water_type: int = 0  # -1=海，0=陆地，1=近水陆地
        self._is_water: Optional[bool] = None

    def _count(self, breed: str) -> int:
        """统计此处的农民或者狩猎采集者的数量"""
        return self.agents.select(agent_type=breed).array("size").sum()

    @raster_attribute
    def farmers(self) -> int:
        """这里的农民有多少（size）"""
        return self._count(Farmer)

    @raster_attribute
    def hunters(self) -> int:
        """这里的农民有多少（size）"""
        return self._count(Hunter)

    @raster_attribute
    def rice_farmers(self) -> int:
        """这里的农民有多少（size）"""
        return self._count(RiceFarmer)

    @raster_attribute
    def is_water(self) -> bool:
        """是否是水体（-1=海，0=陆地，1=近水陆地）"""
        if self._is_water is None:
            return self.water_type == -1  # 只有 -1 才是水体
        return bool(self._is_water)

    @is_water.setter
    def is_water(self, value: bool) -> None:
        if not isinstance(value, (bool, np.bool_)):
            raise TypeError(f"Can only be bool type, got {type(value)}.")
        self._is_water = bool(value)

    @raster_attribute
    def is_near_water(self) -> bool:
        """是否靠近水体（water_type = 1）"""
        return self.water_type == 1

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
        """是否是水稻的可耕地，只有同时满足以下条件，才能成为水稻可耕地:
        1. 坡度小于等于0.5度。
        2. 海拔高度小于200m且大于0。
        3. 不是水体。

        returns:
            是否是水稻可耕地，是则返回 True，否则返回 False。
        """
        # 坡度小于等于0.5度
        cond1 = self.slope <= 0.5
        # 海拔高度小于200m且大于0
        cond2 = (self.elevation < 200) and (self.elevation > 0)
        # 不是水体
        cond3 = not self.is_water
        # 条件都满足才是水稻可耕地
        return cond1 and cond2 and cond3

    @raster_attribute
    def is_only_arable(self) -> bool:
        """是否只是普通可耕地而不是水稻可耕地"""
        return self.is_arable and not self.is_rice_arable

    def able_to_live(self, agent: SiteGroup) -> None:
        """检查该主体能否能到特定的地方:
        1. 格子里必须没有其他主体（每格只能有一个主体）
        2. 对狩猎采集者而言，只要不是水域
        3. 对农民而言，需要是可耕地

        Args:
            agent (SiteGroup): 狩猎采集者或者农民，需要被检查的主体。

        Returns:
            如果被检查的主体能够在此处存活，返回True；否则返回False。
        """
        # 首先检查是否已有其他主体（所有类型都不能重叠）
        if self.agents.has() > 0:
            # 唯一的例外：同一个主体检查自己的位置
            existing = self.agents.select().item("item")
            if existing is not None and existing is not agent:
                return False

        # 然后检查特定类型的要求
        if agent.breed == "Hunter":
            return not self.is_water
        if agent.breed == "RiceFarmer":
            return self.is_rice_arable
        if agent.breed == "Farmer":
            return self.is_arable
        if agent.breed == "SiteGroup":
            return True
        raise TypeError("Agent must be a valid People.")

    def suitable_level(self, breed: type[SiteGroup]) -> float:
        """根据此处的主体类型，返回一个适宜其停留的水平值。

        Args:
            breed (type[SiteGroup]): 主体类型。

        Returns:
            适合该类主体停留此处的适宜度。

        Raises:
            TypeError: 如果输入的主体不是狩猎采集者或者农民，则会抛出TypeError异常。
        """
        if breed == Hunter:
            return 1.0
        if breed == RiceFarmer:
            return self.dem_suitable
        if breed == Farmer:
            return self.dem_suitable * 0.5 + self.slope_suitable * 0.2
        if breed == SiteGroup:
            return 1.0
        raise TypeError("Agent must be Farmer or Hunter.")

    def convert(self, agent: Farmer | Hunter, to: str) -> SiteGroup:
        """让此处的农民与狩猎采集者之间互相转化。

        Args:
            agent (Farmer | Hunter): 狩猎采集者或者农民，需要被转化的主体。
            to (str): 转化成的主体类型名称。

        Returns:
            被转化的主体。输入农民，则转化为一个狩猎采集者；输入狩猎采集者，则转化为一个农民。
            如果转化开关关闭，返回原主体。

        Raises:
            TypeError:
                如果输入的主体不是狩猎采集者或者农民，或者想转化成的类型不从基础主体继承而来，则会抛出TypeError异常。
        """
        # 检查全局转化开关
        try:
            convert_config = self.layer.model.params.get("convert", {})
            if not convert_config.get("enabled", True):
                return agent

            # 检查具体转化类型的开关
            convert_type = f"{agent.breed.lower()}_to_{to.lower()}"
            if not convert_config.get(convert_type, True):
                return agent
        except (AttributeError, KeyError):
            # 如果配置中没有 convert 部分，默认允许转化
            pass

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
    环境类，用于管理模型中的环境信息。

    属性:
        dem (BaseRaster): 数字高程模型。
        slope (BaseRaster): 坡度。
        lim_h (BaseRaster): 狩猎采集者的限制。

    方法:
        setup(): 初始化环境。
        step(): 每一时间步都按照以下顺序执行一次：
            1. 更新农民数量
            2. 所有主体互相转化
            3. 更新狩猎采集者可以移动（这可能触发竞争）
        add_hunters(): 添加初始的狩猎采集者。
        add_farmers(): 添加初始的农民。
    """

    @property
    def agents(self):
        """明确重写agents属性"""
        try:
            # 首先尝试获取BaseNature的agents
            return super().agents
        except AttributeError:
            # 如果失败，返回GeoSpace的agents
            return self._agent_layer.agents if hasattr(self, "_agent_layer") else []

    def __init__(self, model, name="env"):
        super().__init__(model, name)

    def initialize(self):
        """Initialize environment: setup DEM and add initial hunters and farmers."""
        self.setup_dem()
        self.add_hunters(self.p.init_hunters)
        self.add_initial_farmers(Farmer, self.p.get("init_farmers", 0))
        self.add_initial_farmers(RiceFarmer, self.p.get("init_rice_farmers", 0))

    def setup_dem(self):
        """创建数字高程模型并设置为主图层"""
        self.dem = self.create_module(
            raster_file=self.ds.dem,
            cell_cls=CompetingCell,
            attr_name="elevation",
            major_layer=True,
            apply_raster=True,
        )
        arr = self._open_rasterio(self.ds.slope)
        self.dem.apply_raster(arr, attr_name="slope")
        arr = self._open_rasterio(self.ds.lim_h)
        self.dem.apply_raster(arr, attr_name="water_type")

        # 设置完 DEM 后立即计算全局人口上限
        self.calculate_global_hunter_limit()

    def calculate_global_hunter_limit(self):
        """计算全局 Hunter 人口上限 = lim_h * 非水体栅格数量"""
        try:
            # 获取所有非水体栅格（water_type != -1）
            non_water_cells = self.dem.cells_lst.select({"is_water": False})

            # 使用配置中的 lim_h 值（每个栅格的承载力）
            lim_h = self.params.get("lim_h", 31.93)

            # 全局 Hunter 人口上限 = lim_h * 非水体栅格数量
            self.global_hunter_limit = float(lim_h * len(non_water_cells))

            # 将全局限制存储到模型参数中，供 Hunter 类访问
            self.model.params.global_hunter_limit = self.global_hunter_limit
        except Exception:
            # 如果出错，设置默认值并静默失败
            self.global_hunter_limit = 100000.0  # 较大的默认值，不会限制

    def apply_global_hunter_limit(self) -> None:
        """应用全局 Hunter 人口上限控制

        在每个时间步结束时调用，如果总人口超过上限，随机减少 Hunter 的人口，
        直到总人口降到上限以下。
        """
        hunters = self.agents.select(agent_type=Hunter)
        if len(hunters) == 0:
            return

        current_population = hunters.array("size").sum()
        if current_population <= self.global_hunter_limit:
            return  # 未超过上限，不需要调整

        # 计算需要减少的人口数
        excess_population = current_population - self.global_hunter_limit

        # 随机打乱 Hunter 列表
        self.model.random.shuffle(hunters)

        # 逐个减少 Hunter 的人口，直到达到上限
        for hunter in hunters:
            if excess_population <= 0:
                break

            # 计算当前 Hunter 可以减少的人口数
            # 确保至少保留最小人口数（6）或让其死亡
            reduction = min(excess_population, hunter.size - hunter.params.min_size)

            if reduction > 0:
                hunter.size -= reduction
                excess_population -= reduction
            elif hunter.size > 0:
                # 如果已经接近最小值，直接让其死亡
                excess_population -= hunter.size
                hunter.die()

    def _open_rasterio(self, source: str) -> np.ndarray:
        with rasterio.open(source) as dataset:
            arr = dataset.read(1)
            arr = np.where(arr < 0, np.nan, arr)
        return arr.reshape((1, arr.shape[0], arr.shape[1]))

    def step(self) -> None:
        """
        每一时间步都按照以下顺序执行一次：
        1. 更新农民数量
        2. 所有主体互相转化
        3. 更新狩猎采集者可以移动（这可能触发竞争）
        """
        self.add_farmers(Farmer)
        self.add_farmers(RiceFarmer)

    def add_hunters(self, ratio: Optional[float | str] = 0.05) -> ActorsList[Hunter]:
        """
        添加初始的狩猎采集者，随机抽取一些斑块，将初始的狩猎采集者放上去。

        Args:
            ratio (float | None): 狩猎采集者的比例。默认为0.05。

        Returns:
            本次新添加的狩猎采集者列表。
        """
        available_cells = self.major_layer.cells_lst.select({"is_water": False})
        ratio = float(ratio)
        if ratio.is_integer():
            num = int(ratio)
        else:
            num = int(len(available_cells) * ratio)
        hunters = available_cells.random.new(Hunter, size=num, replace=False)
        init_min, init_max = hunters[0].params.init_size
        hunters.apply(lambda h: h.random_size(init_min, init_max))
        return hunters

    def add_initial_farmers(
        self, farmer_cls: type = Farmer, num: int = 0
    ) -> ActorsList[Farmer | RiceFarmer]:
        """
        添加初始的农民，随机选择一些可耕地，将初始的农民放上去。

        Args:
            farmer_cls (type): 农民的类型。可以是 Farmer 或 RiceFarmer。
            num (int): 要添加的农民数量。

        Returns:
            本次新添加的农民列表。
        """
        if num <= 0:
            return ActorsList(self.model, [])

        # 根据农民类型选择合适的可耕地
        if farmer_cls == RiceFarmer:
            arable = self.dem.get_raster("is_rice_arable").reshape(self.dem.shape2d)
        else:
            arable = self.dem.get_raster("is_arable").reshape(self.dem.shape2d)

        arable_cells = ActorsList(self.model, self.dem.array_cells[arable.astype(bool)])
        # 过滤出没有主体的格子
        valid_cells = arable_cells.select(lambda c: c.agents.has() == 0)

        # 如果可耕地数量不够，则减少农民数量
        farmers_num = min(num, len(valid_cells))
        if farmers_num == 0:
            return ActorsList(self.model, [])

        # 随机在满足条件的斑块上创建农民
        farmers = valid_cells.random.new(
            farmer_cls,
            size=farmers_num,
            replace=False,
        )
        # 根据 init_size 参数随机分配初始人口规模
        init_min, init_max = farmers[0].params.init_size
        farmers.apply(lambda f: f.random_size(init_min, init_max))
        return farmers

    def add_farmers(self, farmer_cls: type = Farmer) -> ActorsList[Farmer | RiceFarmer]:
        """
        添加从北方来的农民，根据全局变量的泊松分布模拟。关于泊松分布的介绍可以看[这个链接](https://zhuanlan.zhihu.com/p/373751245)。当泊松分布生成的农民被创建时，将其放置在地图上任意一个可耕地。

        Args:
            farmer_cls (type): 农民的类型。可以是 Farmer 或 RiceFarmer。

        Returns:
            本次新添加的农民列表。
        """
        lam_key = f"lam_{farmer_cls.breed}".lower()
        tick_key = f"tick_{farmer_cls.breed}".lower()
        if self.time.tick < self.params.get(tick_key, 0):
            farmers_num = 0
        else:
            farmers_num = np.random.poisson(self.params.get(lam_key, 0))
        # 从可耕地、没有主体的里面选
        arable = self.dem.get_raster("is_arable").reshape(self.dem.shape2d)
        arable_cells = ActorsList(self.model, self.dem.array_cells[arable.astype(bool)])
        # Use lambda function to filter cells with no agents
        valid_cells = arable_cells.select(lambda c: c.agents.has() == 0)
        # 如果可耕地数量不够，则减少农民数量
        farmers_num = min(farmers_num, len(valid_cells))
        if farmers_num == 0:
            return ActorsList(self.model, [])
        # 随机在满足条件的斑块上创建农民
        farmers = valid_cells.random.new(
            farmer_cls,
            size=farmers_num,
            replace=False,
        )
        # 随机分配大小
        for farmer in farmers:
            min_size, max_size = farmer.params.new_group_size
            farmer.size = farmer.random.randint(int(min_size), int(max_size))
        return farmers
