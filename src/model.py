#!/usr/bin/env python 3.11.0
# -*-coding:utf-8 -*-
# @Author  : Shuang (Twist) Song
# @Contact   : SongshGeo@gmail.com
# GitHub   : https://github.com/SongshGeo
# Website: https://cv.songshgeo.com/

from abses import ActorsList, MainModel
from matplotlib import pyplot as plt

from src.env import Env


class Model(MainModel):
    """运行的模型"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, nature_class=Env, **kwargs)
        self.nature.add_hunters()
        self.farmers_num = []
        self.new_farmers = []
        self.hunters_num = []

    @property
    def farmers(self) -> ActorsList:
        """农民列表"""
        return self.agents.select("Farmer")

    @property
    def hunters(self) -> ActorsList:
        """狩猎采集者列表"""
        return self.agents.select("Hunter")

    def step(self):
        """每一时间步都按照以下顺序执行一次：
        1. 更新农民数量
        2. 所有主体互相转化
        3. 更新狩猎采集者可以移动（这可能触发竞争）
        """
        farmers = self.nature.add_farmers()
        self.farmers.trigger("convert")
        self.hunters.trigger("convert")
        self.agents.trigger("diffuse")
        self.hunters.trigger("move")
        # 更新农民和狩猎采集者数量
        self.new_farmers.append(len(farmers))
        self.farmers_num.append(self.farmers.array("size").sum())
        self.hunters_num.append(self.hunters.array("size").sum())

    def end(self):
        """模型运行结束后，将自动绘制狩猎采集者和农民的数量变化"""
        self.plot()
        plt.show()

    def plot(self):
        """绘制狩猎采集者和农民的数量变化"""
        _, ax = plt.subplots()
        ax.plot(self.farmers_num, label="farmers")
        ax.plot(self.hunters_num, label="hunters")
        ax.set_xlabel("time")
        ax.set_ylabel("population")
        ax.legend()

    def heatmap(self):
        """绘制狩猎采集者和农民的空间分布"""
        _, (ax1, ax2) = plt.subplots(1, 2, figsize=(8, 3))
        mask = self.nature.dem.get_xarray("elevation") >= 0
        farmers = self.nature.dem.get_xarray("farmers").where(mask)
        hunters = self.nature.dem.get_xarray("hunters").where(mask)
        farmers.plot.contourf(ax=ax1, cmap="Reds")
        hunters.plot.contourf(ax=ax2, cmap="Greens")
        ax1.set_xlabel("Farmers")
        ax2.set_xlabel("Hunters")
