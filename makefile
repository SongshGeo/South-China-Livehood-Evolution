# Dependencies are declared in pyproject.toml ([project] + [dependency-groups])
# and pinned in uv.lock. uv is the only package manager; don't add poetry commands.
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

fetch-geany-data:
	@command -v rsync >/dev/null 2>&1 || { echo "Error: rsync is not installed"; exit 1; }
	@mkdir -p ./out/
	@echo "Fetching data from geany server..."
	@rsync -avzP --progress --partial geany:/u/songsh/CodeBase/South-China-Livehood-Evolution/out/ ./out/ || { \
		echo "Error: Failed to fetch data from geany server"; \
		echo "Please check:"; \
		echo "  1. Network connectivity"; \
		echo "  2. SSH access to geany server"; \
		echo "  3. Remote path exists"; \
		exit 1; \
	}
	@echo "Data fetch completed successfully"
