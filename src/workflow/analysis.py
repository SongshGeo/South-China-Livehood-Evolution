#!/usr/bin/env python 3.11.0
# -*-coding:utf-8 -*-
# @Author  : Shuang (Twist) Song
# @Contact   : SongshGeo@gmail.com
# GitHub   : https://github.com/SongshGeo
# Website: https://cv.songshgeo.com/

from typing import List

import matplotlib.pyplot as plt
import pandas as pd
import ruptures as rpt


def detect_breakpoints(
    series: pd.Series, n_bkps: int = 1, algorithm="Dynp", min_size: int = 5
) -> List[int] | int:
    """检查序列数据的变化趋势间断点。

    Parameters:
        series:
            需要判断的时间序列数据，索引是时间，值是判断趋势的值。
        n_bkps:
            预期有多少个间断点，默认为1.
        algorithm:
            依赖于包[ruptures](https://centre-borelli.github.io/ruptures-docs/)进行实现，从以下四种算法中选择一种:
            - "[Dynp](https://centre-borelli.github.io/ruptures-docs/code-reference/detection/dynp-reference/)"
            - "[Binseg](https://centre-borelli.github.io/ruptures-docs/code-reference/detection/binseg-reference/)"
            - "[BottomUp](https://centre-borelli.github.io/ruptures-docs/code-reference/detection/bottomup-reference/)"
            - "[Window](https://centre-borelli.github.io/ruptures-docs/code-reference/detection/window-reference/)"
            默认选用 Dynp。
        min_size:
            切割时间序列后，每一段最小不能少于几个时间单位，默认为5。

    Raises:
        ValueError:
            如果输入了不正确的算法名称。

    Returns:
        识别的断点所在的时间。
    """
    valid_algorithms = ["Dynp", "Binseg", "BottomUp", "Window"]
    if algorithm not in valid_algorithms:
        raise ValueError(
            f"Algorithm should be chosen from {valid_algorithms}, got {algorithm} instead."
        )
    algorithm = getattr(rpt, algorithm, None)
    algo = algorithm(model="l2", min_size=min_size)
    algo.fit(series.values)
    result = algo.predict(n_bkps=n_bkps)
    breakpoints = [series.index[i] for i in result[:-1]]
    if n_bkps == 1:
        return breakpoints[0] if breakpoints else None
    return breakpoints


# 自定义堆积折线图绘制函数
def draw_stacked_lineplot(data, x, y, hue, **kwargs):
    """自定义可输入 seaborn.FaceGrid 的堆积图"""
    # 转换数据为堆叠格式
    pivoted = data.pivot_table(index=x, columns=hue, values=y)
    ratio = pivoted.div(pivoted.sum(axis=1), axis=0)
    # 绘制堆积折线图
    colors = kwargs.get("colors")
    plt.stackplot(ratio.index, ratio.T, colors=colors, labels=ratio.columns)
