#!/bin/bash -l
#SBATCH --job-name=sce_h2f_fine
#SBATCH --array=0-92%8
#SBATCH --time=12:00:00
#SBATCH --output=logs/%x-%A_%a.out
#SBATCH --error=logs/%x-%A_%a.err
#SBATCH --mem=32G
#SBATCH --cpus-per-task=5
#SBATCH --mail-user=song@gea.mpg.de
#SBATCH --mail-type=END,FAIL

# ──────────────────────────────────────────────────────────────────────────────
# h2f 精细扫描实验：转置 v1，固定 3 个 f2h 切片 × h2f 31 个采样点（93 task）
#
# 背景:
#   `grid_f2h_threshold_v1`（11×3）里 h2f 只有 3 档 (0/0.05/0.1)，相对 f2h 的
#   0.002 精细横轴太粗，diffs 图上三条 h2f 曲线几乎重合、看不出差异。已知 h2f 是
#   "源/供给"旋钮（加性抬升基线、右移曲率拐点，但不移动最陡降点 f2h=0.004）。
#   此实验把 h2f 自己做成精细横轴，直接显示其效应。
#
# 设计:
#   • f2h ∈ {0.000, 0.004, 0.010} （3 切片：纯源 / 最陡降点 / 近饱和）
#   • h2f ∈ {0.000, 0.005, ..., 0.150} （31 值，步长 0.005，往上探至 0.15 看饱和）
#   • 3 × 31 = 93 组合 × 5 repeats，每 run 500 步
#   • SLURM array %8 并发；单 task 12h、5 CPUs、对齐 exp.num_process=5
#
# 断点恢复:
#   • Stable 输出目录 out/south_china_evolution/grid_h2f_fine_v1/idx{N}_f2h{a}_h2f{b}/
#   • src/__main__.py 在 batch_run 前检查 5 个 *_tracking.csv 是否齐全；齐全则跳过
#   • 重投 SLURM 自动跳过已完成 combo
#
# 重投示例:
#   sbatch run_slurm.sh                      # 全部重投，已完成的会被跳过
#   sbatch --array=5,12,19%4 run_slurm.sh    # 只重投失败的几个 task
# ──────────────────────────────────────────────────────────────────────────────

echo "Job ID: $SLURM_JOB_ID"
echo "Array Job ID: $SLURM_ARRAY_JOB_ID"
echo "Array Task ID: $SLURM_ARRAY_TASK_ID"
echo "Node: $SLURM_NODELIST"
echo "Start Time: $(date)"
echo "Working Directory: $(pwd)"

module purge
module load python-waterboa/2025.06

export PATH="$HOME/.local/bin:$PATH"

if ! command -v uv &> /dev/null; then
    echo "Error: uv is not found. Please install uv first."
    exit 1
fi

mkdir -p logs

cd "$SLURM_SUBMIT_DIR" || cd "$(dirname "$0")"

# 用 flock 串行化 uv sync，避免多 task 并发写 .venv；uv sync 本身幂等且快
echo "Syncing dependencies with uv (flock-serialized)..."
(
    flock -x 200
    uv sync --no-dev
) 200>.uv-sync.lock

# 参数网格定义：3 × 31 = 93 组合（f2h 3 切片，h2f 在 [0, 0.15] 细分到 0.005）
F2H_VALUES=(0.0 0.004 0.01)
H2F_VALUES=(0.0 0.005 0.01 0.015 0.02 0.025 0.03 0.035 0.04 0.045 0.05 0.055 0.06 0.065 0.07 0.075 0.08 0.085 0.09 0.095 0.1 0.105 0.11 0.115 0.12 0.125 0.13 0.135 0.14 0.145 0.15)

INDEX=$SLURM_ARRAY_TASK_ID
F2H_IDX=$((INDEX % 3))    # 3 个 f2h 切片
H2F_IDX=$((INDEX / 3))    # 31 个 h2f 值
F2H=${F2H_VALUES[$F2H_IDX]}
H2F=${H2F_VALUES[$H2F_IDX]}

# Stable 输出目录（独立于 v1，方便分析时区分两次实验）
SWEEP_ROOT="out/south_china_evolution/grid_h2f_fine_v1"
JOB_DIR="${SWEEP_ROOT}/idx${INDEX}_f2h${F2H}_h2f${H2F}"

echo "Task $INDEX: f2h=$F2H, h2f=$H2F"
echo "Job dir: $JOB_DIR"

uv run python src \
    "Farmer.convert_prob.to_hunter=${F2H}" \
    "Hunter.convert_prob.to_farmer=${H2F}" \
    "hydra.run.dir=${JOB_DIR}"

echo "End Time: $(date)"
echo "Task $INDEX completed"
