# Dependencies are declared in pyproject.toml ([project] + [dependency-groups])
# and pinned in uv.lock. uv is the only package manager; don't add poetry commands.

# Remote checkout used by the fetch-* targets. Override on the command line to
# point at a different host, e.g. make fetch-rerun GEANY_REMOTE=other:/path/repo
GEANY_REMOTE ?= geany:/u/songsh/CodeBase/South-China-Livehood-Evolution
RERUN_REL := out/south_china_evolution/rerun_v3

# The Obsidian longform project the manuscript is written in. Prose travels from
# there to here through the symlinks in paper/; figures and the tables workbook
# travel the other way, which is what `sync-vault` does. See paper/README.md.
# The path contains spaces, so every use of it must stay quoted.
VAULT_PROJECT ?= $(HOME)/Documents/Obsidian/Scholar-Vault/50 - Outputs/Longform/华南农业ABM

# Notebooks under reports/ that generate manuscript assets. `make figures`
# re-executes every one of them.
#
# Deliberately separate from FIGURE_SLUGS below: a figure can be reproducible
# before it has been given a manuscript number, and it should be. An asset that
# no target rebuilds goes stale the moment its data or its code changes, with
# nothing to say so — which is the exact failure `sync-vault` exists to prevent
# one step further downstream.
FIGURE_NOTEBOOKS := manuscript_figures c14_sites

# Figure N in the manuscript <- reports/figure<N>_<slug>.{png,pdf}
# Numbered figures only; sync-vault copies exactly these into the vault as
# SCE_figure<N>.{png,pdf}. Figure 1 (the SI-2 radiocarbon timeline) replaced the
# hand-made study-area map, which was dropped from the manuscript rather than
# moved to the SI. That map was never part of this pipeline, so nothing here had
# to be renumbered.
FIGURE_SLUGS := 1:c14_sites 2:baseline_suppression 3:conversion 4:expansion_factors 5:paddy_vs_dryland

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
	@echo "Fetching $(notdir $(RERUN_REL)) from $(GEANY_REMOTE)..."
	@rsync -avzP --partial \
		"$(GEANY_REMOTE)/$(RERUN_REL)/" "./$(RERUN_REL)/" || { \
		echo "Error: failed to fetch $(notdir $(RERUN_REL))"; \
		echo "Check SSH access to geany and that the remote path exists"; \
		exit 1; \
	}
	@echo "Fetched. Now verify completeness:"
	@echo "  bash run_slurm_rerun.sh --verify"

# Copies the generated assets into the vault's figs/. Run it after rebuilding the
# figure notebook or the workbook — nothing else propagates them, so the vault
# would otherwise export last week's figures without complaining.
#
# Everything is checked before anything is copied, and the copies run under
# `set -e`: a half-synced vault is worse than an unsynced one, because the mix of
# old and new files carries no sign of which is which.
.PHONY: sync-vault figures results check-results
# The gold standard for every number the paper quotes. `results` recomputes and
# rewrites paper/results.json; `check-results` recomputes and diffs without writing,
# naming the key that moved. The same comparison runs inside `make test`
# (tests/test_results_regression.py), which skips the figure tiers when the sweep
# is not on this machine.
results:
	uv run python paper/build_results.py

check-results:
	uv run python paper/build_results.py --check

sync-vault:
	@test -d "$(VAULT_PROJECT)/figs" || { \
		echo "Error: no figs/ under the longform project:"; \
		echo "  $(VAULT_PROJECT)"; \
		echo "Override the location with: make sync-vault VAULT_PROJECT=/path/to/project"; \
		exit 1; \
	}
	@missing=; corrupt=; \
	for pair in $(FIGURE_SLUGS); do \
		n=$${pair%%:*}; slug=$${pair##*:}; \
		for ext in png pdf; do \
			src="reports/figure$${n}_$${slug}.$${ext}"; \
			if [ ! -f "$$src" ]; then \
				missing="$$missing  $$src\n"; \
			else \
				case "$$ext" in png) want=89504e47 ;; pdf) want=25504446 ;; esac; \
				got=$$(od -An -tx1 -N4 "$$src" | tr -d ' \n'); \
				[ "$$got" = "$$want" ] || corrupt="$$corrupt  $$src\n"; \
			fi; \
		done; \
	done; \
	test -f paper/figs/SCE_Tables.xlsx || missing="$$missing  paper/figs/SCE_Tables.xlsx\n"; \
	if [ -n "$$missing" ]; then \
		echo "Error: cannot sync, these generated assets are missing:"; \
		printf "$$missing"; \
		echo "Rebuild everything and sync in one go:"; \
		echo "  make figures"; \
		exit 1; \
	fi; \
	if [ -n "$$corrupt" ]; then \
		echo "Error: cannot sync, these assets exist but are not valid PNG/PDF:"; \
		printf "$$corrupt"; \
		echo "A truncated or clobbered figure passes an existence check and then"; \
		echo "ships to the vault looking like a real one. Rebuild it:"; \
		echo "  make figures"; \
		exit 1; \
	fi
	@set -e; \
	for pair in $(FIGURE_SLUGS); do \
		n=$${pair%%:*}; slug=$${pair##*:}; \
		for ext in png pdf; do \
			cp "reports/figure$${n}_$${slug}.$${ext}" \
			   "$(VAULT_PROJECT)/figs/SCE_figure$${n}.$${ext}"; \
		done; \
	done; \
	cp paper/figs/SCE_Tables.xlsx "$(VAULT_PROJECT)/figs/SCE_Tables.xlsx"
	@echo "Synced SCE_figure*.{png,pdf} + SCE_Tables.xlsx into:"
	@echo "  $(VAULT_PROJECT)/figs/"

# Rebuild every generated manuscript asset, then push it to the vault. The notebooks
# redraw the figures, build_tables rebuilds the workbook, and build_results refreshes
# paper/results.json so the numbers quoted in the prose cannot lag the figures.
figures:
	@set -e; for nb in $(FIGURE_NOTEBOOKS); do \
		test -f "reports/$$nb.ipynb" || { \
			echo "Error: no such notebook: reports/$$nb.ipynb"; \
			echo "Fix the FIGURE_NOTEBOOKS list at the top of this makefile."; \
			exit 1; \
		}; \
	done; \
	for nb in $(FIGURE_NOTEBOOKS); do \
		echo "executing reports/$$nb.ipynb"; \
		uv run jupyter nbconvert --execute --to notebook --inplace "reports/$$nb.ipynb"; \
	done
	uv run python paper/build_tables.py
	uv run python paper/build_results.py
	@$(MAKE) --no-print-directory sync-vault

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
