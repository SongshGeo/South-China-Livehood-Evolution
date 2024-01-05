#!/usr/bin/env python 3.11.0
# -*-coding:utf-8 -*-
# @Author  : Shuang (Twist) Song
# @Contact   : SongshGeo@gmail.com
# GitHub   : https://github.com/SongshGeo
# Website: https://cv.songshgeo.com/

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import seaborn as sns
from matplotlib import pyplot as plt
from matplotlib.axes import Axes

if TYPE_CHECKING:
    from abses_sce.model import Model


class ModelViz:
    """可视化模型结果"""

    def __init__(self, model: Model, save_path: Path | None = None) -> None:
        self.model = model
        self.save = save_path
        self.outpath = ""
        self.data = model.dataset
        self.repeats = model.run_id

    def _wrap_ax(self):
        """包装一个 ax"""

    def histplot(self) -> Axes:
        """绘制主体人数的分布直方图"""
        _, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(10, 3))
        sns.histplot(self.model.farmers.array("size"), ax=ax1)
        sns.histplot(self.model.hunters.array("size"), ax=ax2)
        sns.histplot(self.model.rice.array("size"), ax=ax2)
        ax1.set_xlabel("Farmers")
        ax2.set_xlabel("Hunters")
        ax3.set_xlabel("Rice Farmers")
        if self.save:
            plt.savefig(self.save / f"repeat_{self.repeats}_histplot.jpg")
            plt.close()
        return ax1, ax2

    def dynamic(self) -> Axes:
        """绘制动态变化趋势"""
        _, ax = plt.subplots()
        ax.plot(self.data["farmers_num"], label="farmers size")
        ax.plot(self.data["hunters_num"], label="hunters size")
        ax.plot(self.data["rice_num"], label="rice farmers")
        ax.set_xlabel("time")
        ax.set_ylabel("population")
        ax.legend()
        ax2 = ax.twinx()
        ax2.plot(self.data["len_farmers"], ls=":", label="farmers groups")
        ax2.plot(self.data["len_hunters"], ls=":", label="hunters groups")
        ax2.plot(self.data["len_rice"], ls=":", label="rice farmers")
        if self.save:
            plt.savefig(self.save / f"repeat_{self.repeats}_dynamic.jpg")
            plt.close()
        return ax

    def heatmap(self) -> Axes:
        """绘制狩猎采集者和农民的空间分布"""
        _, (ax1, ax2) = plt.subplots(1, 2, figsize=(8, 3))
        mask = self.model.nature.dem.get_xarray("elevation") >= 0
        farmers = self.model.nature.dem.get_xarray("farmers").where(mask)
        hunters = self.model.nature.dem.get_xarray("hunters").where(mask)
        farmers.plot.contourf(ax=ax1, cmap="Reds")
        hunters.plot.contourf(ax=ax2, cmap="Greens")
        ax1.set_xlabel("Farmers")
        ax2.set_xlabel("Hunters")
        if self.save:
            plt.savefig(self.save / f"repeat_{self.repeats}_heatmap.jpg")
            plt.close()
        return ax1, ax2
