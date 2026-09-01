#!/usr/bin/env python 3.11.0
# -*-coding:utf-8 -*-
# @Author  : Shuang (Twist) Song
# @Contact   : SongshGeo@gmail.com
# GitHub   : https://github.com/SongshGeo
# Website: https://cv.songshgeo.com/

"""见刊数字的算法 :mod:`src.workflow.results` 的单测 / 烟测 / 边界测。

这里全部用合成数据，钉的是**算法**：终态窗口取得对不对、重复是不是等权、可加模型
在完全可加的面上是否给出 $R^2 = 1$。真实数据上「这个数还是不是上次那个数」由
:mod:`tests.test_results_regression` 对着 ``paper/results.json`` 查。
"""

from __future__ import annotations

import inspect

import numpy as np
import pandas as pd
import pytest

from src.workflow import figures as fig
from src.workflow import results as res

# ── 合成数据工具 ─────────────────────────────────────────────────────────
_STEPS = 100  # 末 51 步是 step 50..100


def _run(
    run_id: int, farmers: float, hunters: float = 100.0, rice: float = 0.0, **cols
):
    """一条 tracking 长表：全程常数，所以终态均值就等于给定值。"""
    data = {
        "step": np.arange(_STEPS + 1),
        "num_farmers_n": float(farmers),
        "num_hunters_n": float(hunters),
        "num_rice_n": float(rice),
        "len_farmers_n": 1.0,
        "len_hunters_n": 1.0,
        "len_rice_n": 1.0,
        "run_id": run_id,
    }
    data.update(cols)
    return pd.DataFrame(data)


def _runs(*specs, **cols) -> pd.DataFrame:
    """把若干 ``(run_id, farmers)`` 拼成一张长表。"""
    return pd.concat(
        [_run(rid, farmers, **cols) for rid, farmers in specs], ignore_index=True
    )


# ── 数值截断 ─────────────────────────────────────────────────────────────
class TestRoundSig:
    """有效数字截断——金标准的写盘精度。"""

    @pytest.mark.parametrize(
        ("value", "expected"),
        [
            (13825.349019607844, 13825.3),
            (0.17994353277498895, 0.179944),
            (0.9933932232380348, 0.993393),
            (-0.16334981, -0.16335),
            (0.0, 0.0),
        ],
    )
    def test_keeps_six_significant_figures(self, value: float, expected: float):
        """大小差五个数量级的量共用同一个相对精度。"""
        assert res.round_sig(value) == expected

    def test_non_finite_passes_through(self):
        """NaN 不该在截断里变成别的东西——它是「算不出来」的信号，要留着。"""
        assert np.isnan(res.round_sig(float("nan")))

    def test_zero_digits_raises(self):
        with pytest.raises(ValueError, match="digits"):
            res.round_sig(1.23, digits=0)

    def test_round_tree_leaves_ints_and_strings_alone(self):
        """int 被截断成 float 会让 JSON 里的计数变成 6835.0，diff 就永远不干净。"""
        out = res.round_tree({"n": 6835, "name": "x", "v": 1.234567891, "l": [0.5]})

        assert out == {"n": 6835, "name": "x", "v": 1.23457, "l": [0.5]}
        assert isinstance(out["n"], int)


# ── 终态口径 ─────────────────────────────────────────────────────────────
class TestEndStateWindow:
    """终态窗口与重复权重。"""

    def test_window_is_the_last_51_steps_inclusive(self):
        """左端点含在内——`step >= max - 50` 取的是 51 步，不是 50 步。

        这条差别写在 model-inventory 的 F12 里，也是 results.py 的硬约束之一，但它
        只有一步之差：把判据写成 `>` 仍然能算出一个很像的数。所以这里让**第 50 步
        单独扛起全部的量**：窗口对了均值是 1.0，端点被漏掉就是 0.0。
        """
        df = _runs((1, 0.0))
        df.loc[df["step"] == 50, "num_farmers_n"] = 51.0

        got = res._by_run(df, ["run_id"], "num_farmers_n")["num_farmers_n"].iloc[0]

        assert got == pytest.approx(1.0)  # 51 / 51

    def test_the_panels_use_that_same_window(self):
        """画图和算数共用一个窗口，否则正文的数对不上图。

        比的是两条路径**算出来的数**：面板 builder 走 `_tail_mean` 的默认窗口，
        见刊数字走 `results.TAIL`。断言 `res.TAIL == fig.TAIL_STEPS` 是不行的——
        那只是在断言一句赋值，永远不会失败。第 50 步扛着全部的量，两个窗口只要差
        一步，两个数就不相等。
        """
        df = _runs((1, 0.0))
        df.loc[df["step"] == 50, "num_farmers_n"] = 51.0

        panel = fig._tail_mean(df, ["run_id"], ["num_farmers_n"])["num_farmers_n"]
        number = res._by_run(df, ["run_id"], "num_farmers_n")["num_farmers_n"]

        assert panel.iloc[0] == pytest.approx(number.iloc[0])

    def test_agri_share_matches_the_definition(self):
        """$(F+R)/(F+H+R)$：20 + 20 农业 / 160 总数 = 0.25。"""
        df = _runs((1, 20.0), rice=20.0, hunters=120.0)

        assert res.agri_share_endstate(df) == pytest.approx(0.25)

    def test_only_the_tail_counts(self):
        """前半程的值再离谱也不该进终态——窗口是末 51 步。"""
        early = _runs((1, 0.0))
        early.loc[early["step"] < 50, "num_farmers_n"] = 1e9

        assert res._by_run(early, ["run_id"], "num_farmers_n")["num_farmers_n"].iloc[
            0
        ] == pytest.approx(0.0)

    def test_repeats_are_weighted_equally(self):
        """按 run 聚合再平均：两次重复 10 与 30，结果是 20 而不是按行加权。"""
        df = _runs((1, 10.0), (2, 30.0))
        # 让第二次重复多出一半的行，行加权就会给出 23.3 而不是 20。
        df = pd.concat([df, df[df["run_id"] == 2]], ignore_index=True)

        got = res._by_run(df.assign(_k=0), ["_k"], "num_farmers_n")

        assert got["num_farmers_n"].iloc[0] == pytest.approx(20.0)


# ── Figure 3 ─────────────────────────────────────────────────────────────
class TestConversionRelease:
    """关掉转化之后农民规模被放开多少倍。"""

    def test_ratio(self):
        base = _runs((1, 100.0), (2, 200.0))  # 150
        off = _runs((1, 600.0))

        got = res.conversion_release(base, off)

        assert got["baseline_farmers"] == pytest.approx(150.0)
        assert got["release_ratio"] == pytest.approx(4.0)

    def test_zero_baseline_raises(self):
        """基准为 0 时倍数无定义，要报错而不是返回 inf 让它流进 JSON。"""
        with pytest.raises(ValueError, match="undefined"):
            res.conversion_release(_runs((1, 0.0)), _runs((1, 1.0)))


class TestLogAdditive:
    """log 空间的可分离可加模型。"""

    @staticmethod
    def _surface(alpha, beta) -> pd.DataFrame:
        """$\\log N = \\alpha_i + \\beta_j$，构造上严格可加。"""
        return pd.DataFrame(np.exp(np.add.outer(alpha, beta)))

    def test_perfectly_additive_surface_gives_r2_one(self):
        got = res.fit_log_additive(self._surface([0.0, 1.0, 2.0], [0.0, 0.5, 1.0, 1.5]))

        assert got["r2"] == pytest.approx(1.0)
        assert got["resid_rms"] == pytest.approx(0.0, abs=1e-12)

    def test_an_interaction_shows_up_as_residual(self):
        """加一个交互项，$R^2$ 应当掉下来，且残差范围张开。"""
        table = self._surface([0.0, 1.0, 2.0], [0.0, 0.5, 1.0, 1.5])
        table.iloc[2, 3] *= 2.0

        got = res.fit_log_additive(table)

        assert got["r2"] < 1.0
        assert got["resid_max"] > 0.1

    def test_non_positive_cell_raises(self):
        """取不了对数就报错，而不是让 NaN 一路渗进 $R^2$。"""
        table = self._surface([0.0, 1.0], [0.0, 1.0])
        table.iloc[0, 0] = 0.0

        with pytest.raises(ValueError, match="non-positive"):
            res.fit_log_additive(table)

    def test_constant_surface_raises(self):
        """常数面上 $R^2$ 是 0/0。"""
        with pytest.raises(ValueError, match="constant"):
            res.fit_log_additive(pd.DataFrame(np.ones((3, 3))))


class TestCliff:
    """f2h 悬崖：第一小步吃掉的跌幅占比。"""

    @staticmethod
    def _broad(**by_f2h) -> pd.DataFrame:
        """一行 h2f=0 的网格，外加一行 h2f=0.05 作为不该被算进去的干扰。"""
        frames = []
        for f2h, value in by_f2h.items():
            level = float(f2h.replace("_", "."))
            frames.append(_run(1, value, f2h=level, h2f=0.0))
            frames.append(_run(1, value * 10, f2h=level, h2f=0.05))
        return pd.concat(frames, ignore_index=True)

    def test_share_of_the_drop(self):
        """1000 → 200 → 0：0.02 之前吃掉 800/1000 = 80%。"""
        got = res.cliff_drop(self._broad(**{"0_0": 1000.0, "0_02": 200.0, "0_1": 0.0}))

        assert (got["at_zero"], got["at_knee"], got["at_widest_f2h"]) == (
            1000.0,
            200.0,
            0.0,
        )
        assert got["drop_share_before_knee"] == pytest.approx(0.8)

    def test_missing_knee_raises(self):
        """膝点那一档不在网格里就报错，而不是悄悄挑一个最近的档。"""
        with pytest.raises(ValueError, match="f2h = 0.02"):
            res.cliff_drop(self._broad(**{"0_0": 1000.0, "0_1": 0.0}))

    def test_no_net_drop_raises(self):
        """整行持平（或反向）时占比无定义，要报错而不是把 inf 写进 results.json。"""
        flat = self._broad(**{"0_0": 1000.0, "0_02": 1000.0, "0_1": 1000.0})

        with pytest.raises(ValueError, match="no net drop"):
            res.cliff_drop(flat)

    def test_the_knee_defaults_to_the_shaded_boundary(self):
        """膝点默认值就是面板上金色阴影区的右边界，两处不能各写一个字面量。"""
        knee = inspect.signature(res.cliff_drop).parameters["knee"].default
        shade = inspect.signature(fig.plot_f2h_cliff).parameters["shade"].default

        assert knee == fig.CLIFF_KNEE_F2H
        assert shade == (0.0, fig.CLIFF_KNEE_F2H)


# ── Figure 4 ─────────────────────────────────────────────────────────────
class TestSpreadRatio:
    """三个因素共用的效应量尺子。"""

    def test_max_over_min(self):
        assert res.spread_ratio({"a": 2.0, "b": 5.0, "c": 4.0}) == pytest.approx(2.5)

    @pytest.mark.parametrize(
        ("levels", "match"),
        [({}, "no levels"), ({"a": 0.0, "b": 1.0}, "zero")],
        ids=["empty", "zero-floor"],
    )
    def test_degenerate_input_raises(self, levels: dict, match: str):
        with pytest.raises(ValueError, match=match):
            res.spread_ratio(levels)


# ── Figure 5 ─────────────────────────────────────────────────────────────
class TestLeverage:
    """两条 scan 的终态曲线与重复间变异。"""

    @staticmethod
    def _lev() -> pd.DataFrame:
        frames = []
        for scan, mult, agri in [
            ("lam_farmer", 1.0, 100.0),
            ("lam_farmer", 5.0, 200.0),
            ("lam_ricefarmer", 1.0, 100.0),
            ("lam_ricefarmer", 5.0, 400.0),
        ]:
            for run_id, jitter in ((1, 0.9), (2, 1.1)):
                frames.append(
                    _run(run_id, 0.0, scan=scan, param_mult=mult, agri_n=agri * jitter)
                )
        return pd.concat(frames, ignore_index=True)

    def test_curve_keys_are_multiples(self):
        got = res.leverage_endstate(self._lev())

        assert set(got) == {"lam_farmer", "lam_ricefarmer"}
        assert got["lam_ricefarmer"] == {
            "1x": pytest.approx(100.0),
            "5x": pytest.approx(400.0),
        }

    def test_replicate_cv_is_the_mean_over_slices(self):
        """每个切片两次重复是 ±10%，样本标准差 / 均值 = 0.1·√2 ≈ 0.1414。"""
        assert res.replicate_cv(self._lev()) == pytest.approx(
            0.1 * np.sqrt(2), rel=1e-6
        )
