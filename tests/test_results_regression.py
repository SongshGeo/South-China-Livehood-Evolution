#!/usr/bin/env python 3.11.0
# -*-coding:utf-8 -*-
# @Author  : Shuang (Twist) Song
# @Contact   : SongshGeo@gmail.com
# GitHub   : https://github.com/SongshGeo
# Website: https://cv.songshgeo.com/

"""``paper/results.json`` 是金标准，这里守着它。

投稿定稿之后，图冻住了，但图上读出来的数还会继续被抄进正文、图注、
``paper/model-inventory.md`` 和 SI。返修重跑之后，那些抄写不会自己报错——整理仓库时
就抓到过一次：``model-inventory.md`` 的「What the re-run changed」整节标着 rerun_v3，
七个值却全是 rerun_v2 的。

所以每个数由 :mod:`src.workflow.results` 算一次、冻在 ``paper/results.json`` 里，本文件
拿真实输入重算并逐键比对。失败信息直接指出**哪个键、从多少变成了多少**。

两层，各自的可查范围不同：

* ``landscape`` / ``parameters`` / ``c14`` 的输入（栅格、Hydra 配置、SI-2 附表）都随
  仓库版本管理，任何 clone 和 CI 都能查，所以这一层无条件跑。
* ``figure2``–``figure5`` 要读 ``out/south_china_evolution/rerun_v3``（135 MB，在
  .gitignore 里）。取不到就跳过而不是判红——那不是漂移，只是数据没同步；
  ``make fetch-rerun`` 拉下来之后这一层就会跑起来。

比对的是**截断到 6 位有效数字之后**的值：远严于任何有意义的模型变化，又不会被
NumPy/pandas 换版本时的末位抖动误伤。
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "paper"))

import build_results as br  # noqa: E402

#: 金标准本身。
GOLD = json.loads(br.OUT.read_text(encoding="utf-8"))

#: 只有这几层能在没有扫描数据的机器上重算。
REPO_TIER = ("landscape", "parameters", "c14")
SWEEP_TIER = ("figure2", "figure3", "figure4", "figure5")


def _diff(section: str, fresh: dict) -> list[str]:
    """一层里的逐键差异，复用 ``build_results`` 的展平与对比。"""
    return br.diff({section: GOLD[section]}, {section: fresh[section]})


# 两个重算夹具都放在模块层、按模块缓存：栅格要开三次、扫描要读近千个 CSV，
# 每个 section 各算一遍就是白算四遍。
@pytest.fixture(scope="module", name="fresh_repo")
def _fresh_repo() -> dict:
    return br.round_tree_tier(br.repo_tier())


@pytest.fixture(scope="module", name="fresh_sweep")
def _fresh_sweep() -> dict:
    from src.workflow import results as R

    return br.round_tree_tier(R.compute_results(br.SWEEP))


class TestGoldFile:
    """金标准文件本身的形状——不碰任何数据，任何时候都跑。"""

    def test_it_records_the_sweep_the_figures_came_from(self):
        """被取代的批次都还在 out/ 下，指回去照样能算出一整套数，只是全是旧的。"""
        assert GOLD["_meta"]["sweep"] == "out/south_china_evolution/rerun_v3"

    def test_the_tail_window_matches_the_panels(self):
        """正文的数和图上的线必须是同一个终态窗口。"""
        from src.workflow import figures as F

        assert GOLD["_meta"]["tail_steps"] == F.TAIL_STEPS

    @pytest.mark.parametrize("section", REPO_TIER + SWEEP_TIER)
    def test_every_section_is_present(self, section: str):
        """有扫描数据的机器上重建过一次，就不该再有空层。

        缺层只会以「某个数没人守着」的形式出现，不会有任何报错。
        """
        assert GOLD.get(section), f"results.json 缺 {section} 层，重建：make results"


class TestRepoTier:
    """随仓库版本管理的输入算出来的数——CI 上也查得了。"""

    @pytest.mark.parametrize("section", REPO_TIER)
    def test_matches_the_gold_file(self, section: str, fresh_repo: dict):
        changes = _diff(section, fresh_repo)

        assert not changes, "\n".join(
            [f"{section} 与 paper/results.json 不一致："]
            + changes
            + ["若是有意改动，重建：uv run python paper/build_results.py"]
        )


@pytest.mark.skipif(
    not br.SWEEP.exists(),
    reason=f"扫描结果不在本机（{br.SWEEP.relative_to(ROOT)}）；make fetch-rerun 取数",
)
class TestSweepTier:
    """Figure 2–5 的见刊数字，拿 rerun_v3 重算。"""

    @pytest.mark.parametrize("section", SWEEP_TIER)
    def test_matches_the_gold_file(self, section: str, fresh_sweep: dict):
        changes = _diff(section, fresh_sweep)

        assert not changes, "\n".join(
            [f"{section} 与 paper/results.json 不一致（重跑了？）："]
            + changes
            + [
                "确认是有意的之后，重建金标准，并同步更新每一处抄了这些数的地方",
                "（paper/model-inventory.md、vault 里的正文与 SI、出图 notebook 的说明）：",
                "  uv run python paper/build_results.py",
            ]
        )
