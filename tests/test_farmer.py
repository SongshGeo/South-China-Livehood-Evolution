#!/usr/bin/env python 3.11.0
# -*-coding:utf-8 -*-
# @Author  : Shuang (Twist) Song
# @Contact   : SongshGeo@gmail.com
# GitHub   : https://github.com/SongshGeo
# Website: https://cv.songshgeo.com/

from unittest.mock import MagicMock

import pytest
from abses import MainModel, PatchModule

from src.api import CompetingCell, Farmer, Hunter, RiceFarmer

from .conftest import cfg, set_cell_arable_condition


class TestFarmer:
    """用于测试的农民主体"""

    @pytest.fixture(name="cell")
    def mock_cell(self, layer: PatchModule) -> CompetingCell:
        """用于测试的，农民应该站在的地方"""
        return layer.array_cells[2, 2]

    @pytest.fixture(name="farmer")
    def mock_farmer(self, model: MainModel, cell: CompetingCell) -> Farmer:
        """一个虚假的农民"""
        farmer = model.agents.new(Farmer, singleton=True)
        farmer.move.to(cell)
        return farmer

    def test_init(self, farmer: Farmer):
        """测试初始化"""
        # Arrange
        assert farmer.growth_rate == cfg.Farmer.growth_rate
        assert farmer.area == cfg.Farmer.area

        # Act
        farmer.area = 2  # 2km

        # Assert
        assert farmer.min_size == 6
        assert farmer.max_size == 3142
        assert farmer.size == 6
        assert farmer.on_earth

    @pytest.mark.parametrize(
        "growth_rate, expected",
        [(-0.1, 0.0), (0.1, 0.1), (1.0, 1.0)],
        ids=["负增长", "正常增长", "快速增长"],
    )
    def test_set_growth_rate(self, farmer: Farmer, growth_rate, expected):
        """测试人口增长率是否合规"""
        # Arrange / act
        farmer.growth_rate = growth_rate

        # Assert
        assert farmer.growth_rate == expected

    @pytest.mark.parametrize(
        "area, change, expected",
        [(4, -0.1, 4.0), (4, 0.1, 4.1), (4, 1.0, 5.0)],
        ids=["负增长", "正常增长", "快速增长"],
    )
    def test_set_area(self, farmer: Farmer, area, change, expected):
        """测试人口增长率是否合规"""
        # Arrange
        farmer.area = area

        # Act
        farmer.area += change

        # Assert
        assert farmer.area == expected

    @pytest.mark.parametrize(
        "size, expected",
        [(5, None), (10, 10), (60, 60), (1_000, 1_000), (100_000, 3142)],
    )
    def test_set_size(self, farmer: Farmer, size, expected):
        """测试当设置主体大小"""
        farmer.size = size
        if expected is None:
            assert not farmer.on_earth
        else:
            assert farmer.size == expected

    @pytest.mark.parametrize(
        "size, diffuse_prob, group_size, expected",
        [
            (100, 0.01, 110, False),
            (10, 0.1, 30, False),
            (100, 0.1, 30, False),
            (10, 0.04, 30, False),
            (100, 0.04, 30, True),
        ],
        ids=[
            "force_true",
            "The odds are off. We can't generate a squad",
            "The odds are off. We can't generate a squad",
            "The odds are OK. But not enough size for a squad",
            "A squad, GO!",
        ],
    )
    def test_diffuse(self, farmer, size, diffuse_prob, group_size, expected):
        """测试农民的分散"""
        # Arrange
        farmer.size = size
        assert farmer.size == size
        farmer.random.random = MagicMock(return_value=diffuse_prob)
        assert farmer.params.diffuse_prob == 0.05
        assert farmer.params.new_group_size == [30, 60]
        group_range = [group_size, group_size]

        # Act
        result = farmer.diffuse(group_range=group_range)

        # Assert
        print(getattr(result, "size", None))
        if result != "Died":
            assert isinstance(result, Farmer) is expected

    @pytest.mark.parametrize(
        "growth_rate, area, complexity, expected_growth_rate, expected_area",
        [
            (0.1, 100, 0.1, 0.09, 100 + 2 * (1 - 0.1)),
            (0.2, 200, 0.2, 0.16, 200 + 2 * (1 - 0.2)),
            (0.1, 100, 0.5, 0.05, 100 + 2 * (1 - 0.5)),
            (0.2, 200, 0.5, 0.1, 200 + 2 * (1 - 0.5)),
        ],
        ids=[
            "positive_complexity",
            "positive_complexity",
            "max_complexity",
            "max_complexity",
        ],
    )
    def test_complicate(
        self,
        farmer: Farmer,
        growth_rate,
        area,
        complexity,
        expected_growth_rate,
        expected_area,
    ):
        """测试农民的复杂化"""
        # Arrange
        farmer.growth_rate = growth_rate
        farmer.area = area
        farmer.params.complexity = complexity
        farmer.params.area = 2

        # Act
        farmer.complicate()
        result_growth_rate = farmer.growth_rate
        result_area = farmer.area

        # Assert
        assert round(result_growth_rate, 2) == expected_growth_rate
        assert result_area == expected_area

    @pytest.mark.parametrize(
        "size, no_convert, expected_converted",
        [
            (99, 100, True),
            (100, 100, True),
            (101, 100, False),
        ],
    )
    def test_convert_to_hunter(
        self, farmer: Farmer, size, expected_converted, no_convert
    ):
        """测试是否存在转化的上限"""
        # arrange
        farmer.size = size
        farmer.params.convert_prob.to_hunter = 1
        farmer.params.convert_prob.to_rice = 0

        # act
        farmer.params.convert_threshold.to_hunter = no_convert
        converted = farmer.convert()

        # assert
        assert isinstance(converted, Hunter) == expected_converted

    @pytest.mark.parametrize(
        "size, threshold, is_rice_arable, expected_converted",
        [
            (199, 200, True, False),
            (200, 200, True, True),
            (201, 200, True, True),
            (199, 200, False, False),
            (200, 200, False, False),
            (201, 200, False, False),
        ],
    )
    def test_convert_to_rice(
        self,
        farmer: Farmer,
        cell: CompetingCell,
        size,
        expected_converted,
        threshold,
        is_rice_arable,
    ):
        """测试农民可以转化成水稻农民"""
        # arrange
        farmer.size = size
        farmer.params.convert_prob.to_hunter = 0
        farmer.params.convert_prob.to_rice = 1
        set_cell_arable_condition(cell, arable=True, rice_arable=is_rice_arable)

        # act
        farmer.params.convert_threshold.to_rice = threshold
        converted = farmer.convert()

        # assert
        assert isinstance(converted, RiceFarmer) == expected_converted

    @pytest.mark.parametrize(
        "prob, return_value, rate, expected",
        [
            (0.1, 0.05, 0.1, 90),
            (0.1, 0.1, 0.1, 100),
            (0.1, 0.05, 0.5, 50),
            (0.1, 0.05, 0.9, 10),
            (0.1, 0.2, 0.1, 100),
        ],
    )
    def test_pop_loss(self, farmer: Farmer, prob, return_value, rate, expected):
        """测试人口损失"""
        # arrange
        farmer.random.random = MagicMock(return_value=return_value)
        farmer.size = 100
        farmer.params.loss.prob = prob
        farmer.params.loss.rate = rate

        # act
        farmer.loss()

        # assert
        assert farmer.size == expected
