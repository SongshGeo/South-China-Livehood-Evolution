#!/usr/bin/env python 3.11.0
# -*-coding:utf-8 -*-
# @Author  : Shuang (Twist) Song
# @Contact   : SongshGeo@gmail.com
# GitHub   : https://github.com/SongshGeo
# Website: https://cv.songshgeo.com/

"""SI-2 的华南遗址 ¹⁴C 数据：读取、按遗址聚合、以及生业类型时间覆盖的面板 builder。

数据源是 ``data/si2_c14_sites.xlsx``，即随稿投出的 SI-2 附表原件，未做任何改动。
本模块是它到图件之间唯一的一层：所有清洗、聚合、分箱都在这里。

遵循 project-to-paper 约定，与 :mod:`src.workflow.figures` 并列：

- 加载器不写死路径，路径由调用方传入 ``Path``。
- 数据函数是公开的（notebook 要直接用），每个都有钉值测试；``_`` 前缀留给纯粹
  内部的渲染细节。注意这与 :mod:`src.workflow.figures` 的用法相反——那边 ``_``
  标的是纯数据 helper。
- ``plot_*`` 渲染函数接受 ``ax=``，供 notebook 拼图。
- 图上文字统一英文，便于英文期刊投稿。

**这份数据是"被测过年代的遗址"的记录，不是人口记录。** 面板 b 的曲线读作
"有多少个遗址的定年区间覆盖了这一段时间"，不能读作那一段时间有多少人。
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib import pyplot as plt
from matplotlib.axes import Axes
from matplotlib.lines import Line2D
from matplotlib.patches import Patch

# ── 常量 ─────────────────────────────────────────────────────────────────
#: SI-2 工作簿里逐条测年记录所在的工作表。
SITES_SHEET = "Sites"

#: 原表列名 → 本模块使用的 snake_case 列名。重命名的比现在读到的多：
#: ``load_c14_dates`` 返回的是一张给人用的 tidy 表，测年材料、实验室方法这些列
#: 留着好名字，下游取用时不必回去查原表的列名。没列在这里的列原样保留，所以
#: 上游加列不会改变下游行为。
COLUMN_RENAME: dict[str, str] = {
    "Site Name": "site",
    "Chinese Name": "site_zh",
    "Category": "category",
    "Province": "province",
    "Longitude (°E)": "lon",
    "Latitude (°N)": "lat",
    "Elevation (m)": "elevation",
    "Dating Material": "material",
    "Lab Code": "lab_code",
    "Technique": "technique",
    "14C age (BP)": "c14_bp",
    "Uncertainty (yr)": "c14_sd",
    "95.4% from (cal BP)": "cal_from",
    "95.4% to (cal BP)": "cal_to",
    "Subsistence": "subsistence_raw",
}

#: 原表 `Subsistence` 列的取值（小写去空格后）→ 图上用的标签。原件里是
#: "Hunting Garthering"（拼写如此）和 "farming"，大小写也不统一；这里统一，但
#: **不改原始文件**——原件是随稿投出的那一份。只登记原件里真实出现过的写法：
#: 若哪天附表订正了拼写，`load_c14_dates` 会当场报错，那正是我们想要的——附表
#: 换了，钉住的数字也该跟着复核，而不是被静默吸收。
SUBSISTENCE_LABELS: dict[str, str] = {
    "hunting garthering": "Foraging",
    "farming": "Farming",
}

#: 生业类型的作图顺序，也是覆盖表里类别的顺序。
SUBSISTENCE_ORDER: list[str] = ["Foraging", "Farming"]

#: 生业类型配色。取自 seaborn ``colorblind``，蓝/橙是对色觉障碍最稳的一对。
SUBSISTENCE_COLORS: dict[str, str] = {
    "Foraging": "#0173B2",
    "Farming": "#DE8F05",
}

#: 正文里"华南各地普遍出现农业证据"的时段，3500–3000 BC，换算成 cal BP。
#: 面板上以竖向色带标出，把图和论点连起来。
SPREAD_WINDOW_BC: tuple[int, int] = (3500, 3000)

#: cal BP 的零点：1950 CE。
BP_ZERO_CE = 1950

#: 横轴统一的轴名（两个面板共用，复合图里只在最下面那个显示）。
AGE_AXIS_LABEL = "Calibrated age (cal BP)"


# ── 年代换算 ─────────────────────────────────────────────────────────────
def bp_to_bce(cal_bp: float | np.ndarray) -> float | np.ndarray:
    """cal BP 转公元前年份（BCE，正数表示公元前）。"""
    return cal_bp - BP_ZERO_CE


def bce_to_bp(cal_bce: float | np.ndarray) -> float | np.ndarray:
    """公元前年份转 cal BP，:func:`bp_to_bce` 的逆。"""
    return cal_bce + BP_ZERO_CE


# ── 数据加载与聚合 ───────────────────────────────────────────────────────
def load_c14_dates(path: Path) -> pd.DataFrame:
    """读取 SI-2 的逐条测年记录，一行一个测年。

    参数:
        path: ``si2_c14_sites.xlsx`` 的路径。

    返回:
        原表所有列都保留，另加 :data:`COLUMN_RENAME` 里重命名后的 snake_case 列，
        以及规范化后的生业标签列 ``subsistence``（``Foraging`` / ``Farming``）。

    Raises:
        ValueError: 出现 :data:`SUBSISTENCE_LABELS` 里没有的生业取值；规范化后的
            标签在 :data:`SUBSISTENCE_ORDER` 或 :data:`SUBSISTENCE_COLORS` 里没有
            对应项；或某条记录的 ``cal_from`` 不早于 ``cal_to``。宁可在入口炸掉，
            也不要静默画出一条反向的线、或让一个类别从覆盖表里悄悄消失。
    """
    df = pd.read_excel(path, sheet_name=SITES_SHEET)
    df = df.rename(columns=COLUMN_RENAME)

    key = df["subsistence_raw"].astype(str).str.strip().str.lower()
    unknown = sorted(set(key) - set(SUBSISTENCE_LABELS))
    if unknown:
        raise ValueError(f"Unmapped subsistence values in {path.name}: {unknown}")
    df["subsistence"] = key.map(SUBSISTENCE_LABELS)

    # 三个生业常量必须覆盖同一批标签：漏了顺序表，这个类别会从
    # `subsistence_coverage` 里静默消失；漏了配色表，要到画图时才炸。
    labels = set(df["subsistence"])
    for name, known in (
        ("SUBSISTENCE_ORDER", set(SUBSISTENCE_ORDER)),
        ("SUBSISTENCE_COLORS", set(SUBSISTENCE_COLORS)),
    ):
        if missing := sorted(labels - known):
            raise ValueError(f"Subsistence labels missing from {name}: {missing}")

    bad = df["cal_from"] <= df["cal_to"]
    if bad.any():
        raise ValueError(
            f"{int(bad.sum())} row(s) in {path.name} have cal_from <= cal_to; "
            "'from' must be the older bound of the 95.4% interval."
        )
    return df


def aggregate_sites(dates: pd.DataFrame) -> pd.DataFrame:
    """把逐条测年聚成一行一个遗址。

    参数:
        dates: :func:`load_c14_dates` 的结果。

    返回:
        每个遗址一行，按 ``cal_mid`` 由老到新排序（最老的在最前），列包括
        ``n_dates``、``cal_from``（该遗址最老区间的上界）、``cal_to``（最新区间的
        下界）、``cal_mid``，以及生业、省份、经纬度等随遗址不变的属性。

    Raises:
        ValueError: 同一个遗址出现多于一个生业标签。原始数据里是一遗址一标签，
            若上游改成分层标注，这里的聚合口径就不再成立，必须先改这里。
    """
    per_site_subsistence = dates.groupby("site")["subsistence"].nunique()
    mixed = sorted(per_site_subsistence[per_site_subsistence > 1].index)
    if mixed:
        raise ValueError(
            f"Sites carrying more than one subsistence label: {mixed}. "
            "aggregate_sites() assumes one label per site."
        )

    grouped = dates.groupby("site", as_index=False).agg(
        site_zh=("site_zh", "first"),
        subsistence=("subsistence", "first"),
        province=("province", "first"),
        category=("category", "first"),
        lon=("lon", "first"),
        lat=("lat", "first"),
        elevation=("elevation", "first"),
        n_dates=("lab_code", "size"),
        cal_from=("cal_from", "max"),
        cal_to=("cal_to", "min"),
    )
    grouped["cal_mid"] = (grouped["cal_from"] + grouped["cal_to"]) / 2
    return grouped.sort_values("cal_mid", ascending=False, ignore_index=True)


def subsistence_coverage(dates: pd.DataFrame, bin_width: int = 50) -> pd.DataFrame:
    """每个时间箱里，各生业类型有多少个**不同遗址**的定年区间覆盖到它。

    统计的是逐条 95.4% 区间的并集，不是遗址首末年代之间的连线：Liyuzui 的两个
    测年隔了两千多年，按连线算会凭空造出一段没有证据的占用。

    参数:
        dates: :func:`load_c14_dates` 的结果。
        bin_width: 时间箱宽度（年），默认 50。注意窄于箱宽的定年区间可能整条落在
            两个箱中点之间而不被计入；随稿这份数据最窄的区间是 68 年，
            ``tests/test_c14.py`` 钉住了"每个遗址至少落进一个箱"这个前提。

    返回:
        长表，列为 ``cal_bp``（箱中点）、``subsistence``、``n_sites``。
        每个箱 × 每个生业类型都有一行，没有覆盖的地方是 0 而不是缺行，
        这样画出来的阶梯不会跳过空档。
    """
    if bin_width <= 0:
        raise ValueError(f"bin_width must be positive, got {bin_width}")

    lo = np.floor(dates["cal_to"].min() / bin_width) * bin_width
    hi = np.ceil(dates["cal_from"].max() / bin_width) * bin_width
    centres = np.arange(lo + bin_width / 2, hi, bin_width)

    # 一次广播出"每条测年 × 每个箱中点"的覆盖矩阵，再两级聚合：先按遗址取 any
    # （同一遗址的多条测年只算一次），再按生业求和。
    covers = (dates["cal_to"].to_numpy()[:, None] <= centres) & (
        dates["cal_from"].to_numpy()[:, None] >= centres
    )
    per_date = pd.DataFrame(covers, index=dates.index, columns=centres)
    per_site = per_date.groupby([dates["subsistence"], dates["site"]]).any()
    wide = per_site.groupby(level=0).sum().reindex(SUBSISTENCE_ORDER, fill_value=0)

    long = (
        wide.rename_axis("subsistence")
        .rename_axis("cal_bp", axis="columns")
        .stack()
        .rename("n_sites")
        .reset_index()
    )
    return long[["cal_bp", "subsistence", "n_sites"]]


def overlap_window(coverage: pd.DataFrame) -> tuple[float, float]:
    """两种生业同时有遗址存在的时段，返回 ``(older, younger)``，单位 cal BP。

    参数:
        coverage: :func:`subsistence_coverage` 的结果。

    返回:
        同时满足两类 ``n_sites > 0`` 的箱中点的最老与最新值。两类从未共存时
        返回 ``(nan, nan)``。
    """
    wide = coverage.pivot(index="cal_bp", columns="subsistence", values="n_sites")
    both = wide[(wide[SUBSISTENCE_ORDER] > 0).all(axis=1)]
    if both.empty:
        return (float("nan"), float("nan"))
    return (float(both.index.max()), float(both.index.min()))


def coexistence_fraction(dates: pd.DataFrame, coverage: pd.DataFrame) -> float:
    """两类生业共存的时段占整个记录跨度的比例。

    图注和正文引的就是这个百分比，所以它必须由一个被钉住的函数产出，而不是在
    notebook 里现算一遍、测试里再独立算一遍——那正是 $R^2$ 曾经漂掉的方式。

    参数:
        dates: :func:`load_c14_dates` 的结果。
        coverage: :func:`subsistence_coverage` 的结果。

    返回:
        ``(older - younger) / (最老的 cal_from - 最新的 cal_to)``。两类从未共存时
        返回 0.0。
    """
    older, younger = overlap_window(coverage)
    if not np.isfinite(older):
        return 0.0
    record = dates["cal_from"].max() - dates["cal_to"].min()
    return float((older - younger) / record)


# ── 面板 builder ─────────────────────────────────────────────────────────
def set_age_xlim(ax: Axes, oldest: float, youngest: float, pad: float = 0.02) -> None:
    """把横轴设成"老在左、新在右"，用 ``set_xlim`` 而不是 ``invert_xaxis``。

    复合图里两个面板 ``sharex``，``invert_xaxis`` 会被调用两次而互相抵消；
    直接给定降序的 ``xlim`` 则是幂等的，谁先谁后都一样。

    两个 ``plot_*`` 各自调它，是为了单独使用时也有正确的方向；但它们算出的范围
    并不完全相同（面板 a 用测年端点，面板 b 用箱中点），共享横轴时"谁后画谁说了
    算"。所以复合图应当在拼完之后由 notebook 再调一次，把范围一次性定死。
    """
    margin = (oldest - youngest) * pad
    ax.set_xlim(oldest + margin, youngest - margin)


def add_bce_axis(ax: Axes) -> Axes:
    """在顶部加一条 BCE 副轴，与主轴的 cal BP 刻度一一对应。

    复合图里只给最上面那个面板加，所以由调用方决定加在哪个 ax 上。
    """
    top = ax.secondary_xaxis("top", functions=(bp_to_bce, bce_to_bp))
    top.set_xlabel("Calibrated age (cal BC)")
    return top


def _shade_spread_window(ax: Axes) -> None:
    """标出正文里农业证据普遍出现的 3500–3000 BC 时段。"""
    older, younger = (bce_to_bp(bc) for bc in SPREAD_WINDOW_BC)
    ax.axvspan(older, younger, color="0.85", zorder=0, lw=0)


def _style_age_axis(ax: Axes, oldest: float, youngest: float, grid_axis: str) -> None:
    """两个面板共用的横轴收尾：轴名、方向、网格、去掉上右边框。"""
    ax.set_xlabel(AGE_AXIS_LABEL)
    set_age_xlim(ax, oldest, youngest)
    ax.grid(axis=grid_axis, color="0.9", lw=0.6)
    ax.set_axisbelow(True)
    sns.despine(ax=ax)


def plot_site_timeline(
    dates: pd.DataFrame,
    sites: pd.DataFrame,
    ax: Axes | None = None,
) -> Axes:
    """面板 a：一行一个遗址，画出它每一条测年的 95.4% 区间，按生业着色。

    细虚线是该遗址最老到最新的跨度，粗色段是逐条测年的 95.4% 区间——两者分开画，
    是为了让测年之间的空档看得见，而不是被一条连线抹平。

    参数:
        dates: :func:`load_c14_dates` 的结果。
        sites: :func:`aggregate_sites` 的结果，行序即图上从上到下的顺序。
        ax: 目标 Axes；``None`` 时新建一个。

    返回:
        绘制好的 Axes。
    """
    if ax is None:
        _, ax = plt.subplots(figsize=(9, 8))

    _shade_spread_window(ax)
    positions = {site: i for i, site in enumerate(sites["site"])}

    # 虚线，而且比行网格线深：读者一眼能分清"这是把两条测年连起来的辅助线"和
    # "这一行的网格线"，不会把连线误当成连续占用的证据。
    ax.hlines(
        range(len(sites)),
        sites["cal_to"],
        sites["cal_from"],
        colors="0.55",
        linewidths=0.9,
        linestyles=(0, (2, 2)),
        zorder=1,
    )
    ax.hlines(
        dates["site"].map(positions),
        dates["cal_to"],
        dates["cal_from"],
        colors=dates["subsistence"].map(SUBSISTENCE_COLORS),
        linewidths=3.4,
        zorder=2,
    )

    ax.set_yticks(range(len(sites)))
    ax.set_yticklabels(
        sites["site"]
        + "  ("
        + sites["province"]
        + ", n="
        + sites["n_dates"].astype(str)
        + ")",
        fontsize=8,
    )
    # 顶部空出整整一行：`figures.panel_label` 的白底是半透明的，压在第一行上会把
    # 最老那条测年洗白。留一行的空当，面板字母就有地方放。
    ax.set_ylim(len(sites) - 0.5, -1.5)
    _style_age_axis(ax, dates["cal_from"].max(), dates["cal_to"].min(), grid_axis="x")
    # 行网格线要比连线淡，否则 26 行的网格会盖过它。
    ax.grid(axis="y", color="0.94", lw=0.5)

    counts = sites["subsistence"].value_counts()
    handles = [
        Line2D(
            [],
            [],
            color=SUBSISTENCE_COLORS[label],
            lw=3.4,
            label=f"{label} ({counts.get(label, 0)} sites)",
        )
        for label in SUBSISTENCE_ORDER
    ]
    handles.append(
        Patch(facecolor="0.85", label=f"{SPREAD_WINDOW_BC[0]}–{SPREAD_WINDOW_BC[1]} BC")
    )
    ax.legend(handles=handles, loc="upper right", frameon=False, fontsize=8)
    return ax


def plot_subsistence_coverage(
    coverage: pd.DataFrame,
    ax: Axes | None = None,
    annotate_overlap: bool = True,
    legend: bool = True,
) -> Axes:
    """面板 b：每种生业在各时间箱里有多少个遗址被定年覆盖。

    参数:
        coverage: :func:`subsistence_coverage` 的结果。
        ax: 目标 Axes；``None`` 时新建一个。
        annotate_overlap: 是否标注两类共存的时段跨度。
        legend: 是否画图例。复合图里颜色键由 :func:`plot_site_timeline` 提供，
            这里关掉可以省下一块与面板字母打架的地方。

    返回:
        绘制好的 Axes。
    """
    if ax is None:
        _, ax = plt.subplots(figsize=(9, 3))

    _shade_spread_window(ax)
    for label in SUBSISTENCE_ORDER:
        sub = coverage[coverage["subsistence"] == label].sort_values("cal_bp")
        ax.fill_between(
            sub["cal_bp"],
            sub["n_sites"],
            step="mid",
            color=SUBSISTENCE_COLORS[label],
            alpha=0.35,
            lw=0,
        )
        ax.step(
            sub["cal_bp"],
            sub["n_sites"],
            where="mid",
            color=SUBSISTENCE_COLORS[label],
            lw=1.6,
            label=label,
        )

    ax.set_ylim(0, coverage["n_sites"].max() * 1.45)

    if annotate_overlap:
        older, younger = overlap_window(coverage)
        if np.isfinite(older):
            y = ax.get_ylim()[1] * 0.80
            ax.annotate(
                "",
                xy=(older, y),
                xytext=(younger, y),
                arrowprops={"arrowstyle": "<->", "color": "0.35", "lw": 1.0},
            )
            ax.text(
                (older + younger) / 2,
                y,
                f"both present: {older:.0f}–{younger:.0f} cal BP",
                ha="center",
                va="bottom",
                fontsize=8,
                color="0.25",
            )

    ax.set_ylabel("Dated sites")
    _style_age_axis(
        ax, coverage["cal_bp"].max(), coverage["cal_bp"].min(), grid_axis="y"
    )
    if legend:
        ax.legend(loc="upper left", frameon=False, fontsize=8)
    return ax
