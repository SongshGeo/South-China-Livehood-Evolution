#!/usr/bin/env python 3.11.0
# -*-coding:utf-8 -*-
# @Author  : Shuang (Twist) Song
# @Contact   : SongshGeo@gmail.com
# GitHub   : https://github.com/SongshGeo
# Website: https://cv.songshgeo.com/

import pytest
from abses import MainModel, PatchModule

from abses_sce.env import CompetingCell
from abses_sce.rice_farmer import RiceFarmer

from .conftest import cfg, set_cell_arable_condition


class TestRiceFarmer:
    """测试种植水稻的农民"""

    @pytest.fixture(name="cell")
    def mock_cell(self, layer: PatchModule) -> CompetingCell:
        """用于测试的，农民应该站在的地方"""
        return layer.cells[2][2]

    @pytest.fixture(name="rice")
    def mock_rice(self, model: MainModel, cell: CompetingCell):
        """返回一个种水稻的农民"""
        rice = model.agents.new(RiceFarmer, singleton=True)
        rice.move.to(cell)
        return rice

    def test_init(self, rice: RiceFarmer):
        """测试初始化"""
        # Arrange
        assert rice.growth_rate == cfg.farmer.growth_rate
        assert rice.area == cfg.farmer.area

        # Act
        rice.area = 2  # 2km

        # Assert
        assert rice.min_size == 6
        assert rice.max_size == 3142 * 2
        assert rice.size == 6
        assert rice.on_earth

    @pytest.mark.parametrize(
        "size, expected_conversion",
        [
            (10, True),
            (100, True),
            (300, False),
        ],
    )
    def test_convert_to_farmer(self, rice: RiceFarmer, size, expected_conversion):
        """测试会转化成普通农民"""
        # Arrange
        rice.size = size
        rice.params.convert_threshold.to_farmer = 200

        # Act
        agent = rice.convert()

        # Assert
        assert (rice is agent) != expected_conversion
        assert (agent.breed == "Farmer") == expected_conversion

    @pytest.mark.parametrize(
        "arable, rice_arable, expected_live",
        [
            (True, True, True),
            (False, False, False),
        ],
    )
    def test_viable(self, rice: RiceFarmer, layer, arable, rice_arable, expected_live):
        """测试调整斑块属性后，是否能存活"""
        # arrange
        cell: CompetingCell = layer.cells[0][0]
        set_cell_arable_condition(cell, arable=arable, rice_arable=rice_arable)

        # act / assert
        assert cell.is_rice_arable == expected_live
        assert cell.able_to_live(rice) == expected_live
