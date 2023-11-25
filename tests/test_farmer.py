#!/usr/bin/env python 3.11.0
# -*-coding:utf-8 -*-
# @Author  : Shuang (Twist) Song
# @Contact   : SongshGeo@gmail.com
# GitHub   : https://github.com/SongshGeo
# Website: https://cv.songshgeo.com/

from unittest.mock import MagicMock

import pytest
from abses import MainModel, PatchModule

from src.farmer import Farmer

from .conftest import cfg


class TestFarmer:
    """用于测试的农民主体"""

    @pytest.fixture(name="farmer")
    def mock_farmer(self, model: MainModel, layer: PatchModule) -> Farmer:
        """一个虚假的农民"""
        farmer = model.agents.create(Farmer, singleton=True)
        farmer.put_on(layer.cells[2][2])
        return farmer

    def test_init(self, farmer: Farmer):
        """测试初始化"""
        # Arrange
        assert farmer.growth_rate == cfg.farmer.growth_rate
        assert farmer.area == cfg.farmer.area

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
