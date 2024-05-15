#!/usr/bin/env python 3.11.0
# -*-coding:utf-8 -*-
# @Author  : Shuang (Twist) Song
# @Contact   : SongshGeo@gmail.com
# GitHub   : https://github.com/SongshGeo
# Website: https://cv.songshgeo.com/

from typing import Literal

import hydra
import seaborn as sns
from abses import Experiment
from abses.tools.func import with_axes
from matplotlib import pyplot as plt
from omegaconf import DictConfig

from abses_sce.model import Model

try:
    from typing import TypeAlias
except ImportError:
    from typing_extensions import TypeAlias

ActorType: TypeAlias = Literal["farmers", "rice", "hunters"]
JobType: TypeAlias = Literal["len", "num"]


class MyExperiment(Experiment):
    """订制实验结果"""

    @with_axes(figsize=(6, 4))
    def plot_agg_dynamic(self, y: ActorType, job: JobType = "len", ax=None, save=False):
        """绘制某种人数的变化比例"""
        data = self.get_model_vars_dataframe()
        sns.lineplot(data, x="tick", y=f"{job}_{y}", hue="job_id", ax=ax)
        ax.set_ylim(0, 1)
        if save:
            plt.savefig(self.folder / f"{job}_{y}_ratio.jpg")
            plt.close()
        return ax

    def plot_all_dynamic(self, save=False):
        """绘制所有人数的变化比例"""
        for col in ("farmers", "hunters", "rice"):
            for j in ("num", "len"):
                self.plot_agg_dynamic(col, j, save=save)

    def plot_breakpoints(self, save=False):
        """绘制拐点分布图"""
        df_long = self.summary().melt(
            id_vars=["job_id", "repeat_id"],
            value_vars=["bkp_farmer", "bkp_hunters", "bkp_rice"],
            var_name="cate",
            value_name="bkp",
        )
        sns.displot(
            df_long,
            x="bkp",
            col="job_id",
            hue="cate",
            height=3,
            facet_kws=dict(margin_titles=True),
            palette="viridis",
        )
        if save:
            plt.savefig(self.folder / "breakpoints.jpg")
            plt.close()


@hydra.main(version_base=None, config_path="../config", config_name="config")
def main(cfg: DictConfig | None = None) -> None:
    """批量运行一次实验"""
    exp = MyExperiment(Model)
    exp.batch_run(cfg=cfg)
    exp.plot_all_dynamic(save=True)
    exp.plot_breakpoints(save=True)


if __name__ == "__main__":
    main()
