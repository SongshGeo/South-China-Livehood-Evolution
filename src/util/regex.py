#!/usr/bin/env python 3.11.0
# -*-coding:utf-8 -*-
# @Author  : Shuang (Twist) Song
# @Contact   : SongshGeo@gmail.com
# GitHub   : https://github.com/SongshGeo
# Website: https://cv.songshgeo.com/

import re

COL_NAMES = {
    "size": "num_breed_n",
    "ratio": "num_breed",
    "group": "len_breed_n",
    "group_ratio": "len_breed",
}

PATTERN = r"^(farmers|hunters|rice) (group|size) (ratio|num)$"
BKP = r"^bkp_(farmers|hunters|rice)"
PRE = r"^pre_(farmers|hunters|rice)"
POST = r"^post_(farmers|hunters|rice)"


def clean_name(attribute: str) -> dict:
    """清理属性名

    将属性名转换为字典，包含主体类型、分组或数量、比例或数量。

    Parameters:
        attribute: str
            属性名，例如 "farmers size ratio"

    Returns:
        dict
            包含主体类型、分组或数量、比例或数量的字典
    """
    if not re.match(PATTERN, attribute):
        raise ValueError(f"Invalid attribute name {attribute}.")
    breed, group_or_size, ratio_or_num = attribute.split()
    return {
        "breed": breed,
        "group": group_or_size == "group",
        "ratio": ratio_or_num == "ratio",
    }
