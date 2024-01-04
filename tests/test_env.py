#!/usr/bin/env python 3.11.0
# -*-coding:utf-8 -*-
# @Author  : Shuang (Twist) Song
# @Contact   : SongshGeo@gmail.com
# GitHub   : https://github.com/SongshGeo
# Website: https://cv.songshgeo.com/

import os

import pytest
from abses import MainModel
from hydra import compose, initialize

from abses_sce.env import BaseNature, CompetingCell, Env, Farmer, Hunter

# 加载项目层面的配置
with initialize(version_base=None, config_path="../config"):
    cfg = compose(config_name="config")
os.chdir(cfg.root)


class TestCompetingCell:
    """测试每个斑块的计算"""

    @pytest.fixture(name="model")
    def mock_model(self):
        """一个虚假的模型"""
        model = MainModel(parameters=cfg)
        farmer = model.agents.create(Farmer, singleton=True)
        hunter = model.agents.create(Hunter, singleton=True)
        module = model.nature.create_module(
            how="from_resolution", shape=(4, 4), cell_cls=CompetingCell, name="test"
        )
        return model, module, farmer, hunter

    @pytest.fixture(name="cell")
    def mock_cell(self, model):
        """一个虚假的斑块"""
        _, module, _, _ = model
        return module.array_cells[3][3]

    @pytest.fixture(name="farmer")
    def mock_farmer(self, model):
        _, _, farmer, _ = model
        return farmer

    @pytest.fixture(name="hunter")
    def mock_hunter(self, model):
        _, _, _, hunter = model
        return hunter

    @pytest.fixture(name="the_model")
    def the_mocked_model(self, model):
        model, _, _, _ = model
        return model

    # Happy path tests
    def test_is_arable_true(self, cell):
        """
        ID: TC001
        Arrange:
        - Create a CompetingCell instance.
        - Set the slope, aspect, elevation, and is_water properties to valid values.
        Act:
        - Call the is_arable property.
        Assert:
        - Verify that the result is True.
        """
        cell.slope = 5
        cell.aspect = 67
        cell.elevation = 100
        cell.is_water = False

        assert cell.is_arable is True

    def test_is_arable_false_slope(self, cell):
        """
        ID: TC002
        Arrange:
        - Create a CompetingCell instance.
        - Set the slope property to an invalid value.
        Act:
        - Call the is_arable property.
        Assert:
        - Verify that the result is False.
        """
        cell.slope = 15
        cell.aspect = 60
        cell.elevation = 100
        cell.is_water = False

        assert cell.is_arable is False

    def test_is_arable_false_aspect(self, cell):
        """
        ID: TC003
        Arrange:
        - Create a CompetingCell instance.
        - Set the aspect property to an invalid value.
        Act:
        - Call the is_arable property.
        Assert:
        - Verify that the result is False.
        """
        cell.slope = 5
        cell.aspect = 35
        cell.elevation = 100
        cell.is_water = False

        assert cell.is_arable is False

    def test_is_arable_false_elevation(self, cell):
        """
        ID: TC004
        Arrange:
        - Create a CompetingCell instance.
        - Set the elevation property to an invalid value.
        Act:
        - Call the is_arable property.
        Assert:
        - Verify that the result is False.
        """
        cell.slope = 5
        cell.aspect = 60
        cell.elevation = 400
        cell.is_water = False

        assert cell.is_arable is False

    def test_is_arable_false_water(self, cell):
        """
        ID: TC005
        Arrange:
        - Create a CompetingCell instance.
        - Set the is_water property to True.
        Act:
        - Call the is_arable property.
        Assert:
        - Verify that the result is False.
        """
        cell.slope = 5
        cell.aspect = 50
        cell.elevation = 100
        cell.is_water = True

        assert cell.is_arable is False

    def test_able_to_live_hunter(self, cell, hunter):
        """
        ID: TC006
        Arrange:
        - Create a CompetingCell instance.
        - Set the is_water property to False.
        Act:
        - Call the able_to_live method with a Hunter instance.
        Assert:
        - Verify that the result is True.
        """
        cell.is_water = False

        assert cell.able_to_live(hunter) is True

    def test_able_to_live_farmer(self, cell, farmer):
        """
        ID: TC007
        Arrange:
        - Create a CompetingCell instance.
        - Set the is_arable property to True.
        Act:
        - Call the able_to_live method with a Farmer instance.
        Assert:
        - Verify that the result is True.
        """
        cell.slope = 5
        cell.aspect = 50
        cell.elevation = 100
        cell.is_water = False
        assert cell.has_agent() is False
        assert cell.able_to_live(farmer) is True

    # Edge cases

    def test_is_arable_true_edge(self, cell):
        """
        ID: TC008
        Arrange:
        - Create a CompetingCell instance.
        - Set the slope, aspect, elevation, and is_water properties to the minimum valid values.
        Act:
        - Call the is_arable property.
        Assert:
        - Verify that the result is True.
        """
        cell.slope = 0
        cell.aspect = 60
        cell.elevation = 1
        cell.is_water = False

        assert cell.is_arable is True

    def test_is_arable_false_edge(self, cell):
        """
        ID: TC009
        Arrange:
        - Create a CompetingCell instance.
        - Set the slope, aspect, elevation, and is_water properties to the maximum invalid values.
        Act:
        - Call the is_arable property.
        Assert:
        - Verify that the result is False.
        """
        cell.slope = 30
        cell.aspect = 315
        cell.elevation = 300
        cell.is_water = True

        assert cell.is_arable is False

    # Error cases

    def test_convert_farmer(self, cell, farmer, the_model):
        """
        ID: TC011
        Arrange:
        - Create a CompetingCell instance.
        - Create a Farmer instance.
        Act:
        - Call the convert method with the Farmer instance.
        Assert:
        - Verify that a Hunter instance is returned.
        - Verify that the size of the returned instance is the same as the original Farmer instance.
        - Verify that the original Farmer instance is dead.
        - Verify that the returned Hunter instance is on the CompetingCell instance.
        """
        converted = cell.convert(farmer, "Hunter")

        assert isinstance(converted, Hunter)
        assert converted.size == farmer.size
        assert farmer not in the_model.agents
        assert converted.pos == cell.pos

    def test_convert_hunter(self, cell, hunter, the_model):
        """
        ID: TC012
        Arrange:
        - Create a CompetingCell instance.
        - Create a Hunter instance.
        Act:
        - Call the convert method with the Hunter instance.
        Assert:
        - Verify that a Farmer instance is returned.
        - Verify that the size of the returned instance is the same as the original Hunter instance.
        - Verify that the original Hunter instance is dead.
        - Verify that the returned Farmer instance is on the CompetingCell instance.
        """

        converted = cell.convert(hunter, "Farmer")

        assert isinstance(converted, Farmer)
        assert converted.size == hunter.size
        assert hunter not in the_model.agents
        assert converted.pos == cell.pos


class TestEnvironmentSettings:
    """测试环境的初始设置"""

    @pytest.fixture
    def model(self):
        """设置用于测试的环境"""

        class MockNature(BaseNature):
            """模仿自然环境，但设置为简单的环境"""

            def __init__(self, model, name="nature"):
                super().__init__(model, name)
                self.dem = self.create_module(
                    how="from_resolution",
                    shape=(1, 2),
                    cell_cls=CompetingCell,
                )
                self.setup_is_water("right")

            def add_hunters(self, *args, **kwargs):
                """Mock Env add hunters"""
                return getattr(Env, "add_hunters")(self, *args, **kwargs)

            def setup_is_water(self, how: str = "right"):
                """设置测试斑块为水体"""
                if how == "right":
                    self.dem.cells[0][0].is_water = False
                    self.dem.cells[1][0].is_water = True
                elif how == "left":
                    self.dem.cells[0][0].is_water = True
                    self.dem.cells[1][0].is_water = False
                elif how == "all":
                    self.dem.cells[0][0].is_water = False
                    self.dem.cells[1][0].is_water = False

        model = MainModel(parameters=cfg, nature_class=MockNature)
        model.nature.params["init_hunters"] = 0.5
        return model

    def test_setup_is_correct(self, model: MainModel):
        """测试环境的设置如预期"""
        assert model.nature.dem.shape2d == (1, 2)
        is_water = model.nature.dem.get_raster("is_water").reshape((1, 2))
        assert is_water.sum() == 1
        assert (~is_water.astype(bool)).any()

    def test_setup_hunters(self, model: MainModel):
        """测试能设置主体"""
        model.nature.add_hunters(1)
        assert len(model.agents) == 1
        left_cell: CompetingCell = model.nature.dem.cells[0][0]
        assert model.agents.to_list()[0] in left_cell.agents

    def test_random_setup_hunters(self, model: MainModel):
        """测试能否随机设置主体"""
        model.nature.setup_is_water(how="all")
        model.nature.add_hunters(0.6)
        assert len(model.agents) == 1
