#!/usr/bin/env python 3.11.0
# -*-coding:utf-8 -*-
# @Author  : Shuang (Twist) Song
# @Contact   : SongshGeo@gmail.com
# GitHub   : https://github.com/SongshGeo
# Website: https://cv.songshgeo.com/

from unittest.mock import MagicMock, patch

import numpy as np
import pytest
from abses import MainModel, PatchModule

from src.env import CompetingCell
from src.farmer import Farmer
from src.hunter import Hunter
from src.people import SiteGroup

from .conftest import cfg

INTENSITY = cfg.hunter.intensified_coefficient


class TestHunters:
    """用于测试狩猎采集者主体"""

    @pytest.fixture(name="hunter")
    def mock_hunter(self, model, layer) -> Hunter:
        """一个虚假的农民"""
        hunter = model.agents.create(Hunter, size=50, singleton=True)
        hunter.put_on(layer.array_cells[3][2])
        return hunter

    @pytest.fixture(name="other_group")
    def mock_other_group(self, model):
        """一个虚假的聚落"""
        agent = model.agents.create(Hunter, size=60, singleton=True)
        module = model.nature.create_module(
            how="from_resolution", shape=(4, 4), cell_cls=CompetingCell, name="test"
        )
        agent.put_on(module.array_cells[3][3])
        return agent

    def test_hunter_init(self, hunter: Hunter, layer):
        """测试狩猎采集者的初始化"""
        # arrange
        assert hunter.size == 50
        assert hunter.min_size == 6
        assert hunter.is_complex
        assert hunter.max_size == np.ceil(cfg.sitegroup.max_size) == 31

        # act
        layer.array_cells[2][2].lim_h = 15

    @pytest.mark.parametrize(
        "size, expected, settled",
        [
            (20, 20, False),
            (0, None, False),
            (31, 31, False),
            (70, 70, True),
        ],
        ids=["positive_size", "zero_size", "max_size", "large_size"],
    )
    def test_size_property(self, hunter: Hunter, size, expected, settled):
        """测试人口规模有最大最小值限制"""
        # Arrange
        assert hunter.on_earth
        assert hunter.loc("lim_h") == cfg.sitegroup.max_size

        # Act
        hunter.size = size
        result = hunter.size

        # Assert
        if expected is None:
            assert not hunter.on_earth
        else:
            assert result == expected
        assert hunter.is_complex == settled

    @pytest.mark.parametrize(
        "growth_rate, initial_size, expected",
        [
            (0.1, 10, 11),
            (0, 6, 6),
            (-0.1, 20, 18),
            (0.5, 10, 15),
        ],
        ids=["positive_growth", "zero_growth", "negative_growth", "large_growth"],
    )
    def test_population_growth(self, hunter, growth_rate, initial_size, expected):
        """测试人口增长"""
        # Arrange
        hunter.size = initial_size
        assert hunter.size == initial_size

        # Act
        hunter.population_growth(growth_rate)

        # Assert
        assert hunter.size == expected

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
    def test_convert(
        self, model, layer, hunter, convert_prob, random_value, changed, arable
    ):
        """测试当小于一定概率时，农民与狩猎采集者可能发生相互转化"""
        # Arrange
        hunter.params.convert_prob = convert_prob
        hunter.random.random = MagicMock(return_value=random_value)
        cell = layer.array_cells[3][2]

        # 配置，转化需要旁边有农民
        farmer = model.agents.create(Farmer, singleton=1)
        farmer.put_on(layer.array_cells[2][2])

        # 配置是否是可耕地的条件
        cell.slope = 5
        cell.aspect = 100
        cell.elevation = 100 if arable else 300

        size = hunter.size  # 转化之前hunter的人数
        print(size, "origin")
        # Act
        convert = hunter.convert()

        # Assert
        assert isinstance(convert, SiteGroup)
        assert (isinstance(convert, Hunter)) != changed
        assert convert.size == size

    @pytest.mark.parametrize(
        "size, expected_move",
        [(20, True), (6, True), (31, True), (60, False)],
        ids=["positive_size", "zero_size", "max_size", "large_size"],
    )
    def test_move(self, hunter, size, expected_move):
        """测试有移动能力才能移动，在周围随机选取一个格子移动"""
        # Arrange
        hunter.size = size
        initial_pos = hunter.pos

        # Act
        hunter.move()

        # assert
        assert (hunter.pos != initial_pos) is expected_move

    @pytest.mark.parametrize(
        "other_size, expected",
        # intensified = 1.5
        [
            (10 * INTENSITY - 1, True),
            (10 * INTENSITY + 1, False),
        ],
        ids=["Hunter success", "Farmer success"],
    )
    def test_compete_with_farmers(
        self, hunter: Hunter, model: MainModel, layer: PatchModule, other_size, expected
    ):
        """测试主体之间的竞争"""
        # arrange
        hunter.size = 10
        farmer = model.agents.create(Farmer, singleton=True)
        farmer.put_on(layer.array_cells[3][3])
        farmer.size = other_size
        assert hunter.on_earth
        assert farmer.on_earth

        # Act
        with patch("src.hunter.Hunter._compete_with_farmer") as mock:
            hunter.compete(farmer)
            assert mock.called

        # Assert
        assert hunter.compete(farmer) == expected

    @pytest.mark.parametrize(
        "other_size, expected",
        # intensified = 1.5
        [
            (9, True),
            (11, False),
            # Add more test cases as needed
        ],
    )
    def test_compete(self, hunter, other_group, other_size, expected):
        """测试主体之间的竞争"""
        hunter.size = 10
        other_group.size = other_size
        result = hunter.compete(other_group)
        assert result == expected
