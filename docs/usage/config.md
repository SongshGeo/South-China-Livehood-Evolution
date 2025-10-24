---
title: 配置文件
author: Shuang Song
---

配置文件是模型运行的重要组成部分。模型运行时，会根据配置文件中的参数进行模拟。配置文件的格式为YAML，用户可以在配置文件中修改模型参数。

配置文件的默认位置为`config/config.yaml`，用户也可以在运行模型时通过命令行参数指定配置文件的位置。

## 2.0 版本主要特性

### 核心规则
- **每格一主体**：每个格子只能有一个主体，严格遵守空间约束
- **水体类型系统**：支持 -1（海）、0（陆地）、1（近水陆地）三种水体类型
- **全局人口上限**：Hunter 人口有全局上限控制机制
- **无竞争机制**：主体不能移动到已有其他主体的格子

### 使用方式
```bash
# 基本运行
python src

# 使用 poetry 环境
poetry run python src

# 多情景运行测试
poetry run python src --multirun init_hunters=0.05,0.1,0.2 env.lam_farmer=1,2,3
```

## 配置文件结构

配置文件主要分为以下几个部分：

### convert

转化机制开关，控制不同主体类型之间的转化行为。

| 参数名 | 类型 | 默认值 | 说明 |
| :--- | :--- | :--- | :--- |
| enabled | bool | true | 全局转化开关，关闭后所有转化都不会发生 |
| hunter_to_farmer | bool | true | 狩猎采集者能否转化为农民 |
| hunter_to_rice | bool | true | 狩猎采集者能否转化为水稻农民 |
| farmer_to_hunter | bool | true | 农民能否转化为狩猎采集者 |
| farmer_to_rice | bool | true | 农民能否转化为水稻农民 |
| rice_to_farmer | bool | true | 水稻农民能否转化为农民 |

> **注意**：此功能允许您关闭转化机制，以对比有/无转化的模型行为差异。

### exp

实验配置，包括实验名称、重复次数、进程数、绘图变量等。

| 参数名 | 类型 | 默认值 | 说明 |
| :--- | :--- | :--- | :--- |
| name | str | - | 实验名称 |
| repeats | int | 1 | 每组参数的重复次数 |
| num_process | int | 1 | 并行运算的进程数 |
| plot_heatmap | str | - | [绘制热图]的变量 |

### model

模型配置，包括模型参数，如断点检测方法等。

| 参数名 | 类型 | 默认值 | 说明 |
| :--- | :--- | :--- | :--- |
| save_plots | bool | True | 是否保存绘图 |
| n_bkps | int | 1 | [断点数量] |
| detect_bkp_by | str | 'size' | [断点检测方法] |

> **注意**：`loss_rate` 参数已在 2.0 版本中移除，因为不再有竞争机制。

### reports

决定了报告的输出内容，包括报告的名称、报告的变量等。变量命名规则为 `{report_type}_{group}_{variable_type}`，例如：

- `len_farmers`: 农民，团体数，占总人口比例
- `num_farmers_n`: 农民，人口数，绝对人口数量

- 报告名称包括：
  - `model`: 模型报告，单次实验每个时间步都记录的变量
  - `final`: 实验报告，每次实验只在结束时记录的变量
- 主体包括：
  - `farmers`: 农民
  - `hunters`: 狩猎采集者
  - `rice`: 水稻
- 变量类型包括：
  - `num`: 绝对人口数量
  - `len`: 团体数
  - `ratio`: 占总人口比例（什么尾缀都没加时默认使用这个）
  - `bkp`: 断点位置（年份，或tick数）
  - `pre`: 断点前的人口增长率
  - `post`: 断点后的人口增长率

### env

环境配置，包括环境参数，如环境容量、初始主体数量等。

| 参数名 | 类型 | 默认值 | 说明 |
| :--- | :--- | :--- | :--- |
| lim_h | float | 31.93 | **全局 Hunter 人口上限基础值（人/百平方公里）** |
| init_hunters | float | 0.05 | 初始狩猎采集者比例或数量（<1时为比例，≥1时为数量） |
| init_farmers | int | 80 | 初始普通农民主体数量（推荐范围 60-100） |
| init_rice_farmers | int | 350 | 初始水稻农民主体数量（推荐范围 300-400） |
| lam_farmer | float | 1 | 每步添加农民的期望值（泊松分布参数） |
| lam_ricefarmer | float | 1 | 每步添加水稻农民的期望值（泊松分布参数） |
| tick_farmer | int | 0 | 农民开始添加的时间步（0表示从一开始就有） |
| tick_ricefarmer | int | 0 | 水稻农民开始添加的时间步（0表示从一开始就有） |
| width | int | 10 | 网格宽度（玩具模型使用） |
| height | int | 10 | 网格高度（玩具模型使用） |

> **提示**：`tick_farmer` 和 `tick_ricefarmer` 现在默认为 0，表示从模型初始化时就创建这些主体，而不是在运行过程中才开始添加。

### time

时间配置，包括时间参数，如时间步数、时间步长等。

| 参数名 | 类型 | 默认值 | 说明 |
| :--- | :--- | :--- | :--- |
| end | int | 10 | 时间步数 |

### Farmer

农民配置，包括农民参数，如农民人口增长率、扩散概率等。

| 参数名 | 类型 | 默认值 | 说明 |
| :--- | :--- | :--- | :--- |
| area | int | 2 | 农民活动范围（公里） |
| growth_rate | float | 0.004 | 农民人口增长率（每步） |
| min_size | int | 6 | 最小农民群体数，小于这个数时会死掉 |
| init_size | list | [60, 100] | **初始农民人口规模范围**（初始化时随机取值） |
| new_group_size | list | [30, 60] | 扩散时新农民群体大小范围 |
| diffuse_prob | float | 0.05 | 农民扩散概率，每步有此概率向外扩散 |
| complexity | float | 0.1 | 复杂化后人口增长率下降比例 |
| convert_prob | dict | - | 转换概率（to_hunter, to_rice） |
| convert_threshold | dict | - | 转换阈值（to_hunter: 超过此值不再转化，to_rice: 超过此值才能转化） |
| max_travel_distance | int | 5 | 扩散时最大搜索距离 |
| capital_area | float | 0.004 | 人均耕地面积（平方公里） |
| loss | dict | - | 损失机制（prob: 发生概率，rate: 损失比率） |

### Hunter

狩猎采集者配置，包括狩猎采集者参数，如人口增长率、移动规则等。

| 参数名 | 类型 | 默认值 | 说明 |
| :--- | :--- | :--- | :--- |
| init_size | list | [0, 35] | 初始化时的人口规模范围，小于 min_size 时自动调整为 min_size |
| growth_rate | float | 0.0008 | 狩猎采集者人口增长率（每步） |
| min_size | int | 6 | 最小群体规模，小于此值会死亡 |
| **max_size** | int | 100 | **单位主体人口最大值（普通情况）** |
| **max_size_water** | int | 500 | **临近水体时的最大值** |
| new_group_size | list | [6, 31] | 扩散时新群体大小范围 |
| convert_prob | dict | - | 转换概率（to_farmer, to_rice） |
| max_travel_distance | int | 5 | 移动时最大搜索距离 |
| is_complex | int | 100 | 超过此值变为定居狩猎采集者，不再移动 |
| **loss** | dict | - | **损失机制（prob: 发生概率，rate: 损失比率）** |

> **重要变更**：
> - ❌ 已删除 `intensified_coefficient` 参数（不再有竞争机制）
> - ✅ 新增 `max_size` 和 `max_size_water` 参数
> - ✅ 新增 `loss` 参数，狩猎采集者现在也会经历随机损失
> - ✅ **全局 Hunter 人口上限**：自动计算为 `lim_h × 非水体栅格数量`

### RiceFarmer

水稻农民配置，包括水稻农民参数，如人口增长率、扩散概率等。

| 参数名 | 类型 | 默认值 | 说明 |
| :--- | :--- | :--- | :--- |
| area | int | 2 | 水稻农民活动范围（公里） |
| growth_rate | float | 0.005 | 水稻农民人口增长率（每步） |
| min_size | int | 6 | 最小群体规模，小于此值会死亡 |
| **init_size** | list | [300, 400] | **初始水稻农民人口规模范围**（初始化时随机取值） |
| new_group_size | list | [200, 300] | 扩散时新群体大小范围 |
| diffuse_prob | float | 0.05 | 扩散概率，每步有此概率向外扩散 |
| complexity | float | 0.1 | 复杂化后人口增长率下降比例 |
| convert_prob | dict | - | 转换概率（to_farmer），不能向狩猎采集者转换 |
| convert_threshold | dict | - | 转换阈值（to_farmer: 低于此值才能转化） |
| max_travel_distance | int | 5 | 扩散时最大搜索距离 |
| capital_area | float | 0.002 | 人均耕地面积（平方公里） |
| loss | dict | - | 损失机制（prob: 发生概率，rate: 损失比率） |

### ds

数据源配置，包括数据源参数，如数据路径等。

| 参数名 | 类型 | 默认值 | 说明 |
| :--- | :--- | :--- | :--- |
| dem | str | - | 数字高程模型路径 |
| slope | str | - | 坡度路径 |
| asp | str | - | 坡向路径 |
| farmland | str | - | 耕地路径 |
| lim_h | str | - | **水体数据路径（-1=海，0=陆地，1=近水陆地）** |

> **重要变更**：
> - `lim_h` 现在表示水体类型数据，而不是 Hunter 人口上限数据
> - 支持三种水体类型：-1（海）、0（陆地）、1（近水陆地）

<!-- Links -->
  [断点检测方法]: ../tech/breakpoint.md#断点检测方法
  [断点数量]: ../tech/breakpoint.md#断点检测方法
  [绘制热图]: ./plots.md#绘制热图
