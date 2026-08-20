#!/usr/bin/env python 3.11.0
# -*-coding:utf-8 -*-
# @Author  : Shuang (Twist) Song
# @Contact   : SongshGeo@gmail.com
# GitHub   : https://github.com/SongshGeo
# Website: https://cv.songshgeo.com/

"""出图 notebook 的数据来源，以及跨文件重复引用的拟合优度。

Figures 2–5 至今换过两次数据源，每次旧目录都原地留着：

1. 最早的一批日期目录，产于 #28（每步损失两次）和 #29（水稻移民落在旱作掩膜上）
   修复之前，且完全没有种子。修好之后重跑进 `rerun_v2/`。
2. `rerun_v2/` 用的 `env.lim_h` = 35 是拍在"人/格"上的，没按格子面积换算。改成
   35 人/百平方公里 × 80 km²/格 = 28 人/格之后，六组实验全部重算，进了
   `out/south_china_evolution/rerun_v3/`，notebook 也随之改指。

两类漂移都是"无声"的，所以都要钉住：

1. **数据来源**：旧目录仍留在 `out/` 下，任何一个路径常量被改回去，notebook
   照样跑通、照样出图，只是出的是修复前的图，没有任何报错。
2. **可加模型的 R²**：同一个数字被抄在多处（主文场景、SI、notebook
   正文）。重跑后手工更新时确实漏掉了其中一处，靠人眼没抓住。这里只要求各处
   相等，不判定数值本身对不对——数值要靠重新拟合，而 `out/` 在 .gitignore 里，
   CI 上没有数据。

同理，本文件全部只做纯文本检查，不碰真实数据。

**手稿正文不在本仓库**：主文与 SI 都写在 Obsidian vault 的 longform 项目里，
`paper/manuscript` 与 `paper/si_odd_protocol` 是指向它 `manuscript/`、
`supplementary/` 两个文件夹的软链接，两边都以场景（scene）分文件存放。软链接存
的是绝对路径，所以在别人的 clone 或 CI 上必然悬空——此时这两部分检查跳过，而不是
把整个套件判红。notebook 是本仓库自带的，任何时候都仍然要引到 R²。
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

#: 主文的写作源：vault 里 longform 项目的 manuscript/，经软链接接入。
MS_SCENES = ROOT / "paper" / "manuscript"

#: SI 的写作源：vault 里 longform 项目的 supplementary/，经软链接接入。
SI_SCENES = ROOT / "paper" / "si_odd_protocol"


def _scenes(folder: Path) -> list[Path]:
    """一个 longform 文件夹里的场景文件。

    只取场景本身：索引笔记（`* (Index).md`）是草稿定义不是正文，而
    `<项目名>_Supplementary.md` 之类是 longform 编译出来的产物——把产物算进去会让
    同一处 R² 被数两遍，且产物永远与场景一致，检查不出任何东西。

    软链接悬空时返回空表，让上层跳过而不是判红。
    """
    if not folder.is_dir():
        return []
    return sorted(
        p
        for p in folder.glob("*.md")
        if not p.stem.endswith("(Index)") and not p.stem.endswith("_Supplementary")
    )


#: 抄了同一个 R² 的地方。notebook 用 Markdown 单元，其余是正文。
#: 主文与 SI 都在 vault 里，在别人的 clone 上整批悬空——此时两边都收不到场景，
#: 只有 notebook 是本仓库自带、任何时候都必须引到的那一处。
R2_SOURCES = (NOTEBOOK, *_scenes(MS_SCENES), *_scenes(SI_SCENES))

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

    def test_rerun_root_points_at_rerun_v3(self):
        """RERUN 必须是 rerun_v3——重跑脚本写死的输出根。"""
        assert 'RERUN = DATA / "rerun_v3"' in SOURCE

    @pytest.mark.parametrize("name", PATH_CONSTANTS)
    def test_every_path_constant_derives_from_rerun(self, name):
        """七个常量逐个检查，避免只改了一部分、剩下的还指向旧目录。"""
        assignments = _assignments(name)

        assert assignments, f"{name} 未在 notebook 中赋值"
        for line in assignments:
            assert "RERUN" in line, (
                f"{name} 不是从 RERUN 派生的：{line}；"
                "rerun_v2 和更早的日期目录仍在 out/ 下，指回去不会报错，只会出旧图"
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
    """可加模型 R² 的各处抄写必须一致。"""

    @staticmethod
    def _quoted() -> dict[str, list[str]]:
        """各文件里引到的 R²，只保留真的引了的那些。

        读不到的直接跳过：主文与 SI 的场景都在 vault 里，在别人的 clone 或 CI 上
        必然读不到，那不是这份检查要抓的漂移。
        """
        found = {}
        for path in R2_SOURCES:
            try:
                text = path.read_text(encoding="utf-8")
            except OSError:
                continue
            found[path.name] = sorted(set(R2_RE.findall(text)))
        return {name: vs for name, vs in found.items() if vs}

    def test_both_manuscript_tiers_quote_it(self):
        """主文与 notebook 都得引到，否则下面的相等断言会变成空转。

        SI 不在这里要求：它按场景分文件，R² 只出现在其中一个场景。主文同样按场景
        分文件，R² 落在 `methods.md` 那一篇；两边的软链接悬空时都只查 notebook。
        """
        quoted = self._quoted()

        if _scenes(MS_SCENES):
            assert (
                "methods.md" in quoted
            ), "paper/manuscript/methods.md 里找不到 R² 引用"
        assert NOTEBOOK.name in quoted, f"{NOTEBOOK.name} 里找不到 R² 引用"

    def test_si_quotes_it_too(self):
        """SI 也抄了同一个数——正是这一处在上次手工更新时被漏掉。"""
        if not _scenes(SI_SCENES):
            pytest.skip("SI 软链接未解析（不是本机的 Obsidian vault）")
        quoted = self._quoted()

        si_names = {p.name for p in _scenes(SI_SCENES)}
        assert si_names & quoted.keys(), "SI 的场景里找不到 R² 引用"

    def test_all_files_agree(self):
        """重跑后重新拟合，各处要一起改；漏掉任何一处都在这里失败。"""
        quoted = self._quoted()
        values = {v for vs in quoted.values() for v in vs}

        assert len(values) == 1, f"R² 在各处不一致: {quoted}"
