#!/usr/bin/env python 3.11.0
# -*-coding:utf-8 -*-
# @Author  : Shuang (Twist) Song
# @Contact   : SongshGeo@gmail.com
# GitHub   : https://github.com/SongshGeo
# Website: https://cv.songshgeo.com/

import os
from unittest.mock import MagicMock

import pytest
from hydra import compose, initialize

from abses import MainModel
from src.env import CompetingCell
from src.farmer import Farmer
from src.hunter import Hunter

# 加载项目层面的配置
with initialize(version_base=None, config_path="../config"):
    cfg = compose(config_name="config")
os.chdir(cfg.root)

MIN_SIZE = cfg.farmer.min_size
G_RATE = cfg.farmer.growth_rate
AREA = cfg.farmer.area


class TestFarmer:
    @pytest.fixture(name="raw_model")
    def mock_model(self) -> MainModel:
        """一个虚假的模型"""
        model = MainModel(parameters=cfg)
        layer = model.nature.create_module(
            how="from_resolution",
            shape=(4, 4),
            cell_cls=CompetingCell,
        )
        farmer = model.agents.create(Farmer, singleton=True)
        cell = layer.array_cells[3][2]
        # 模拟最大可支持的人口规模
        cell.lim_h = cfg.hunter.settle_size
        # 将虚假的农民放到它旁边
        farmer.put_on(layer.array_cells[3][2])
        hunter = model.agents.create(Hunter, size=50, singleton=True)
        return model, hunter, farmer, cell

    @pytest.fixture(name="farmer")
    def mock_farmer(self, raw_model) -> Farmer:
        """一个虚假的农民"""
        _, _, farmer, _ = raw_model
        return farmer

    @pytest.fixture(name="cell")
    def mock_cell(self, raw_model) -> CompetingCell:
        """一个虚假的格子"""
        _, _, _, cell = raw_model
        return cell

    def test_init(self, farmer):
        """测试初始化"""
        # Arrange / Act / Assert
        assert farmer.growth_rate == G_RATE
        assert farmer.area == AREA

    @pytest.mark.parametrize(
        "growth_rate, expected",
        [
            (0.1, 0.1),
            (0.2, 0.2),
            (-0.1, 0),
            (-0.2, 0),
        ],
        ids=[
            "positive_growth_rate",
            "positive_growth_rate",
            "negative_growth_rate",
            "negative_growth_rate",
        ],
    )
    def test_growth_rate_setter(self, farmer, growth_rate, expected):
        """测试人口增长率变化"""
        # Arrange / Act
        farmer.growth_rate = growth_rate
        result = farmer.growth_rate

        # Assert
        assert result == expected

    @pytest.mark.parametrize(
        "area, expected",
        [
            (1, 2),
            (2, 2),
            (3, 3),
            (-100, 2),
        ],
        ids=["positive_area", "positive_area", "zero_area", "negative_area"],
    )
    def test_area_setter(self, farmer, area, expected):
        """测试耕地面积变化"""
        # Arrange / Act
        assert farmer.area == AREA
        farmer.area = area

        # Assert
        assert farmer.area == expected

    @pytest.mark.parametrize(
        "force, size, lim_h, diffuse_prob, expected_result",
        [
            (True, 100, 50, 0.0, True),
            (False, 10, 50, 0.1, False),
            (False, 100, 50, 0.1, False),
            (False, 10, 50, 0.04, False),
            (False, 100, 50, 0.04, True),
        ],
        ids=[
            "force_true",
            "cond1_false_cond2_false",
            "cond1_true_cond2_false",
            "cond1_false_cond2_true",
            "cond1_true_cond2_true",
        ],
    )
    def test_diffuse(
        self, farmer, cell, force, size, lim_h, diffuse_prob, expected_result
    ):
        """测试农民的分散"""
        # Arrange
        farmer.size = size
        cell.lim_h = lim_h
        farmer.random.random = MagicMock(return_value=diffuse_prob)
        # Act
        result = farmer.diffuse(force)

        # Assert
        assert isinstance(result, Farmer) is expected_result

    @pytest.mark.parametrize(
        "growth_rate, area, complexity, expected_growth_rate",
        [
            (0.1, 100, 0.1, 0.09),
            (0.2, 200, 0.2, 0.16),
            (0.1, 100, 0.5, 0.05),
            (0.2, 200, 0.5, 0.1),
        ],
        ids=[
            "positive_complexity",
            "positive_complexity",
            "max_complexity",
            "max_complexity",
        ],
    )
    def test_complicate(
        self, farmer, growth_rate, area, complexity, expected_growth_rate
    ):
        """测试农民的复杂化"""
        # Arrange
        farmer.growth_rate = growth_rate
        farmer.area = area
        farmer.params.complexity = complexity

        # Act
        farmer.complicate()
        result_growth_rate = farmer.growth_rate
        result_area = farmer.area

        # Assert
        assert round(result_growth_rate, 2) == expected_growth_rate
        assert result_area == area + cfg.farmer.area * (1 - complexity)
