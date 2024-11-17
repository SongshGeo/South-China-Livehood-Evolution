#!/usr/bin/env python 3.11.0
# -*-coding:utf-8 -*-
# @Author  : Shuang (Twist) Song
# @Contact   : SongshGeo@gmail.com
# GitHub   : https://github.com/SongshGeo
# Website: https://cv.songshgeo.com/

import os

import numpy as np
from abses.viz.solara import make_mpl_space_component
from hydra import compose, initialize
from matplotlib.colors import hex2color
from mesa.visualization import SolaraViz, make_plot_component, make_space_component

from src.api import CompetingCell, ToyEnv
from src.core import Model

# 加载项目层面的配置
with initialize(version_base=None, config_path="../config"):
    cfg = compose(config_name="config")
os.chdir(cfg.root)

WATER_COLOR = "#0D92F4"


def cell_portrayal(cell: CompetingCell):
    """斑块的绘制"""
    if np.isnan(cell.elevation):
        return 0, 0, 0, 0
    if cell.is_water:
        return *hex2color(WATER_COLOR), 1.0
    return (
        (1 - cell.elevation / 1000) * 74,
        (1 - cell.elevation / 1000) * 141,
        0,
        1,
    )


def agent_portrayal(agent):
    if agent.breed == "Farmer":
        return {
            "color": "red",
            "shape": "o",
            "size": 20,
        }
    elif agent.breed == "Hunter":
        return {
            "color": "blue",
            "shape": "o",
            "size": 5,
        }
    else:
        return {}


propertylayer_portrayal = {
    "elevation": {
        "colormap": "Greens",
        "alpha": 1,
    },
    # "temperature": {
    #     "colormap": "coolwarm",
    #     "alpha": 0.333,
    #     "vmin": 0,
    #     "vmax": 100
    # },
}


model = Model(cfg, nature_class=ToyEnv)
model.register_agents()
model.nature.setup()

page = SolaraViz(
    model,
    [
        # make_geospace_leaflet(cell_portrayal, zoom=4.3),
        make_mpl_space_component(agent_portrayal),
        make_plot_component(["len_farmers", "len_hunters", "len_rice"]),
    ],
    name="South China Agricultural Livelihood Evolution",
)

if __name__ == "__main__":
    page
