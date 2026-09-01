#!/usr/bin/env python 3.11.0
# -*-coding:utf-8 -*-
# @Author  : Shuang (Twist) Song
# @Contact   : SongshGeo@gmail.com
# GitHub   : https://github.com/SongshGeo
# Website: https://cv.songshgeo.com/

"""稿件主图（Figure 2–5）的核心绘图构件。

本模块承接**扫描级 / 跨 repeat** 的面板 builder，与 :mod:`src.workflow.plot`
（单次 run 的 ``ModelViz``）并列。遵循 project-to-paper 约定：

- 数据加载器把 multirun 目录读成 tidy 长表，不写死路径（路径由调用方传入 ``Path``）。
- 纯数据逻辑用 ``_`` 前缀，单独钉值测试；``plot_*`` 渲染函数接受 ``ax=``，供
  notebook 用 ``add_gridspec`` 拼成复合主图。
- 图上文字统一英文，便于英文期刊投稿。
"""

from __future__ import annotations

import re
from pathlib import Path

import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib import pyplot as plt
from matplotlib.axes import Axes
from matplotlib.colors import LogNorm
from matplotlib.figure import Figure

# ── 常量 ─────────────────────────────────────────────────────────────────
#: 每条 tracking.csv 里参与主图的六个 tracker 指标（人口数 + 群体数）。
METRIC_COLS: list[str] = [
    "num_farmers_n",
    "num_hunters_n",
    "num_rice_n",
    "len_farmers_n",
    "len_hunters_n",
    "len_rice_n",
]

#: 单次 run 输出文件名 ``<run_id>_tracking.csv``。
TRACK_RE = re.compile(r"^(?P<run_id>\d+)_tracking\.csv$")
#: multirun 子目录名 ``<job_id>_<override,override,...>``。
JOB_DIR_RE = re.compile(r"^(?P<job_id>\d+)_(?P<rest>.+)$")
#: 精细网格子目录名 ``idx<n>_f2h<a>_h2f<b>``（SLURM job array 产出）。
FINE_DIR_RE = re.compile(r"^idx(?P<idx>\d+)_f2h(?P<f2h>[\d.]+)_h2f(?P<h2f>[\d.]+)$")

#: 终态窗口长度（步）。``_tail_mean`` 取 ``step >= max_step - TAIL_STEPS``，左端点含在
#: 内，所以实际是末 51 步（model-inventory 的 F12）。图和 :mod:`src.workflow.results`
#: 共用这一个值——两边各写一个 50，就是两条能各自漂移的终态定义。
TAIL_STEPS: int = 50

#: 三类人群的英文图例标签。
GROUP_LABEL: dict[str, str] = {
    "farmers": "Rainfed farmer",
    "hunters": "Hunter-gatherer",
    "rice": "Paddy farmer",
}

#: 地貌均质化四场景（DEM 文件, slope 文件）→ 英文标签。
TERRAIN_LABELS: dict[tuple[str, str], str] = {
    ("ohndem10.tif", "ohnslo10.tif"): "Baseline (real terrain)",
    ("ohndem10.tif", "ohn_value0.tif"): "Homogenized slope",
    ("ohn_value1.tif", "ohnslo10.tif"): "Homogenized DEM",
    ("ohn_value1.tif", "ohn_value0.tif"): "Fully homogenized",
}

#: 一批重跑结果里，主图要读的七个目录（相对扫描根目录）。
#:
#: 目录名由 ``run_slurm_rerun.sh`` 的 override 串派生，这里是**读侧**的唯一一份：
#: ``paper/build_results.py`` 直接经 :func:`rerun_dirs` 取用。出图 notebook 出于「投稿
#: 前不再改动出图代码」的考虑仍写着自己的字面量，改由
#: ``tests/test_manuscript_figures_source.py`` 逐个比对到本表——两边任何一处被改回旧
#: 目录，图照样出、数照样算，只是全都属于旧数据，不会有任何报错。
RERUN_SUBDIRS: dict[str, str] = {
    # Figure 2 / 3a 的基准：f2h 0.1、h2f 0.05、h2r 0.05（convert3 组内第 22 个）。
    "baseline": (
        "convert3/22_Farmer.convert_prob.to_hunter=0.1,"
        "Hunter.convert_prob.to_farmer=0.05,Hunter.convert_prob.to_rice=0.05"
    ),
    # Figure 3a 的对照：三条转化路径全关（组内第 0 个）。
    "convert_off": (
        "convert3/0_Farmer.convert_prob.to_hunter=0.0,"
        "Hunter.convert_prob.to_farmer=0.0,Hunter.convert_prob.to_rice=0.0"
    ),
    "lam": "lam",  # 5×5 移民强度：Figure 4a 与 Figure 5
    "limh": "limh",  # 狩猎采集者承载力三档：Figure 4b
    "terrain": "terrain",  # 地貌均质化 2×2：Figure 4c
    "grid_broad": "grid_broad",  # 6×6，f2h/h2f ∈ [0, 0.10]：Figure 3b
    "grid_fine": "grid_fine",  # 11×11 详查区：Figure 3c
}


def rerun_dirs(root: Path) -> dict[str, Path]:
    """把 :data:`RERUN_SUBDIRS` 接到某个扫描根目录上，并当场检查七个都在。

    早失败是有意的：任一目录缺失时，下游的加载器只会在半程抛一个看不出所以然的
    ``FileNotFoundError``，而缺失最常见的原因是数据还没同步下来。

    参数:
        root: 扫描输出根目录，如 ``out/south_china_evolution/rerun_v3``。

    返回:
        ``{名字: 绝对/相对路径}``，键与 :data:`RERUN_SUBDIRS` 一致。

    异常:
        FileNotFoundError: 任一目录不存在，报文里附上取数与核验命令。
    """
    dirs = {name: Path(root) / sub for name, sub in RERUN_SUBDIRS.items()}
    missing = [f"{name}: {p}" for name, p in dirs.items() if not p.exists()]
    if missing:
        raise FileNotFoundError(
            "扫描结果目录缺失：\n  " + "\n  ".join(missing) + "\n"
            "先把重跑结果同步下来：make fetch-rerun\n"
            "再核对完整性：bash run_slurm_rerun.sh --verify"
        )
    return dirs


# ── 数据加载器 ───────────────────────────────────────────────────────────
def _cast(v: str) -> bool | int | float | str:
    """把 Hydra override 字符串还原成 bool / int / float / str。"""
    vl = v.lower()
    if vl in {"true", "false"}:
        return vl == "true"
    try:
        return int(v) if "." not in v else float(v)
    except ValueError:
        return v


def parse_job_dir(name: str) -> tuple[int, dict]:
    """解析 multirun 子目录名，返回 ``(job_id, overrides)``。

    参数:
        name: 形如 ``12_env.lim_h=15`` 的目录名。

    返回:
        ``(job_id, {override_key: 还原后的值})``。

    异常:
        ValueError: 目录名不符合 ``<job_id>_<rest>`` 格式。
    """
    m = JOB_DIR_RE.match(name)
    if not m:
        raise ValueError(name)
    overrides: dict = {}
    for token in m.group("rest").split(","):
        if "=" in token:
            k, v = token.split("=", 1)
            overrides[k] = _cast(v)
    return int(m.group("job_id")), overrides


def load_trajectories(
    multirun_dir: Path, cols: list[str] | None = None
) -> pd.DataFrame:
    """遍历 multirun 目录，把每次 repeat 的 tracking.csv 拼成长表。

    参数:
        multirun_dir: 含若干 ``<job_id>_<override>/`` 子目录的 Hydra multirun 根目录。
        cols: 需要保留的指标列，默认 :data:`METRIC_COLS`。

    返回:
        长表，列含 ``step``、指标列、``job_id``、``run_id`` 以及各 override 键。
    """
    cols = list(cols) if cols is not None else list(METRIC_COLS)
    frames = []
    for jd in sorted(Path(multirun_dir).iterdir()):
        if not (jd.is_dir() and JOB_DIR_RE.match(jd.name)):
            continue
        job_id, overrides = parse_job_dir(jd.name)
        for tp in sorted(jd.glob("*_tracking.csv")):
            m = TRACK_RE.match(tp.name)
            if not m:
                continue
            usecols = {"step", *cols}
            t = pd.read_csv(tp, usecols=lambda c: c in usecols)
            t["job_id"] = job_id
            t["run_id"] = int(m.group("run_id"))
            for k, v in overrides.items():
                t[k] = v
            frames.append(t)
    if not frames:
        raise FileNotFoundError(f"no <job>/<run>_tracking.csv under {multirun_dir}")
    return pd.concat(frames, ignore_index=True)


def load_single_run(
    dir_: Path, label: str, cols: list[str] | None = None
) -> pd.DataFrame:
    """加载一个直接含 ``<run_id>_tracking.csv`` 的目录（单参数组的多次 repeat）。

    参数:
        dir_: 直接含 tracking.csv 的目录。
        label: 写入 ``scenario`` 列的场景名（英文）。
        cols: 需要保留的指标列，默认 :data:`METRIC_COLS`。

    返回:
        长表，列含 ``step``、指标列、``run_id``、``scenario``。
    """
    cols = list(cols) if cols is not None else list(METRIC_COLS)
    frames = []
    for f in sorted(Path(dir_).glob("*_tracking.csv")):
        m = TRACK_RE.match(f.name)
        if not m:
            continue
        usecols = {"step", *cols}
        t = pd.read_csv(f, usecols=lambda c: c in usecols)
        t["run_id"] = int(m.group("run_id"))
        t["scenario"] = label
        frames.append(t)
    if not frames:
        raise FileNotFoundError(f"no <run>_tracking.csv under {dir_}")
    return pd.concat(frames, ignore_index=True)


def load_grid(root: Path, cols: list[str] | None = None) -> pd.DataFrame:
    """加载 convert_prob 3³ 网格，并把三条转化路径重命名为 ``f2h/h2f/h2r``。

    参数:
        root: 3³ 网格的 multirun 根目录。
        cols: 需要保留的指标列，默认 :data:`METRIC_COLS`。

    返回:
        :func:`load_trajectories` 的结果，转化路径列名已简化。
    """
    df = load_trajectories(root, cols)
    return df.rename(
        columns={
            "Farmer.convert_prob.to_hunter": "f2h",
            "Hunter.convert_prob.to_farmer": "h2f",
            "Hunter.convert_prob.to_rice": "h2r",
        }
    )


def load_fine_grid(root: Path, cols: list[str] | None = None) -> pd.DataFrame:
    """加载 ``idx<n>_f2h<a>_h2f<b>/`` 精细网格（SLURM job array 产出）。

    重跑后的 ``rerun_v2/grid_broad``（6×6）与 ``rerun_v2/grid_fine``（11×11），
    以及修复前的 ``grid_f2h_h2f_v1`` / ``grid_2d_fine_v1`` / ``grid_h2f_fine_v1``，
    命名格式一致，都能用这个函数加载。

    参数:
        root: 含 ``idx..._f2h..._h2f...`` 子目录的网格根目录。
        cols: 需要保留的指标列，默认 :data:`METRIC_COLS`。

    返回:
        长表，列含 ``step``、指标列、``run_id``、``f2h``、``h2f``、``idx``。
    """
    cols = list(cols) if cols is not None else list(METRIC_COLS)
    frames = []
    for jd in sorted(Path(root).iterdir()):
        m = FINE_DIR_RE.match(jd.name)
        if not m:
            continue
        f2h, h2f, idx = float(m["f2h"]), float(m["h2f"]), int(m["idx"])
        for tp in sorted(jd.glob("*_tracking.csv")):
            mm = TRACK_RE.match(tp.name)
            if not mm:
                continue
            usecols = {"step", *cols}
            t = pd.read_csv(tp, usecols=lambda c: c in usecols)
            t["run_id"] = int(mm.group("run_id"))
            t["f2h"] = f2h
            t["h2f"] = h2f
            t["idx"] = idx
            frames.append(t)
    if not frames:
        raise FileNotFoundError(f"no idx*_f2h*_h2f*/<run>_tracking.csv under {root}")
    return pd.concat(frames, ignore_index=True)


def load_terrain(root: Path, cols: list[str] | None = None) -> pd.DataFrame:
    """加载地貌均质化 2×2 实验，按 (DEM, slope) 打英文 ``scenario`` 标签。

    Hydra override 值里的 ``/`` 被当成路径分隔符，故 combo 目录是两层嵌套：
    ``<N>_ds.dem=data/<dem>.tif,ds.slope=data/<slope>.tif/<run>_tracking.csv``。

    参数:
        root: 地貌实验 multirun 根目录。
        cols: 需要保留的指标列，默认 :data:`METRIC_COLS`。

    返回:
        长表，列含 ``step``、指标列、``run_id``、``scenario``。
    """
    cols = list(cols) if cols is not None else list(METRIC_COLS)
    frames = []
    for f in sorted(Path(root).rglob("*_tracking.csv")):
        m = TRACK_RE.match(f.name)
        if not m:
            continue
        slope_dir = f.parent.name  # e.g. 'ohnslo10.tif'
        dem_file = f.parents[1].name.split(",")[0]  # e.g. 'ohndem10.tif'
        label = TERRAIN_LABELS.get((dem_file, slope_dir))
        if label is None:
            continue
        usecols = {"step", *cols}
        t = pd.read_csv(f, usecols=lambda c: c in usecols)
        t["run_id"] = int(m.group("run_id"))
        t["scenario"] = label
        frames.append(t)
    if not frames:
        raise FileNotFoundError(f"no terrain tracking.csv under {root}")
    return pd.concat(frames, ignore_index=True)


# ── 纯数据逻辑（单独钉值测试） ───────────────────────────────────────────
def _agri_share(df: pd.DataFrame) -> pd.Series:
    r"""逐行农业人口占总人口比例 $\frac{f+r}{f+h+r}$（f/h/r = 农民/狩猎者/水田人口数）。"""
    total = df["num_farmers_n"] + df["num_hunters_n"] + df["num_rice_n"]
    return (df["num_farmers_n"] + df["num_rice_n"]) / total


def _tail_mean(
    df: pd.DataFrame,
    group_cols: list[str],
    value_cols: list[str],
    last: int = TAIL_STEPS,
) -> pd.DataFrame:
    """取每条轨迹最后 ``last`` 步的均值作为终态，按 ``group_cols`` 聚合。

    参数:
        df: 含 ``step`` 的长表。
        group_cols: 聚合分组键（如 ``["scenario", "run_id"]``）。
        value_cols: 求均值的指标列。
        last: 末尾窗口长度（步），默认 :data:`TAIL_STEPS`。

    返回:
        分组终态均值表（``as_index=False``）。
    """
    tail = df[df["step"] >= df["step"].max() - last]
    return tail.groupby(group_cols, as_index=False)[value_cols].mean()


def _convert_heatmap_table(
    grid_df: pd.DataFrame,
    metric: str = "num_farmers_n",
    h2r: float = 0.05,
    last: int = TAIL_STEPS,
) -> pd.DataFrame:
    """把 3³ 网格在固定 ``h2r`` 切片上聚成 ``f2h × h2f`` 的终态透视表。

    参数:
        grid_df: :func:`load_grid` 的结果（含 ``f2h/h2f/h2r``）。
        metric: 终态指标列，默认 ``num_farmers_n``。
        h2r: 固定的 hunter→rice 概率切片，默认基准值 0.05。
        last: 终态窗口长度，默认 :data:`TAIL_STEPS`。

    返回:
        行索引 ``f2h``（高在上）、列 ``h2f``（低在左）的透视表。
    """
    tail = _tail_mean(grid_df, ["f2h", "h2f", "h2r", "run_id"], [metric], last)
    sub = tail[np.isclose(tail["h2r"], h2r)]
    combo = sub.groupby(["f2h", "h2f"], as_index=False)[metric].mean()
    return (
        combo.pivot(index="f2h", columns="h2f", values=metric)
        .sort_index(ascending=False)
        .sort_index(axis=1)
    )


def _grid_endstate(
    df: pd.DataFrame,
    index_col: str = "f2h",
    col_col: str = "h2f",
    metric: str = "num_farmers_n",
    last: int = TAIL_STEPS,
) -> pd.DataFrame:
    """把网格聚成 ``index_col × col_col`` 的终态透视表（行索引降序）。

    参数:
        df: 含 ``step``、``run_id`` 与两个网格轴列的长表。
        index_col: 行轴列名，默认 ``f2h``。
        col_col: 列轴列名，默认 ``h2f``。
        metric: 终态指标列，默认 ``num_farmers_n``。
        last: 终态窗口长度，默认 :data:`TAIL_STEPS`。

    返回:
        行 ``index_col``（高在上）、列 ``col_col``（低在左）的透视表。
    """
    tail = _tail_mean(df, [index_col, col_col, "run_id"], [metric], last)
    combo = tail.groupby([index_col, col_col], as_index=False)[metric].mean()
    return (
        combo.pivot(index=index_col, columns=col_col, values=metric)
        .sort_index(ascending=False)
        .sort_index(axis=1)
    )


def build_leverage_frame(
    traj: pd.DataFrame, base_farmer: float = 2.0, base_rice: float = 0.1
) -> pd.DataFrame:
    r"""从 ``lam_farmer × lam_ricefarmer`` 网格切出两条撬动曲线（Figure 5）。

    定义农业总人口 $agri\_n = f + r$，切两片再归一化到"相对基准的倍数"
    $param\_mult = value / baseline$：

    - ``scan='lam_farmer'``：固定 ``lam_ricefarmer=base_rice``，扫 ``lam_farmer``；
    - ``scan='lam_ricefarmer'``：固定 ``lam_farmer=base_farmer``，扫 ``lam_ricefarmer``。

    参数:
        traj: :func:`load_trajectories`（含 ``env.lam_farmer/env.lam_ricefarmer``）。
        base_farmer: ``lam_farmer`` 基准值，默认 2。
        base_rice: ``lam_ricefarmer`` 基准值，默认 0.1。

    返回:
        两片拼接的长表，新增 ``agri_n / len_agri_n / scan / param_value / param_mult``。
    """
    d = traj.copy()
    d["agri_n"] = d["num_farmers_n"] + d["num_rice_n"]
    d["len_agri_n"] = d["len_farmers_n"] + d["len_rice_n"]

    slice_a = d[np.isclose(d["env.lam_ricefarmer"], base_rice)].assign(
        scan="lam_farmer"
    )
    slice_b = d[d["env.lam_farmer"] == base_farmer].assign(scan="lam_ricefarmer")
    slice_a["param_value"] = slice_a["env.lam_farmer"].astype(float)
    slice_a["param_mult"] = slice_a["param_value"] / base_farmer
    slice_b["param_value"] = slice_b["env.lam_ricefarmer"].astype(float)
    slice_b["param_mult"] = slice_b["param_value"] / base_rice

    out = pd.concat([slice_a, slice_b], ignore_index=True)
    out["param_mult"] = out["param_mult"].round(2)
    return out


# ── 导出 ─────────────────────────────────────────────────────────────────
def save_figure(fig: Figure, name: str, out_dir: Path, dpi: int = 300) -> Path:
    """主图存 ``<out_dir>/<name>.png`` + 同名 ``.pdf`` 矢量孪生。

    「PNG 加同名 PDF」不是排版偏好，是构建约定：``make sync-vault`` 要求每张图两
    个扩展名都在，缺一个就整体中止。所以这条策略必须只有一份，而不是在每个
    notebook 里各抄一遍——抄两份就等于两份可以各自漂移的构建契约。

    参数:
        fig: 要保存的 Figure。
        name: 不带扩展名的文件名（如 ``"figure2_baseline_suppression"``）。
        out_dir: 输出目录，通常是 ``reports/``。
        dpi: PNG 的分辨率，默认 300。PDF 是矢量的，不受影响。

    返回:
        写出的 PNG 路径。
    """
    png = Path(out_dir) / f"{name}.png"
    fig.savefig(png, dpi=dpi, bbox_inches="tight")
    fig.savefig(png.with_suffix(".pdf"), bbox_inches="tight")
    print(f"saved: {png}  (+ .pdf)")
    return png


# ── 面板 builder（接受 ax=，渲染，返回 Axes） ───────────────────────────
def panel_label(ax: Axes, letter: str, x: float = 0.02, y: float = 0.98) -> Axes:
    """在子图左上角手工标注面板字母（``a. b. c.``）。

    垫一层半透明白底，保证在深色热图或图例上也清晰可读。
    """
    ax.text(
        x,
        y,
        f"{letter}.",
        transform=ax.transAxes,
        weight="bold",
        va="top",
        ha="left",
        bbox=dict(facecolor="white", alpha=0.6, edgecolor="none", pad=1.5),
    )
    return ax


def plot_agri_share(df: pd.DataFrame, ax: Axes | None = None) -> Axes:
    """Figure 2：农业人口占总人口比例随时间的均值 ± 95% CI。

    参数:
        df: 单一场景多 repeat 的长表（含 ``step`` 与三类 ``*_n`` 指标、``run_id``）。
        ax: 目标 Axes，None 时自建。

    返回:
        绘好的 Axes。占比长期低位即"狩猎者持续压制农业传播"的视觉证据。
    """
    if ax is None:
        _, ax = plt.subplots()
    d = df.copy()
    d["agri_share"] = _agri_share(d)
    sns.lineplot(
        data=d,
        x="step",
        y="agri_share",
        estimator="mean",
        errorbar=("ci", 95),
        color="#2a7f62",
        linewidth=2.0,
        ax=ax,
    )
    ax.set_xlabel("Time step")
    ax.set_ylabel("Agricultural share of total population")
    ax.set_ylim(0, None)
    return ax


def plot_convert_off_vs_on(
    df: pd.DataFrame, ax: Axes | None = None, metric: str = "num_farmers_n"
) -> Axes:
    """Figure 3a：基准 vs 关闭转化 两场景下农民规模的时间演化。

    参数:
        df: 含 ``scenario`` 列的两场景长表（``load_single_run`` 拼出）。
        ax: 目标 Axes，None 时自建。
        metric: 纵轴指标，默认 ``num_farmers_n``。

    返回:
        绘好的 Axes；灰=基准，红=关闭转化。
    """
    if ax is None:
        _, ax = plt.subplots()
    scenarios = list(pd.unique(df["scenario"]))
    palette = {scenarios[0]: "#555555"}
    if len(scenarios) > 1:
        palette[scenarios[1]] = "#d94f4f"
    sns.lineplot(
        data=df,
        x="step",
        y=metric,
        hue="scenario",
        palette=palette,
        estimator="mean",
        errorbar=("ci", 95),
        linewidth=2.2,
        ax=ax,
    )
    ax.set_xlabel("Time step")
    ax.set_ylabel("Rainfed farmer population")
    ax.legend(title="", frameon=False, fontsize=8, loc="upper left")
    return ax


def plot_convert_heatmap(
    grid_df: pd.DataFrame,
    ax: Axes | None = None,
    metric: str = "num_farmers_n",
    h2r: float = 0.05,
) -> Axes:
    """Figure 3b：终态农民规模在 ``f2h × h2f`` 平面上的热图（固定 ``h2r`` 切片）。

    参数:
        grid_df: :func:`load_grid` 的结果。
        ax: 目标 Axes，None 时自建。
        metric: 终态指标，默认 ``num_farmers_n``。
        h2r: 固定的 hunter→rice 概率切片，默认 0.05。

    返回:
        绘好的 Axes。
    """
    if ax is None:
        _, ax = plt.subplots()
    table = _convert_heatmap_table(grid_df, metric=metric, h2r=h2r)
    sns.heatmap(
        table,
        annot=True,
        fmt=".2g",
        cmap="viridis",
        cbar_kws={"label": "Rainfed farmer population (end state)"},
        ax=ax,
    )
    ax.set_xlabel("Hunter → farmer prob. (h2f)")
    ax.set_ylabel("Farmer → hunter prob. (f2h)")
    return ax


def plot_f2h_cliff(
    df: pd.DataFrame,
    ax: Axes | None = None,
    metric: str = "num_farmers_n",
    shade: tuple[float, float] | None = (0.0, 0.02),
    last: int = TAIL_STEPS,
) -> Axes:
    """Figure 3b：终态农民规模随 ``f2h`` 的"悬崖"曲线（每条线一个 ``h2f`` 切片）。

    纵轴 log 化后可见：``f2h`` 从 0 迈到 ~0.02 一步就吃掉绝大部分跌幅——
    farmer→hunter 退化路径是压制农业扩散的主导机制。

    参数:
        df: :func:`load_fine_grid` 的结果（含 ``f2h/h2f``）。
        ax: 目标 Axes，None 时自建。
        metric: 终态指标，默认 ``num_farmers_n``。
        shade: 高亮的详查区间 ``(x0, x1)``，None 不画。
        last: 终态窗口长度，默认 :data:`TAIL_STEPS`。

    返回:
        绘好的 Axes（log 纵轴）。
    """
    if ax is None:
        _, ax = plt.subplots()
    tail = _tail_mean(df, ["f2h", "h2f", "run_id"], [metric], last)
    combo = tail.groupby(["f2h", "h2f"], as_index=False)[metric].mean()
    h2f_vals = sorted(combo["h2f"].unique())
    palette = sns.color_palette("viridis", n_colors=len(h2f_vals))
    if shade is not None:
        ax.axvspan(shade[0], shade[1], color="gold", alpha=0.15, zorder=0)
    for color, h in zip(palette, h2f_vals):
        s = combo[combo["h2f"] == h].sort_values("f2h")
        ax.plot(
            s["f2h"], s[metric], marker="o", ms=5, lw=1.8, color=color, label=f"{h:.3g}"
        )
    ax.set_yscale("log")
    ax.set_xlabel("Farmer → hunter prob. (f2h)")
    ax.set_ylabel("Rainfed farmer population (end state)")
    ax.legend(title="h2f", fontsize=7, ncol=2, frameon=False, loc="upper right")
    return ax


def plot_grid_heatmap(
    df: pd.DataFrame,
    ax: Axes | None = None,
    metric: str = "num_farmers_n",
    log: bool = True,
    last: int = TAIL_STEPS,
) -> Axes:
    """Figure 3c：精细 ``f2h × h2f`` 网格上终态农民规模的热图。

    参数:
        df: :func:`load_fine_grid` 的结果。
        ax: 目标 Axes，None 时自建。
        metric: 终态指标，默认 ``num_farmers_n``。
        log: 是否 log 归一化色标（全为正时生效），默认 True。
        last: 终态窗口长度，默认 :data:`TAIL_STEPS`。

    返回:
        绘好的 Axes。
    """
    if ax is None:
        _, ax = plt.subplots()
    table = _grid_endstate(df, "f2h", "h2f", metric, last)
    norm = LogNorm() if (log and (table.to_numpy() > 0).all()) else None
    sns.heatmap(
        table,
        ax=ax,
        cmap="viridis",
        norm=norm,
        cbar_kws={"label": "Rainfed farmer population (end state)"},
    )
    ax.set_xticklabels([f"{c:.3g}" for c in table.columns], rotation=0)
    ax.set_yticklabels([f"{r:.3g}" for r in table.index], rotation=0)
    ax.set_xlabel("Hunter → farmer prob. (h2f)")
    ax.set_ylabel("Farmer → hunter prob. (f2h)")
    return ax


def plot_metric_by_hue(
    df: pd.DataFrame,
    hue: str,
    ax: Axes | None = None,
    metric: str = "num_farmers_n",
    palette: str | dict = "viridis",
    hue_order: list | None = None,
    ylabel: str | None = None,
) -> Axes:
    """通用单指标轨迹面板：按 ``hue`` 分组画 ``metric`` 的均值 ± 95% CI。

    Figure 4 三个因素面板（``lam_farmer`` / ``lim_h`` / 地貌）与 Figure 5a 轨迹共用。

    参数:
        df: 长表。
        hue: 分组列（如 ``env.lam_farmer`` / ``env.lim_h`` / ``scenario``）。
        ax: 目标 Axes，None 时自建。
        metric: 纵轴指标，默认 ``num_farmers_n``。
        palette: seaborn 调色板名或映射。
        hue_order: 图例顺序，None 时由 seaborn 决定。
        ylabel: 纵轴标签，None 时用 ``metric``。

    返回:
        绘好的 Axes。
    """
    if ax is None:
        _, ax = plt.subplots()
    sns.lineplot(
        data=df,
        x="step",
        y=metric,
        hue=hue,
        hue_order=hue_order,
        palette=palette,
        estimator="mean",
        errorbar=("ci", 95),
        ax=ax,
    )
    ax.set_xlabel("Time step")
    ax.set_ylabel(ylabel or metric)
    ax.legend(title=hue, frameon=False, fontsize=8)
    return ax


def plot_leverage_endstate(
    df: pd.DataFrame,
    ax: Axes | None = None,
    metric: str = "agri_n",
    last: int = TAIL_STEPS,
) -> Axes:
    """Figure 5b：终态农业总人口随参数倍数的响应（两条 scan 曲线对比斜率）。

    参数:
        df: :func:`build_leverage_frame` 的结果（含 ``scan/param_mult/agri_n``）。
        ax: 目标 Axes，None 时自建。
        metric: 响应指标，默认 ``agri_n``。
        last: 终态窗口长度，默认 :data:`TAIL_STEPS`。

    返回:
        绘好的 Axes；``lam_ricefarmer`` 斜率应更陡。
    """
    if ax is None:
        _, ax = plt.subplots()
    resp = _tail_mean(df, ["scan", "param_mult", "run_id"], [metric], last)
    sns.pointplot(
        data=resp,
        x="param_mult",
        y=metric,
        hue="scan",
        errorbar=("ci", 95),
        dodge=0.15,
        ax=ax,
    )
    ax.set_xlabel("Parameter ÷ baseline (×1 = baseline)")
    ax.set_ylabel("Total agricultural population (end state)")
    ax.legend(title="Scan", frameon=False)
    return ax
