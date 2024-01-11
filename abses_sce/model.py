#!/usr/bin/env python 3.11.0
# -*-coding:utf-8 -*-
# @Author  : Shuang (Twist) Song
# @Contact   : SongshGeo@gmail.com
# GitHub   : https://github.com/SongshGeo
# Website: https://cv.songshgeo.com/

from pathlib import Path

import pandas as pd
from abses import ActorsList, MainModel

from abses_sce.farmer import Farmer
from abses_sce.plot import ModelViz
from abses_sce.rice_farmer import RiceFarmer

from .env import Env


class Model(MainModel):
    """运行的模型"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, nature_class=Env, **kwargs)
        self.nature.add_hunters()
        self.farmers_num = []
        self.new_farmers = []
        self.hunters_num = []
        self.len_farmers = []
        self.len_hunters = []
        self.len_rice = []
        self.rice_num = []
        self.outpath = kwargs.get("outpath", "")

    @property
    def outpath(self) -> str:
        """输出文件夹"""
        return self._path

    @outpath.setter
    def outpath(self, path: str) -> None:
        """设置输出文件夹"""
        path_obj = Path(path)
        if not path_obj.is_dir():
            raise FileExistsError(f"{path} not exist.")
        self._path = path_obj

    @property
    def farmers(self) -> ActorsList:
        """农民列表"""
        return self.agents.select("Farmer")

    @property
    def hunters(self) -> ActorsList:
        """狩猎采集者列表"""
        return self.agents.select("Hunter")

    @property
    def rice(self) -> ActorsList:
        """种水稻的农民列表"""
        return self.agents.select("RiceFarmer")

    def trigger(self, actors: ActorsList, func: str, *args, **kwargs) -> None:
        """触发所有还活着的主体的行动"""
        for actor in actors:
            if not actor.on_earth:
                continue
            getattr(actor, func)(*args, **kwargs)

    def step(self):
        """每一时间步都按照以下顺序执行一次：
        1. 更新农民数量
        2. 所有主体互相转化
        3. 更新狩猎采集者可以移动（这可能触发竞争）
        """
        farmers = self.nature.add_farmers(Farmer)
        farmers = self.nature.add_farmers(RiceFarmer)
        self.trigger(self.actors, "population_growth")
        self.trigger(self.actors, "convert")
        self.trigger(self.actors, "diffuse")
        self.trigger(self.hunters, "move")
        # 更新农民和狩猎采集者数量
        self.new_farmers.append(len(farmers))
        self.farmers_num.append(self.farmers.array("size").sum())
        self.hunters_num.append(self.hunters.array("size").sum())
        self.rice_num.append(self.rice.array("size").sum())
        self.len_hunters.append(len(self.hunters))
        self.len_farmers.append(len(self.farmers))
        self.len_rice.append(len(self.rice))

    @property
    def dataset(self) -> pd.DataFrame:
        """数据"""
        data = {
            "new_farmers": self.new_farmers,
            "farmers_num": self.farmers_num,
            "hunters_num": self.hunters_num,
            "rice_num": self.rice_num,
            "len_hunters": self.len_hunters,
            "len_farmers": self.len_farmers,
            "len_rice": self.len_rice,
        }
        return pd.DataFrame(data=data, index=range(self.time.tick))

    def export_data(self) -> None:
        """导出实验数据"""
        self.dataset.to_csv(self.outpath / f"repeat_{self.run_id}.csv")

    def end(self):
        """模型运行结束后，将自动绘制狩猎采集者和农民的数量变化"""
        self.plot.dynamic()
        self.plot.heatmap()
        self.plot.histplot()
        self.export_data()

    @property
    def plot(self) -> ModelViz:
        """绘制狩猎采集者和农民的数量变化"""
        save_fig = self.params.get("save_plots", False)
        path = self.outpath if save_fig else None
        return ModelViz(model=self, save_path=path)
