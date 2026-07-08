#!/usr/bin/env python 3.11.0
# -*-coding:utf-8 -*-
# @Author  : Shuang (Twist) Song
# @Contact   : SongshGeo@gmail.com
# GitHub   : https://github.com/SongshGeo
# Website: https://cv.songshgeo.com/

"""稿件主图构件 :mod:`src.workflow.figures` 的单测 / 烟测 / 边界测。"""

from __future__ import annotations

from pathlib import Path

import matplotlib
import numpy as np
import pandas as pd
import pytest
from matplotlib import pyplot as plt

from src.workflow import figures as fig

matplotlib.use("Agg")  # 无显示后端，供 CI / headless 跑图
# ── 合成数据工具 ─────────────────────────────────────────────────────────
_METRICS = fig.METRIC_COLS


def _traj(n_steps: int = 10, **fills) -> pd.DataFrame:
    """造一条 tracking 长表：step 0..n-1，指标列用 fills 覆盖（默认 1.0）。"""
    data = {"step": np.arange(n_steps)}
    for col in _METRICS:
        data[col] = np.full(n_steps, fills.get(col, 1.0), dtype=float)
    return pd.DataFrame(data)


def _write_tracking(dir_: Path, run_id: int, **fills) -> None:
    """把一条合成 tracking 写到 ``<dir>/<run_id>_tracking.csv``。"""
    dir_.mkdir(parents=True, exist_ok=True)
    _traj(**fills).to_csv(dir_ / f"{run_id}_tracking.csv", index=False)


# ── 加载器 ───────────────────────────────────────────────────────────────
class TestLoaders:
    """multirun / 单目录 / 地貌 三个加载器。"""

    def test_load_trajectories_shape_and_overrides(self, tmp_path: Path):
        """两个 job × 各若干 repeat 应拼成含 override 列的长表。"""
        _write_tracking(tmp_path / "1_env.lim_h=15", 1)
        _write_tracking(tmp_path / "1_env.lim_h=15", 2)
        _write_tracking(tmp_path / "2_env.lim_h=25", 1)

        df = fig.load_trajectories(tmp_path)

        assert len(df) == 3 * 10  # 3 runs × 10 steps
        assert set(df["job_id"]) == {1, 2}
        assert set(df["env.lim_h"]) == {15, 25}
        assert set(df.loc[df["job_id"] == 1, "run_id"]) == {1, 2}

    def test_load_single_run_tags_scenario(self, tmp_path: Path):
        """单目录加载应打上传入的 scenario 标签。"""
        _write_tracking(tmp_path, 1)
        _write_tracking(tmp_path, 2)

        df = fig.load_single_run(tmp_path, "baseline")

        assert set(df["run_id"]) == {1, 2}
        assert (df["scenario"] == "baseline").all()

    def test_load_terrain_maps_english_labels(self, tmp_path: Path):
        """三层嵌套的 (DEM, slope) 目录应映射成英文 scenario。"""
        base = (
            tmp_path / "0_ds.dem=data" / "ohndem10.tif,ds.slope=data" / "ohnslo10.tif"
        )
        _write_tracking(base, 1)
        homo = (
            tmp_path
            / "3_ds.dem=data"
            / "ohn_value1.tif,ds.slope=data"
            / "ohn_value0.tif"
        )
        _write_tracking(homo, 1)

        df = fig.load_terrain(tmp_path)

        assert set(df["scenario"]) == {"Baseline (real terrain)", "Fully homogenized"}

    def test_load_fine_grid_parses_idx_names(self, tmp_path: Path):
        """idx<n>_f2h<a>_h2f<b> 目录应解析出 f2h/h2f/idx。"""
        _write_tracking(tmp_path / "idx0_f2h0.0_h2f0.0", 1)
        _write_tracking(tmp_path / "idx7_f2h0.012_h2f0.09", 1)

        df = fig.load_fine_grid(tmp_path)

        assert set(df["f2h"]) == {0.0, 0.012}
        assert set(df["h2f"]) == {0.0, 0.09}
        assert set(df["idx"]) == {0, 7}

    def test_load_grid_renames_paths(self, tmp_path: Path):
        """3³ 网格加载应把三条转化路径重命名成 f2h/h2f/h2r。"""
        d = tmp_path / (
            "0_Farmer.convert_prob.to_hunter=0.1,"
            "Hunter.convert_prob.to_farmer=0.05,"
            "Hunter.convert_prob.to_rice=0.0"
        )
        _write_tracking(d, 1)

        df = fig.load_grid(tmp_path)

        assert {"f2h", "h2f", "h2r"} <= set(df.columns)
        assert df["f2h"].iloc[0] == 0.1 and df["h2r"].iloc[0] == 0.0

    def test_load_trajectories_empty_dir_raises(self, tmp_path: Path):
        """空目录无 tracking.csv 应抛 FileNotFoundError。"""
        with pytest.raises(FileNotFoundError):
            fig.load_trajectories(tmp_path)

    def test_parse_job_dir_bad_name_raises(self):
        """不合法目录名应抛 ValueError。"""
        with pytest.raises(ValueError):
            fig.parse_job_dir("no-leading-int")


# ── 纯数据逻辑（钉值） ───────────────────────────────────────────────────
class TestDataLogic:
    """_agri_share / _tail_mean / _convert_heatmap_table / build_leverage_frame。"""

    def test_agri_share_value(self):
        """(f+r)/(f+h+r)：10/(10+80+10)=0.2、20/(20+60+20)=0.4。"""
        df = pd.DataFrame(
            {
                "num_farmers_n": [10.0, 20.0],
                "num_hunters_n": [80.0, 60.0],
                "num_rice_n": [10.0, 20.0],
            }
        )
        share = fig._agri_share(df)
        assert share.tolist() == pytest.approx([0.2, 0.4])

    def test_agri_share_missing_column_raises(self):
        """缺指标列应抛 KeyError。"""
        with pytest.raises(KeyError):
            fig._agri_share(pd.DataFrame({"num_farmers_n": [1.0]}))

    def test_tail_mean_window(self):
        """last=5 保留 step>=max-5 即 4..9（含边界共 6 步）；value=step，均值 6.5。"""
        df = pd.DataFrame({"step": range(10), "g": ["a"] * 10, "v": range(10)})
        out = fig._tail_mean(df, ["g"], ["v"], last=5)
        assert out.loc[0, "v"] == pytest.approx(6.5)

    def test_convert_heatmap_table_shape_and_slice(self):
        """固定 h2r 切片后透视成 f2h×h2f，取值为终态均值。"""
        rows = []
        for f2h in (0.0, 0.1):
            for h2f in (0.0, 0.05):
                for h2r in (0.0, 0.05):
                    rows.append(
                        {
                            "step": 100,
                            "run_id": 1,
                            "f2h": f2h,
                            "h2f": h2f,
                            "h2r": h2r,
                            "num_farmers_n": f2h * 1000 + h2f,  # 可辨识
                        }
                    )
        grid = pd.DataFrame(rows)
        table = fig._convert_heatmap_table(grid, h2r=0.05, last=0)
        assert table.shape == (2, 2)
        # f2h 高在上（index 降序）
        assert list(table.index) == [0.1, 0.0]
        assert table.loc[0.1, 0.05] == pytest.approx(100.05)

    def test_grid_endstate_pivot(self):
        """终态透视：行 f2h 降序、列 h2f 升序，取值为终态均值。"""
        rows = []
        for f2h in (0.0, 0.01):
            for h2f in (0.0, 0.05):
                rows.append(
                    {
                        "step": 100,
                        "run_id": 1,
                        "f2h": f2h,
                        "h2f": h2f,
                        "num_farmers_n": 1000 * (1 - 10 * f2h) + h2f,
                    }
                )
        table = fig._grid_endstate(pd.DataFrame(rows), last=0)
        assert list(table.index) == [0.01, 0.0]
        assert list(table.columns) == [0.0, 0.05]
        assert table.loc[0.0, 0.0] == pytest.approx(1000.0)

    def test_build_leverage_frame_agri_and_mult(self):
        """agri_n=f+r；param_mult=value/baseline；两 scan 都在。"""
        rows = []
        for lf, lr in [(2, 0.1), (4, 0.1), (2, 0.2)]:
            rows.append(
                {
                    "step": 100,
                    "run_id": 1,
                    "env.lam_farmer": lf,
                    "env.lam_ricefarmer": lr,
                    "num_farmers_n": 100.0,
                    "num_rice_n": 50.0,
                    "len_farmers_n": 3.0,
                    "len_rice_n": 1.0,
                }
            )
        out = fig.build_leverage_frame(pd.DataFrame(rows))
        assert (out["agri_n"] == 150.0).all()
        assert set(out["scan"]) == {"lam_farmer", "lam_ricefarmer"}
        # lam_farmer=4 → mult 2；lam_ricefarmer=0.2 → mult 2
        assert set(out["param_mult"]) == {1.0, 2.0}


# ── 渲染烟测 ─────────────────────────────────────────────────────────────
class TestRenderSmoke:
    """每个 plot_* 给定 ax 应能画完不抛错。"""

    def teardown_method(self):
        plt.close("all")

    def test_plot_agri_share_smoke(self):
        """Figure 2 面板烟测。"""
        df = pd.concat(
            [
                _traj(num_farmers_n=10, num_hunters_n=80, num_rice_n=10).assign(
                    run_id=r
                )
                for r in (1, 2)
            ]
        )
        _, ax = plt.subplots()
        assert fig.plot_agri_share(df, ax=ax) is ax

    def test_plot_convert_off_vs_on_smoke(self):
        """Figure 3a 面板烟测。"""
        df = pd.concat(
            [
                _traj(num_farmers_n=100).assign(run_id=1, scenario="baseline"),
                _traj(num_farmers_n=900).assign(run_id=1, scenario="conversion off"),
            ]
        )
        _, ax = plt.subplots()
        assert fig.plot_convert_off_vs_on(df, ax=ax) is ax

    def test_plot_convert_heatmap_smoke(self):
        """Figure 3b 面板烟测。"""
        rows = []
        for f2h in (0.0, 0.1):
            for h2f in (0.0, 0.05):
                rows.append(
                    {
                        "step": 100,
                        "run_id": 1,
                        "f2h": f2h,
                        "h2f": h2f,
                        "h2r": 0.05,
                        "num_farmers_n": 1000 * (1 - f2h),
                    }
                )
        _, ax = plt.subplots()
        assert fig.plot_convert_heatmap(pd.DataFrame(rows), ax=ax) is ax

    def test_plot_f2h_cliff_smoke(self):
        """Figure 3b 悬崖曲线烟测。"""
        rows = []
        for f2h in (0.0, 0.01, 0.02):
            for h2f in (0.0, 0.075, 0.15):
                for run in (1, 2):
                    rows.append(
                        {
                            "step": 100,
                            "run_id": run,
                            "f2h": f2h,
                            "h2f": h2f,
                            "num_farmers_n": 1e5 * (1 - 40 * f2h) + 1,
                        }
                    )
        _, ax = plt.subplots()
        assert fig.plot_f2h_cliff(pd.DataFrame(rows), ax=ax, last=0) is ax

    def test_plot_grid_heatmap_smoke(self):
        """Figure 3c 精细热图烟测（含 log 归一化路径）。"""
        rows = []
        for f2h in (0.0, 0.01, 0.02):
            for h2f in (0.0, 0.075, 0.15):
                rows.append(
                    {
                        "step": 100,
                        "run_id": 1,
                        "f2h": f2h,
                        "h2f": h2f,
                        "num_farmers_n": 1e5 * (1 - 40 * f2h) + 1,
                    }
                )
        _, ax = plt.subplots()
        assert fig.plot_grid_heatmap(pd.DataFrame(rows), ax=ax, last=0) is ax

    def test_plot_metric_by_hue_smoke(self):
        """Figure 4 通用面板烟测。"""
        df = pd.concat(
            [
                _traj(num_farmers_n=v).assign(run_id=1, **{"env.lam_farmer": v})
                for v in (2, 4)
            ]
        )
        _, ax = plt.subplots()
        assert fig.plot_metric_by_hue(df, hue="env.lam_farmer", ax=ax) is ax

    def test_plot_leverage_endstate_smoke(self):
        """Figure 5b 面板烟测。"""
        rows = []
        for scan in ("lam_farmer", "lam_ricefarmer"):
            for mult in (1.0, 2.0):
                for run in (1, 2):
                    rows.append(
                        {
                            "step": 100,
                            "scan": scan,
                            "param_mult": mult,
                            "run_id": run,
                            "agri_n": mult * (200 if scan == "lam_ricefarmer" else 100),
                        }
                    )
        _, ax = plt.subplots()
        assert fig.plot_leverage_endstate(pd.DataFrame(rows), ax=ax, last=0) is ax

    def test_panel_label_writes_text(self):
        """panel_label 应在 ax 上写下字母。"""
        _, ax = plt.subplots()
        fig.panel_label(ax, "a")
        assert any("a." in t.get_text() for t in ax.texts)
