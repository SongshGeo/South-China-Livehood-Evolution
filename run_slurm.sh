#!/bin/bash -l
#SBATCH --job-name=sce_grid_search
#SBATCH --time=24:00:00
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

# Create logs directory if it doesn't exist
mkdir -p logs

# Change to project directory (adjust if needed when submitting from different location)
cd "$SLURM_SUBMIT_DIR" || cd "$(dirname "$0")"

# Run the parameter grid search
# This will create 25 parameter combinations (5x5), each repeated 5 times = 125 total runs
uv run python src -m env.lam_farmer=2,4,6,8,10 env.lam_ricefarmer=0.1,0.2,0.3,0.4,0.5

echo "End Time: $(date)"
echo "Job completed successfully"
