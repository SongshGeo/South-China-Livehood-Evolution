#!/bin/bash -l
#SBATCH --job-name=sce_grid_search
#SBATCH --time=150:00:00
#SBATCH --output=logs/%x-%j.out
#SBATCH --error=logs/%x-%j.err
#SBATCH --mem=32G
#SBATCH --cpus-per-task=8

# Print job information
echo "Job ID: $SLURM_JOB_ID"
echo "Job Name: $SLURM_JOB_NAME"
echo "Node: $SLURM_NODELIST"
echo "Start Time: $(date)"
echo "Working Directory: $(pwd)"

# Load modules
module purge
module load python-waterboa/2025.06

# Add uv to PATH (adjust if uv is installed elsewhere)
export PATH="$HOME/.local/bin:$PATH"

# Verify uv is available
if ! command -v uv &> /dev/null; then
    echo "Error: uv is not found. Please install uv first:"
    echo "  curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

# Create logs directory if it doesn't exist
mkdir -p logs

# Change to project directory (adjust if needed when submitting from different location)
cd "$SLURM_SUBMIT_DIR" || cd "$(dirname "$0")"

# Sync dependencies first (this will generate/update uv.lock if needed)
# uv sync reads pyproject.toml and installs all dependencies
echo "Syncing dependencies with uv..."
uv sync --no-dev

# Run the parameter grid search using Hydra multirun
# 扫描 hunter↔farmer / hunter→rice 三条转化路径的概率，每条 {0.0, 0.05, 0.1} → 3^3 = 27 组
echo "Starting 3^3 convert_prob grid search (27 combinations)..."

uv run python src -m \
    Farmer.convert_prob.to_hunter=0.0,0.05,0.1 \
    Hunter.convert_prob.to_farmer=0.0,0.05,0.1 \
    Hunter.convert_prob.to_rice=0.0,0.05,0.1

echo "End Time: $(date)"
echo "Job completed successfully"
