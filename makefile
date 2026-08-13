# Dependencies are declared in pyproject.toml ([project] + [dependency-groups])
# and pinned in uv.lock. uv is the only package manager; don't add poetry commands.

# Remote checkout used by the fetch-* targets. Override on the command line to
# point at a different host, e.g. make fetch-rerun GEANY_REMOTE=other:/path/repo
GEANY_REMOTE ?= geany:/u/songsh/CodeBase/South-China-Livehood-Evolution
RERUN_REL := out/south_china_evolution/rerun_v2

setup: uv-setup uv-geo uv-install install-pre-commit

# Runtime + dev tooling (pytest, black, flake8, isort, pre-commit).
sync:
	uv sync

# Adds the notebook group (ipykernel, jupyterlab) on top of `sync`.
sync-all:
	uv sync --all-groups

install-pre-commit:
	uv run pre-commit install

test:
	@if [ -x .venv/bin/python ]; then \
		. .venv/bin/activate && python -m pytest -vs --clean-alluredir --alluredir tmp/allure_results --cov=src --no-cov-on-fail; \
	else \
		uv run python -m pytest -vs --clean-alluredir --alluredir tmp/allure_results --cov=src --no-cov-on-fail; \
	fi

report:
	uv run allure serve tmp/allure_results

# Refresh uv.lock after editing pyproject.toml (also enforced by the uv-lock hook).
lock:
	uv lock

clean:
	rm -rf tmp/ outputs/ multirun/

# ==== UV-based CI helpers ====
uv-setup:
	uv venv --python 3.11 .venv --clear

uv-geo:
	. .venv/bin/activate && uv pip install --only-binary=:all: shapely==2.0.4 rasterio==1.4.3 geopandas==0.14.4 fiona==1.9.6 rtree pyproj

uv-install:
	. .venv/bin/activate && uv pip install -e .
	. .venv/bin/activate && uv pip install pytest allure-pytest pytest-cov pytest-clarity pytest-sugar

ci: uv-setup uv-geo uv-install test

# Fetches only the re-run sweep (~135 MB); fetch-geany-data syncs all of out/.
fetch-rerun:
	@command -v rsync >/dev/null 2>&1 || { echo "Error: rsync is not installed"; exit 1; }
	@mkdir -p ./$(RERUN_REL)/
	@echo "Fetching rerun_v2 from $(GEANY_REMOTE)..."
	@rsync -avzP --partial \
		"$(GEANY_REMOTE)/$(RERUN_REL)/" "./$(RERUN_REL)/" || { \
		echo "Error: failed to fetch rerun_v2"; \
		echo "Check SSH access to geany and that the remote path exists"; \
		exit 1; \
	}
	@echo "Fetched. Now verify completeness:"
	@echo "  bash run_slurm_rerun.sh --verify"

fetch-geany-data:
	@command -v rsync >/dev/null 2>&1 || { echo "Error: rsync is not installed"; exit 1; }
	@mkdir -p ./out/
	@echo "Fetching data from geany server..."
	@rsync -avzP --progress --partial "$(GEANY_REMOTE)/out/" ./out/ || { \
		echo "Error: Failed to fetch data from geany server"; \
		echo "Please check:"; \
		echo "  1. Network connectivity"; \
		echo "  2. SSH access to geany server"; \
		echo "  3. Remote path exists"; \
		exit 1; \
	}
	@echo "Data fetch completed successfully"
