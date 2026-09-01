# 结果分析

## 一次运行实际产出什么

一个参数组合的输出目录（`out/<exp.name>/<...>/<job_id>_<overrides>/`）里只有数据和
日志，没有图：

| 文件 | 内容 |
| :--- | :--- |
| `1_tracking.csv` … `<repeats>_tracking.csv` | **主力数据**。每次重复一份，一行一个时间步，列是 `tracker` 配置里声明的指标（`num_farmers_n`、`num_hunters_n`、`len_rice_n` …） |
| `repeat_1_conversion.csv` … | 每次重复的人口转化矩阵：模拟结束时各类主体的「出身 × 现状」，4 行 × 3 列 |
| `model.log` / `<exp.name>.log` | 运行日志 |

:::caution 文档曾经写过、但现在不产出的文件
`summary.csv`、`breakpoints.jpg`、`heatmap.jpg`、`len_<breed>_<ratio>.jpg`、
`num_<breed>_<ratio>.jpg` 都来自 `MyExperiment` 的实验级绘图方法，那个类在投稿定稿时
删除了（稿件的图由 `reports/` 下的 notebook 单独产出，见[从模型到手稿]）。
配置里驱动其中热力图的 `exp.plot_heatmap` 键也一并删除。
:::

单次运行的 `dynamic.jpg` / `heatmap.jpg` 仍然存在，但**默认不写盘**：只有把参数
`save_plots` 设为 true，`Model.plot` 才会拿到保存路径（`src/core/model.py`）。

## 怎么把 multirun 拼成一张长表

不要自己再写一遍加载器。`src/workflow/figures.py` 里有四个成品，覆盖四种目录布局：

| 函数 | 适用的目录 |
| :--- | :--- |
| `load_trajectories` | `<job_id>_<k=v,k=v>/`（Hydra multirun 的常规输出） |
| `load_single_run` | 直接含 `<run_id>_tracking.csv` 的单个组合目录 |
| `load_fine_grid` | `idx<n>_f2h<a>_h2f<b>/`（SLURM job array 的网格） |
| `load_terrain` | 地貌实验那种两层嵌套的目录 |

四个都返回 tidy 长表，列含 `step`、指标列、`run_id` 以及从目录名解析出的各 override，
可以直接交给 `seaborn.relplot`。原理和最小实现见[数据输出指南]，稿件里的用法见
[从模型到手稿]。

## 终态怎么取

跨重复比较时统一取**末 51 步的均值**（`step >= max_step - 50`，左端点含在内），
由 `figures.TAIL_STEPS` 持有这一个值，`src/workflow/results.py` 复用同一个函数。
两边各写一个 50，就会变成两条能各自漂移的终态定义。

## 示例

```python
from pathlib import Path
from src.workflow import figures as F

lam = F.load_trajectories(Path("out/south_china_evolution/rerun_v3/lam"))
end = F._tail_mean(lam, ["env.lam_farmer", "run_id"], ["num_farmers_n"])
print(end.groupby("env.lam_farmer")["num_farmers_n"].mean())
```

<!-- Links -->
[数据输出指南]: /docs/output_data_guide
[从模型到手稿]: /docs/usage/manuscript_pipeline
