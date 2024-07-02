#!/usr/bin/env python 3.11.0
# -*-coding:utf-8 -*-
# @Author  : Shuang (Twist) Song
# @Contact   : SongshGeo@gmail.com
# GitHub   : https://github.com/SongshGeo
# Website: https://cv.songshgeo.com/

"""Main model for South China Livelihood
"""
from __future__ import annotations

from functools import lru_cache
from typing import TYPE_CHECKING, Dict, Tuple

import pandas as pd
from abses import ActorsList, MainModel

from src.api import Farmer, RiceFarmer
from src.api.env import Env
from src.workflow.analysis import detect_breakpoints
from src.workflow.plot import ModelViz

if TYPE_CHECKING:
    from src.core.exp import ActorType

COL_NAMES = {
    "size": "num_breed_n",
    "ratio": "num_breed",
    "group": "len_breed_n",
    "group_ratio": "len_breed",
}


class Model(MainModel):
    """运行的模型"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, nature_class=Env, **kwargs)
        self.nature.add_hunters()

    @property
    def farmers(self) -> ActorsList:
        """农民列表"""
        return self.agents("Farmer")

    @property
    def hunters(self) -> ActorsList:
        """狩猎采集者列表"""
        return self.agents("Hunter")

    @property
    def rice(self) -> ActorsList:
        """种水稻的农民列表"""
        return self.agents("RiceFarmer")

    @lru_cache
    def get_data_col(self, actor: ActorType) -> str:
        """获取主体的数据列"""
        data = self.datacollector.get_model_vars_dataframe()
        col_by = self.p.get("detect_bkp_by", "size")
        col = COL_NAMES[col_by].replace("breed", actor)
        return data[col]

    @lru_cache
    def detect_breakpoints(self, actor: ActorType) -> int:
        """检测某个主体数量发展中的拐点。
        Parameters:
            actor: str
                主体类型，可以是 "farmers", "hunters", "rice" 之一

        Returns:
            int
                拐点的索引。
        """
        n_bkps = self.p.get("n_bkps", 1)
        if n_bkps != 1:
            raise NotImplementedError("Only support one breakpoint detection so far.")
        data = self.get_data_col(actor)
        return detect_breakpoints(data, n_bkps=n_bkps)

    @lru_cache
    def calc_rate(self, actor: ActorType) -> Tuple[float, float]:
        """计算某个主体的增长率。"""
        data = self.get_data_col(actor)
        bkp = self.detect_breakpoints(actor)
        rate = data.pct_change()
        return rate.iloc[:bkp].mean(), rate.iloc[bkp:].mean()

    def step(self):
        """每一时间步都按照以下顺序执行一次：
        1. 更新农民数量
        2. 所有主体互相转化
        3. 更新狩猎采集者可以移动（这可能触发竞争）
        """
        self.nature.add_farmers(Farmer)
        self.nature.add_farmers(RiceFarmer)

    def _inspect_sources(self, breed: str) -> Dict[str, int]:
        """获取来源于某种人的转换结果"""
        if breed not in {"Farmer", "RiceFarmer", "Hunter"}:
            raise TypeError(f"Invalid breed {breed}.")
        total = self.agents.select({"source": breed})
        farmers = total.select("Farmer")
        hunters = total.select("Hunter")
        rice = total.select("RiceFarmer")
        return {
            "farmers_end": len(farmers),
            "hunters_end": len(hunters),
            "rice_end": len(rice),
            "total_end": len(total),
        }

    def export_conversion_data(self) -> None:
        """导出转换过程"""
        return pd.DataFrame(
            {
                "farmer_init": self._inspect_sources("Farmer"),
                "hunter_init": self._inspect_sources("Hunter"),
                "rice_init": self._inspect_sources("RiceFarmer"),
            }
        ).to_csv(self.outpath / f"repeat_{self.run_id}_conversion.csv")

    def end(self):
        """模型运行结束后，将自动绘制狩猎采集者和农民的数量变化"""
        self.plot.dynamic()
        self.plot.heatmap()
        self.actors.plot.hist(
            attr="size", savefig=self.outpath / f"repeat_{self.run_id}_hist.jpg"
        )
        self.export_conversion_data()

    @property
    def plot(self) -> ModelViz:
        """绘制狩猎采集者和农民的数量变化"""
        save_fig = self.params.get("save_plots", False)
        path = self.outpath if save_fig else None
        return ModelViz(model=self, save_path=path)
