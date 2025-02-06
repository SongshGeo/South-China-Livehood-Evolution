#!/usr/bin/env python 3.11.0
# -*-coding:utf-8 -*-
# @Author  : Shuang (Twist) Song
# @Contact   : SongshGeo@gmail.com
# GitHub   : https://github.com/SongshGeo
# Website: https://cv.songshgeo.com/

"""
处理一组实验的结果。
"""

from itertools import product
from typing import Literal

import seaborn as sns
from abses import Experiment
from abses.tools.func import with_axes
from matplotlib import pyplot as plt
from matplotlib.axes import Axes

try:
    from typing import TypeAlias
except ImportError:
    from typing_extensions import TypeAlias

ActorType: TypeAlias = Literal["farmers", "rice", "hunters"]
JobType: TypeAlias = Literal["len", "num"]


class MyExperiment(Experiment):
    """分析实验结果。"""

    @with_axes(figsize=(6, 4))
    def plot_agg_dynamic(
        self, y: ActorType, job: JobType = "len", ax=None, save=False
    ) -> Axes:
        """绘制某种人数的变化比例"""
        data = self.summary()
        sns.lineplot(data, x="tick", y=f"{job}_{y}", hue="job_id", ax=ax)
        ax.set_ylim(0, 1)
        if save:
            plt.savefig(self.folder / f"{job}_{y}_ratio.jpg")
            plt.close()
        return ax

    def plot_all_dynamic(self, save=False) -> None:
        """绘制所有人数的变化比例"""
        breed = ("farmers", "hunters", "rice")
        cate = ("num", "len")
        for col, j in product(breed, cate):
            self.plot_agg_dynamic(col, j, save=save)

    def plot_breakpoints(self, save=False):
        """绘制拐点分布图

        对总结数据制作长格式，然后绘制每种的数量分布图。
        """
        df_long = self.summary().melt(
            id_vars=["job_id", "repeat_id"],
            value_vars=["bkp_farmer", "bkp_hunters", "bkp_rice"],
            var_name="cate",
            value_name="bkp",
        )
        sns.displot(
            df_long,
            x="bkp",
            col="cate",
            row="job_id",
            height=3,
            facet_kws=dict(margin_titles=True),
        )
        if save:
            plt.savefig(self.folder / "breakpoints.jpg")
            plt.close()

    @with_axes(figsize=(6, 4))
    def plot_heatmap(self, var: str, save=False, ax=None) -> Axes:
        """绘制热力图"""
        if not self.overrides:
            raise AttributeError("overrides not found")
        overrides = list(self.overrides.keys())
        if len(overrides) != 2:
            raise ValueError("overrides must be a dict with two keys")
        v1, v2 = overrides
        pivot = self.summary().pivot_table(
            index=v1,
            columns=v2,
            values=var,
        )
        sns.heatmap(pivot, annot=True, fmt=".0f", ax=ax)
        if save:
            plt.savefig(self.folder / "heatmap.jpg")
            plt.close()
        return ax
