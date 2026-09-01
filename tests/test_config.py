#!/usr/bin/env python 3.11.0
# -*-coding:utf-8 -*-
# @Author  : Shuang (Twist) Song
# @Contact   : SongshGeo@gmail.com
# GitHub   : https://github.com/SongshGeo
# Website: https://cv.songshgeo.com/

"""基线配置的组合结果。

`config/config.yaml` 是文稿参数表（Table S1 / S4）唯一的数值来源，也是所有实验的
起点，所以这里锁住 Hydra **实际组合出来**的值，而不是逐行读 yaml。

曾经有一个 `scenario` 配置组用来切换 Hunter/Farmer/RiceFarmer 的 loss 组合，但四个
文件都漏了 `# @package _global_`，于是 Hydra 把它们并到 `cfg.scenario.*` 之下，从未
覆盖到顶层的 loss 参数——四个“情景”组合出完全相同的参数（issue #31）。该实验臂已删除。

这里刻意在模块层直接 compose，而不复用 `conftest.py` 的夹具：被测对象就是组合本身，
借助辅助函数只会变成拿组合结果去断言辅助函数。
"""

import pytest
from hydra import compose, initialize
from omegaconf import OmegaConf

with initialize(version_base=None, config_path="../config"):
    cfg = compose(config_name="config")


class TestBaselineComposition:
    """Hydra 组合出的基线参数。"""

    def test_no_inert_config_group_remains(self):
        """组合结果里不应再有 `scenario` 键。

        它的存在本身就是那个失效实验臂的标志：值待在 `cfg.scenario.*`，
        真正生效的却是 `config.yaml` 里的内联块。
        """
        assert "scenario" not in cfg

    def test_every_exp_key_still_has_a_reader(self):
        """`exp:` 底下不能有没人读的键。

        这是 F5 那条教训的一般化：`scenario` 组失效了整整四个实验臂，唯一的症状
        就是"配置在、文档在、没人读、不报错"。`exp.plot_heatmap` 后来重蹈覆辙——
        它驱动的是 `MyExperiment.plot_heatmap`，那个类删掉之后键就成了哑弹，而
        文档站还在教人怎么用它。这里把每个键和它的消费者一一对上：

        - `outdir` / `name`  abses 的 `hydra.run.dir` 插值（`abses/conf/default.yaml`），
          即 `out/<name>/...`。这两个由 abses 的默认配置提供，本仓库只覆盖 `name`。
        - `repeats`     `src/__main__.py`：断点恢复判据 + `batch_run`
        - `num_process` `src/__main__.py`：`batch_run(parallels=...)`
        - `logging`     abses（`abses/utils/config.py` 校验 once/always/bool）
        - `save_data`   `src/core/model.py::export_tracker_data` 的开关

        新增键时把消费者一起写进来；写不出消费者，就说明这个键不该存在。
        """
        assert set(cfg.exp) == {
            "outdir",
            "name",
            "repeats",
            "num_process",
            "logging",
            "save_data",
        }

    @pytest.mark.parametrize(
        # 这三组值同时写在文稿的 Table S1 / S4 里，改动时两边都要更新
        "breed, prob, rate",
        [
            ("Hunter", 0.05, 0.01),
            ("Farmer", 0.01, 0.05),
            ("RiceFarmer", 0.01, 0.05),
        ],
        ids=["hunter", "farmer", "rice_farmer"],
    )
    def test_baseline_loss_parameters(self, breed, prob, rate):
        """基线 loss 参数就是文稿里报告的那一组。

        这不是拿 yaml 断言 yaml：`defaults: - default` 经 `hydra.searchpath` 解析到
        `pkg://abses.conf`，组合结果是跨包合并的产物。缺了 loss 块也不会报错——
        `SiteGroup.loss` 会安静跳过——死亡机制会无声消失，所以这里断言的是全等。
        """
        assert OmegaConf.to_container(cfg[breed].loss) == {"prob": prob, "rate": rate}
