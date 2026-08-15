#!/usr/bin/env python 3.11.0
# -*-coding:utf-8 -*-
# @Author  : Shuang (Twist) Song
# @Contact   : SongshGeo@gmail.com
# GitHub   : https://github.com/SongshGeo
# Website: https://cv.songshgeo.com/

"""出图 notebook 的数据来源，以及跨文件重复引用的拟合优度。

Figures 2–5 曾经指向一批日期目录，那批数据产于 #28（每步损失两次）和 #29
（水稻移民落在旱作掩膜上）修复之前，且完全没有种子。修好之后重跑进了
`out/south_china_evolution/rerun_v2/`，notebook 也随之改指。

两类漂移都是"无声"的，所以都要钉住：

1. **数据来源**：旧目录仍留在 `out/` 下，任何一个路径常量被改回去，notebook
   照样跑通、照样出图，只是出的是修复前的图，没有任何报错。
2. **可加模型的 R²**：同一个数字被抄在三处（`paper/methods.md`、
   `paper/si_odd_protocol.md`、notebook 正文）。重跑后手工更新时确实漏掉了
   其中一处，靠人眼没抓住。这里只要求三处相等，不判定数值本身对不对——
   数值要靠重新拟合，而 `out/` 在 .gitignore 里，CI 上没有数据。

同理，本文件全部只做纯文本检查，不碰真实数据。
"""

import json
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
NOTEBOOK = ROOT / "reports" / "manuscript_figures.ipynb"

#: notebook 里全部七个数据路径常量，每一个都必须从 RERUN 派生。
PATH_CONSTANTS = (
    "BASELINE_DIR",
    "OFF_DIR",
    "LAM_ROOT",
    "LIMH_ROOT",
    "TERRAIN_ROOT",
    "BROAD_GRID",
    "FINE_GRID",
)

#: 抄了同一个 R² 的三个文件。notebook 用 Markdown 单元，另两个是正文。
R2_SOURCES = (
    ROOT / "paper" / "methods.md",
    ROOT / "paper" / "si_odd_protocol.md",
    NOTEBOOK,
)

#: `$R^2 = 0.993$`，容忍 `R^2`/`R²` 与等号周围的空格。
R2_RE = re.compile(r"R(?:\^2|²)\s*=\s*(0\.\d+)")


def _cells(kind: str) -> str:
    """notebook 中指定类型单元的源码，拼成一段文本。"""
    nb = json.loads(NOTEBOOK.read_text(encoding="utf-8"))
    return "\n".join(
        "".join(c["source"]) for c in nb["cells"] if c["cell_type"] == kind
    )


#: 只读一次——与 test_config.py / test_env.py 在模块层组装夹具的写法一致。
SOURCE = _cells("code")


def _assignments(name: str) -> list[str]:
    """`name = ...` 的全部赋值行，去掉行尾注释。

    取全部而非第一处：只看第一处的话，后面再赋一次值就能悄悄绕过检查，
    而那正是本文件要防的事。
    """
    return [
        line.split("#", 1)[0].strip()
        for line in SOURCE.splitlines()
        if line.strip().startswith(f"{name} = ")
    ]


class TestFigureDataSource:
    """Figures 2–5 的数据来源。"""

    def test_rerun_root_points_at_rerun_v2(self):
        """RERUN 必须是 rerun_v2——重跑脚本写死的输出根。"""
        assert 'RERUN = DATA / "rerun_v2"' in SOURCE

    @pytest.mark.parametrize("name", PATH_CONSTANTS)
    def test_every_path_constant_derives_from_rerun(self, name):
        """七个常量逐个检查，避免只改了一部分、剩下的还指向旧目录。"""
        assignments = _assignments(name)

        assert assignments, f"{name} 未在 notebook 中赋值"
        for line in assignments:
            assert "RERUN" in line, (
                f"{name} 不是从 RERUN 派生的：{line}；"
                "修复前的日期目录仍在 out/ 下，指回去不会报错，只会出旧图"
            )

    @pytest.mark.parametrize(
        "needle",
        ["raise FileNotFoundError", "make fetch-rerun", "run_slurm_rerun.sh --verify"],
        ids=["raises", "how-to-fetch", "how-to-verify"],
    )
    def test_missing_data_fails_loudly(self, needle):
        """数据缺失时要抛错并给出取数与核验命令，而不是让后面的单元自己炸。"""
        assert needle in SOURCE


class TestQuotedGoodnessOfFit:
    """可加模型 R² 的三处抄写必须一致。"""

    def test_every_file_quotes_a_goodness_of_fit(self):
        """三处都得能解析出 R²，否则下面的相等断言会变成空转。"""
        for path in R2_SOURCES:
            text = path.read_text(encoding="utf-8")

            assert R2_RE.search(text), f"{path.name} 里找不到 R² 引用"

    def test_all_three_files_agree(self):
        """重跑后重新拟合，三处要一起改；漏掉任何一处都在这里失败。"""
        quoted = {
            path.name: sorted(set(R2_RE.findall(path.read_text(encoding="utf-8"))))
            for path in R2_SOURCES
        }
        values = {v for vs in quoted.values() for v in vs}

        assert len(values) == 1, f"R² 在各处不一致: {quoted}"
