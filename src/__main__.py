#!/usr/bin/env python 3.11.0
# -*-coding:utf-8 -*-
# @Author  : Shuang (Twist) Song
# @Contact   : SongshGeo@gmail.com
# GitHub   : https://github.com/SongshGeo
# Website: https://cv.songshgeo.com/

"""
运行一次实验
"""
import logging

import hydra
from omegaconf import DictConfig
from twist_academic import notify

from src.api import Env
from src.core import Model, MyExperiment

logger = logging.getLogger(__name__)


@hydra.main(version_base=None, config_path="../config", config_name="config")
def main(cfg: DictConfig | None = None) -> None:
    """
    执行一次完整的实验流程。

    该函数是模型的主入口点,用于批量运行实验并生成相关图表和摘要。具体步骤包括:
    1. 初始化实验对象
    2. 批量运行模型
    3. 绘制动态图表(人口数量、比例,群体数量、比例)
    4. 绘制断点图(数量、位置、分布)
    5. 生成并保存实验摘要(summary.csv)
    6. 根据配置绘制热力图(如果指定)

    参数:
        cfg (DictConfig | None, optional): Hydra配置对象。默认为None。
        在命令行中运行时,使用以下命令:
        ```bash
        python src --multirun xxx.yyy=a,b,c
        ```
        其中xxx.yyy是配置文件中的参数名,a,b,c是参数的取值。

    返回:
        None

    异常:
        ValueError: 热力图绘制出现问题时可能引发。
        AttributeError: 热力图绘制出现问题时可能引发。
    """
    exp = MyExperiment(Model, cfg=cfg, nature_class=Env)
    exp.batch_run(repeats=cfg.exp.repeats, parallels=cfg.exp.num_process)
    logger.info(f"Experiment folder: {exp.folder}")


if __name__ == "__main__":
    notify("华南农业实验开始运行")
    main()
    notify("华南农业实验结束")
