#!/usr/bin/env python 3.11.0
# -*-coding:utf-8 -*-
# @Author  : Shuang (Twist) Song
# @Contact   : SongshGeo@gmail.com
# GitHub   : https://github.com/SongshGeo
# Website: https://cv.songshgeo.com/

"""
处理一组实验的结果。
"""

from collections import defaultdict
from itertools import product
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional, Tuple

import pandas as pd
import seaborn as sns
from abses import Experiment
from matplotkit import with_axes
from matplotlib import pyplot as plt
from matplotlib.axes import Axes
from omegaconf import DictConfig

try:
    from typing import TypeAlias
except ImportError:
    from typing_extensions import TypeAlias

ActorType: TypeAlias = Literal["farmers", "rice", "hunters"]
JobType: TypeAlias = Literal["len", "num"]


def nested_defaultdict():
    """创建嵌套的defaultdict"""
    return defaultdict(list)


class MyExperiment(Experiment):
    """分析实验结果。"""

    bkps = defaultdict(nested_defaultdict)

    def run(
        self, cfg: DictConfig, repeat_id: int, outpath: Optional[Path] = None
    ) -> Tuple[Dict[str, Any], pd.DataFrame]:
        """运行模型一次"""
        cfg = self._update_log_config(cfg, repeat_id)
        # 获取日志
        model = self.model(
            parameters=cfg,
            run_id=repeat_id,
            outpath=outpath,
            experiment=self,
            nature_class=self._types["nature"],
            human_class=self._types["human"],
        )
        model.run_model()
        if model.datacollector.model_reporters:
            df = model.datacollector.get_model_vars_dataframe()
        else:
            df = pd.DataFrame()
        final_report = model.datacollector.get_final_vars_report(model)
        # TODO: 把这个重构到 ABSESpy 中，直接返回 model
        for k, v in model.bkps.items():
            MyExperiment.bkps[k][self.job_id].extend(v)
        return final_report, df

    @with_axes(figsize=(6, 4))
    def plot_agg_dynamic(
        self, y: ActorType, job: JobType = "len", ax=None, save=False
    ) -> Axes:
        """绘制某种人数的变化比例"""
        data = self.get_model_vars_dataframe()
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

    def plot_bkps(self, save=False):
        """
        绘制拐点分布图

        数据结构:
            self.bkps[cate][job_id] = [breakpoints]
        """
        # 检查数据
        print("Original data structure:", dict(MyExperiment.bkps))

        data = []
        for cate, job_dict in MyExperiment.bkps.items():
            for job_id, bkps in job_dict.items():
                for bkp in bkps:
                    data.append(
                        {"cate": cate, "job_id": str(job_id), "breakpoint": bkp}
                    )

        df = pd.DataFrame(data)
        print("\nDataFrame columns:", df.columns)
        print("\nDataFrame head:\n", df.head())

        # 使用正确的列名创建FacetGrid
        g = sns.FacetGrid(df, col="cate", col_wrap=3, height=4, aspect=1.2)
        g.map_dataframe(
            sns.histplot, x="breakpoint", hue="job_id", alpha=0.6, multiple="layer"
        )

        g.add_legend(title="Job ID")

        if save:
            plt.savefig(self.folder / "multi_breakpoints.jpg", bbox_inches="tight")
            plt.close()

        return g
