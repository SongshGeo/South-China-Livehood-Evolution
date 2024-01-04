#!/usr/bin/env python 3.11.0
# -*-coding:utf-8 -*-
# @Author  : Shuang (Twist) Song
# @Contact   : SongshGeo@gmail.com
# GitHub   : https://github.com/SongshGeo
# Website: https://cv.songshgeo.com/

import warnings

import hydra
from hydra.core.hydra_config import HydraConfig
from omegaconf import DictConfig

from abses_sce.model import Model

warnings.filterwarnings("ignore", module="abses")


class Experiment:
    """一次批量实验"""

    def __init__(self, name):
        self._name = name
        self._n_runs = 0

    @property
    def name(self) -> str:
        """The name of the experiment."""
        return self._name

    def run(self, cfg: DictConfig, unique_run_id: int, outpath) -> bool:
        """运行模型一次"""
        model = Model(parameters=cfg, run_id=unique_run_id, outpath=outpath)
        model.run_model()

    def batch_run(self, cfg: DictConfig, repeats: int, outpath: str) -> None:
        """Run the experiment multiple times."""
        for repeat_id in range(1, repeats + 1):
            self.run(cfg, unique_run_id=repeat_id, outpath=outpath)
            self._n_runs += 1


@hydra.main(version_base=None, config_path="../config", config_name="config")
def main(cfg: DictConfig | None = None) -> None:
    """批量运行一次实验"""
    hydra_config = HydraConfig.get()
    name = hydra_config.job.name  # 实验的名称
    repeats = cfg.exp.repeats  # 每次运行的重复次数
    # run_id = 1 if cfg.exp.run_id is None else int(cfg.exp.run_id) + 1
    exp = Experiment(name=name)  # 获取实验名称的实例
    exp.batch_run(cfg=cfg, repeats=repeats, outpath=hydra_config.runtime.output_dir)


if __name__ == "__main__":
    main()
