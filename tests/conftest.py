#!/usr/bin/env python 3.11.0
# -*-coding:utf-8 -*-
# @Author  : Shuang (Twist) Song
# @Contact   : SongshGeo@gmail.com
# GitHub   : https://github.com/SongshGeo
# Website: https://cv.songshgeo.com/

"""用于测试的基本模型，和图层。
"""

import os

import numpy as np
import pytest
from abses import MainModel, PatchModule
from hydra import compose, initialize

from abses_sce.env import CompetingCell

# 加载项目层面的配置
with initialize(version_base=None, config_path="."):
    cfg = compose(config_name="config_test")
os.chdir(cfg.root)


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
    layer.apply_raster(np.ones((1, 4, 4)) * cfg.sitegroup.max_size, "lim_h")
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


def set_cell_arable_condition(cell: CompetingCell, arable: bool, rice_arable: bool):
    """将一个斑块的值设置成指定的情况，用于测试"""
    cell.is_water = False
    cell.elevation = 1
    if not arable and not rice_arable:
        cell.slope = 20
    elif not rice_arable:
        cell.slope = 5
    elif arable:
        cell.slope = 0.1
    else:
        raise ValueError("只能种水稻，不能种旱稻")
