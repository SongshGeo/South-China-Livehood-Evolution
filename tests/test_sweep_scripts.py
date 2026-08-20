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
import shutil
import subprocess
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


class TestForagerCapacityArms:
    """Figure 4b 的三档承载力，以及基线必须是其中一档。

    `{15, 25, 35}` 这个三元组曾同时硬编码在四个互不相干的地方：产数据的
    `run_slurm_rerun.sh`、`paper/build_tables.py` 的两处字符串字面量、以及主文
    Methods。改一处不会有任何报错，表里报告的扫描范围就与真正跑的数据不符。
    `build_tables.limh_swept()` 现在从脚本里读，这里锁住剩下的那条不变式：
    `config/config.yaml` 的基线取值必须落在被扫的三档里——否则 Fig 4b 的三条曲线
    没有一条对应其它所有图共用的基线，"以基线为参照"这句话就没有着落。
    """

    @staticmethod
    def _swept() -> list[int]:
        import sys

        sys.path.insert(0, str(ROOT / "paper"))
        from build_tables import limh_swept

        return limh_swept()

    def test_script_declares_three_arms(self):
        """Fig 4b 是三条曲线，脚本里就该正好三档。"""
        assert len(self._swept()) == 3

    def test_baseline_is_one_of_the_swept_arms(self):
        """`config/config.yaml` 的 env.lim_h 必须是被扫的一档。"""
        text = (ROOT / "config" / "config.yaml").read_text(encoding="utf-8")
        # `env.lim_h` 是两个同名键中的标量那个；`ds.lim_h` 是栅格路径，不能误取。
        baseline = int(re.search(r"^  lim_h: (\d+)", text, re.MULTILINE).group(1))

        assert baseline in self._swept(), (
            f"基线 lim_h={baseline} 不在扫描值 {self._swept()} 里；"
            "Fig 4b 的三条曲线将没有一条对应其它图的基线"
        )


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


class TestVerifyAndResubmit:
    """`--verify` 与它给出的重投命令。

    重跑失败后，这两样东西决定了"哪些组合还要再跑"。算错了要么白跑几百个
    task-hour，要么漏掉组合、拿不完整的数据出图，所以直接拿真实脚本跑。
    每个用例都在临时目录里搭一个只含必要文件的假仓库，不碰真实的 out/。
    """

    @pytest.fixture(name="repo")
    def mock_repo(self, tmp_path):
        """假仓库：脚本副本 + verify 要读的 config/config.yaml。"""
        shutil.copy(ROOT / "run_slurm_rerun.sh", tmp_path / "run_slurm_rerun.sh")
        (tmp_path / "config").mkdir()
        (tmp_path / "config" / "config.yaml").write_text(
            "exp:\n  repeats: 5\n", encoding="utf-8"
        )
        return tmp_path

    @staticmethod
    def _run(repo: Path, *args: str) -> subprocess.CompletedProcess:
        """跑假仓库里的那份脚本——它会把工作目录切到自己所在的仓库根。"""
        return subprocess.run(
            ["bash", str(repo / "run_slurm_rerun.sh"), *args],
            capture_output=True,
            text=True,
            cwd=repo,
        )

    @staticmethod
    def _fill(repo: Path, task_dir: str, run_ids) -> None:
        """在某个组合目录里放上指定编号的 tracking.csv。"""
        target = repo / task_dir
        target.mkdir(parents=True, exist_ok=True)
        for i in run_ids:
            (target / f"{i}_tracking.csv").write_text("step\n", encoding="utf-8")

    def _first_task_dir(self, repo: Path) -> str:
        listing = self._run(repo, "--list").stdout.splitlines()
        return listing[0].split(None, 1)[1].split("|", 1)[0]

    def test_reports_everything_missing_when_nothing_ran(self, repo):
        """一个产出都没有时全部计入 missing，并以非零退出。"""
        out = self._run(repo, "--verify")

        assert "complete: 0" in out.stdout
        assert "missing: 216" in out.stdout
        assert out.returncode == 1

    def test_complete_combination_is_excluded_from_the_resubmit(self, repo):
        """凑齐 repeats 个确切命名的 CSV 才算完成，且不再出现在重投区间里。"""
        self._fill(repo, self._first_task_dir(repo), range(1, 6))

        out = self._run(repo, "--verify")

        assert "complete: 1" in out.stdout
        # 0 号已完成，重投区间必须从 1 开始
        assert "--array=1-215" in out.stdout

    def test_stray_csv_does_not_count_towards_completion(self, repo):
        """杂散的 *_tracking.csv 不能顶数。

        `src/__main__.py` 要的是 1..repeats 这些确切文件名。verify 若用通配去数，
        两边判据就会分歧：verify 报完成，实际投出去却整组重跑。
        """
        self._fill(repo, self._first_task_dir(repo), [1, 2, 3, 4, 99])

        out = self._run(repo, "--verify")

        assert "complete: 0" in out.stdout
        assert "has 4/5" in out.stdout

    def test_all_complete_reports_success(self, repo):
        """全部齐了要以 0 退出，并且不再打印重投命令。"""
        for line in self._run(repo, "--list").stdout.splitlines():
            if not re.match(r"^\s*\d+\s", line):
                continue
            self._fill(repo, line.split(None, 1)[1].split("|", 1)[0], range(1, 6))

        out = self._run(repo, "--verify")

        assert "all tasks complete" in out.stdout
        assert "resubmit" not in out.stdout
        assert out.returncode == 0

    def test_resubmit_line_compresses_runs_into_ranges(self, repo):
        """未完成的任务号要压成 SLURM 区间，几百个逗号是没法用的。"""
        dirs = [
            line.split(None, 1)[1].split("|", 1)[0]
            for line in self._run(repo, "--list").stdout.splitlines()
            if re.match(r"^\s*\d+\s", line)
        ]
        for index in (0, 1, 2, 5):
            self._fill(repo, dirs[index], range(1, 6))

        out = self._run(repo, "--verify")

        assert "--array=3-4,6-215" in out.stdout
