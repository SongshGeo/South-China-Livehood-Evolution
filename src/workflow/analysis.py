#!/usr/bin/env python 3.11.0
# -*-coding:utf-8 -*-
# @Author  : Shuang (Twist) Song
# @Contact   : SongshGeo@gmail.com
# GitHub   : https://github.com/SongshGeo
# Website: https://cv.songshgeo.com/

from typing import List, Optional, Sequence

import matplotlib.pyplot as plt
import pandas as pd
import ruptures as rpt


# 自定义堆积折线图绘制函数
def draw_stacked_lineplot(data, x, y, hue, **kwargs):
    """自定义可输入 seaborn.FaceGrid 的堆积图"""
    # 转换数据为堆叠格式
    pivoted = data.pivot_table(index=x, columns=hue, values=y)
    ratio = pivoted.div(pivoted.sum(axis=1), axis=0)
    # 绘制堆积折线图
    colors = kwargs.get("colors")
    plt.stackplot(ratio.index, ratio.T, colors=colors, labels=ratio.columns)
