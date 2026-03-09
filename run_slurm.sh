#!/bin/bash -l
#SBATCH --job-name=sce_grid_search
#SBATCH --time=150:00:00
#SBATCH --output=logs/%x-%j.out
#SBATCH --error=logs/%x-%j.err
#SBATCH --mem=16G
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

# Run the parameter grid search
# This will create parameter combinations over convert flags and ds datasets
echo "Starting parameter grid search..."
# uv run python src -m env.lam_farmer=2,4,6,8,10 env.lam_ricefarmer=0.1,0.2,0.3,0.4,0.5
uv run python src -m \
  ds.dem=data/ohndem10.tif,data/ohn_value1.tif \
  ds.slope=data/ohnslo10.tif,data/ohn_value0.tif

echo "End Time: $(date)"
echo "Job completed successfully"
