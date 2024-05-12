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


@hydra.main(version_base=None, config_path="../config", config_name="config")
def main(cfg: DictConfig | None = None) -> None:
    """批量运行一次实验"""
    exp = MyExperiment(Model)
    exp.batch_run(cfg=cfg)
    for col in ("farmers", "hunters", "rice"):
        for j in ("num", "len"):
            exp.plot_agg_dynamic(col, j, save=True)


if __name__ == "__main__":
    main()
