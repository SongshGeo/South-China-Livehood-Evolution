#!/usr/bin/env python 3.11.0
# -*-coding:utf-8 -*-
# @Author  : Shuang (Twist) Song
# @Contact   : SongshGeo@gmail.com
# GitHub   : https://github.com/SongshGeo
# Website: https://cv.songshgeo.com/

"""种子可复现性测试。

模型的每一次抽样都必须走模型自己的 seeded 生成器。历史上有两个缺陷叠在一起：
`Env.add_farmers` 的移民数量用的是全局 NumPy 流（issue #30），而且 `src/__main__.py`
根本没有把种子传给 `Experiment`，所以每个 replicate 都退回操作系统熵。移民是农业
人口的唯一来源，两者合起来意味着同一份配置的两次运行不会逐步一致。这里把修复后的
行为锁住。

注意这里合成的是生产配置 `config/config.yaml` 而不是 `tests/config_test.yaml`：
后者没有 `ds` 栅格路径，`Env.setup_dem` 无法初始化，跑不了整模型。
"""

from unittest.mock import MagicMock, patch

import numpy as np
import pandas as pd
from hydra import compose, initialize
from omegaconf import OmegaConf

from src.api import Env
from src.core import Model

with initialize(version_base=None, config_path="../config"):
    cfg = compose(config_name="config")


def _fast_cfg(tmp_path):
    """一份跑得快的配置副本：少量初始狩猎采集者、三步就停。

    `init_hunters` 取整数时按"个数"而非"比例"解释（`Env.add_hunters`），所以 20
    就是 20 个狩猎采集者。`outpath` 指向临时目录，避免模型把 `Model/` 落到仓库根目录。
    """
    fast = OmegaConf.create(OmegaConf.to_container(cfg, resolve=True))
    fast.env.init_hunters = 20
    fast.time.end = 3
    fast.exp.save_data = False
    fast.outpath = str(tmp_path)
    return fast


def _tracking_of(seed: int, tmp_path) -> pd.DataFrame:
    """跑一次短模型，返回它逐步记录的追踪数据。"""
    model = Model(parameters=_fast_cfg(tmp_path), nature_class=Env, seed=seed)
    model.run_model()
    return model.datacollector.get_model_vars_dataframe()


class TestSeededReproducibility:
    """同种子逐 run 复现，不同种子给出不同轨迹。"""

    def test_same_seed_reproduces_exactly(self, tmp_path):
        """同一个种子的两次运行必须逐行相等。"""
        assert _tracking_of(7, tmp_path).equals(_tracking_of(7, tmp_path))

    def test_different_seeds_diverge(self, tmp_path):
        """不同种子必须给出不同轨迹，否则说明种子根本没起作用。"""
        assert not _tracking_of(7, tmp_path).equals(_tracking_of(8, tmp_path))

    def test_run_does_not_touch_the_global_numpy_stream(self, tmp_path):
        """回归 #30：模型不得消费全局 NumPy 流。

        `np.random.poisson` 走的是全局流，会让同种子的两次 run 分道扬镳。修复后
        整个 run 都不应该改变全局流的状态。
        """
        np.random.seed(0)
        before = np.random.get_state()
        _tracking_of(7, tmp_path)
        after = np.random.get_state()

        assert before[0] == after[0]
        np.testing.assert_array_equal(before[1], after[1])
        assert before[2:] == after[2:]


class TestSeedIsWiredThrough:
    """种子必须真的从配置流到 Experiment。

    这一组测的是 `src/__main__.py` 那一行本身——直接构造 `Experiment(..., seed=...)`
    的测试无法发现"入口忘了传种子"，而那正是当初的缺陷。
    """

    def test_config_carries_a_base_seed(self):
        """config.yaml 必须带一个基种子，否则 Experiment 会退回操作系统熵。"""
        assert cfg.get("seed") is not None

    def test_main_passes_the_config_seed_to_the_experiment(self, tmp_path):
        """入口必须把 cfg.seed 作为具名参数交给 Experiment。

        混进 `**kwargs` 会被转发给模型构造函数，replicate 仍然拿不到种子，所以这里
        断言的是关键字本身而不只是"调用过"。
        """
        from src import __main__ as entry

        run_cfg = _fast_cfg(tmp_path)
        run_cfg.seed = 4321

        with patch.object(entry, "Experiment") as fake_experiment:
            # outpath 下的 tracking.csv 被认为已存在，main 因此在 batch_run 前返回
            fake_experiment.return_value = MagicMock()
            entry.main(run_cfg)

        assert fake_experiment.call_args.kwargs["seed"] == 4321
