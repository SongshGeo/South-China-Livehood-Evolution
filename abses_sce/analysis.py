#!/usr/bin/env python 3.11.0
# -*-coding:utf-8 -*-
# @Author  : Shuang (Twist) Song
# @Contact   : SongshGeo@gmail.com
# GitHub   : https://github.com/SongshGeo
# Website: https://cv.songshgeo.com/

import sys
from functools import cached_property
from pathlib import Path
from typing import Callable, Iterable, List

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import yaml
from omegaconf import DictConfig


# 自定义堆积折线图绘制函数
def draw_stacked_lineplot(data, x, y, hue, **kwargs):
    """自定义可输入 seaborn.FaceGrid 的堆积图"""
    # 转换数据为堆叠格式
    pivoted = data.pivot_table(index=x, columns=hue, values=y)
    ratio = pivoted.div(pivoted.sum(axis=1), axis=0)
    # 绘制堆积折线图
    colors = kwargs.get("colors")
    plt.stackplot(ratio.index, ratio.T, colors=colors, labels=ratio.columns)


class MultipleAnalysis:
    """分析某组重复实验结果的文件夹"""

    def __init__(self, path: str) -> None:
        self._home = Path(path)
        if not self._is_hydra_multiple_home():
            raise FileExistsError(f"{path} is not a hydra output folder.")
        self._overrides_ids = {}
        self._path_ids = {}
        self._cache_run_ids()

    def __str__(self) -> str:
        return self._home.__str__()

    @property
    def home(self) -> Path:
        """输出路径"""
        return self._home

    @property
    def repeats(self) -> int:
        """每组实验的重复次数"""
        return self.config.exp.repeats

    @property
    def _config(self) -> Path:
        """配置文件所在路径"""
        return self._home / "multirun.yaml"

    @cached_property
    def config(self) -> dict:
        """本次实验的配置"""
        with open(self._config, "r", encoding="utf-8") as file:
            params = yaml.load(file.read(), Loader=yaml.FullLoader)
            file.close()
        return DictConfig(params)

    @cached_property
    def _overrides(self) -> DictConfig:
        """被覆盖的配置"""
        overrides_lst = self.config.hydra.overrides.task
        overrides = {}
        for item in overrides_lst:
            tmp_lst = item.split("=", maxsplit=1)
            overrides[tmp_lst[0]] = pd.to_numeric(pd.Series(tmp_lst[1].split(",")))
        return overrides

    @property
    def overrides(self) -> pd.DataFrame:
        """实验ID和被覆盖的设置"""
        df = pd.DataFrame(self._overrides_ids).T
        df.index.name = "ID"
        return df.sort_index()

    @property
    def sub_folders(self) -> List[Path]:
        """所有实验的子文件夹"""
        return [p for p in self._home.iterdir() if p.is_dir()]

    def _cache_run_ids(self) -> None:
        """将每个实验的配置和对应的id进行缓存"""
        for folder in self.sub_folders:
            config = folder / ".hydra/overrides.yaml"
            with open(config, "r", encoding="utf-8") as file:
                params = yaml.load(file.read(), Loader=yaml.FullLoader)
                file.close()
            dic = {p.split("=")[0]: p.split("=")[1] for p in params}
            flag = int(folder.name.split("_")[-1])
            self._overrides_ids[flag] = pd.to_numeric(pd.Series(dic))
            self._path_ids[flag] = folder

    def _get_data_by_id(self, exp_id: int) -> pd.DataFrame:
        """获取某个实验的所有数据"""
        if not (path := self._path_ids.get(exp_id)):
            raise FileNotFoundError(
                f"Could not find exp id {exp_id}, please choose from {self.overrides.index}."
            )
        dfs = []
        for repeat in range(1, self.repeats + 1):
            df = pd.read_csv(path / f"repeat_{repeat}.csv", index_col=0)
            df["repeat"] = repeat
            df["exp_id"] = exp_id
            for key, value in self.overrides.loc[exp_id, :].items():
                df[key] = value
            dfs.append(df.reset_index().rename(columns={"index": "time"}))
        return pd.concat(dfs)

    def show_overrides(self, key: str | None = None) -> pd.Series:
        """展示所有被覆盖的配置"""
        if key is None:
            return pd.Series(self._overrides.keys())
        return pd.to_numeric(pd.Series(self._overrides[key]))

    def _is_hydra_multiple_home(self) -> bool:
        """判断是否是合适的 hydra multiple 输出文件夹"""
        return self._config.is_file()

    def get_dataset(
        self, exp_ids: int | List[int] | None = None, solver: Callable | None = None
    ) -> pd.DataFrame:
        """根据实验序号获取一组数据。"""
        if exp_ids is None:
            exp_ids = self.overrides.index.to_list()
        if isinstance(exp_ids, int):
            return self._get_data_by_id(exp_ids)
        if isinstance(exp_ids, Iterable):
            dataset = []
            for exp_id in exp_ids:
                data = self._get_data_by_id(exp_id)
                if solver is not None:
                    data = solver(data)
                dataset.append(data)
            return pd.concat(dataset)
        raise TypeError(f"{type(exp_ids)} is not supported.")

    def _clean_to_long_df(
        self,
        df: pd.DataFrame,
        flag: str,
        id_vars: List[str] | None = None,
        to_ratio: bool = False,
    ) -> pd.DataFrame:
        """将一个数据表转换成长表"""
        labels = ["Hunting", "Rainfed", "Paddy"]
        if flag == "num":
            value_vars = ["hunters_num", "farmers_num", "rice_num"]
        elif flag == "len":
            value_vars = ["len_hunters", "len_farmers", "len_rice"]
        else:
            raise ValueError(f"{flag} must be 'num' or 'len'.")
        df.rename(dict(zip(value_vars, labels)), axis=1, inplace=True)
        if id_vars is None:
            id_vars = [col for col in df.columns if col not in labels]
        if to_ratio:
            ratios = df[labels].div(df[labels].sum(axis=1), axis=0)
            df[labels] = ratios
        return pd.melt(
            df,
            id_vars=id_vars,
            value_vars=labels,
            var_name="Agent",
            value_name="Groups" if flag == "len" else "Population",
        )

    def grid_plots(
        self,
        plot_function,
        flag: str,
        col_by: str | None = None,
        row_by: str | None = None,
        hue_by: str | None = None,
        col_wrap: int = None,
        palette_name: str = "Set2",
        **kwargs,
    ) -> sns.FacetGrid:
        """批量画图"""
        df = self.get_dataset()
        data = self._clean_to_long_df(df, flag=flag, to_ratio=True)
        g = sns.FacetGrid(
            data=data,
            row=row_by,
            col=col_by,
            hue=hue_by,
            col_wrap=col_wrap,
            palette=palette_name,
        )
        colors = sns.color_palette(palette_name, 3)
        kwargs["colors"] = colors
        g.map_dataframe(plot_function, **kwargs)
        g.add_legend()
        return g

    def grid_stackplots(
        self, flag: str, col_by: str | None = None, row_by: str | None = None, **kwargs
    ) -> sns.FacetGrid:
        """绘制不同参数组合下的人数比例堆积图"""
        g = self.grid_plots(
            flag=flag,
            col_by=col_by,
            row_by=row_by,
            plot_function=draw_stacked_lineplot,
            x="time",
            y="Population" if flag == "num" else "Groups",
            hue="Agent",
            **kwargs,
        )
        g.set_titles(
            row_template="{row_var}:{row_name}\n", col_template="{col_var}:{col_name}"
        )
        return g


def main(path: str) -> None:
    """绘制路径"""
    analysis = MultipleAnalysis(path)
    overriding_lst = [*analysis.show_overrides()]
    if len(overriding_lst) > 2:
        raise ValueError(
            f"Multiple Exp auto plots only support 1~2 overriding parameters, got {len(overriding_lst)}"
        )
    analysis.grid_stackplots("num", *overriding_lst)
    plt.savefig(analysis.home / "analysis_num.jpg")
    analysis.grid_stackplots("len", *overriding_lst)
    plt.savefig(analysis.home / "analysis_len.jpg")


if __name__ == "__main__":
    main(sys.argv[1])
