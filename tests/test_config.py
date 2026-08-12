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
