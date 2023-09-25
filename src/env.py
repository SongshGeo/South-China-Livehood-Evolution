#!/usr/bin/env python 3.11.0
# -*-coding:utf-8 -*-
# @Author  : Shuang (Twist) Song
# @Contact   : SongshGeo@gmail.com
# GitHub   : https://github.com/SongshGeo
# Website: https://cv.songshgeo.com/


class Env:
    """
    环境类
    """

    def __init__(self):
        pass

    def __str__(self):
        pass

    def add_farmers(self):
        """
        添加从北方来的农民，根据全局变量的泊松分布模拟
        """
        farmers = None
        positions = None
        # TODO 农民迁移过来就直接定居吗
        # 根据适合居住的程度来确定概率？ （1）
        # ratio % <- 调参
        return farmers, positions

    def update_climate(self):
        """气候变化"""
        pass

    def update_map(self):
        """海陆变迁"""
        pass
