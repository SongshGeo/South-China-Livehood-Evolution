#!/usr/bin/env python 3.11.0
# -*-coding:utf-8 -*-
# @Author  : Shuang (Twist) Song
# @Contact   : SongshGeo@gmail.com
# GitHub   : https://github.com/SongshGeo
# Website: https://cv.songshgeo.com/

"""Main model for South China Livelihood
"""
from __future__ import annotations

import re
from functools import lru_cache
from typing import TYPE_CHECKING, Dict, Tuple

import pandas as pd
from abses import ActorsList, MainModel

from src.api import Farmer, RiceFarmer
from src.workflow.analysis import detect_breakpoints
from src.workflow.plot import ModelViz

# 正则表达式
if TYPE_CHECKING:
    from src.core.exp import ActorType

COL_NAMES = {
    "size": "num_breed_n",
    "ratio": "num_breed",
    "group": "len_breed_n",
    "group_ratio": "len_breed",
}

PATTERN = r"^(farmers|hunters|rice) (group|size) (ratio|num)$"
BKP = r"^bkp_(farmers|hunters|rice)"
PRE = r"^pre_(farmers|hunters|rice)"
POST = r"^post_(farmers|hunters|rice)"


def clean_name(attribute: str) -> dict:
    """清理属性名"""
    if not re.match(PATTERN, attribute):
        raise ValueError(f"Invalid attribute name {attribute}.")
    breed, group_or_size, ratio_or_num = attribute.split()
    return {
        "breed": breed,
        "group": group_or_size == "group",
        "ratio": ratio_or_num == "ratio",
    }


def counting(
    model: Model,
    breed: ActorType,
    ratio: bool = False,
    group: bool = False,
) -> int | float:
    """统计某个主体的数量"""
    actors: ActorsList = getattr(model, breed)
    num = len(actors) if group else actors.array("size").sum()
    if num == 0:
        return 0.0
    if not ratio:
        return num
    if group:
        return num / len(model.agents)
    return num / model.actors.array("size").sum()


class Model(MainModel):
    """运行的模型"""

    def __getattr__(self, name: str):
        # 断点识别
        if re.match(BKP, name):
            return self.detect_breakpoints(name.replace("bkp_", ""))
        # 计算断点之前的增长率
        if re.match(PRE, name):
            return self.calc_rate(name.replace("pre_", ""))[0]
        # 计算断点之后的增长率
        if re.match(POST, name):
            return self.calc_rate(name.replace("post_", ""))[1]
        # 计数
        if kwargs := clean_name(name):
            return counting(model=self, **kwargs)
        return super().__getattribute__(name)

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
