#!/usr/bin/env python 3.11.0
# -*-coding:utf-8 -*-
# @Author  : Shuang (Twist) Song
# @Contact   : SongshGeo@gmail.com
# GitHub   : https://github.com/SongshGeo
# Website: https://cv.songshgeo.com/

"""
运行一次实验
"""
import hydra
from omegaconf import DictConfig

from src.api import Env
from src.core import Model, MyExperiment


@hydra.main(version_base=None, config_path="../config", config_name="config")
def main(cfg: DictConfig | None = None) -> None:
    """批量运行一次实验"""
    exp = MyExperiment(Model, nature_cls=Env)
    exp.batch_run(cfg=cfg)
    exp.plot_all_dynamic(save=True)
    exp.plot_breakpoints(save=True)
    exp.summary().to_csv(exp.folder / "summary.csv")


if __name__ == "__main__":
    main()
