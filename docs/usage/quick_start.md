# 快速开始

本模型的主要工作流程已经集成完毕。用户可以在命令行中运行模型。

- [快速开始](#快速开始)
  - [环境配置](#环境配置)
  - [运行模型](#运行模型)
  - [数据输出与分析](#数据输出与分析)
    - [多次实验](#多次实验)
    - [单次实验](#单次实验)

## 环境配置

> [!note]
> 本模型依赖`Python > 3.9`或以上版本，请先安装好`Python`，并安装好`poetry`或`pip`。

首先将本模型克隆到本地，注意替换`<your folder name>`为你喜欢的文件夹名称：

```bash
git clone https://github.com/SongshGeo/SC-20230710-SCE.git <your folder name>
```

然后在终端进入模型所在文件夹：

```bash
cd <your folder name>
```

安装依赖：

**选项1**: 使用`poetry`安装依赖：

```bash
make setup
```

**选项2**: 使用`pip`安装依赖：

```bash
pip install -r requirements.txt
```

## 运行模型

您可以修改[配置文件]中的参数，让实验结果更符合您的预期，或进行多组实验。参数名称一般都很直观，您可以根据需要进行修改。请注意保持参数名称前的缩进，不要轻易修改参数名，并小心保持YAML格式的正确性。

为了方便进行多组实验，您可以创建多个配置文件，而不是在一个文件中反复修改。例如，您可以在项目目录下的`config`文件夹中创建一个新的配置文件`config_2.yaml`。然后在运行模型时，选择对应的参数文件：

```bash
python main.py --config-name config_2
```

如果您的配置文件位于不同的文件夹中，可以指定完整路径：

```bash
python main.py --config-name config/custom/config_2
```

您还可以在运行时覆盖特定的参数值：

```bash
python main.py --config-name config_2 model.parameter1=new_value
```

您还可以在指定配置文件后，指定参数进行**批量运行的实验**：

```bash
python main.py --config-name config_2 model.parameter1=v1,v2,v3 model.parameter2=a1,a2
```

批量运行实验时，所有参数的笛卡尔积组合都会被运行。即如上例所示，如果 `model.parameter1` 有3个取值，`model.parameter2` 有2个取值，那么最终会运行 `3 * 2 = 6` 组参数实验，而且每次实验都会进行 `exp.repeat` 次重复实验（默认为5次）。

## 数据输出与分析

模型或实验运行后，通常会自动输出您可以使用的数据并绘制相应图表，具体包括：

### 多次实验

运行一次实验后，在`out/<model name>/<date>/<time>`路径下会保存本次实验的所有输出结果。其中 `<model name>` 是您在配置文件中设置的模型名称（默认为 `south_china_evolution`），`<date>` 是实验运行的日期，`<time>` 是实验运行的时间，每个文件夹中包括：

- `multirun.yaml`：实验配置文件，记录了实验的参数设置，有哪些参数被修改过，取值范围等；
- 文件夹 `<job.id>_<config>`：记录了当前 `<config>` 配置下，所有[单次实验](#单次实验)的输出结果；`<job.id>` 是子实验的唯一标识符，即该组参数配置相同。
- `breakpoints.jpg`: 一个 `3 * <jobs>` 的矩阵图，对每组参数配置（唯一的 `<job.id>`），绘制了该组参数下，所有子实验的 `breakpoint` 分布图。
- `heatmap.jpg`: 一个 `x * y` 的矩阵图，应满足 `x * y = jobs`，展示2维参数配置俩俩组合下，实验某变量的平均输出结果。
- `len_<breed>_<ratio>.jpg`: 每组参数配置下，所有子实验 `<breed>` 这种主体的**群体数**占全部群体数的比例变化图。
- `num_<breed>_<ratio>.jpg`: 每组参数配置下，所有子实验 `<breed>` 这种主体的**个体数**占全部群体数的比例变化图。
- summary.csv: 对本次实验的总结，每个参数配置下每次重复的最终结果。

### 单次实验

- `ABSESpyExp.log`：实验日志
- `repeat_<x>_<figure>.png/jpg`：实验图表，`<x>`为实验序号，`<figure>`为图表名称，包括：
    1. `hist.jpg`: 人口和族群数量的分布
    2. `dynamic.jpg`: 人口和族群数量的变化趋势
    3. `heatmap.jpg`: 人口空间分布热力图（地图）
- `repeat_<x>_conversion.csv`: 人口转化情况，记录每种主体的转化情况

如果您遇到任何问题或有改进建议，欢迎在 [GitHub] 上提出 issue 或贡献代码。

**祝您使用愉快！**

<!-- Links -->
[配置文件]: ./config.md
[GitHub]: https://github.com/SongshGeo/SC-20230710-SCE
