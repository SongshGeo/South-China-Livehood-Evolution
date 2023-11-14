#!/usr/bin/env python 3.11.0
# -*-coding:utf-8 -*-
# @Author  : Shuang (Twist) Song
# @Contact   : SongshGeo@gmail.com
# GitHub   : https://github.com/SongshGeo
# Website: https://cv.songshgeo.com/


"""测试基本主体类，包括其规模的设置，以及衍生。
"""

from typing import Tuple

import pytest

from src.people import SiteGroup


class TestGroup:
    """测试基本的主体类型"""

    @pytest.fixture(name="people")
    def mock_people(self, model, layer) -> SiteGroup:
        """一个虚假的主体"""
        people: SiteGroup = model.agents.create(SiteGroup, singleton=True)
        cell = layer.array_cells[3][3]
        people.put_on(cell=cell)
        return people

    def test_size_setup(self, people: SiteGroup):
        """测试主体的大小设置"""
        assert people.size == 6
        assert people.min_size == 6
        assert people.max_size == 31

    @pytest.mark.parametrize(
        "growth_rate, years, expected_size",
        [
            (0.0025, 1, 51),  # 50.125 -> 51
            (0.0025, 10, 52),  # 51.26415666138926 -> 52
            (0.0025, 100, 64),  # 64.18124443692305 -> 65 -> max_size(64)
            (0.0, 100, 50),  # 增长100年，但没有增长率
        ],
        ids=["one year", "10 years", "100 years", "No growth"],
    )
    def test_growth(
        self,
        people: SiteGroup,  # 增长的基本人口
        growth_rate,  # 人口增长比率
        years,  # 以该比率进行人口增长的总年份
        expected_size,  # 期望得到的人口数量
    ):
        """测试人口增长"""
        # Arrange
        people.max_size = 64.0
        people.size = 50

        # Act
        for _ in range(years):
            people.population_growth(growth_rate=growth_rate)

        # Assert
        assert people.size == expected_size

    @pytest.mark.parametrize(
        "group_range, initial_size, expected_size, expected_new_size",
        [
            ([15, 15], 20, None, 15),  # 必定选15，原来死掉，新的15
            ([10, 10], 20, 10, 10),  # 必定选10，原来剩10，新的10
            ([200, 300], 20, 20, None),  # 不足以组成一支最小的小队
        ],
        ids=["not_enough_old", "within_range", "above_maximum"],
    )
    def test_diffuse(
        self,
        people: SiteGroup,
        group_range: Tuple[int, int],
        initial_size: int,
        expected_size: int,
        expected_new_size: int,
    ):
        """测试人口分散，随机选择一个最小和最大的规模，分裂出去"""
        # Arrange
        cell = people.model.nature.layer.cells[3][3]
        people.put_on(cell)
        people.size = initial_size
        people.min_size = 6

        # Act
        new_group = people.diffuse(group_range)

        # Assert
        if expected_size is None:
            assert not people.on_earth
        else:
            assert people.size == expected_size
        new_size = getattr(new_group, "size", None)
        assert new_size == expected_new_size
