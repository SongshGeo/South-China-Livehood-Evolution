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
from omegaconf import OmegaConf

from src.api.env import BaseNature, CompetingCell, Env, Farmer, Hunter, RiceFarmer

from .conftest import set_cell_arable_condition

# 加载项目层面的配置
with initialize(version_base=None, config_path="../config"):
    cfg = compose(config_name="config")


class TestCompetingCell:
    """测试每个斑块的计算"""

    @pytest.fixture(name="model")
    def mock_model(self):
        """一个虚假的模型"""
        model = MainModel(parameters=cfg)
        farmer = model.agents.new(Farmer, singleton=True)
        hunter = model.agents.new(Hunter, singleton=True)
        module = model.nature.create_module(
            shape=(4, 4), resolution=1, cell_cls=CompetingCell, name="test"
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
        """测试当格子已经有主体时，其他主体不能进入（每格只能有一个主体）

        ID: TC008
        Arrange:
        - Create a CompetingCell instance.
        - Set the is_arable property to True.
        - Add a Farmer instance to the agents list.
        Act:
        - Call the able_to_live method with another agent.
        Assert:
        - Verify that no other agent can enter (result is False).
        - Verify that the same agent can still check its own position (result is True).
        """
        cell.slope = 5
        cell.elevation = 100
        cell.is_water = False
        cell.agents.add(farmer)
        assert cell.agents.has()
        # 其他主体不能进入已有主体的格子
        assert cell.able_to_live(hunter) is False
        # 同一个主体检查自己的位置应该返回 True
        assert cell.able_to_live(farmer) is True

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
                    shape=(1, 2),
                    resolution=1,
                    cell_cls=CompetingCell,
                    major_layer=True,
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
        is_water = model.nature.dem.get_raster("is_water").reshape((1, 2))
        assert is_water.sum() == 1
        assert (~is_water.astype(bool)).any()

    def test_setup_hunters(self, model: MainModel):
        """测试能设置主体"""
        model.nature.add_hunters(1)  # using 0.5 ratio by default
        assert model.nature.dem.get_xarray("is_water").sum() == 1
        assert len(model.agents) == 1
        left_cell: CompetingCell = model.nature.dem.array_cells[0, 0]
        assert model.agents.select().item() in left_cell.agents

    def test_random_setup_hunters(self, model: MainModel):
        """测试能否随机设置主体"""
        model.nature.setup_is_water(how="all")
        model.nature.add_hunters(0.6)
        assert len(model.agents) == 1


class TestGlobalHunterLimit:
    """全局狩猎采集者承载力上限。

    这个上限决定狩猎采集者对空间的占据强度，也就是农业被压制的直接原因，而且是
    Figure 4 的实验因子之一。它曾被包在一个裸 `except Exception` 里，出错就静默改成
    100000——比真实上限（35 × 6835 = 239225）还低一半有余（issue #34）。
    """

    @staticmethod
    def _tiny_env(parameters):
        """一个只有 2×3 个陆地格子的极简环境。

        模块名必须是 `env`，否则 `self.params` 取不到 `cfg.env` 下的参数。
        """

        class TinyEnv(Env):
            """跳过栅格读取，只保留承载力计算这一段。"""

            def setup_dem(self):
                self.dem = self.create_module(
                    shape=(2, 3),
                    resolution=1,
                    cell_cls=CompetingCell,
                    major_layer=True,
                )
                self.calculate_global_hunter_limit()

        # MainModel 构造时就会走 Env.initialize() → setup_dem()，无需再手动调用
        model = MainModel(parameters=parameters, nature_class=TinyEnv)
        return model.nature

    def test_ceiling_is_lim_h_times_land_cells(self):
        """上限就是 lim_h × 陆地格子数，没有别的项。"""
        nature = self._tiny_env(cfg)

        assert nature.global_hunter_limit == cfg.env.lim_h * 6

    def test_missing_lim_h_raises_rather_than_capping_silently(self):
        """回归 #34：取不到 lim_h 必须抛错，不能悄悄换成一个魔数。"""
        without_lim_h = OmegaConf.create(OmegaConf.to_container(cfg, resolve=True))
        del without_lim_h.env.lim_h

        with pytest.raises(KeyError):
            self._tiny_env(without_lim_h)


class TestImmigrantPlacement:
    """移民的落点必须和该品种的生存判据一致。

    水稻可耕地（坡度 ≤ 0.5°）是旱作可耕地（≤ 10°）的真子集。`add_farmers` 曾经无论
    品种一律用 `is_arable` 掩膜，而放置走 `random.new()` 不经过 `able_to_live()`，
    于是水稻移民会被放在本不该生存的格子上，且此后永不被淘汰（issue #29）。
    """

    @staticmethod
    def _mixed_arability_nature():
        """一行 4 格的环境：2 格只满足旱作，2 格同时满足水稻。"""

        class TinyEnv(Env):
            """跳过栅格读取，只保留放置逻辑。"""

            def initialize(self):
                """只建栅格，不放初始狩猎采集者——否则它们会占掉这 4 格里的一部分。"""
                self.setup_dem()

            def setup_dem(self):
                self.dem = self.create_module(
                    shape=(1, 4),
                    resolution=1,
                    cell_cls=CompetingCell,
                    major_layer=True,
                )
                self.calculate_global_hunter_limit()

        # lam 调大，确保被测的这一步一定有移民进入
        parameters = OmegaConf.create(OmegaConf.to_container(cfg, resolve=True))
        parameters.env.lam_farmer = 10
        parameters.env.lam_ricefarmer = 10
        model = MainModel(parameters=parameters, nature_class=TinyEnv)

        # 前两格只能旱作，后两格旱作和水稻都可以
        for index, rice_arable in enumerate((False, False, True, True)):
            set_cell_arable_condition(
                model.nature.dem.array_cells[0, index],
                arable=True,
                rice_arable=rice_arable,
            )
        return model.nature

    def test_vacant_arable_cells_narrows_for_paddy(self):
        """水稻取到的候选格子是旱作候选的真子集。"""
        nature = self._mixed_arability_nature()

        assert len(nature._vacant_arable_cells(Farmer)) == 4
        assert len(nature._vacant_arable_cells(RiceFarmer)) == 2

    @pytest.mark.parametrize(
        "farmer_cls", [Farmer, RiceFarmer], ids=["rainfed", "paddy"]
    )
    def test_immigrants_land_where_they_can_live(self, farmer_cls):
        """回归 #29：每个新落地的移民都必须通过 able_to_live()。"""
        # Arrange
        nature = self._mixed_arability_nature()

        # Act
        placed = nature.add_farmers(farmer_cls)

        # Assert
        assert len(placed) > 0
        assert all(f.at.able_to_live(f) for f in placed)

    def test_paddy_immigrants_never_use_rainfed_only_cells(self):
        """水稻移民不会落在只满足旱作条件的格子上。"""
        nature = self._mixed_arability_nature()

        placed = nature.add_farmers(RiceFarmer)

        assert all(f.at.is_rice_arable for f in placed)
        # 只满足旱作的那两格必须仍然空着
        rainfed_only = [nature.dem.array_cells[0, i] for i in (0, 1)]
        assert all(cell.agents.has() == 0 for cell in rainfed_only)
