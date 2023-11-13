#!/usr/bin/env python 3.11.0
# -*-coding:utf-8 -*-
# @Author  : Shuang (Twist) Song
# @Contact   : SongshGeo@gmail.com
# GitHub   : https://github.com/SongshGeo
# Website: https://cv.songshgeo.com/


"""测试基本主体类，包括其规模的设置，以及衍生。
"""

import os
from typing import Tuple

import pytest
from abses import MainModel, PatchModule
from hydra import compose, initialize

from src.env import CompetingCell
from src.people import SiteGroup

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


class TestGroup:
    """测试基本的主体类型"""

    @pytest.fixture(name="people")
    def mock_people(self, model, layer) -> SiteGroup:
        """一个虚假的主体"""
        people: SiteGroup = model.agents.create(SiteGroup, singleton=True)
        cell = layer.array_cells[3][3]
        people.put_on(cell=cell)
        return people

    def test_size_setup(self, people: SiteGroup):
        """测试主体的大小设置"""
        assert people.size == 6
        assert people.min_size == 6
        assert people.max_size == 31

    @pytest.mark.parametrize(
        "growth_rate, years, expected_size",
        [
            (0.0025, 1, 51),  # 50.125 -> 51
            (0.0025, 10, 52),  # 51.26415666138926 -> 52
            (0.0025, 100, 64),  # 64.18124443692305 -> 65 -> max_size(64)
        ],
        ids=["增长一年", "增长10年", "增长100年"],
    )
    def test_growth(
        self,
        people: SiteGroup,  # 增长的基本人口
        growth_rate,  # 人口增长比率
        years,  # 以该比率进行人口增长的总年份
        expected_size,  # 期望得到的人口数量
    ):
        """测试人口增长"""
        # Arrange
        people.max_size = 64.0
        people.size = 50

        # Act
        for _ in range(years):
            people.population_growth(growth_rate=growth_rate)

        # Assert
        assert people.size == expected_size

    @pytest.mark.parametrize(
        "group_range, initial_size, expected_size, expected_new_size",
        [
            ([15, 15], 20, None, 15),  # 必定选15，原来死掉，新的15
            ([10, 10], 20, 10, 10),  # 必定选10，原来剩10，新的10
            ([200, 300], 20, None, 20),  # 选一个很大的数，按当前有的人数出动，原来的死掉，新的是原来的数量
        ],
        ids=["not_enough_old", "within_range", "above_maximum"],
    )
    def test_diffuse(
        self,
        people: SiteGroup,
        group_range: Tuple[int, int],
        initial_size: int,
        expected_size: int,
        expected_new_size: int,
    ):
        """测试人口分散，随机选择一个最小和最大的规模，分裂出去"""
        # Arrange
        cell = people.model.nature.layer.cells[3][3]
        people.put_on(cell)
        people.size = initial_size
        people.min_size = 6

        # Act
        new_group = people.diffuse(group_range)

        # Assert
        if expected_size is None:
            assert not people.on_earth
        else:
            assert people.size == expected_size
        new_size = getattr(new_group, "size", None)
        assert new_size == expected_new_size
