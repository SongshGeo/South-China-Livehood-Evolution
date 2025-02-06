#!/usr/bin/env python 3.11.0
# -*-coding:utf-8 -*-
# @Author  : Shuang (Twist) Song
# @Contact   : SongshGeo@gmail.com
# GitHub   : https://github.com/SongshGeo
# Website: https://cv.songshgeo.com/

import os
from pprint import pformat

import numpy as np
import solara
from abses.viz.solara import make_mpl_space_component
from hydra import compose, initialize
from mesa.visualization import Slider, SolaraViz, make_plot_component

from src.api import CompetingCell, Env
from src.core import Model

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
        self.dem.apply_raster(np.ones(shape), attr_name="lim_h")
        self.dem.apply_raster(water, attr_name="is_water")


class ToyModel(Model):
    """玩具模型"""

    def __init__(self, **kwargs):
        super().__init__(parameters=cfg, nature_class=ToyEnv, **kwargs)
        self.input_settings = kwargs
        self.register_agents()
        self.nature.setup_dem()
        self.nature.setup()


def agent_portrayal(agent):
    """绘制代理
    其中农民用红色，猎人用蓝色
    """
    if agent.breed == "Farmer":
        return {
            "color": "red",
            "shape": "o",
            "size": 20,
        }
    if agent.breed == "Hunter":
        return {
            "color": "blue",
            "shape": "o",
            "size": 5,
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


model_params = {
    "seed": {
        "type": "InputText",
        "value": 42,
        "label": "Random Seed",
    },
    "env.init_hunters": {
        "type": "InputText",
        "value": 1,
        "label": "Initial Hunters",
    },
    "env.width": Slider(
        "Width",
        value=15,
        min=1,
        max=100,
        step=1,
    ),
    "env.height": Slider(
        "Height",
        value=15,
        min=1,
        max=100,
        step=1,
    ),
}


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
