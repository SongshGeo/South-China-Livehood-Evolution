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
from itertools import product
from typing import TYPE_CHECKING, Dict, List, Literal, Tuple

import numpy as np
import pandas as pd
from abses import ActorsList, MainModel
from multi_ruptures.api import detect_breakpoints, iterative_pettitt
from scipy import stats

from src.util.regex import BKP, COL_NAMES, POST, PRE, clean_name
from src.util.stat import counting
from src.workflow.plot import ModelViz

# 正则表达式
if TYPE_CHECKING:
    from src.core.exp import ActorType


AGENT_TYPES = Literal["Farmer", "Hunter", "RiceFarmer"]
TYPES: List[AGENT_TYPES] = ["Farmer", "Hunter", "RiceFarmer"]


class LivelihoodModel(MainModel):
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
    def get_data_col(self, actor: ActorType) -> pd.Series:
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
        """计算某个主体在断点前后的线性增长率（斜率）。"""
        data = self.get_data_col(actor)
        bkp = self.detect_breakpoints(actor)

        def calculate_slope(series: pd.Series) -> float:
            if len(series) <= 1:
                return 0
            x = np.arange(len(series))
            slope, _, _, _, _ = stats.linregress(x, series)
            return slope

        before_rate = calculate_slope(data[: bkp + 1])
        after_rate = calculate_slope(data[bkp:])

        return before_rate, after_rate

    def _inspect_sources(self, source: AGENT_TYPES, target: AGENT_TYPES) -> int:
        """获取从source转换到target的主体数量"""
        if source not in TYPES:
            raise TypeError(f"Invalid source {source}.")
        total = self.agents.select({"source": source})
        return len(total.select(target))

    def export_conversion_data(self) -> None:
        """导出转换过程数据"""
        # 创建所有可能的转换组合
        conversions = {
            f"{source.lower()}_to_{target.lower()}": self._inspect_sources(
                source, target
            )
            for source, target in product(TYPES, TYPES)
        }
        # 导出为DataFrame并保存
        df = pd.DataFrame([conversions])
        df.to_csv(self.outpath / f"repeat_{self.run_id}_conversion.csv", index=False)

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

    @property
    def bkps(self) -> Dict[str, List[int]]:
        """拐点"""
        return (
            self.datacollector.get_model_vars_dataframe()
            .apply(
                iterative_pettitt,
                axis=0,
                alpha=self.p.get("pettitt_alpha", 0.005),
                sim=self.p.get("pettitt_sim", 2000),
                min_size=self.p.get("pettitt_min_size", None),
            )
            .to_dict()
        )
