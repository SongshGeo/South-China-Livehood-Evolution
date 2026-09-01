# 模型输出数据说明

本文档详细介绍华南生计演变模型（South China Livelihood Evolution Model）的输出数据结构、文件格式与字段含义，帮助研究者理解和分析实验结果。

---

## 一、模型背景

本模型采用基于主体的方法（Agent-Based Model），模拟华南地区史前三类人群在地理网格上的扩张、转化与竞争过程：

| 主体类型 | 说明 |
|---------|------|
| **Hunter（狩猎采集者）** | 初始种群，受全局人口上限约束。可通过转化变为农民或水稻农民。 |
| **Farmer（普通农民）** | 通过泊松过程逐步引入。可以向外扩散建立新群体，也可发生类型转化。 |
| **RiceFarmer（水稻农民）** | 通过泊松过程逐步引入。与普通农民类似但参数不同，代表更高级的农业形态。 |

每个主体占据地图上的一个格子，拥有一个"人口规模"属性。主体可以增长、迁移、分裂（扩散）并在不同类型之间转化。模型默认运行 500 个时间步，每组参数组合默认重复运行 5 次。

---

## 二、输出目录结构

### 2.1 多参数扫描（Multirun）根目录

模型通过 Hydra 框架管理多参数组合实验。一次多参数扫描的输出存放在如下路径：

```
out/south_china_evolution/<日期>/<时间>/
```

该目录下包含：

- **multirun.yaml**：记录本次扫描的完整配置快照，包括扫描了哪些参数、每个参数有哪些取值。
- **若干子目录**：每个子目录对应一组参数组合的全部实验结果。

子目录命名规则为 `<序号>_<参数覆盖信息>`，例如：
- `0_env.lam_farmer=2,env.lam_ricefarmer=0.1` — 数值参数扫描
- `7_convert.farmer_to_hunter=False,convert.hunter_to_farmer=False,convert.hunter_to_rice=False` — 布尔开关扫描

其中序号是该参数组合在笛卡尔积中的位置编号，参数覆盖信息列出了与默认配置不同的参数及其取值。

### 2.2 单组实验目录

每个参数组合目录内包含该组参数下所有重复实验的输出：

| 文件/目录 | 说明 |
|----------|------|
| `.hydra/config.yaml` | 本组实验的完整配置（所有参数的最终取值） |
| `.hydra/overrides.yaml` | 仅列出与默认配置不同的参数（快速识别本组实验的独特之处） |
| `.hydra/hydra.yaml` | Hydra 框架内部配置，一般无需关注 |
| `1_tracking.csv` ~ `5_tracking.csv` | 每次重复实验的时间序列数据（核心输出） |
| `repeat_1_conversion.csv` ~ `repeat_5_conversion.csv` | 每次重复实验的人口转化矩阵 |
| `model.log` | 详细运行日志，记录每一步的模型事件 |
| `south_china_evolution.log` | 实验级别日志，记录实验启动、重复次数等概要信息 |

---

## 三、时间序列文件（tracking.csv）

### 3.1 文件概述

文件名格式为 `<重复编号>_tracking.csv`（如 `1_tracking.csv`），是模型最核心的输出文件。每一行记录某一个时间步上模型的整体状态，共约 500 行（对应 500 个时间步）。

### 3.2 字段含义

tracking.csv 共有 14 列（不含索引列），可以分为四组理解：

#### 第一组：时间与标识

| 列名 | 类型 | 说明 |
|------|------|------|
| `step` | 整数 | 模拟时间步，从 0 开始，到配置中设定的结束时间（默认 500） |
| `run_id` | 整数 | 重复实验编号，与文件名前缀一致 |

#### 第二组：群体数量比例（len 系列）

"群体"指的是地图上的一个主体实例（占据一个格子）。一个群体内部可能有几十到几百人。

| 列名 | 类型 | 说明 |
|------|------|------|
| `len_farmers` | 小数 | 农民群体数 ÷ 全部群体总数 |
| `len_hunters` | 小数 | 狩猎采集者群体数 ÷ 全部群体总数 |
| `len_rice` | 小数 | 水稻农民群体数 ÷ 全部群体总数 |

三者之和在每个时间步上约等于 1.0，反映的是"三种类型各自在地图上占据了多少比例的格子"。

#### 第三组：人口规模比例（num 系列）

"人口规模"是所有同类群体内人口的加总。

| 列名 | 类型 | 说明 |
|------|------|------|
| `num_farmers` | 小数 | 农民总人口 ÷ 全部人口 |
| `num_hunters` | 小数 | 狩猎采集者总人口 ÷ 全部人口 |
| `num_rice` | 小数 | 水稻农民总人口 ÷ 全部人口 |

三者之和在每个时间步上约等于 1.0，反映的是"三种类型各自占据了多少比例的人口"。

#### 第四组：绝对数量（带 _n 后缀）

| 列名 | 类型 | 说明 |
|------|------|------|
| `len_farmers_n` | 整数 | 农民群体的个数（地图上有多少个农民聚落） |
| `len_hunters_n` | 整数 | 狩猎采集者群体的个数 |
| `len_rice_n` | 整数 | 水稻农民群体的个数 |
| `num_farmers_n` | 数值 | 农民的总人口数 |
| `num_hunters_n` | 数值 | 狩猎采集者的总人口数 |
| `num_rice_n` | 数值 | 水稻农民的总人口数 |

### 3.3 命名规则总结

所有 tracker 字段遵循统一的命名规则 `<度量方式>_<主体类型>[_n]`：

- **度量方式**：`len` = 群体数（有多少个聚落），`num` = 人口规模（有多少人）
- **主体类型**：`farmers` = 农民，`hunters` = 狩猎采集者，`rice` = 水稻农民
- **是否带 `_n`**：不带 = 占总量的比例（0~1 之间的小数），带 `_n` = 绝对数值

### 3.4 典型分析用途

- **看扩张趋势**：关注 `num_farmers_n`、`num_hunters_n`、`num_rice_n` 随 `step` 的变化曲线。
- **看结构变化**：关注 `num_farmers`、`num_hunters`、`num_rice` 三条比例曲线的此消彼长。
- **看空间占据**：关注 `len_*_n` 系列，了解哪种类型在地图上占据了更多格子。
- **看拐点**：对某条时间序列做变点检测（breakpoint detection），识别趋势发生显著变化的时间步。

---

## 四、人口转化矩阵（conversion.csv）

### 4.1 文件概述

文件名格式为 `repeat_<重复编号>_conversion.csv`。它记录的是：模拟结束时，各类主体的"出身"与"现状"之间的对应关系。这是一个 4 行 × 3 列的小表。

### 4.2 表格结构

以下是一个实际示例：

|  | farmer_init | hunter_init | rice_init |
|--|------------|------------|----------|
| **farmers_end** | 351 | 57 | 148 |
| **hunters_end** | 4950 | 4175 | 411 |
| **rice_end** | 1 | 0 | 101 |
| **total_end** | 5301 | 4232 | 559 |

### 4.3 如何理解

**列（横向标题）**：代表主体的"出身"，即该主体在模拟开始时最初被创建为什么类型：
- `farmer_init`：最初是农民的主体
- `hunter_init`：最初是狩猎采集者的主体
- `rice_init`：最初是水稻农民的主体

**行（纵向标题）**：代表主体在模拟结束时的"现状"：
- `farmers_end`：最终变成了农民
- `hunters_end`：最终变成了狩猎采集者
- `rice_end`：最终变成了水稻农民
- `total_end`：该出身类型的主体总数

**读法举例**：

- `farmers_end` 行 × `hunter_init` 列 = 57：意思是有 57 个主体"最初是狩猎采集者，但到模拟结束时已经转化成了农民"。
- `hunters_end` 行 × `hunter_init` 列 = 4175：意思是有 4175 个主体"最初是狩猎采集者，到结束时仍然是狩猎采集者"（未发生转化）。
- `total_end` 行 × `farmer_init` 列 = 5301：意思是最初被创建为农民的主体一共有 5301 个（不管最终变成了什么）。

**对角线**（如 `farmers_end × farmer_init`）代表"保持原类型未变"的主体数量。**非对角线**代表发生了类型转化的主体数量。

### 4.4 典型分析用途

- **了解转化方向**：哪些出身类型更容易转化成什么？非对角线数值越大，说明该转化路径越活跃。
- **计算保留率**：对角线值 ÷ `total_end` 行对应值 = 该类型的保留率（有多少比例的主体保持了原来的类型）。
- **对比不同实验**：在不同参数组合下比较转化矩阵，可以直观看出参数对转化行为的影响。

---

## 五、配置文件

### 5.1 overrides.yaml（最常用）

该文件位于 `.hydra/overrides.yaml`，仅列出本组实验与默认配置不同的参数。示例：

```
- convert.farmer_to_hunter=False
- convert.hunter_to_farmer=False
- convert.hunter_to_rice=False
```

这是判断"这组实验改了什么"最快捷的方式。

### 5.2 config.yaml（完整配置）

该文件位于 `.hydra/config.yaml`，包含本次运行的所有参数最终取值。主要配置段落包括：

| 配置段 | 内容 |
|--------|------|
| `exp` | 实验设置：重复次数、并行进程数、是否保存数据等 |
| `convert` | 5 条转化路径的开关（True/False） |
| `env` | 环境参数：农民引入速率、初始狩猎采集者比例、网格大小等 |
| `time` | 模拟时长（结束步数） |
| `Farmer` | 农民主体参数：增长率、扩散概率、转化概率与阈值、损失参数等 |
| `Hunter` | 狩猎采集者参数：人口上限、移动距离、损失参数等 |
| `RiceFarmer` | 水稻农民参数 |
| `ds` | 地理数据路径：高程、坡度、水体栅格文件 |

---

## 六、转化路径说明

模型支持 5 条可配置的主体类型转化路径，由 `convert` 配置段中的布尔开关控制：

```
        ┌──────────┐          ┌──────────────┐
        │  Hunter  │          │  RiceFarmer  │
        └──────────┘          └──────────────┘
          ↑      ↓                ↑      ↓
  farmer     hunter       farmer     rice
  _to_       _to_         _to_       _to_
  hunter     farmer       rice       farmer
          ↓      ↑                ↓      ↑
        ┌──────────┐          ┌──────────┐
        │  Farmer  │←─────────│  Farmer  │
        └──────────┘          └──────────┘
                    hunter_to_rice
          Hunter ──────────────→ RiceFarmer
```

| 开关 | 转化方向 | 触发条件 |
|------|---------|---------|
| `convert.hunter_to_farmer` | 狩猎采集者 → 农民 | 每时间步以一定概率自发转化 |
| `convert.hunter_to_rice` | 狩猎采集者 → 水稻农民 | 每时间步以一定概率自发转化 |
| `convert.farmer_to_hunter` | 农民 → 狩猎采集者 | 农民群体人口低于阈值时触发 |
| `convert.farmer_to_rice` | 农民 → 水稻农民 | 农民群体人口高于阈值时触发 |
| `convert.rice_to_farmer` | 水稻农民 → 农民 | 水稻农民群体人口低于阈值时触发 |

> 注意：不存在"水稻农民 → 狩猎采集者"的直接路径。

---

## 七、整合 multirun 数据并绘制增长轨迹

Hydra 的 multirun 把每组参数、每次重复分散在单独的文件里。真正用于分析之前，需要把它们拼成一张「长表」（tidy DataFrame），再交给 `seaborn.relplot` 等函数作图。下面给出可复用的最小范式；`src/workflow/figures.py` 的四个加载器就是它的成品版本，出图 notebook 与 `paper/build_results.py` 都用那一份，不要在别处再抄一遍。

### 7.1 解析 job 目录名

子目录命名 `<job_id>_<key>=<val>,<key>=<val>,...`（§2.1）。用一段正则即可同时拿到 `job_id` 与各 override 的 `{参数名: 取值}` 字典：

```python
import re

JOB_DIR_RE = re.compile(r"^(?P<job_id>\d+)_(?P<rest>.+)$")
TRACK_RE = re.compile(r"^(?P<run_id>\d+)_tracking\.csv$")

def _cast(v: str):
    if v.lower() in {"true", "false"}:
        return v.lower() == "true"
    try:
        return int(v) if "." not in v else float(v)
    except ValueError:
        return v

def parse_job_dir(name: str) -> tuple[int, dict]:
    m = JOB_DIR_RE.match(name)
    job_id = int(m.group("job_id"))
    overrides = {}
    for token in m.group("rest").split(","):
        if "=" not in token:
            continue
        k, v = token.split("=", 1)
        overrides[k] = _cast(v)
    return job_id, overrides
```

> 想知道本次扫描了哪些参数，读 `multirun.yaml` 的 `hydra.overrides.task`（而非 `override_dirname`）：`OmegaConf.load(dir / "multirun.yaml").hydra.overrides.task` 会返回 `["Farmer.max_travel_distance=5,10,20", ...]`。

### 7.2 拼接所有 `tracking.csv` 为一张长表

遍历子目录、逐 repeat 读 CSV，把参数作为列注入，最后 `pd.concat`：

```python
from pathlib import Path
import pandas as pd

def load_trajectories(multirun_dir: Path, cols: list[str]) -> pd.DataFrame:
    """拼出 (step, job_id, run_id, 参数..., 指标...) 的 tidy DataFrame。"""
    frames = []
    for jd in sorted(multirun_dir.iterdir()):
        if not (jd.is_dir() and JOB_DIR_RE.match(jd.name)):
            continue
        job_id, overrides = parse_job_dir(jd.name)
        for tp in sorted(jd.glob("*_tracking.csv")):
            m = TRACK_RE.match(tp.name)
            if not m:
                continue
            usecols = {"step", *cols}
            t = pd.read_csv(tp, usecols=lambda c: c in usecols)
            t["job_id"] = job_id
            t["run_id"] = int(m.group("run_id"))
            for k, v in overrides.items():
                t[k] = v
            frames.append(t)
    return pd.concat(frames, ignore_index=True)
```

几点要点：

- 只读需要的列（`usecols`），避免大扫描时内存爆炸；
- 把 override 同步注入为列，之后可以直接作为 `hue/col/row` 分面；
- `run_id` 来自文件名，`job_id` 来自目录名——二者合起来唯一标识一条 repeat。

如需 `ExperimentManager` 风格的「行 = 一条 repeat」长表，用同一张 DataFrame 按 `(job_id, run_id)` 聚合并调用 `ExperimentManager.update_result()` 即可。

### 7.3 用 `sns.relplot` 画分面轨迹图

`relplot(kind="line")` 自带跨 `run_id` 的均值 + 置信带，几行代码就能同时比较数十组参数：

```python
import seaborn as sns

g = sns.relplot(
    data=traj,
    x="step", y="num_farmers_n",
    hue="Hunter.max_travel_distance",
    col="Farmer.max_travel_distance",
    row="RiceFarmer.max_travel_distance",
    kind="line",
    estimator="mean", errorbar=("ci", 95),
    height=2.4, aspect=1.2,
    palette="viridis",
    facet_kws={"sharey": True},
)
g.set_titles("Farmer dist={col_name} | Rice dist={row_name}")
g.fig.suptitle("Farmer population trajectories (mean ± 95% CI)", y=1.02)
```

调校清单：

- **三参数网格**：`col` + `row` 用两个参数，第三个参数给 `hue`。若还有第四维，用 `style`（线型）承载，但同一张图最多可读维度约为 3–4。
- **同时画多条指标**：先 `melt` 成 `metric/value` 两列，再把 `metric` 放到 `style` 或再加一个 facet；此时通常 `sharey=False`。
- **快慢两类叠加**：先用末态均值把 `job_id` 分成 fast / slow，两次 `lineplot` 叠在同一 `ax`——第一次 `units="job_id", estimator=None, alpha=0.3` 画所有个体轨迹，第二次 `estimator="mean", linewidth=2.5, legend=False` 画组均值。
- **配色**：有序数值参数用连续色板（`viridis` / `mako`），类别变量用 `tab10` / `Set2`；`hue_order` 固定顺序便于跨图对比。
- **稳态窗口**：只取后半段 `df[df["step"] >= max_step // 2]` 做 mean / CV / t 检验，可去掉启动瞬态，让参数效应更清晰。

### 7.4 组成结构图

想在同一面板内展示三类主体此消彼长，先 `melt` 再 `relplot`：

```python
long = traj.melt(
    id_vars=["step", "job_id", "run_id", *param_cols],
    value_vars=["num_farmers", "num_hunters", "num_rice"],
    var_name="group", value_name="share",
)
long["group"] = long["group"].str.replace("num_", "", regex=False)

sns.relplot(
    data=long, x="step", y="share",
    hue="group", col=param_cols[0], row=param_cols[1],
    kind="line", estimator="mean", errorbar=None,
    height=2.4, aspect=1.2,
)
```

---

## 八、日志文件

| 文件 | 说明 |
|------|------|
| `model.log` | 详细日志（DEBUG 级别），记录模型初始化信息和每一步的事件。适合排查单次运行问题。 |
| `south_china_evolution.log` | 实验概要日志（INFO 级别），记录实验启动参数、重复次数、并行设置等。 |

---

## 九、术语表

| 术语 | 含义 |
|------|------|
| **群体（Group）** | 地图上一个格子中的主体实例。每个群体有一个人口规模（size）属性。 |
| **出身（Source）** | 主体在最初被创建时的类型。即使后来发生了转化，出身信息也会保留，用于追踪转化来源。 |
| **参数组合（Job）** | 一次多参数扫描中的一种参数配置。每个 Job 对应输出目录中的一个子文件夹。 |
| **重复实验（Repeat）** | 在相同参数下重复运行的随机化实验。由于模型包含随机过程，多次重复可以评估结果的稳定性。 |
| **变点/拐点（Breakpoint）** | 时间序列中趋势发生显著变化的时间点，通过 ruptures 算法检测。 |
| **lam_farmer** | 泊松过程的期望值，控制每个时间步引入新农民群体的数量。值越大，农民出现越快。 |
| **lam_ricefarmer** | 泊松过程的期望值，控制每个时间步引入新水稻农民群体的数量。 |
| **loss.prob / loss.rate** | 每个时间步中，群体遭受人口损失的概率和损失比率。 |
