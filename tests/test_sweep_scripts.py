#!/usr/bin/env python 3.11.0
# -*-coding:utf-8 -*-
# @Author  : Shuang (Twist) Song
# @Contact   : SongshGeo@gmail.com
# GitHub   : https://github.com/SongshGeo
# Website: https://cv.songshgeo.com/

"""SLURM 扫描脚本与文稿表格的一致性。

`paper/build_tables.py::swept_ranges` 从 `run_slurm.sh` 里读 `F2H_VALUES` /
`H2F_VALUES` 两个数组，填进 Table S1 的 "Swept" 列。但重跑用的是
`run_slurm_rerun.sh`。两个脚本各写一份扫描值，一旦分叉，表里报告的扫描范围就与
真正产出数据的脚本不符——而且不会有任何报错。这里把等式锁住。
"""

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = (ROOT / "run_slurm.sh", ROOT / "run_slurm_rerun.sh")


def _bash_array(script: Path, name: str) -> list[float]:
    """从 bash 脚本里读出顶层的 `NAME=(v1 v2 ...)` 数组。

    只认顶格声明，与 `build_tables.py::swept_ranges` 的解析方式保持一致。
    """
    for line in script.read_text(encoding="utf-8").splitlines():
        if line.startswith(f"{name}="):
            body = line.split("(", 1)[1].rstrip(")")
            return [float(v) for v in body.split()]
    raise AssertionError(f"{name} not declared at top level in {script.name}")


class TestSweptValuesAgree:
    """两个扫描脚本必须报告同一组精细网格取值。"""

    @pytest.mark.parametrize("name", ["F2H_VALUES", "H2F_VALUES"])
    def test_both_scripts_declare_the_same_values(self, name):
        """run_slurm.sh 与 run_slurm_rerun.sh 的扫描值逐项相等。"""
        original, rerun = (_bash_array(s, name) for s in SCRIPTS)

        assert original == rerun, (
            f"{name} 在两个脚本里不一致；"
            f"paper/build_tables.py 读的是 run_slurm.sh，会把错误的范围写进 Table S1"
        )

    @pytest.mark.parametrize("name", ["F2H_VALUES", "H2F_VALUES"])
    def test_values_are_an_even_grid(self, name):
        """取值必须是等距的——Table S1 用首末值加步长概括，不等距就会失真。"""
        values = _bash_array(SCRIPTS[0], name)
        steps = {round(b - a, 12) for a, b in zip(values, values[1:])}

        assert len(values) == 11
        assert len(steps) == 1, f"{name} 不是等距网格: {sorted(steps)}"


class TestRerunTaskList:
    """重跑脚本的任务清单本身。"""

    @staticmethod
    def _task_dirs() -> list[str]:
        import subprocess

        out = subprocess.run(
            ["bash", str(ROOT / "run_slurm_rerun.sh"), "--list"],
            capture_output=True,
            text=True,
            check=True,
        ).stdout
        return [
            line.split(None, 1)[1].split("|", 1)[0]
            for line in out.splitlines()
            if re.match(r"^\s*\d+\s", line)
        ]

    def test_task_count_matches_the_sbatch_array(self):
        """任务数必须与 #SBATCH --array 的上界一致，否则末尾的组合永远不会被投出。"""
        dirs = self._task_dirs()
        header = (ROOT / "run_slurm_rerun.sh").read_text(encoding="utf-8")
        upper = int(re.search(r"#SBATCH --array=0-(\d+)", header).group(1))

        assert len(dirs) == upper + 1

    def test_every_task_has_a_distinct_output_dir(self):
        """两个任务写进同一个目录会互相覆盖，且断点恢复会误判为已完成。"""
        dirs = self._task_dirs()

        assert len(set(dirs)) == len(dirs)

    def test_fine_grid_index_matches_the_original_run(self):
        """精细网格的组内 idx 必须与 run_slurm.sh 的 INDEX%11 映射一致。

        这样同一个 idx 在新旧两批数据里指同一组参数，可以交叉核对。
        """
        f2h_values = _bash_array(SCRIPTS[0], "F2H_VALUES")
        h2f_values = _bash_array(SCRIPTS[0], "H2F_VALUES")
        fine = [d for d in self._task_dirs() if "/grid_fine/" in d]

        assert len(fine) == len(f2h_values) * len(h2f_values)
        for index, path in enumerate(fine):
            m = re.search(r"idx(\d+)_f2h([\d.]+)_h2f([\d.]+)$", path)
            assert m and int(m.group(1)) == index
            assert float(m.group(2)) == f2h_values[index % 11]
            assert float(m.group(3)) == h2f_values[index // 11]
