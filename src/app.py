#!/usr/bin/env python 3.11.0
# -*-coding:utf-8 -*-
# @Author  : Shuang (Twist) Song
# @Contact   : SongshGeo@gmail.com
# GitHub   : https://github.com/SongshGeo
# Website: https://cv.songshgeo.com/

import os
from importlib import resources
from pathlib import Path
from pprint import pformat
from typing import Any, Dict

import numpy as np
import solara
import yaml
from abses.viz.solara import make_mpl_space_component
from hydra import compose, initialize
from mesa.visualization import Slider, SolaraViz, make_plot_component
from omegaconf import OmegaConf

from src.api import CompetingCell, Env
from src.core import Model

# 加载可视化配置
with open(
    Path(str(resources.files("config") / "viz_config.yaml")), "r", encoding="utf-8"
) as f:
    VIZ_CONFIG: Dict[str, dict[str, Any]] = yaml.safe_load(f)

# 加载项目层面的配置
with initialize(version_base=None, config_path="../config"):
    cfg = compose(config_name="config")
os.chdir(cfg.root)

notes = []


class ToyEnv(Env):
    """玩具环境"""

    def setup_dem(self):
        """创建数字高程模型"""
        width = self.p.width
        height = self.p.height
        shape = height, width
        arable_ratio = self.p.get("arable_ratio", 0.1)  # 默认可耕地比例为10%
        water_ratio = self.p.get("water_ratio", 0.2)  # 水体比例
        rice_arable_ratio = self.p.get("rice_arable_ratio", 0.05)  # 水稻可耕地比例，默认为5%

        # 计算水稻可耕地在可耕地中的比例，限制最大为0.7（70%）
        rice_in_arable_ratio = min(0.2, rice_arable_ratio / max(arable_ratio, 0.001))

        self.dem = self.create_module(
            how="from_resolution",
            shape=shape,
            cell_cls=CompetingCell,
        )

        # 计数器，用于调试
        arable_count = 0
        rice_count = 0
        water_count = 0

        # 遍历所有单元格，设置属性
        for i in range(height):
            for j in range(width):
                cell = self.dem.array_cells[i, j]

                # 设置水体
                is_water = np.random.random() < water_ratio
                cell.is_water = is_water
                if is_water:
                    water_count += 1
                    # 水体的属性
                    cell.elevation = 0
                    cell.slope = 30  # 设置一个大坡度，确保不会被识别为可耕地
                    continue

                # 随机决定是否为可耕地
                is_arable = np.random.random() < arable_ratio

                if is_arable:
                    arable_count += 1
                    # 设置可耕地的属性
                    cell.elevation = np.random.uniform(1, 199)

                    # 随机决定是否为水稻可耕地，使用固定的比例
                    if np.random.random() < rice_in_arable_ratio:
                        rice_count += 1
                        # 设置水稻可耕地的属性（坡度更小）
                        cell.slope = np.random.uniform(0, 0.5)
                    else:
                        # 设置普通可耕地的属性（坡度较大但仍在可耕地范围内）
                        cell.slope = np.random.uniform(0.6, 9.9)
                else:
                    # 非可耕地的随机属性
                    cell.elevation = np.random.uniform(0, 1000)
                    cell.slope = np.random.uniform(10, 30)

                # 设置lim_h
                cell.lim_h = self.p.lim_h

        # 打印调试信息
        total_cells = width * height
        notes.append(f"总单元格数: {total_cells}")
        notes.append(f"水体数量: {water_count} ({water_count / total_cells : .2%})")
        notes.append(f"可耕地数量: {arable_count} ({arable_count / total_cells : .2%})")
        notes.append(f"水稻可耕地数量: {rice_count} ({rice_count / total_cells : .2%})")
        notes.append(f"水稻可耕地目标比例: {rice_in_arable_ratio : .2%}")

        # 验证实际的可耕地和水稻可耕地
        actual_arable = 0
        actual_rice = 0
        actual_only_arable = 0
        for i in range(height):
            for j in range(width):
                cell = self.dem.array_cells[i, j]
                if cell.is_arable:
                    actual_arable += 1
                if cell.is_rice_arable:
                    actual_rice += 1
                if cell.is_only_arable:
                    actual_only_arable += 1

        notes.append(f"实际可耕地数量: {actual_arable} ({actual_arable / total_cells:.2%})")
        notes.append(f"实际水稻可耕地数量: {actual_rice} ({actual_rice / total_cells:.2%})")
        notes.append(
            f"实际仅普通可耕地数量: {actual_only_arable} ({actual_only_arable / total_cells:.2%})"
        )
        notes.append(f"水稻可耕地占可耕地比例: {actual_rice / max(actual_arable, 1):.2%}")


class ToyModel(Model):
    """玩具模型"""

    def __init__(self, **kwargs):
        super().__init__(parameters=cfg, nature_class=ToyEnv, **kwargs)
        self.input_settings = kwargs


def agent_portrayal(agent):
    """绘制代理"""
    if agent.breed == "Farmer":
        return {
            "color": "blue",
            "shape": "o",
            "size": agent.size,
        }
    if agent.breed == "Hunter":
        return {
            "color": "orange",
            "shape": "o",
            "size": agent.size,
        }
    if agent.breed == "RiceFarmer":
        return {
            "color": "green",
            "shape": "o",
            "size": agent.size,
        }
    return {}


propertylayer_portrayal = {
    "is_only_arable": {
        "colormap": "YlOrBr",  # 使用黄橙棕色系表示普通可耕地
        "alpha": 0.8,
        "zorder": 2,
        "vmin": 0,
        "vmax": 1,
    },
    "is_rice_arable": {
        "colormap": "Greens",  # 使用绿色系表示水稻可耕地
        "alpha": 0.8,
        "zorder": 1,
        "vmin": 0,
        "vmax": 1,
    },
    "is_water": {
        "colormap": "Blues",
        "alpha": 0.8,
        "vmin": 0,
        "vmax": 1,
        "zorder": 0,
    },
}


def display_model_settings(my_model: Model):
    """Display the model settings in a formatted way."""
    settings_str = pformat(my_model.settings, indent=2)
    return solara.Markdown(f"**Model Settings:**\n```python\n{settings_str}\n```")


def display_input_settings(my_model: Model):
    """Display the input settings in a formatted way."""
    settings_str = pformat(my_model.input_settings, indent=2)
    return solara.Markdown(f"\n**Input Settings:**\n```python\n{settings_str}\n```")


def display_statistics(my_model: Model):
    """Display the statistics in a formatted way."""
    n1 = f"最大群体人口数量: {my_model.actors.array('size').max():.2f}"
    n2 = f"最小群体人口数量: {my_model.actors.array('size').min():.2f}"
    n3 = f"平均群体人口数量: {my_model.actors.array('size').mean():.2f}"
    return solara.Markdown("\n".join(notes) + "\n" + n1 + "\n" + n2 + "\n" + n3)


model_params = {}
for k, v in VIZ_CONFIG.items():
    default_value = v.get("min", 0) + v.get("max", 1) / 2
    value = OmegaConf.select(cfg, k, default=default_value)
    v.update(value=value)
    if v["type"] == "Slider":
        del v["type"]
        model_params[k] = Slider(**v)
    elif v["type"] == "InputText":
        model_params[k] = v
    else:
        raise ValueError(f"Unsupported type: {v['type']}")


page = SolaraViz(
    model=ToyModel(),
    components=[
        make_mpl_space_component(agent_portrayal, propertylayer_portrayal),
        make_plot_component(
            [
                "len_farmers",
                "len_hunters",
                "len_rice",
            ],
        ),
        make_plot_component(
            [
                "num_farmers",
                "num_hunters",
                "num_rice",
            ],
        ),
        display_model_settings,
        display_statistics,
        display_input_settings,
    ],
    name="Livelihood Evolution",
    model_params=model_params,
)

if __name__ == "__main__":
    page
