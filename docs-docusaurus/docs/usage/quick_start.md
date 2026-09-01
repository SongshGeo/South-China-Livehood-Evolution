# 快速开始

本模型的主要工作流程已经集成完毕。用户可以在命令行中运行模型。

## 核心规则

- **每格一主体**：每个格子只能有一个主体，严格遵守空间约束
- **水体类型系统**：水体图层区分 -1（海）、0（陆地）、1（近水陆地）。注意实际输入里
  海洋是该图层的 nodata、随整幅栅格一起被掩掉，所以 6835 个建模格子全是陆地；水体的
  作用是通过 1064 个近水格把 `Hunter.max_size` 从 100 抬到 500
- **全局人口上限**：狩猎采集者总人口不超过 `lim_h × 建模栅格数量`（基线 28 × 6835 = 191 380），
  由环境在每个时间步末统一施加
- **无竞争机制**：主体不能移动到已有其他主体的格子

## 环境配置

:::note
本模型需要 Python 3.11，依赖由 [uv](https://docs.astral.sh/uv/) 管理。请先安装 `uv`（macOS/Linux：`curl -LsSf https://astral.sh/uv/install.sh | sh`）。
:::

首先将本模型克隆到本地，注意替换`<your folder name>`为你喜欢的文件夹名称：

```bash
git clone https://github.com/SongshGeo/South-China-Livehood-Evolution.git <your folder name>
```

然后在终端进入模型所在文件夹：

```bash
cd <your folder name>
```

安装依赖：

```bash
# 运行时 + 开发依赖
uv sync

# 如果还要跑 reports/ 下的 notebook
uv sync --all-groups
```

`uv sync` 会按 `uv.lock` 创建 `.venv` 并以可编辑方式安装本项目。

## 运行模型

### 基本运行

```bash
uv run python src
```

### 多情景运行测试

```bash
uv run python src --multirun init_hunters=0.05,0.1,0.2 env.lam_farmer=1,2,3
```

### 参数覆盖

您可以在运行时覆盖特定的参数值：

```bash
# 覆盖单个参数
uv run python src env.init_farmers=100

# 覆盖多个参数
uv run python src env.init_farmers=100 env.init_rice_farmers=400
```

### 批量实验

批量运行实验时，所有参数的笛卡尔积组合都会被运行：

```bash
# 批量实验示例
uv run python src --multirun init_hunters=0.05,0.1,0.2 env.lam_farmer=1,2,3
```

如果 `init_hunters` 有3个取值，`env.lam_farmer` 有3个取值，那么最终会运行 `3 * 3 = 9` 组参数实验，而且每次实验都会进行 `exp.repeats` 次重复实验（默认为5次）。

### 配置文件

您可以修改[配置文件]中的参数，让实验结果更符合您的预期。典型的参数包括：

- `env.init_farmers`: 初始普通农民数量
- `env.init_rice_farmers`: 初始水稻农民数量
- `env.init_hunters`: 初始 Hunter 比例
- `time.end`: 模型运行时间步数
- `Hunter.max_size`: Hunter 最大人口数
- `Hunter.max_size_water`: Hunter 在近水陆地的最大人口数

## 数据输出与分析

模型或实验运行后，通常会自动输出您可以使用的数据并绘制相应图表，具体包括：

### 多次实验

运行一次实验后，输出保存在 `out/<exp.name>/<date>/<time>/`（`exp.name` 默认
`south_china_evolution`）。用 `hydra.run.dir` 可以把它固定成一个不带日期的稳定路径，
稿件那批扫描就是这么做的——目录稳定，断点恢复才有意义。目录里包括：

- `multirun.yaml`：本次扫描的配置快照，记录扫了哪些参数、每个参数有哪些取值；
- 文件夹 `<job_id>_<overrides>/`：每个参数组合一个，内含该组合的全部重复。

:::note 实验级的汇总图与 `summary.csv` 已经不再产出
它们由 `MyExperiment` 的四个绘图方法提供，那个类在投稿定稿时删除了。稿件的图改由
`reports/` 下的两个 notebook 独立产出，见[从模型到手稿]。
:::

### 单次实验

每个参数组合的目录里：

- `<run_id>_tracking.csv`：**主力数据**，一行一个时间步，列是 `tracker` 里声明的指标；
  每次重复一份，`<run_id>` 从 1 数到 `exp.repeats`。
- `repeat_<run_id>_conversion.csv`：该次重复的人口转化矩阵（出身 × 现状）。
- `model.log` / `<exp.name>.log`：运行日志。

只有把 `save_plots` 设为 true 时，才会额外写出 `repeat_<x>_dynamic.jpg` 与
`repeat_<x>_heatmap.jpg`；默认不写盘。

怎么把这些文件读成一张可分析的长表，见[数据输出与分析]。

如果您遇到任何问题或有改进建议，欢迎在 [GitHub] 上提出 issue 或贡献代码。

**祝您使用愉快！**

<!-- Links -->
[配置文件]: /docs/usage/config
[数据输出与分析]: /docs/usage/plots
[从模型到手稿]: /docs/usage/manuscript_pipeline
[GitHub]: https://github.com/SongshGeo/South-China-Livehood-Evolution
