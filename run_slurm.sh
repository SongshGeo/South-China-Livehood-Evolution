#!/bin/bash -l
#SBATCH --job-name=sce_grid
#SBATCH --array=0-35%8
#SBATCH --time=12:00:00
#SBATCH --output=logs/%x-%A_%a.out
#SBATCH --error=logs/%x-%A_%a.err
#SBATCH --mem=32G
#SBATCH --cpus-per-task=5
#SBATCH --mail-user=song@gea.mpg.de
#SBATCH --mail-type=END,FAIL

# ──────────────────────────────────────────────────────────────────────────────
# 6×6 farmer↔hunter convert_prob 网格扫描（36 个 array task）
#
# 设计:
#   • SLURM array job: 36 个 task，每 task 跑 1 个参数组合 × 5 repeats
#   • %8 = 同时最多并发 8 个 task（按集群负载可调）
#   • 每 task 12h walltime，足以容纳一组 5 repeats × 500 步
#   • 每 task --cpus-per-task=5 对齐 exp.num_process=5（5 repeats 并行跑）
#   • 单 task 失败/超时不影响其它 task；整体壁钟 ≈ ceil(36/8) × 5h ≈ 25h
#
# 断点恢复:
#   • 每个 task 用 stable 输出目录 (无时间戳)，路径形如
#     out/south_china_evolution/grid_f2h_h2f_v1/idx{N}_f2h{a}_h2f{b}/
#   • src/__main__.py 在 batch_run 前检查 5 个 *_tracking.csv 是否已就位
#   • 若已就位则直接 return → 重投 SLURM 自动跳过已完成 combo
#
# 重投示例:
#   sbatch run_slurm.sh                       # 全部重投，已完成的会被跳过
#   sbatch --array=12,17,23%4 run_slurm.sh    # 只重投失败的几个 task
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

# 参数网格定义：6×6 = 36 组合
F2H_VALUES=(0.0 0.02 0.04 0.06 0.08 0.1)
H2F_VALUES=(0.0 0.02 0.04 0.06 0.08 0.1)

INDEX=$SLURM_ARRAY_TASK_ID
F2H_IDX=$((INDEX / 6))
H2F_IDX=$((INDEX % 6))
F2H=${F2H_VALUES[$F2H_IDX]}
H2F=${H2F_VALUES[$H2F_IDX]}

# Stable 输出目录：sweep 根目录无时间戳；子目录用简洁命名避免 Hydra override
# 解析含 `=`/`,` 的边角情况。analysis 端用 `idx{N}_f2h{a}_h2f{b}` 正则解析即可。
SWEEP_ROOT="out/south_china_evolution/grid_f2h_h2f_v1"
JOB_DIR="${SWEEP_ROOT}/idx${INDEX}_f2h${F2H}_h2f${H2F}"

echo "Task $INDEX: f2h=$F2H, h2f=$H2F"
echo "Job dir: $JOB_DIR"

uv run python src \
    "Farmer.convert_prob.to_hunter=${F2H}" \
    "Hunter.convert_prob.to_farmer=${H2F}" \
    "hydra.run.dir=${JOB_DIR}"

echo "End Time: $(date)"
echo "Task $INDEX completed"
