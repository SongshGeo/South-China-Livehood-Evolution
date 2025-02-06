#!/usr/bin/env python 3.11.0
# -*-coding:utf-8 -*-
# @Author  : Shuang (Twist) Song
# @Contact   : SongshGeo@gmail.com
# GitHub   : https://github.com/SongshGeo
# Website: https://cv.songshgeo.com/

from unittest.mock import MagicMock

import numpy as np
import pytest
from abses import MainModel, PatchModule

from src.api import CompetingCell, Farmer, Hunter, RiceFarmer, SiteGroup

from .conftest import cfg, set_cell_arable_condition

INTENSITY = cfg.hunter.intensified_coefficient


class TestHunters:
    """用于测试狩猎采集者主体"""

    @pytest.fixture(name="cell")
    def mock_cell(self, layer) -> CompetingCell:
        """狩猎采集者存在的斑块"""
        return layer.array_cells[3][2]

    @pytest.fixture(name="hunter")
    def mock_hunter(self, model, cell: CompetingCell) -> Hunter:
        """一个虚假的狩猎采集者"""
        hunter = model.agents.new(Hunter, size=50, singleton=True)
        hunter.move.to(cell)
        return hunter

    @pytest.fixture(name="other_group")
    def mock_other_group(self, model: MainModel):
        """一个虚假的聚落"""
        module = model.nature.create_module(
            how="from_resolution", shape=(4, 4), cell_cls=CompetingCell, name="test"
        )
        cell = module.array_cells[2][3]
        cell.lim_h = 35
        return cell.agents.new(Hunter)

    def test_hunter_init(self, hunter: Hunter):
        """测试狩猎采集者的初始化"""
        # arrange
        assert hunter.size == 50
        assert hunter.min_size == 6
        assert not hunter.is_complex
        assert hunter.max_size == np.ceil(cfg.sitegroup.max_size) == 31

    @pytest.mark.parametrize(
        "size, expected, settled",
        [
            (20, 20, False),
            (0, None, False),
            (100, 31, False),
            (101, 31, False),
        ],
        ids=["positive_size", "zero_size", "max_size", "large_size"],
    )
    def test_size_property(self, hunter: Hunter, size, expected, settled):
        """测试人口规模有最大最小值限制"""
        # Arrange
        assert hunter.on_earth
        assert hunter.get("lim_h", target="cell") == cfg.sitegroup.max_size

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
    def test_convert_to_farmer(
        self, model, layer, cell, hunter, convert_prob, random_value, changed, arable
    ):
        """测试当小于一定概率时，农民与狩猎采集者可能发生相互转化"""
        # Arrange
        hunter.params.convert_prob.to_farmer = convert_prob
        hunter.params.convert_prob.to_rice = 0
        hunter.random.random = MagicMock(return_value=random_value)

        # 配置，转化需要旁边有农民
        farmer = model.agents.new(Farmer, singleton=True)
        farmer.move.to(layer.array_cells[2][2])
        # 配置是否是可耕地的条件
        set_cell_arable_condition(cell, arable=arable, rice_arable=False)

        size = hunter.size  # 转化之前hunter的人数
        print(size, "origin")

        # Act
        convert = hunter.convert()

        # Assert
        assert isinstance(convert, SiteGroup)
        assert (isinstance(convert, Hunter)) != changed
        assert convert.size == size

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
    def test_convert_to_rice(
        self, model, layer, cell, hunter, convert_prob, random_value, changed, arable
    ):
        """测试当小于一定概率时，农民与狩猎采集者可能发生相互转化"""
        # Arrange
        hunter.params.convert_prob.to_farmer = 0
        hunter.params.convert_prob.to_rice = convert_prob
        hunter.random.random = MagicMock(return_value=random_value)

        # 配置，转化需要旁边有农民
        farmer = model.agents.new(RiceFarmer, singleton=True)
        farmer.move.to(layer.array_cells[2][2])
        # 配置是否是可耕地的条件
        set_cell_arable_condition(cell, arable=True, rice_arable=arable)

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
        [(20, True), (6, True), (131, False), (160, False)],
        ids=["positive_size", "zero_size", "max_size", "large_size"],
    )
    def test_move(self, hunter: Hunter, size, expected_move):
        """测试有移动能力才能移动，在周围随机选取一个格子移动"""
        # Arrange
        setattr(hunter, "_size", size)
        initial_pos = hunter.at.indices

        # Act
        hunter.move_one()

        # assert
        assert (hunter.at.indices != initial_pos) is expected_move

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
        farmer = model.agents.new(Farmer, singleton=True)
        farmer.move.to(layer.array_cells[3][3])
        farmer.size = other_size
        assert hunter.on_earth
        assert farmer.on_earth

        # Act / Assert
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
    def test_compete(self, hunter: Hunter, other_group: Hunter, other_size, expected):
        """测试主体之间的竞争"""
        hunter.size = 10
        other_group.size = other_size
        result = hunter.compete(other_group)
        assert result == expected
