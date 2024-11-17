#!/usr/bin/env python 3.11.0
# -*-coding:utf-8 -*-
# @Author  : Shuang (Twist) Song
# @Contact   : SongshGeo@gmail.com
# GitHub   : https://github.com/SongshGeo
# Website: https://cv.songshgeo.com/

from __future__ import annotations

from typing import TYPE_CHECKING

from abses import ActorsList

if TYPE_CHECKING:
    from src.core.exp import ActorType
    from src.core.model import LivelihoodModel


def counting(
    model: LivelihoodModel,
    breed: ActorType,
    ratio: bool = False,
    group: bool = False,
) -> int | float:
    """根据条件，统计某个主体的数量

    Parameters:
        model: LivelihoodModel
            模型实例，必须是生计模型
        breed: ActorType
            主体类型
        ratio: bool
            是否计算比例
        group: bool
            是否计算分组
    """
    actors: ActorsList = getattr(model, breed)
    num = len(actors) if group else actors.array("size").sum()
    if num == 0:
        return 0.0
    if not ratio:
        return num
    if group:
        return num / len(model.agents)
    return num / model.actors.array("size").sum()
