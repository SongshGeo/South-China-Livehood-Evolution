#!/bin/bash -l
#SBATCH --job-name=sce_rerun_v3
#SBATCH --array=0-215%32
#SBATCH --time=3-00:00:00
#SBATCH --output=logs/%x-%A_%a.out
#SBATCH --error=logs/%x-%A_%a.err
#SBATCH --mem=32G
#SBATCH --cpus-per-task=5
#SBATCH --mail-user=song@gea.mpg.de
#SBATCH --mail-type=END,FAIL

# ──────────────────────────────────────────────────────────────────────────────
# 全量重跑：Figure 2–5 的六组实验，一次投完
#
# 为什么要重跑（本轮 = rerun_v3）:
#   `env.lim_h` 的取值口径变了。它送进代码的单位一直是【人/格】（env.py 直接乘格子
#   数量），但此前的取值 35 是拍在"人/格"上的，没有做面积换算——而 5 弧分格子平均只有
#   78.3 km²，35 人/格 隐含 ≈45 人/百平方公里，高于 Binford 2001 的 31.93 / 39.77。
#   现在改成先定密度再换算：35 人/百平方公里 × 80 km²/格 = 28 人/格，扫描的三档
#   随之从 {15, 25, 35} 变为 {12, 20, 28}。区域天花板 35×6835=239225 → 28×6835=191380。
#   见 paper/model-inventory.md 的 F8 / issue #35——本轮反转了那条"不做面积换算"的结论。
#
#   注意基线是从 config/config.yaml 继承的，limh 之外的 213 组都不 override 这个键，
#   所以**六组实验全部要重算**，不能只补 limh 那三组。
#
# 上一轮 (rerun_v2) 为什么重跑，仍然适用于本轮的数据:
#   两个改变模型行为的缺陷已修复，更早的 out/ 结果全部由修复前的代码产出：
#   • #28 (commit d4553ab) 农民与水稻农民每步做两次死亡抽样，现在只做一次。
#     解析上每步期望存活乘子从 0.999 变为 0.9995，500 步累积约 1.28×。
#   • #29 (commit 见 git log) 水稻移民曾用旱作可耕地掩膜落点，31% 的水稻群体坐在
#     不满足水稻坡度条件的格子上且永不被淘汰；现在按品种取掩膜。
#   同时 #38/#30 (commit 39d47a0) 接通了随机种子，所以这批新结果可逐 run 复现。
#
# rerun_v2 不要删:
#   它留在原地是为了对照。天花板从 239225 降到 191380 之后，初始布局的狩猎采集者
#   （seed=42 实测第 0 步 183763 人）从占满 77% 变成占满 96%，一开局就几乎顶到上限，
#   之后会长期被削。各条轨迹因此变了多少，只有把两批数据摆在一起才看得出来。
#
# 设计:
#   216 个任务 = 每个任务跑一个参数组合 × exp.repeats(5) 次重复。
#   六组实验拼成一个扁平数组，一次 sbatch 投完，靠数组末尾的 %N 控制并发。
#   目录名严格对齐 src/workflow/figures.py 的四个加载器，否则画图读不到：
#     load_trajectories / load_grid  ->  <job_id>_<k=v,k=v>/
#     load_fine_grid                 ->  idx<n>_f2h<a>_h2f<b>/
#     load_terrain                   ->  <n>_ds.dem=data/<dem>.tif,ds.slope=data/<slo>.tif/
#   前四组的目录名由 override 串直接派生（空格换成逗号），所以参数名只写一次——
#   figures.py 是从目录名里解析参数值的，两处写错一处就会画出标错参数的图。
#
# 与旧数据的差异（有意为之，不是笔误）:
#   • 广网格补齐成 6×6=36 组，旧的 grid_f2h_h2f_v1 只有 25 组（当时有任务未完成）。
#   • lam 补齐成 5×5=25 组，旧的 2026-01-18 只有 23 组（缺 lam_farmer=10 × 0.4/0.5）。
#   两处都是把原设计跑完整，不是改设计；代价很小，但会让 Fig 3b / 4a 的输入比旧版更密。
#
# 随机种子:
#   数组里每个任务都是独立进程，ABSESpy 的 Experiment._get_seed 看到的 job_id 恒为 0，
#   因此**所有组合共用同一串 replicate 种子**（base=42）——初始狩猎采集者布局在各组合
#   间完全相同。这是有意的 common random numbers：参数扫描里它成对化了各组合、
#   压低了跨组合比较的方差。代价是各组合的重复不独立，所以整张网格的置信区间不能当作
#   互相独立来解释，且一次"不走运"的实现会同向影响每个格点。
#   若确实需要各组合独立抽样，在下面 .venv/bin/python 那行加 `seed=$((42 + SLURM_ARRAY_TASK_ID))`。
#
# 编号:
#   任务号 = 数组下标（全局，0–215）；目录里的 <n> / idx<n> 是**组内**序号，每组从 0
#   重新开始。例如 grid_fine/idx0_... 是全局任务 95。重投单个任务要用全局号，
#   例如 `sbatch --array=95,96%2 run_slurm_rerun.sh`。
#
# 断点恢复:
#   输出目录是稳定的（不带日期），src/__main__.py 在 batch_run 前检查 5 个
#   *_tracking.csv 是否齐全，齐全就跳过。重投整个数组会自动跳过已完成的组合。
#   ⚠️ build_tasks 的输出顺序就是任务号，改动顺序会让所有任务重新映射到别的目录，
#      断点恢复随之失效。只应在末尾追加，不要插入或重排。
#
# 资源预算:
#   实测单个组合（5 次重复并行，cpus-per-task=5）约 3.4 小时；转化全关的组合最慢，
#   因为农民不再被抽回狩猎采集，主体数量持续膨胀。
#   ⚠️ 这个 3.4 小时是 rerun_v2（lim_h=35）的实测值。本轮天花板降到 28，狩猎采集者被
#   削得更狠、农民扩张更快，主体数量大概率更多，单任务只会更慢不会更快——所以
#   --time=3-00:00:00 的余量该留还得留，别照着 3.4 小时去缩。
#   默认 --time=3-00:00:00 是实测值的约 21 倍。留这么大余量的理由是：任务一旦被墙钟
#   杀掉，该组合的 5 次重复不会全部落盘，断点恢复判定为"未完成"，整组要从头重跑——
#   宁可多要时间，也不要多投一轮。集群上限 7 天，需要时 `--time=7-00:00:00` 顶满。
#   但注意 --time 只是上限，不影响实际用时：**要缩短总时长应该调并发（%N）**，
#   请求越长 SLURM 的 backfill 越难塞，排队反而更久。
#   216 × 3.4h ≈ 730 task-hours：%32 约 23 小时跑完，%64 约 12 小时，%16 约 46 小时。
#
# 用法:
#   bash run_slurm_rerun.sh --prep                # ① 登录节点上先备好 .venv（只需一次）
#   bash run_slurm_rerun.sh --smoke               # ② 十几秒的冒烟测试
#   sbatch run_slurm_rerun.sh                     # ③ 全部投出（已完成的会跳过）
#   sbatch --array=0-215%64 run_slurm_rerun.sh    # 队列宽裕时再调高并发
#   sbatch --array=0-58%32 run_slurm_rerun.sh     # 先出 Fig 2/4/5，精细网格后投
#   sbatch --array=0,22,27-215%32 run_slurm_rerun.sh
#       ↑ 只跑正文要用的：convert3 里 manuscript_figures.ipynb 只读第 0（全关）和第 22
#         （基线）两个目录，其余 25 组是为复现原始 3³ 扫描而跑的（约 85 task-hours）。
#         完整 3³ 是为复现原始扫描留的，正文用不到——只想出图的话可以省掉。
#   bash run_slurm_rerun.sh --list                # 本地打印任务清单，不提交
#   TASK=5 bash run_slurm_rerun.sh --dry-run      # 看第 5 个任务会执行什么
#   bash run_slurm_rerun.sh --verify              # 跑完后核对产出，列出未完成的任务号
#
# 投递前的冒烟测试（强烈建议，十几秒）:
#   bash run_slurm_rerun.sh --smoke               # 默认第 0 号任务
#   TASK=55 bash run_slurm_rerun.sh --smoke       # 挑路径带 / 和 , 的那个更保险
#   两步跑通即说明解释器、依赖和 override 引号都对；产出在临时目录，不碰 out/。
#
# 邮件通知:
#   --mail-type=END,FAIL 没有带 ARRAY_TASKS，所以 SLURM 把整个数组当一个作业发信：
#   全部结束发一封，失败发一封，而不是 216 封。想要每个任务都发信就改成
#   --mail-type=END,FAIL,ARRAY_TASKS（不建议）。邮件只说"数组结束了"，不保证每个
#   组合都成功——完成与否请以 `--verify` 为准。
# ──────────────────────────────────────────────────────────────────────────────

set -euo pipefail

# 统一工作目录。build_tasks 的 SWEEP_ROOT、verify 读的 config/config.yaml、
# 以及 .venv/bin/python 全是相对路径，子命令从任何目录调用都必须先站到仓库根。
# sbatch 执行的是 spool 里的一份副本（/var/spool/slurmd/...），$0 指不到仓库，
# 所以在数组作业里只能靠 SLURM_SUBMIT_DIR，不能用 dirname "$0" 兜底。
if [[ -n "${SLURM_ARRAY_TASK_ID:-}" ]]; then
    : "${SLURM_SUBMIT_DIR:?running under sbatch without SLURM_SUBMIT_DIR; submit from the repo root}"
    cd "$SLURM_SUBMIT_DIR"
else
    cd "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
fi

# 集群上加载 Python 模块。--prep 和任务体必须走同一套解释器：.venv/bin/python 是
# 指向"创建它的那个解释器"的符号链接。如果 --prep 用登录节点的默认 Python 建 venv，
# 而任务体 module purge 之后换成 python-waterboa，venv 就指向一个已被 purge 的解释器
# ——而且两道预检还都会通过。26949 日志里那句
#   Using CPython 3.11.15 interpreter at: /usr/bin/python3.11
# 正是这个登录节点默认解释器。
load_cluster_python() {
    if command -v module >/dev/null 2>&1; then
        module purge
        module load python-waterboa/2025.06
    else
        echo "note: no 'module' command here; using the ambient Python." >&2
    fi
}

SWEEP_ROOT="out/south_china_evolution/rerun_v3"

# 精细网格的扫描值。paper/build_tables.py::swept_ranges 直接读这两个数组来填 Table S1
# 的 "Swept" 列——读的就是产出数据的这个脚本，所以表里的范围不可能与真正跑过的组合
# 分家。（早先还有一个 run_slurm.sh 各写一份，靠测试锁两者相等；rerun_v3 定稿后它被
# 删掉了。）tests/test_sweep_scripts.py 锁住取值等距、以及基线落在被扫的档位里。
#
# 同理，下面 build_tasks 里 `for lh in ...` 那一行被 build_tables.py::limh_swept
# 直接解析，填 Table 1 / Table S1 的承载力扫描列。改那一行等于改表，别改成
# 数组或别的写法；tests/test_sweep_scripts.py::TestForagerCapacityArms 兜着。
F2H_VALUES=(0.0 0.002 0.004 0.006 0.008 0.01 0.012 0.014 0.016 0.018 0.02)
H2F_VALUES=(0.0 0.015 0.03 0.045 0.06 0.075 0.09 0.105 0.12 0.135 0.15)

# ── 任务清单 ─────────────────────────────────────────────────────────────────
# 每行: <相对输出目录>|<override1 override2 ...>
build_tasks() {
    local n ov

    # 任务 0-26：convert 3³。Fig 2 基线 = f2h 0.1 / h2f 0.05 / h2r 0.05（组内 22），
    # Fig 3a 全关对照 = 三者皆 0（组内 0）——notebook 按这两个目录名直接取用。
    n=0
    for f2h in 0.0 0.05 0.1; do
        for h2f in 0.0 0.05 0.1; do
            for h2r in 0.0 0.05 0.1; do
                ov="Farmer.convert_prob.to_hunter=${f2h} Hunter.convert_prob.to_farmer=${h2f} Hunter.convert_prob.to_rice=${h2r}"
                echo "${SWEEP_ROOT}/convert3/${n}_${ov// /,}|${ov}"
                n=$((n + 1))
            done
        done
    done

    # 任务 27-51：移民强度 5×5。Fig 4a 的 lam_farmer 与 Fig 5 的 lam_ricefarmer。
    n=0
    for lf in 2 4 6 8 10; do
        for lr in 0.1 0.2 0.3 0.4 0.5; do
            ov="env.lam_farmer=${lf} env.lam_ricefarmer=${lr}"
            echo "${SWEEP_ROOT}/lam/${n}_${ov// /,}|${ov}"
            n=$((n + 1))
        done
    done

    # 任务 52-54：狩猎采集者承载力，Fig 4b。取值是密度按格子面积换算来的：
    # 15/25/35 人/百平方公里 × 80 km²/格 = 12/20/28 人/格，基线 28 是其中一档。
    n=0
    for lh in 12 20 28; do
        ov="env.lim_h=${lh}"
        echo "${SWEEP_ROOT}/limh/${n}_${ov// /,}|${ov}"
        n=$((n + 1))
    done

    # 任务 55-58：地貌均质化 2×2，Fig 4c。
    # override 值里的 / 会被 Hydra 当成路径分隔符，目录因此是两层嵌套——
    # load_terrain 正是按这个结构解析的，不要"修正"成单层。
    n=0
    for dem in ohndem10 ohn_value1; do
        for slo in ohnslo10 ohn_value0; do
            ov="ds.dem=data/${dem}.tif ds.slope=data/${slo}.tif"
            echo "${SWEEP_ROOT}/terrain/${n}_${ov// /,}|${ov}"
            n=$((n + 1))
        done
    done

    # 任务 59-94：转化概率广网格 6×6，Fig 3b 的 f2h 悬崖曲线。
    # 这两组的目录名是 load_fine_grid 要的 idx<n>_f2h<a>_h2f<b>，不能由 ov 派生；
    # 但名字里的数值和 ov 里的数值同出于循环变量，仍然只写了一遍。
    n=0
    for f2h in 0.0 0.02 0.04 0.06 0.08 0.1; do
        for h2f in 0.0 0.02 0.04 0.06 0.08 0.1; do
            echo "${SWEEP_ROOT}/grid_broad/idx${n}_f2h${f2h}_h2f${h2f}|Farmer.convert_prob.to_hunter=${f2h} Hunter.convert_prob.to_farmer=${h2f}"
            n=$((n + 1))
        done
    done

    # 任务 95-215：转化概率精细网格 11×11，Fig 3c 的响应面。
    # 循环顺序刻意让 f2h 变得最快（h2f 在外层），这样组内 idx 与 run_slurm.sh 的
    # F2H_IDX=$((INDEX % 11)) 完全一致——同一个 idx 在新旧两批数据里指同一组参数，
    # 便于交叉核对。
    n=0
    for h2f in "${H2F_VALUES[@]}"; do
        for f2h in "${F2H_VALUES[@]}"; do
            echo "${SWEEP_ROOT}/grid_fine/idx${n}_f2h${f2h}_h2f${h2f}|Farmer.convert_prob.to_hunter=${f2h} Hunter.convert_prob.to_farmer=${h2f}"
            n=$((n + 1))
        done
    done
}

# 取第 N 个任务（0-based），越界即报错。
# sed 用 -n "Np" 而不是 "Np;q"：不加 q 才会把 stdin 读完，否则 build_tasks 会吃到
# SIGPIPE，在 set -o pipefail 下变成伪失败。
task_line() {
    local index="$1" line
    line=$(build_tasks | sed -n "$((index + 1))p")
    if [[ -z "$line" ]]; then
        echo "Error: no task defined for index ${index} (valid: 0-$(($(build_tasks | wc -l) - 1)))" >&2
        return 1
    fi
    printf '%s\n' "$line"
}

# 把递增的任务号压成 SLURM 的 --array 语法：0 1 2 5 7 8 -> 0-2,5,7-8。
# 不压缩的话几百个逗号分隔的下标会长得没法用。
compress_indices() {
    local out="" start prev n
    for n in "$@"; do
        if [[ -z "${start:-}" ]]; then
            start=$n; prev=$n; continue
        fi
        if [[ $n -eq $((prev + 1)) ]]; then
            prev=$n; continue
        fi
        if [[ $start -eq $prev ]]; then out+="${start},"; else out+="${start}-${prev},"; fi
        start=$n; prev=$n
    done
    if [[ -n "${start:-}" ]]; then
        if [[ $start -eq $prev ]]; then out+="${start}"; else out+="${start}-${prev}"; fi
    fi
    printf '%s' "$out"
}

# 逐个任务检查产出是否齐全，打印未完成的任务号。
# 判定口径与 src/__main__.py 的跳过逻辑一致：目录里要有 exp.repeats 个 *_tracking.csv。
verify_tasks() {
    local repeats done_n partial_n missing_n dir count incomplete=()
    # -E 而非基本正则：BSD sed（macOS）不认 \+，集群上的 GNU sed 两者都认
    repeats=$(sed -nE 's/^[[:space:]]*repeats:[[:space:]]*([0-9]+).*/\1/p' config/config.yaml | head -1)
    : "${repeats:?cannot read exp.repeats from config/config.yaml}"
    done_n=0; partial_n=0; missing_n=0

    local index=0
    while IFS= read -r line; do
        dir="${line%%|*}"
        if [[ ! -d "$dir" ]]; then
            missing_n=$((missing_n + 1)); incomplete+=("$index")
        else
            # 数确切的 1..repeats，与 src/__main__.py 的跳过判据完全一致；
            # 用 *_tracking.csv 通配会把杂散文件也算进来，两边就会有分歧。
            count=0
            for i in $(seq 1 "$repeats"); do
                [[ -f "${dir}/${i}_tracking.csv" ]] && count=$((count + 1))
            done
            if [[ "$count" -eq "$repeats" ]]; then
                done_n=$((done_n + 1))
            else
                partial_n=$((partial_n + 1)); incomplete+=("$index")
                echo "  partial: task ${index} has ${count}/${repeats} in ${dir}"
            fi
        fi
        index=$((index + 1))
    done < <(build_tasks)

    echo "complete: ${done_n}   partial: ${partial_n}   missing: ${missing_n}   (of ${index})"
    if [[ ${#incomplete[@]} -gt 0 ]]; then
        echo
        echo "resubmit the rest with:"
        echo "  sbatch --array=$(compress_indices "${incomplete[@]}")%32 $(basename "$0")"
        return 1
    fi
    echo "all tasks complete — safe to repoint the notebook at ${SWEEP_ROOT}"
}

# ── 本地辅助：--prep / --smoke / --list / --dry-run / --verify 不需要 SLURM ──
# 在登录节点跑一次，把 .venv 准备好。任务本身不再碰环境（见下面 SLURM 段的说明）。
if [[ "${1:-}" == "--prep" ]]; then
    if [[ -n "${SLURM_ARRAY_TASK_ID:-}" ]]; then
        echo "Error: --prep must run once on the login node, not inside an array task." >&2
        echo "Running it in every task at once is what corrupted .venv in job 26949." >&2
        exit 1
    fi
    command -v uv >/dev/null 2>&1 || { echo "Error: uv is not found." >&2; exit 1; }
    load_cluster_python
    export PATH="$HOME/.local/bin:$PATH"
    echo "Syncing .venv once, on this node..."
    # --inexact：不删除不属于本组的包。这个 .venv 也服务于出图流程（notebook 组的
    # nbconvert 等），默认的剪枝会把分析环境一起清掉。
    uv sync --no-dev --inexact
    .venv/bin/python -c "import src; print('env ready:', src.__file__)"
    exit 0
fi

# 投递前的冒烟测试：两步跑通一个任务，确认解释器、依赖和 override 引号都没问题。
# 产出写进临时目录，绝不碰 out/——真实目录里留半截产物会让 --verify 误判为 partial。
if [[ "${1:-}" == "--smoke" ]]; then
    smoke_index="${TASK:-0}"
    smoke_line=$(task_line "$smoke_index")
    smoke_tmp=$(mktemp -d)
    trap 'rm -rf "$smoke_tmp"' EXIT
    load_cluster_python
    if [[ ! -x .venv/bin/python ]]; then
        echo "Error: .venv/bin/python not found; run --prep first." >&2
        exit 1
    fi
    echo "smoke-testing task ${smoke_index} in ${smoke_tmp} (2 steps, 1 repeat)"
    # 保留任务真实的相对目录名，带 / 和 , 的路径也一并验到
    # shellcheck disable=SC2086  # override 串必须按空格拆开
    .venv/bin/python src ${smoke_line#*|} time.end=2 exp.repeats=1 \
        "hydra.run.dir='${smoke_tmp}/${smoke_line%%|*}'"
    echo "smoke test OK — nothing was written under out/"
    exit 0
fi

if [[ "${1:-}" == "--verify" ]]; then
    # 显式收口：全绿时 verify_tasks 返回 0，若只写 `verify_tasks` 就会继续往下掉进
    # SLURM 段，报一句莫名其妙的 "not running under sbatch"。
    verify_tasks || exit 1
    exit 0
fi

if [[ "${1:-}" == "--list" ]]; then
    build_tasks | nl -v 0 -w4 -s'  '
    echo "total: $(build_tasks | wc -l) tasks"
    exit 0
fi

if [[ "${1:-}" == "--dry-run" ]]; then
    TASK_LINE=$(task_line "${TASK:-0}")
    echo "would run:"
    echo "  .venv/bin/python src ${TASK_LINE#*|} \"hydra.run.dir='${TASK_LINE%%|*}'\""
    exit 0
fi

# ── SLURM 正式执行 ───────────────────────────────────────────────────────────
# 先确认确实在数组作业里，再动 module / uv——否则会白跑一次几分钟的 uv sync 才失败。
: "${SLURM_ARRAY_TASK_ID:?not running under sbatch; use --prep / --smoke / --list / --dry-run / --verify locally}"

# SCE_EXTRA_OVERRIDES 曾用于冒烟测试，现在由 --smoke 承担。留这个口子很危险：
# sbatch 默认 --export=ALL，在冒烟测试后的同一个 shell 里投递，216 个任务会静默继承
# time.end=2，跑出一批两步的垃圾数据、而且全都"成功"。
if [[ -n "${SCE_EXTRA_OVERRIDES:-}" ]]; then
    echo "Error: SCE_EXTRA_OVERRIDES is set inside a batch job; refusing to run." >&2
    echo "It was probably exported while smoke testing; use --smoke instead and unset" >&2
    echo "it before sbatch (sbatch exports your whole environment by default)." >&2
    exit 1
fi
TASK_LINE=$(task_line "${SLURM_ARRAY_TASK_ID}")
JOB_DIR="${TASK_LINE%%|*}"
OVERRIDES="${TASK_LINE#*|}"

echo "Job ID: ${SLURM_JOB_ID:-NA}"
echo "Array Job ID: ${SLURM_ARRAY_JOB_ID:-NA}"
echo "Array Task ID: ${SLURM_ARRAY_TASK_ID}"
echo "Node: ${SLURM_NODELIST:-NA}"
echo "Start Time: $(date)"
echo "Working Directory: $(pwd)"
echo "  dir:       ${JOB_DIR}"
echo "  overrides: ${OVERRIDES}"

load_cluster_python
mkdir -p logs

# 任务里**不做**任何环境同步——这正是 26949 那次全军覆没的原因：
# 几十个任务分散在不同节点上同时 `uv sync` 同一个共享 .venv，把它写坏了
#   error: failed to remove directory `.venv/lib`: Not a directory (os error 20)
# flock 只在单机内有效，跨节点锁不住；而且 `uv run` 默认也会自己同步一次，
# 所以光去掉显式的 uv sync 还不够，必须绕开 uv 直接用 venv 里的解释器。
# 环境请在投递前用 `bash run_slurm_rerun.sh --prep` 在登录节点准备好一次。
if [[ ! -x .venv/bin/python ]]; then
    echo "Error: .venv/bin/python not found." >&2
    echo "Run 'bash $(basename "$0") --prep' on the login node before submitting." >&2
    exit 1
fi
# 这验的是"用这个解释器能否 import src 及其依赖"（src 从当前目录解析，运行时也一样），
# 不是"项目装没装进 venv"。依赖缺失、或 venv 指向已被 purge 的解释器，都会在这里挂。
if ! .venv/bin/python -c "import src" 2>/dev/null; then
    echo "Error: .venv/bin/python cannot import src (missing deps, or the venv points" >&2
    echo "at an interpreter this node purged)." >&2
    echo "Run 'bash $(basename "$0") --prep' on the login node before submitting." >&2
    exit 1
fi

# hydra.run.dir 的值里带 = 和 ,（为了对齐 figures.py 的目录解析），必须用单引号
# 包起来交给 Hydra 的 override 语法，否则会报 "mismatched input '=' expecting <EOF>"。
# shellcheck disable=SC2086  # OVERRIDES 必须按空格拆成多个参数
.venv/bin/python src $OVERRIDES "hydra.run.dir='${JOB_DIR}'"

echo "End Time: $(date)"
echo "Task ${SLURM_ARRAY_TASK_ID} completed"
