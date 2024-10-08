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

from src.api.env import BaseNature, CompetingCell, Env, Farmer, Hunter

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
        farmer = model.agents.new(Farmer, singleton=True)
        hunter = model.agents.new(Hunter, singleton=True)
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
        """一个虚假的用于测试的农民"""
        _, _, farmer, _ = model
        return farmer

    @pytest.fixture(name="hunter")
    def mock_hunter(self, model):
        """用于测试的狩猎采集"""
        _, _, _, hunter = model
        return hunter

    @pytest.fixture(name="the_model")
    def the_mocked_model(self, model):
        """用于测试环境的这个模型"""
        model, _, _, _ = model
        return model

    @pytest.mark.parametrize(
        "slope, elevation, is_water, expected",
        [
            (5, 100, False, True),
            (15, 100, False, False),
            (5, 400, False, False),
            (5, 100, True, False),
            (0, 1, False, True),
            (30, 300, True, False),
        ],
        ids=[
            "Arable",
            "False slope",
            "False elevation",
            "False is water",
            "True edge case",
            "False edge case",
        ],
    )
    def test_is_arable(self, cell, slope, elevation, is_water, expected):
        """测试普通的农用地能否耕种"""
        # arrange / act
        cell.slope = slope
        cell.elevation = elevation
        cell.is_water = is_water

        # assert
        assert cell.is_arable == expected

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
        cell.elevation = 100
        cell.is_water = False
        assert not cell.agents.has()
        assert cell.able_to_live(farmer) is True

    def test_able_to_live_when_has_agent(self, cell, farmer, hunter):
        """
        ID: TC008
        Arrange:
        - Create a CompetingCell instance.
        - Set the is_arable property to True.
        - Add a Farmer instance to the agents list.
        Act:
        - Call the able_to_live method with a Farmer instance.
        Assert:
        - Verify that the result is False.
        """
        cell.slope = 5
        cell.elevation = 100
        cell.is_water = False
        cell.agents.add(farmer)
        assert cell.agents.has()
        assert cell.able_to_live(hunter) is True
        assert cell.able_to_live(farmer) is False

    def test_convert_farmer(self, cell, farmer, the_model):
        """测试能够转换农民成为狩猎采集者"""
        # arrange / act
        converted = cell.convert(farmer, "Hunter")

        # assert
        assert isinstance(converted, Hunter)
        assert converted.size == farmer.size
        assert farmer not in the_model.agents
        assert converted.at is cell
        assert converted.source == "Farmer"

    def test_convert_hunter(self, cell, hunter, the_model):
        """测试能够转化狩猎采集者为农民"""
        # arrange / act
        converted = cell.convert(hunter, "Farmer")

        # assert
        assert isinstance(converted, Farmer)
        assert converted.size == hunter.size
        assert hunter not in the_model.agents
        assert converted.at is cell
        assert converted.source == "Hunter"


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
                if how == "all":
                    self.dem.array_cells[0, 0].is_water = False
                    self.dem.array_cells[0, 1].is_water = False

                elif how == "left":
                    self.dem.array_cells[0, 0].is_water = True
                    self.dem.array_cells[0, 1].is_water = False
                elif how == "right":
                    self.dem.array_cells[0, 0].is_water = False
                    self.dem.array_cells[0, 1].is_water = True

        return MainModel(parameters=cfg, nature_class=MockNature)

    def test_setup_is_correct(self, model: MainModel):
        """测试环境的设置如预期"""
        assert model.nature.shape2d == (1, 2)
        is_water = model.nature.get_raster("is_water").reshape((1, 2))
        assert is_water.sum() == 1
        assert (~is_water.astype(bool)).any()

    def test_setup_hunters(self, model: MainModel):
        """测试能设置主体"""
        model.nature.add_hunters(1)  # using 0.5 ratio by default
        assert model.nature.get_xarray("is_water").sum() == 1
        assert len(model.agents) == 1
        left_cell: CompetingCell = model.nature.array_cells[0, 0]
        assert model.agents.item() in left_cell.agents

    def test_random_setup_hunters(self, model: MainModel):
        """测试能否随机设置主体"""
        model.nature.setup_is_water(how="all")
        model.nature.add_hunters(0.6)
        assert len(model.agents) == 1
