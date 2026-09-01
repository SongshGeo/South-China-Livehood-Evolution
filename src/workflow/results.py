#!/usr/bin/env python 3.11.0
# -*-coding:utf-8 -*-
# @Author  : Shuang (Twist) Song
# @Contact   : SongshGeo@gmail.com
# GitHub   : https://github.com/SongshGeo
# Website: https://cv.songshgeo.com/

r"""稿件里每一个「见正文的数」的唯一算法。

投稿定稿之后，图是冻住的，但**图上读出来的数**会以别的方式继续流动：写进正文、
写进图注、写进 ``paper/model-inventory.md``、写进 SI。这些抄写彼此独立，一旦返修
重跑，漏改任何一处都不会报错——只会安静地把一个属于旧数据的数字留在投出去的稿子
里。整理这个仓库时就抓到过一次：``model-inventory.md`` 的「What the re-run changed」
整节标着 rerun_v3，值却全是 rerun_v2 的。

所以每个数只在这里算一次，由 ``paper/build_results.py`` 冻进 ``paper/results.json``
（金标准，随仓库版本管理），再由 :mod:`tests.test_results_regression` 拿真实数据
重算并逐键比对。返修重跑之后测试会直接指出**哪个键、从多少变成了多少**。

三条口径上的硬约束：

1. **终态窗口与图上完全一致**。面板用的是 :func:`src.workflow.figures._tail_mean`
   （``step >= max_step - 50``，含左端点，即末 51 步；见 model-inventory 的 F12），
   这里直接复用同一个函数，而不是另写一遍——另写一遍就是又开一条能各自漂移的路。
2. **先按 run 聚合，再跨 run 求均值**，各 repeat 等权。唯一例外是
   :func:`agri_share_endstate`，它按行汇总，因为图上那条标注线就是这么画的。
3. **数值只在写盘时做有效数字截断**（:func:`round_sig`），本模块内部一律返回全精度。
"""

from __future__ import annotations

import math
from pathlib import Path

import numpy as np
import pandas as pd

from src.workflow import figures as F

#: 终态窗口长度（步）。与面板 builder 共用一个值，改这里等于同时改图和数。
TAIL: int = F.TAIL_STEPS

#: 农业扩张效率的代表指标——Figure 4 三个面板的纵轴都是它。
FARMER_METRIC: str = "num_farmers_n"

#: Figure 5 的响应量：农业总人口 $N^F + N^R$，由 :func:`figures.build_leverage_frame` 造出。
AGRI_METRIC: str = "agri_n"


# ── 数值工具 ─────────────────────────────────────────────────────────────
def round_sig(value: float, digits: int = 6) -> float:
    """截到 ``digits`` 位有效数字。

    金标准存的是截断后的值，比对也在截断后进行。用有效数字而不是小数位，是为了让
    一条 1.4 万人的轨迹和一个 0.18 的比例落在同一个相对容差上：6 位有效数字对应
    约 1e-6 的相对精度，远严于任何有意义的模型变化，又远松于 pandas/NumPy 换版本
    可能带来的末位抖动。

    走 Python 的 ``round``，即银行家舍入（.5 进偶数），不是截断——两个方向都比模型
    变化小若干个数量级，选哪个都不影响判定，但文档要说的是代码真正在做的事。

    参数:
        value: 待处理的数。
        digits: 有效数字位数，默认 6。

    返回:
        舍入后的 float；0 与非有限值原样返回。

    异常:
        ValueError: ``digits`` 小于 1。
    """
    if digits < 1:
        raise ValueError(f"digits must be >= 1, got {digits}")
    v = float(value)
    if v == 0.0 or not math.isfinite(v):
        return v
    return round(v, -int(math.floor(math.log10(abs(v)))) + (digits - 1))


def _by_run(df: pd.DataFrame, group_cols: list[str], metric: str) -> pd.DataFrame:
    """先按 ``group_cols + run_id`` 取终态，再对 ``group_cols`` 跨 repeat 求均值。

    两步而不是一步，是因为各参数组合的 repeat 数不必相同（断点恢复补跑过的组合可能
    多出一次）。一步 groupby 会按行数加权，悄悄让补跑过的组合权重更高。
    """
    tail = F._tail_mean(df, group_cols + ["run_id"], [metric], last=TAIL)
    return tail.groupby(group_cols, as_index=False)[metric].mean()


def _levels(df: pd.DataFrame, level_col: str, metric: str) -> dict[str, float]:
    """按 ``level_col`` 逐档的终态值，键统一转成字符串以便写进 JSON。"""
    tab = _by_run(df, [level_col], metric)
    return {str(k): float(v) for k, v in zip(tab[level_col], tab[metric])}


def spread_ratio(levels: dict[str, float]) -> float:
    """一个因素的效应量：各档终态里最大比最小。

    Figure 4 三个面板就是用这把同一的尺子横向比较三个因素的，所以三者必须共用一个
    定义，不能一个用 max/min、另一个用 max/baseline。

    异常:
        ValueError: 传入空表，或最小档为 0（比值无定义）。
    """
    if not levels:
        raise ValueError("no levels to compare")
    lo, hi = min(levels.values()), max(levels.values())
    if lo == 0:
        raise ValueError("smallest level is zero; the ratio is undefined")
    return hi / lo


# ── Figure 2：被压制的农业传播 ───────────────────────────────────────────
def agri_share_endstate(baseline: pd.DataFrame) -> float:
    r"""终态农业人口占比 $s = (N^F + N^R)/(N^F + N^R + N^H)$。

    按**行**汇总（不先按 run 聚合），因为 notebook 里那条 ``end-state ≈`` 虚线就是
    这么算的；各 repeat 步数相同，两种口径的差别也仅在末位。

    参数:
        baseline: 基准组的长表（:func:`figures.load_single_run` 的结果）。

    返回:
        末 51 步的农业人口占比均值。
    """
    tail = baseline[baseline["step"] >= baseline["step"].max() - TAIL]
    return float(F._agri_share(tail).mean())


# ── Figure 3：转化机制 ───────────────────────────────────────────────────
def conversion_release(base: pd.DataFrame, off: pd.DataFrame) -> dict[str, float]:
    """关掉全部转化路径之后，普通农民终态规模被放开多少倍（Figure 3a）。

    参数:
        base: 基准组长表。
        off: 三条转化路径全关的对照组长表。

    返回:
        ``{"baseline_farmers", "convert_off_farmers", "release_ratio"}``。

    异常:
        ValueError: 基准组终态为 0，倍数无定义。
    """
    b = float(_by_run(base.assign(_k=0), ["_k"], FARMER_METRIC)[FARMER_METRIC].iloc[0])
    o = float(_by_run(off.assign(_k=0), ["_k"], FARMER_METRIC)[FARMER_METRIC].iloc[0])
    if b == 0:
        raise ValueError("baseline end-state is zero; the release ratio is undefined")
    return {
        "baseline_farmers": b,
        "convert_off_farmers": o,
        "release_ratio": o / b,
    }


def fit_log_additive(table: pd.DataFrame) -> dict[str, float]:
    r"""在 log 空间拟合可分离的可加模型 $\log N \approx \alpha(f2h)+\beta(h2f)+\gamma$。

    设计矩阵是两组 one-hot 加一个截距，故意保留冗余列，用最小二乘的最小范数解——
    系数本身不解释，只看拟合优度与残差结构。正文引的 $R^2$ 就是这里的 ``r2``。

    参数:
        table: 终态透视表，行是一个轴、列是另一个轴（:func:`figures._grid_endstate`
            的结果）。全部取值必须为正，否则取不了对数。

    返回:
        ``{"r2", "resid_rms", "resid_min", "resid_max"}``，后三项都在 log 空间。

    异常:
        ValueError: 表里有非正值，或响应面是常数（$R^2$ 无定义）。
    """
    values = table.to_numpy(dtype=float)
    if not np.all(values > 0):
        raise ValueError("the response surface has non-positive cells; cannot take log")

    log = np.log(values)
    n_i, n_j = log.shape
    design = np.zeros((n_i * n_j, n_i + n_j + 1))
    for k, (i, j) in enumerate(np.ndindex(n_i, n_j)):
        design[k, i] = 1.0
        design[k, n_i + j] = 1.0
        design[k, -1] = 1.0

    y = log.reshape(-1)
    ss_tot = float(((y - y.mean()) ** 2).sum())
    if ss_tot == 0:
        raise ValueError("the response surface is constant; R^2 is undefined")

    beta, *_ = np.linalg.lstsq(design, y, rcond=None)
    resid = y - design @ beta
    return {
        "r2": 1.0 - float((resid**2).sum()) / ss_tot,
        "resid_rms": float(np.sqrt((resid**2).mean())),
        "resid_min": float(resid.min()),
        "resid_max": float(resid.max()),
    }


def cliff_drop(broad: pd.DataFrame, knee: float = F.CLIFF_KNEE_F2H) -> dict[str, float]:
    """f2h「悬崖」：在 h2f = 0 那一行上，第一小步吃掉了多少跌幅（Figure 3b）。

    只取 ``h2f`` = 0 的一行，因为正文的说法是「没有补偿通路时，``f2h`` 一小步就吃掉
    绝大部分跌幅」；混进 ``h2f`` > 0 的行会把补偿效应算进来，说的就不是同一件事了。

    参数:
        broad: :func:`figures.load_fine_grid` 读出的广网格长表。
        knee: 悬崖右端的 ``f2h``，默认 :data:`figures.CLIFF_KNEE_F2H`——与面板上
            金色阴影区的右边界同出一处。

    返回:
        ``{"at_zero", "at_knee", "at_widest_f2h", "drop_share_before_knee"}``，前三项
        是终态农民数（``at_widest_f2h`` 是**最大 f2h 那一档的值**，不是最大值），
        最后一项是 ``knee`` 之前吃掉的跌幅占全程跌幅的比例。

    异常:
        ValueError: 网格里没有 ``h2f`` = 0 的行、缺 ``f2h`` = 0 / ``knee`` 这两档，
            或者这一行没有净跌幅（比值无定义）。
    """
    row = broad[np.isclose(broad["h2f"], 0.0)]
    if row.empty:
        raise ValueError("the broad grid has no h2f = 0 row")

    levels = _levels(row, "f2h", FARMER_METRIC)
    by_f2h = {float(k): v for k, v in levels.items()}

    def pick(want: float) -> float:
        """按浮点近似取一档——网格值来自目录名的字符串，不能指望精确相等。"""
        for level, value in by_f2h.items():
            if np.isclose(level, want):
                return value
        raise ValueError(f"the broad grid has no f2h = {want:g} level")

    at_zero, at_knee = pick(0.0), pick(knee)
    at_widest = by_f2h[max(by_f2h)]

    # 全程跌幅是分母。曲线要是不再单调下降（或整行持平），这个差会是 0 或负数，比值
    # 随即变成 inf / 负占比，而它会一路流进 results.json 和正文。兄弟函数
    # spread_ratio / conversion_release 都挡了各自的退化情形，这里也得挡。
    total_drop = at_zero - at_widest
    if total_drop <= 0:
        raise ValueError(
            f"no net drop across f2h on the h2f = 0 row "
            f"(f2h=0 -> {at_zero:g}, f2h={max(by_f2h):g} -> {at_widest:g}); "
            "the cliff share is undefined"
        )

    return {
        "at_zero": at_zero,
        "at_knee": at_knee,
        "at_widest_f2h": at_widest,
        "drop_share_before_knee": (at_zero - at_knee) / total_drop,
    }


# ── Figure 5：水田 vs 旱地的撬动力 ───────────────────────────────────────
def leverage_endstate(lev: pd.DataFrame) -> dict[str, dict[str, float]]:
    """两条 scan 各自「参数倍数 → 终态农业总人口」的曲线（Figure 5b）。

    参数:
        lev: :func:`figures.build_leverage_frame` 的结果。

    返回:
        ``{scan: {倍数: 终态农业总人口}}``。
    """
    tab = _by_run(lev, ["scan", "param_mult"], AGRI_METRIC)
    return {
        str(scan): {
            f"{m:g}x": float(v) for m, v in zip(g["param_mult"], g[AGRI_METRIC])
        }
        for scan, g in tab.groupby("scan")
    }


def replicate_cv(lev: pd.DataFrame) -> float:
    """Figure 5 那十个切片上，终态在 5 次重复之间的变异系数均值。

    这是「加种子 + 共同随机数」买到的精度，正文用它说明重复之间的噪声水平。

    参数:
        lev: :func:`figures.build_leverage_frame` 的结果。

    返回:
        各切片 CV（样本标准差 / 均值）的均值。
    """
    per_run = F._tail_mean(
        lev, ["scan", "param_mult", "run_id"], [AGRI_METRIC], last=TAIL
    )
    cv = per_run.groupby(["scan", "param_mult"])[AGRI_METRIC].agg(
        lambda s: s.std(ddof=1) / s.mean()
    )
    return float(cv.mean())


# ── 汇总 ─────────────────────────────────────────────────────────────────
def compute_results(rerun_root: Path) -> dict:
    """把 Figure 2–5 的全部见刊数字从一批扫描结果里算出来。

    参数:
        rerun_root: 扫描输出根目录，形如 ``out/south_china_evolution/rerun_v3``。

    返回:
        嵌套 dict（未做有效数字截断），结构见 ``paper/results.json``。

    异常:
        FileNotFoundError: 七个数据目录里有任何一个不存在。
    """
    dirs = F.rerun_dirs(rerun_root)

    base = F.load_single_run(dirs["baseline"], "baseline")
    off = F.load_single_run(dirs["convert_off"], "conversion off")
    lam = F.load_trajectories(dirs["lam"])
    limh = F.load_trajectories(dirs["limh"])
    terrain = F.load_terrain(dirs["terrain"])
    broad = F.load_fine_grid(dirs["grid_broad"])
    fine = F.load_fine_grid(dirs["grid_fine"])

    # Figure 4a 只看 lam_ricefarmer 固定在基准 0.1 的那一片，和面板画的一致。
    lam_slice = lam[np.isclose(lam["env.lam_ricefarmer"], F.BASELINE_LAM_RICEFARMER)]

    lam_levels = _levels(lam_slice, "env.lam_farmer", FARMER_METRIC)
    limh_levels = _levels(limh, "env.lim_h", FARMER_METRIC)
    terrain_levels = _levels(terrain, "scenario", FARMER_METRIC)

    lev = F.build_leverage_frame(lam)
    curves = leverage_endstate(lev)
    x5 = {scan: curve["5x"] / curve["1x"] for scan, curve in curves.items()}

    return {
        "figure2": {
            "end_agri_share": agri_share_endstate(base),
        },
        "figure3": {
            **conversion_release(base, off),
            "cliff": cliff_drop(broad),
            "log_additive": fit_log_additive(F._grid_endstate(fine)),
        },
        "figure4": {
            "lam_farmer_levels": lam_levels,
            "lim_h_levels": limh_levels,
            "terrain_levels": terrain_levels,
            "spread_ratio": {
                "lam_farmer": spread_ratio(lam_levels),
                "lim_h": spread_ratio(limh_levels),
                "terrain": spread_ratio(terrain_levels),
            },
        },
        "figure5": {
            "leverage_curves": curves,
            "x5_over_x1": x5,
            "leverage_ratio": x5["lam_ricefarmer"] / x5["lam_farmer"],
            "replicate_cv_mean": replicate_cv(lev),
        },
    }


def round_tree(node, digits: int = 6):
    """递归把嵌套结构里的 float 截到 ``digits`` 位有效数字；int / str 原样保留。"""
    if isinstance(node, dict):
        return {k: round_tree(v, digits) for k, v in node.items()}
    if isinstance(node, list):
        return [round_tree(v, digits) for v in node]
    if isinstance(node, bool) or isinstance(node, int):
        return node
    if isinstance(node, float):
        return round_sig(node, digits)
    return node
