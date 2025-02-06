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

WATER_COLOR = "#0D92F4"


class ToyEnv(Env):
    """玩具环境"""

    def setup_dem(self):
        """创建数字高程模型"""
        width = self.p.width
        height = self.p.height
        shape = height, width

        self.dem = self.create_module(
            how="from_resolution",
            shape=shape,
            cell_cls=CompetingCell,
        )
        water = np.random.random(shape) < 0.2
        self.dem.apply_raster(np.random.randint(0, 1000, shape), attr_name="elevation")
        self.dem.apply_raster(np.ones(shape), attr_name="slope")
        self.dem.apply_raster(np.full(shape, self.p.lim_h), attr_name="lim_h")
        self.dem.apply_raster(water, attr_name="is_water")


class ToyModel(Model):
    """玩具模型"""

    def __init__(self, **kwargs):
        super().__init__(parameters=cfg, nature_class=ToyEnv, **kwargs)
        self.input_settings = kwargs


def agent_portrayal(agent):
    """绘制代理
    其中农民用红色，猎人用蓝色
    """
    if agent.breed == "Farmer":
        return {
            "color": "red",
            "shape": "o",
            "size": agent.size,
        }
    if agent.breed == "Hunter":
        return {
            "color": "blue",
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
    "elevation": {
        "colormap": "viridis",
        "alpha": 0.3,
        "zorder": 1,
    },
    "is_water": {
        "colormap": "Blues",
        "alpha": 0.8,
        "vmin": 0,
        "vmax": 1,
        "zorder": 2,
    },
}


def display_model_settings(my_model: Model):
    """Display the model settings in a formatted way."""
    settings_str = pformat(my_model.settings, indent=2)
    return solara.Markdown(f"**Model Settings:**\n```python\n{settings_str}\n```")


def display_input_settings(my_model: Model):
    """Display the input settings in a formatted way."""
    settings_str = pformat(my_model.input_settings, indent=2)
    return solara.Markdown(f"**Input Settings:**\n```python\n{settings_str}\n```")


model_params = {}
for k, v in VIZ_CONFIG.items():
    value = OmegaConf.select(cfg, k)
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
        make_plot_component(["len_farmers", "len_hunters", "len_rice"]),
        display_model_settings,
        display_input_settings,
    ],
    name="Livelihood Evolution",
    model_params=model_params,
)

if __name__ == "__main__":
    page
