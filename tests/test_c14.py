#!/usr/bin/env python 3.11.0
# -*-coding:utf-8 -*-
# @Author  : Shuang (Twist) Song
# @Contact   : SongshGeo@gmail.com
# GitHub   : https://github.com/SongshGeo
# Website: https://cv.songshgeo.com/

"""SI-2 ¹⁴C 数据模块 :mod:`src.workflow.c14` 的单测、钉值测与边界测。

钉值测（:class:`TestShippedDataset`）读的是随稿投出的 ``data/si2_c14_sites.xlsx``
原件。它们的作用是：若有人替换或修订了这份附表，图上的数字会跟着变，测试先炸，
而不是等到图已经进了稿子才发现。改数据时应当同步改这里的期望值，并检查引用了
这些数字的正文。
"""

from __future__ import annotations

from pathlib import Path

import matplotlib
import pandas as pd
import pytest
from matplotlib import pyplot as plt

from src.workflow import c14

matplotlib.use("Agg")  # 无显示后端，供 CI / headless 跑图

#: 随稿投出的附表原件。
DATASET = Path(__file__).resolve().parents[1] / "data" / "si2_c14_sites.xlsx"


# ── 合成数据工具 ─────────────────────────────────────────────────────────
def _dates() -> pd.DataFrame:
    """造一张最小的逐条测年表：两个遗址，各一条测年，生业各不相同。

    调用方用 ``.assign(...)`` 改需要改的列。
    """
    return pd.DataFrame(
        {
            "site": ["A", "B"],
            "site_zh": ["甲", "乙"],
            "category": ["Settlement", "Settlement"],
            "province": ["Guangxi", "Fujian"],
            "lon": [108.0, 119.0],
            "lat": [23.0, 26.0],
            "elevation": [100, 50],
            "lab_code": ["L1", "L2"],
            "cal_from": [8000.0, 5000.0],
            "cal_to": [7000.0, 4000.0],
            "subsistence": ["Foraging", "Farming"],
        }
    )


def _write_raw(
    tmp_path: Path,
    subsistence: list[str],
    cal_from: list[int],
    cal_to: list[int],
) -> Path:
    """写一个最小的 SI-2 形状工作簿，只带加载器真正校验的那几列。"""
    raw = pd.DataFrame(
        {
            "Site Name": [f"S{i}" for i in range(len(subsistence))],
            "Subsistence": subsistence,
            "95.4% from (cal BP)": cal_from,
            "95.4% to (cal BP)": cal_to,
        }
    )
    path = tmp_path / "mini.xlsx"
    raw.to_excel(path, sheet_name=c14.SITES_SHEET, index=False)
    return path


# ── 加载器 ───────────────────────────────────────────────────────────────
class TestLoader:
    """`load_c14_dates` 的规范化与校验。"""

    def test_maps_the_raw_subsistence_spellings(self, tmp_path: Path):
        """原表的 'Hunting Garthering'（拼写如此）与 'farming' 都要被认出来。"""
        path = _write_raw(
            tmp_path, ["Hunting Garthering", "farming"], [8000, 5000], [7000, 4000]
        )

        out = c14.load_c14_dates(path)

        assert list(out["subsistence"]) == ["Foraging", "Farming"]

    def test_rejects_an_unknown_subsistence_label(self, tmp_path: Path):
        """没见过的生业取值必须报错，而不是变成 NaN 被画成没有颜色的一行。"""
        path = _write_raw(tmp_path, ["fishing"], [8000], [7000])

        with pytest.raises(ValueError, match="Unmapped subsistence"):
            c14.load_c14_dates(path)

    def test_rejects_a_reversed_calibrated_interval(self, tmp_path: Path):
        """`from` 必须是更老的一端，否则线段会被画反。"""
        path = _write_raw(tmp_path, ["farming"], [4000], [5000])

        with pytest.raises(ValueError, match="cal_from <= cal_to"):
            c14.load_c14_dates(path)

    def test_rejects_a_label_missing_from_the_plotting_constants(
        self, tmp_path: Path, monkeypatch
    ):
        """标签映射表和顺序/配色表必须覆盖同一批类别。

        只加进 `SUBSISTENCE_LABELS` 而忘了 `SUBSISTENCE_ORDER`，这个类别会从
        `subsistence_coverage` 里静默消失——所以在入口就要拦住。
        """
        monkeypatch.setitem(c14.SUBSISTENCE_LABELS, "fishing", "Fishing")
        path = _write_raw(tmp_path, ["fishing"], [8000], [7000])

        with pytest.raises(ValueError, match="missing from SUBSISTENCE_ORDER"):
            c14.load_c14_dates(path)


# ── 聚合 ─────────────────────────────────────────────────────────────────
class TestAggregate:
    """`aggregate_sites` 的口径。"""

    def test_takes_the_outer_bounds_and_sorts_oldest_first(self):
        """遗址跨度取最老的上界到最新的下界，行序由老到新。"""
        second_a = (
            _dates().iloc[[0]].assign(lab_code="L3", cal_from=6000.0, cal_to=5000.0)
        )
        dates = pd.concat([_dates(), second_a], ignore_index=True)

        sites = c14.aggregate_sites(dates)

        assert list(sites["site"]) == ["A", "B"]  # A 的中点更老
        row_a = sites[sites["site"] == "A"].iloc[0]
        assert row_a["cal_from"] == 8000  # 两条测年里最老的上界
        assert row_a["cal_to"] == 5000  # 最新的下界
        assert row_a["n_dates"] == 2

    def test_rejects_a_site_with_two_subsistence_labels(self):
        """一遗址一标签是聚合的前提；上游若改成分层标注必须先改这里。"""
        dates = _dates().assign(site=["A", "A"])

        with pytest.raises(ValueError, match="more than one subsistence label"):
            c14.aggregate_sites(dates)


# ── 时间覆盖 ─────────────────────────────────────────────────────────────
class TestCoverage:
    """`subsistence_coverage`、`overlap_window` 与 `coexistence_fraction`。"""

    def test_counts_distinct_sites_not_dates(self):
        """同一遗址的多条测年覆盖同一个箱，只能算一个遗址。"""
        dates = pd.concat(
            [_dates().iloc[[0]], _dates().iloc[[0]].assign(lab_code="L3")],
            ignore_index=True,
        )

        coverage = c14.subsistence_coverage(dates, bin_width=500)
        foraging = coverage[coverage["subsistence"] == "Foraging"]

        assert foraging["n_sites"].max() == 1

    def test_emits_zero_rows_rather_than_dropping_empty_bins(self):
        """没有覆盖的箱要留 0，否则阶梯图会跳过空档、把间断连成一片。"""
        coverage = c14.subsistence_coverage(_dates(), bin_width=500)

        farming = coverage[coverage["subsistence"] == "Farming"]
        assert (farming["n_sites"] == 0).any()  # 8000–5000 段没有农业遗址
        assert len(coverage) == 2 * coverage["cal_bp"].nunique()

    def test_keeps_a_livelihood_with_no_dates_at_all(self):
        """某一类完全没有测年时，仍要有一整列 0，而不是整类消失。"""
        only_foraging = _dates().iloc[[0]]

        coverage = c14.subsistence_coverage(only_foraging, bin_width=500)

        assert set(coverage["subsistence"]) == set(c14.SUBSISTENCE_ORDER)
        farming = coverage[coverage["subsistence"] == "Farming"]
        assert (farming["n_sites"] == 0).all()

    def test_overlap_window_is_nan_when_the_two_never_coexist(self):
        """两类互不重叠时不能返回一个假的区间，占比也必须是 0。"""
        coverage = c14.subsistence_coverage(_dates(), bin_width=500)

        older, younger = c14.overlap_window(coverage)

        assert pd.isna(older) and pd.isna(younger)
        assert c14.coexistence_fraction(_dates(), coverage) == 0.0

    def test_overlap_window_spans_the_shared_bins(self):
        """有重叠时返回共存箱中点的最老与最新。"""
        dates = _dates().assign(cal_from=[8000.0, 7500.0], cal_to=[7000.0, 6500.0])

        older, younger = c14.overlap_window(c14.subsistence_coverage(dates, 500))

        assert older == 7250 and younger == 7250

    def test_rejects_a_non_positive_bin_width(self):
        with pytest.raises(ValueError, match="bin_width must be positive"):
            c14.subsistence_coverage(_dates(), bin_width=0)


# ── 年代换算 ─────────────────────────────────────────────────────────────
class TestAgeConversion:
    """`bp_to_bce` 与 `bce_to_bp` 必须互为逆——BCE 副轴的刻度全靠这一对。"""

    @pytest.mark.parametrize("cal_bp", [4158, 5450, 8635])
    def test_round_trip(self, cal_bp: int):
        assert c14.bce_to_bp(c14.bp_to_bce(cal_bp)) == cal_bp

    def test_the_spread_window_lands_where_the_manuscript_says(self):
        """3500–3000 BC 就是 5450–4950 cal BP，图上的灰带按这个画。"""
        assert [c14.bce_to_bp(bc) for bc in c14.SPREAD_WINDOW_BC] == [5450, 4950]


# ── 渲染烟测 ─────────────────────────────────────────────────────────────
class TestPanels:
    """两个 `plot_*` 只做烟测：能画出来、接受传入的 ax、行序与数据一致。"""

    def test_timeline_draws_one_row_per_site_in_the_given_order(self):
        dates = _dates()
        sites = c14.aggregate_sites(dates)
        _, ax = plt.subplots()

        out = c14.plot_site_timeline(dates, sites, ax=ax)

        assert out is ax
        assert [t.get_text().split()[0] for t in ax.get_yticklabels()] == list(
            sites["site"]
        )
        plt.close("all")

    def test_timeline_puts_older_on_the_left(self):
        """横轴必须是降序的 cal BP；`sharex` 下这一点靠 set_xlim 的幂等性保证。"""
        dates = _dates()
        _, ax = plt.subplots()

        c14.plot_site_timeline(dates, c14.aggregate_sites(dates), ax=ax)
        lo, hi = ax.get_xlim()

        assert lo > hi
        plt.close("all")

    def test_coverage_panel_renders_both_livelihoods(self):
        coverage = c14.subsistence_coverage(_dates(), bin_width=500)
        _, ax = plt.subplots()

        out = c14.plot_subsistence_coverage(coverage, ax=ax)

        assert out is ax
        assert {t.get_text() for t in ax.get_legend().get_texts()} == set(
            c14.SUBSISTENCE_ORDER
        )
        plt.close("all")


# ── 钉住随稿投出的那份数据 ───────────────────────────────────────────────
@pytest.mark.skipif(not DATASET.exists(), reason=f"{DATASET} not present")
class TestShippedDataset:
    """对 ``data/si2_c14_sites.xlsx`` 原件的钉值测，见模块 docstring。"""

    # class 作用域：这份工作簿要过 openpyxl，函数作用域会让它被解析五六遍，占掉
    # 整个测试文件近四成的时间。下面的用例都只读不写，共享同一个 frame 是安全的。
    # classmethod：pytest 10 起，class 作用域的 fixture 写成实例方法会告警。
    @pytest.fixture(name="dates", scope="class")
    @classmethod
    def fixture_dates(cls) -> pd.DataFrame:
        return c14.load_c14_dates(DATASET)

    def test_shape(self, dates: pd.DataFrame):
        """78 条测年、26 个遗址、3 个省。"""
        assert len(dates) == 78
        assert dates["site"].nunique() == 26
        assert set(dates["province"]) == {"Guangdong", "Guangxi", "Fujian"}

    def test_every_row_carries_a_subsistence_and_an_interval(self, dates):
        """两个生业类别都有，且没有缺失的定年区间。"""
        assert set(dates["subsistence"]) == set(c14.SUBSISTENCE_ORDER)
        assert not dates[["cal_from", "cal_to", "lon", "lat"]].isna().any().any()

    def test_site_counts_by_subsistence(self, dates):
        """18 个采集狩猎遗址、8 个农业遗址——图例和正文引的就是这两个数。"""
        sites = c14.aggregate_sites(dates)
        counts = sites["subsistence"].value_counts().to_dict()
        assert counts == {"Foraging": 18, "Farming": 8}

    def test_record_span(self, dates):
        """整个记录覆盖 8635–4158 cal BP。"""
        assert dates["cal_from"].max() == 8635
        assert dates["cal_to"].min() == 4158

    def test_the_two_livelihoods_overlap_for_most_of_the_record(self, dates):
        """图要说的话：两种生业在记录的绝大部分时间里同时存在。

        图注和正文引的那个百分比必须出自 `coexistence_fraction`，notebook 也调
        同一个函数——两边各算一遍正是 $R^2$ 当年漂掉的方式。
        """
        coverage = c14.subsistence_coverage(dates, bin_width=50)
        older, younger = c14.overlap_window(coverage)

        assert (older, younger) == (7575.0, 4325.0)
        assert round(c14.coexistence_fraction(dates, coverage), 3) == 0.726

    def test_no_site_falls_between_two_bin_centres(self, dates):
        """默认 50 年箱宽的前提：窄于箱宽的区间可能整条落在两个箱中点之间而漏统计。

        这份数据最窄的 95.4% 区间是 68 年，所以每个遗址都至少落进一个箱。附表若
        换上更窄的区间，这条会先炸，提醒去改分箱，而不是接受一张少了遗址的覆盖图。
        """
        assert (dates["cal_from"] - dates["cal_to"]).min() == 68

        centres = c14.subsistence_coverage(dates, bin_width=50)["cal_bp"].unique()
        covered = dates.apply(
            lambda r: ((centres >= r["cal_to"]) & (centres <= r["cal_from"])).any(),
            axis=1,
        )
        assert set(dates.loc[covered, "site"]) == set(dates["site"])
