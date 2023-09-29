#!/usr/bin/env python 3.11.0
# -*-coding:utf-8 -*-
# @Author  : Shuang (Twist) Song
# @Contact   : SongshGeo@gmail.com
# GitHub   : https://github.com/SongshGeo
# Website: https://cv.songshgeo.com/

from matplotlib import pyplot as plt

from abses import ActorsList, MainModel


class Model(MainModel):
    """运行的模型"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
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
        print(f"step, time: {self.time}")
        farmers = self.nature.add_farmers()
        self.new_farmers.append(len(farmers))
        self.farmers.trigger("convert")
        self.farmers.trigger("diffuse")
        self.hunters.trigger("diffuse")
        self.hunters.trigger("move")
        self.farmers_num.append(self.farmers.array("size").sum())
        self.hunters_num.append(self.hunters.array("size").sum())
        if not all(self.agents.to_list().array("on_earth")):
            raise AttributeError("Agent not on earth")

    def plot(self):
        """绘图"""
        fig, ax = plt.subplots()
        ax.plot(self.farmers_num, label="farmers")
        ax.plot(self.hunters_num, label="hunters")
        ax.set_xlabel("time")
        ax.set_ylabel("population")
        ax.legend()
