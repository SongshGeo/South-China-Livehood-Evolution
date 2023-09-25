#!/usr/bin/env python 3.11.0
# -*-coding:utf-8 -*-
# @Author  : Shuang (Twist) Song
# @Contact   : SongshGeo@gmail.com
# GitHub   : https://github.com/SongshGeo
# Website: https://cv.songshgeo.com/

from typing import Tuple

# ===== 所有人都适用的参数 ======
# 单个群体的最小、最大规模
MIN_SIZE = 6
MAX_SIZE = 5024

# ===== 农民的参数 ======
SCALE: Tuple[int, int] = (30, 60)
GROWTH_RATE_FARMER = 0.1  # 0.1~0.25
COMPLEXITY = 1.25  # 复杂化时人口规模上限的增加系数
AFFILIATED = 0.5  # 复杂化时附属农民的人口上限规模

CONVERT_RATE_FARMER = 0.01  # 农民转化成狩猎采集者的概率

# ===== 狩猎采集者的参数 ======
GROWTH_RATE_HUNTER = 0.04
INTENSIFIED = 1.5  # 狩猎采集者相对农民具有优势
# TODO：狩猎采集者的分化系数 SCALE 是多少？
CONVERT_RATE_HUNTER = 0.01  # 狩猎采集者转化成农民的概率

# ===== 交互 =====
LOSS = 0.5  # 竞争失败者的人口损失系数
