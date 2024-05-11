#!/usr/bin/env python 3.11.0
# -*-coding:utf-8 -*-
# @Author  : Shuang (Twist) Song
# @Contact   : SongshGeo@gmail.com
# GitHub   : https://github.com/SongshGeo
# Website: https://cv.songshgeo.com/

import hydra
from abses import Experiment
from omegaconf import DictConfig

from abses_sce.model import Model


@hydra.main(version_base=None, config_path="../config", config_name="config")
def main(cfg: DictConfig | None = None) -> None:
    """批量运行一次实验"""
    exp = Experiment(Model)
    exp.batch_run(cfg=cfg)


if __name__ == "__main__":
    main()
    Experiment.summary(save=False)
