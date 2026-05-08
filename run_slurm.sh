#!/bin/bash -l
#SBATCH --job-name=sce_threshold
#SBATCH --array=0-32%8
#SBATCH --time=12:00:00
#SBATCH --output=logs/%x-%A_%a.out
#SBATCH --error=logs/%x-%A_%a.err
#SBATCH --mem=32G
#SBATCH --cpus-per-task=5
#SBATCH --mail-user=song@gea.mpg.de
#SBATCH --mail-type=END,FAIL

# ──────────────────────────────────────────────────────────────────────────────
# f2h 阈值锁定实验：在 [0, 0.02] 区间细分 11 个采样点 × h2f 3 档（33 task）
#
# 背景:
#   `grid_f2h_h2f_v1`（6×6, 间隔 0.02）发现 f2h: 0 → 0.02 这一步占总下降的 80%+，
#   存在"软阈值"。此实验在 [0, 0.02] 内细分到 0.002 步长以精确定位阈值位置，
#   并用 3 档 h2f (0/0.05/0.1) 看阈值是否随 h2f 变化。
#
# 设计:
#   • f2h ∈ {0.000, 0.002, 0.004, ..., 0.020} （11 值，间隔 0.002）
#   • h2f ∈ {0.0, 0.05, 0.10} （3 档：低/默认/高）
#   • 11 × 3 = 33 组合 × 5 repeats，每 run 500 步
#   • SLURM array %8 并发；单 task 12h、5 CPUs、对齐 exp.num_process=5
#
# 断点恢复:
#   • Stable 输出目录 out/south_china_evolution/grid_f2h_threshold_v1/idx{N}_f2h{a}_h2f{b}/
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

# 参数网格定义：11 × 3 = 33 组合（f2h 在 [0, 0.02] 细分，h2f 3 档）
F2H_VALUES=(0.0 0.002 0.004 0.006 0.008 0.01 0.012 0.014 0.016 0.018 0.02)
H2F_VALUES=(0.0 0.05 0.1)

INDEX=$SLURM_ARRAY_TASK_ID
F2H_IDX=$((INDEX / 3))   # 11 个 f2h 值
H2F_IDX=$((INDEX % 3))   # 3 个 h2f 值
F2H=${F2H_VALUES[$F2H_IDX]}
H2F=${H2F_VALUES[$H2F_IDX]}

# Stable 输出目录（独立于 v1，方便分析时区分两次实验）
SWEEP_ROOT="out/south_china_evolution/grid_f2h_threshold_v1"
JOB_DIR="${SWEEP_ROOT}/idx${INDEX}_f2h${F2H}_h2f${H2F}"

echo "Task $INDEX: f2h=$F2H, h2f=$H2F"
echo "Job dir: $JOB_DIR"

uv run python src \
    "Farmer.convert_prob.to_hunter=${F2H}" \
    "Hunter.convert_prob.to_farmer=${H2F}" \
    "hydra.run.dir=${JOB_DIR}"

echo "End Time: $(date)"
echo "Task $INDEX completed"
