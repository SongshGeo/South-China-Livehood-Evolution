#!/usr/bin/env python 3.11.0
# -*-coding:utf-8 -*-
# @Author  : Shuang (Twist) Song
# @Contact   : SongshGeo@gmail.com
# GitHub   : https://github.com/SongshGeo
# Website: https://cv.songshgeo.com/

"""用于测试的基本模型，和图层。
"""

import os

import pytest
from abses import MainModel, PatchModule
from hydra import compose, initialize

from src.env import CompetingCell

# 加载项目层面的配置
with initialize(version_base=None, config_path="../config"):
    cfg = compose(config_name="config")
os.chdir(cfg.root)

MAX_SIZE = int(cfg.hunter.max_size)
MIN_SIZE = int(cfg.hunter.min_size)
G_RATE = cfg.hunter.growth_rate
INTENSITY = cfg.hunter.intensified_coefficient


@pytest.fixture(name="model_and_layer")
def mock_model_layer():
    """创建一个用于测试的基本模型，拥有一个 4 * 4 的名为'layer'的图层。"""
    model = MainModel(parameters=cfg)
    layer = model.nature.create_module(
        name="layer",
        how="from_resolution",
        shape=(4, 4),
        cell_cls=CompetingCell,
    )
    return model, layer


@pytest.fixture(name="model")
def mock_model(model_and_layer) -> MainModel:
    """只提取模型"""
    model, _ = model_and_layer
    return model


@pytest.fixture(name="layer")
def mock_layer(model_and_layer) -> PatchModule:
    """只提取图层"""
    _, layer = model_and_layer
    return layer
