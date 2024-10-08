#!/usr/bin/env python 3.11.0
# -*-coding:utf-8 -*-
# @Author  : Shuang (Twist) Song
# @Contact   : SongshGeo@gmail.com
# GitHub   : https://github.com/SongshGeo
# Website: https://cv.songshgeo.com/

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, List

import numpy as np
import xarray as xr
from matplotlib import pyplot as plt
from matplotlib.axes import Axes

if TYPE_CHECKING:
    from src.core.model import Model


class ModelViz:
    """
    用于可视化模型结果的类。

    属性:
        model (Model): 要可视化的模型实例。
        save (Path | None): 保存图表的路径。如果为None，则不保存图表。
        outpath (str): 输出路径。
        data (DataFrame): 模型变量的数据框。
        repeats (int): 模型运行的次数。
    """

    def __init__(self, model: Model, save_path: Path | None = None) -> None:
        """
        初始化ModelViz实例。

        参数:
            model (Model): 要可视化的模型实例。
            save_path (Path | None): 保存图表的路径。如果为None，则不保存图表。
        """
        self.model = model
        self.save = save_path
        self.outpath = ""
        self.data = model.datacollector.get_model_vars_dataframe()
        self.repeats = model.run_id

    def dynamic(self) -> Axes:
        """
        绘制人口和群体数量的动态变化趋势。

        返回:
            Axes: matplotlib的Axes对象，包含绘制的图表。
        """
        _, ax = plt.subplots()
        ax.plot(self.data["num_farmers_n"], label="farmers size")
        ax.plot(self.data["num_hunters_n"], label="hunters size")
        ax.plot(self.data["num_rice_n"], label="rice farmers")
        ax.set_xlabel("time")
        ax.set_ylabel("population")
        ax.legend()
        ax2 = ax.twinx()
        ax2.plot(self.data["len_farmers_n"], ls=":", label="farmers groups")
        ax2.plot(self.data["len_hunters_n"], ls=":", label="hunters groups")
        ax2.plot(self.data["len_rice_n"], ls=":", label="rice farmers")
        if self.save:
            plt.savefig(self.save / f"repeat_{self.repeats}_dynamic.jpg")
            plt.close()
        return ax

    def stack_dynamic(
        self, flag: List[str] | None = None, ax: Axes | None = None
    ) -> Axes:
        """
        绘制堆积图，展示不同类型人口或群体的比例变化。

        参数:
            flag (List[str] | None):
                指定绘制哪种统计数据。
                如果 flag='num'，则绘制人口数量。
                如果 flag='len'，则绘制群体数量。
                如果 flag is None，则两个都绘制。
            ax (Axes | None):
                指定的matplotlib Axes对象。如果为None，则创建新的Axes。

        返回:
            Axes: 包含堆积图的matplotlib Axes对象。
        """
        if ax is None and flag is not None:
            _, ax = plt.subplots()
        if flag == "num":
            cols = ["num_farmers", "num_hunters", "num_rice"]
        elif flag == "len":
            cols = ["len_farmers", "len_hunters", "len_rice"]
        else:
            _, (ax1, ax2) = plt.subplots(1, 2, figsize=(7, 3))
            ax1 = self.stack_dynamic("num", ax1)
            ax2 = self.stack_dynamic("len", ax2)
            return ax1, ax2
        labels = ["Rainfed", "Hunting", "Paddy"]
        ratios = self.data[cols].div(self.data[cols].sum(axis=1), axis=0)
        ax.stackplot(self.data.index, [ratios[col] for col in cols], labels=labels)
        ax.legend()
        ax.set_xlabel("Population" if flag == "num" else "Groups")
        if self.save:
            plt.savefig(self.save / f"repeat_{self.repeats}_stackplots.jpg")
            plt.close()
        return ax

    def heatmap(self) -> Axes:
        """
        绘制狩猎采集者、农民和水稻农民的空间分布热力图。

        返回:
            Tuple[Axes, Axes, Axes]: 包含三个热力图的matplotlib Axes对象元组。
        """

        def log(xda_: xr.DataArray):
            return xr.apply_ufunc(np.log, xda_.where(xda_ != 0))

        _, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(10, 3))
        mask = self.model.nature.get_xarray("elevation") >= 0
        farmers = self.model.nature.get_xarray("farmers").where(mask)
        hunters = self.model.nature.get_xarray("hunters").where(mask)
        rice = self.model.nature.get_xarray("rice_farmers").where(mask)
        # Calculate logarithmically, without warnings
        log(farmers).plot.contourf(ax=ax1, cmap="Reds")
        log(hunters).plot.contourf(ax=ax2, cmap="Greens")
        log(rice).plot.contourf(ax=ax3, cmap="Oranges")

        ax1.set_xlabel("Farmers")
        ax2.set_xlabel("Hunters")
        ax3.set_xlabel("Rice Farmers")
        if self.save:
            plt.savefig(self.save / f"repeat_{self.repeats}_heatmap.jpg")
            plt.close()
        return ax1, ax2, ax3
