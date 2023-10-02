#!/usr/bin/env python 3.11.0
# -*-coding:utf-8 -*-
# @Author  : Shuang (Twist) Song
# @Contact   : SongshGeo@gmail.com
# GitHub   : https://github.com/SongshGeo
# Website: https://cv.songshgeo.com/

import os
from unittest.mock import MagicMock, patch

import pytest

# import numpy as np
from abses import MainModel
from hydra import compose, initialize

from src.env import CompetingCell
from src.farmer import Farmer
from src.hunter import Hunter
from src.people import SiteGroup

# 加载项目层面的配置
with initialize(version_base=None, config_path="../config"):
    cfg = compose(config_name="config")
os.chdir(cfg.root)

MAX_SIZE = cfg.hunter.max_size
MIN_SIZE = cfg.hunter.min_size
G_RATE = cfg.hunter.growth_rate
INTENSITY = cfg.hunter.intensified_coefficient


class TestHunter:
    """测试狩猎采集者"""

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
        cell = layer.array_cells[3][3]
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
        """一个虚假的斑块"""
        _, _, _, cell = raw_model
        return cell

    @pytest.fixture(name="group")
    def site_group(self, raw_model):
        """原始的聚落"""
        # size = np.random.uniform(30, 60)
        _, hunter, _, _ = raw_model
        return hunter

    @pytest.fixture(name="other_group")
    def mock_other_group(self):
        """一个虚假的聚落"""
        model = MainModel(parameters=cfg)
        return model.agents.create(Hunter, size=60, singleton=True)

    @pytest.mark.parametrize(
        "size, expected, settled",
        [
            (100, 100, False),
            (0, MIN_SIZE, False),
            (500, 500, True),
            (7000, MAX_SIZE, True),
        ],
        ids=["positive_size", "zero_size", "max_size", "large_size"],
    )
    def test_size_property(self, group, size, expected, settled):
        """测试人口规模有最大最小值限制"""
        # Arrange
        group.size = size

        # Act
        result = group.size

        # Assert
        assert result == expected
        assert group.is_complex is settled

    @pytest.mark.parametrize(
        "growth_rate, initial_size, expected",
        [
            (0.1, 100, 110),
            (0.2, 0, 7),
            (-0.1, 500, 450),
            (0.5, 1000, 1500),
        ],
        ids=["positive_growth", "zero_growth", "negative_growth", "large_growth"],
    )
    def test_population_growth(self, group, growth_rate, initial_size, expected):
        """测试人口增长"""
        # Arrange
        group.size = initial_size

        # Act
        group.population_growth(growth_rate)

        # Assert
        assert group.size == expected

    @pytest.mark.parametrize(
        "s_min, s_max, initial_size, expected_size, expected_new_group_size",
        [
            (50, 50, 100, 50, 50),
            (200, 300, 99, 99, None),
            # (100, 200, 100, 0, 100),
        ],
        ids=[
            "within_range",
            "above_max_size",
            # "below_min_size"
        ],
    )
    def test_diffuse(
        self,
        group,
        cell,
        s_min,
        s_max,
        initial_size,
        expected_size,
        expected_new_group_size,
    ):
        """测试人口分散，随机选择一个最小和最大的规模，分裂出去"""
        # Arrange
        group.put_on(cell)
        group.params.new_group_size = (s_min, s_max)
        group.size = initial_size
        assert group.size == initial_size
        assert group.loc("lim_h") == cfg.hunter.settle_size

        # Act
        new_group = group.diffuse()

        # Assert
        assert group.size == expected_size
        assert getattr(new_group, "size", None) == expected_new_group_size

    @pytest.mark.parametrize(
        "convert_prob, random_value, arable, changed",
        [
            (0.5, 0.4, True, True),
            (0.5, 0.6, True, False),
            (0.1, 0.05, False, False),
            (0.1, 0.2, False, False),
        ],
        ids=["convert", "no_convert", "convert_low_prob", "no_convert_high_prob"],
    )
    def test_convert(self, cell, group, convert_prob, random_value, changed, arable):
        """测试当小于一定概率时，农民与狩猎采集者可能发生相互转化"""
        # Arrange
        group.params.convert_prob = convert_prob
        group.random.random = MagicMock(return_value=random_value)
        group.put_on(cell)
        # 配置是否是可耕地的条件
        cell.slope = 5
        cell.aspect = 100
        cell.elevation = 100 if arable else 300

        size = group.size
        # Act
        convert = group.convert()

        # Assert
        assert isinstance(convert, SiteGroup)
        assert (isinstance(convert, Hunter)) != changed
        assert convert.size == size

    @pytest.mark.parametrize(
        "size, expected_cell",
        [(100, True), (0, True), (500, False), (7000, False)],
        ids=["positive_size", "zero_size", "max_size", "large_size"],
    )
    def test_move(self, group, cell, size, expected_cell):
        """测试有移动能力才能移动，在周围随机选取一个格子移动"""
        # Arrange
        group.size = size
        group.put_on(cell)
        initial_pos = group.pos
        group.move()

        assert (group.pos != initial_pos) is expected_cell

    @pytest.mark.parametrize(
        "other_size, expected",
        # intensified = 1.5
        [
            (10 * INTENSITY - 1, True),
            (10 * INTENSITY + 1, False),
            # Add more test cases as needed
        ],
    )
    def test_compete_with_farmers(self, group, farmer, other_size, expected):
        """测试主体之间的竞争"""
        group.size = 10
        farmer.size = other_size
        with patch("src.hunter.Hunter._compete_with_farmer") as mock:
            group.compete(farmer)
            assert mock.called
        assert group.compete(farmer) == expected

    @pytest.mark.parametrize(
        "other_size, expected",
        # intensified = 1.5
        [
            (9, True),
            (11, False),
            # Add more test cases as needed
        ],
    )
    def test_compete(self, group, other_group, other_size, expected):
        """测试主体之间的竞争"""
        group.size = 10
        other_group.size = other_size
        result = group.compete(other_group)
        assert result == expected
