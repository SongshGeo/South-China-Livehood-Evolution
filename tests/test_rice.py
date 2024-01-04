#!/usr/bin/env python 3.11.0
# -*-coding:utf-8 -*-
# @Author  : Shuang (Twist) Song
# @Contact   : SongshGeo@gmail.com
# GitHub   : https://github.com/SongshGeo
# Website: https://cv.songshgeo.com/

import pytest
from abses import MainModel

from .conftest import cfg


class TestRiceFarmer:
    """测试种植水稻的农民"""

    @pytest.fixture(name="rice")
    def mock_farmer(self, model: MainModel):
        """返回一个种水稻的农民"""
