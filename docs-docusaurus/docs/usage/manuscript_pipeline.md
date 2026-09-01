# 从模型到手稿

这一页讲的是本仓库的**主产出**：那篇论文的五张图、一个表格工作簿，以及正文里引用的
每一个数字，分别由什么产生、怎么重建、怎么防止它们悄悄失效。

模型本身怎么跑见[快速开始]；这里假定你已经有一批扫描结果。

## 四层，不要互相越界

| 层 | 在哪 | 做什么 | 绝不做什么 |
| :--- | :--- | :--- | :--- |
| 核心包 | `src/` | 常量、类、核心函数、面板 builder——全部带测试 | 写死路径；放一次性的实验胶水 |
| 批处理脚本 | `run_slurm_rerun.sh` | 一次性批量运行 → 数据落进 `out/` | 碰 `results.json`；持有核心算法 |
| Notebook | `reports/*.ipynb` | 每格调一次核心函数，拼出成图 | 内联大段分析逻辑 |
| 手稿 | `paper/` + Obsidian vault | 正文、图、`results.json`、表格工作簿 | 分析逻辑；手打数字 |

越界的代价是具体的：同一段逻辑一旦有两份，它们就能各自漂移，而且**两份都能跑通、都不
报错**——只是其中一份属于旧数据。本仓库已经被这样咬过一次，见文末。

## 一条完整的链路

```
run_slurm_rerun.sh          216 个 SLURM 任务，六组实验
        │                   输出目录名严格对齐 figures.py 的四个加载器
        ▼
out/south_china_evolution/rerun_v3/     134 MB，gitignore，make fetch-rerun 取
        │
        ├──▶ reports/manuscript_figures.ipynb  ──▶ reports/figure2-5.{png,pdf}
        │       用 src/workflow/figures.py 的 plot_* builder
        │
        ├──▶ reports/c14_sites.ipynb           ──▶ reports/figure1.{png,pdf}
        │       用 src/workflow/c14.py，数据是 data/si2_c14_sites.xlsx（SI-2 原件）
        │
        ├──▶ paper/build_results.py            ──▶ paper/results.json   ★金标准
        │       用 src/workflow/results.py
        │
        └──▶ paper/build_tables.py             ──▶ paper/figs/SCE_Tables.xlsx
                读 Hydra 配置、输入栅格、扫描脚本，一个值都不重打

                            │  make sync-vault
                            ▼
        Obsidian vault 的 figs/：SCE_figure1-5.{png,pdf} + SCE_Tables.xlsx
```

一条命令跑完整条链路：

```bash
make figures      # 重跑两个 notebook → build_tables → build_results → sync-vault
```

## 金标准：`paper/results.json`

图是文件，文件旧了至少看得见。**图上读出来的数**不是：一个终态占比、一个效应量比值、
一个 $R^2$，会被抄进正文、图注、`paper/model-inventory.md` 和 SI，每一份都能单独变旧。

所以每个数只算一次，由 `src/workflow/results.py` 负责，冻进 `paper/results.json`（随 git
版本管理）：

```bash
make results        # 重算并改写 results.json
make check-results  # 重算、比对、不写盘；指出哪个键、从多少变成了多少
```

`tests/test_results_regression.py` 在 `make test` 里跑同一套比对。文件分两层：

| 层 | 键 | 哪里能查 |
| :--- | :--- | :--- |
| 仓库层 | `landscape`、`parameters`、`c14` | 任何地方，包括 CI——输入（栅格、Hydra 配置、SI-2 附表）都随仓库版本管理 |
| 扫描层 | `figure2`–`figure5` | 只在 `rerun_v3` 在本机时；否则跳过而不是判红 |

存 6 位有效数字：远严于任何有意义的模型变化，又不会被 NumPy/pandas 换版本时的末位抖动
误伤。

**返修重跑之后**，回归测试会失败并逐键报出旧值、新值和变化百分比。确认是有意的之后重建
金标准，再把每一处抄了这些数的地方一起改。

## 四道防线，各防一种「不报错的错」

| 防线 | 防的是 |
| :--- | :--- |
| `tests/test_manuscript_figures_source.py` | notebook 的七个数据路径常量被改回被取代的目录。旧目录本机已删，但 `make fetch-geany-data` 一条命令就能全部拉回来；届时指回去照样出图，只是出的是旧图 |
| `tests/test_results_regression.py` | 数据或算法变了，而正文里的数字没跟着变 |
| `tests/test_config.py::test_every_exp_key_still_has_a_reader` | 配置里出现没人读的哑弹键 |
| `make sync-vault` 的前置检查 | 产物缺失或损坏时半同步 vault——它先全部校验再拷贝，缺一个就整体中止 |

## 手稿正文不在本仓库

正文与 SI 写在 Obsidian vault 的 longform 项目里，`paper/manuscript`、
`paper/si_odd_protocol`、`paper/refs.bib` 是指向它的**软链接**——同一份文件，改哪边都
一样，不需要也无法「不同步」。三个链接都在 `.gitignore` 里，因为它们存的是本机绝对路径。

真正是两份拷贝的只有图和表格工作簿，靠 `make sync-vault` 单向搬运。细节见
`paper/README.md`。

## 这些防线是被咬出来的

投稿前整理时发现，`paper/model-inventory.md` 里「What the re-run changed」整节标着
`rerun_v3`，七个 headline 数值却全是上一批 `rerun_v2` 的——重跑发生过，这一节没跟着改，
而且没有任何东西会因此报错。终态农业占比实际是 18.0% 而非记录的 15.4%，地貌效应是
1.80× 而非 1.91×。

`results.json` 就是为了让这种事不能再无声发生。

<!-- Links -->
[快速开始]: /docs/usage/quick_start
