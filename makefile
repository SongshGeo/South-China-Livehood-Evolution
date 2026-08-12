setup:
	make install-tests
	make install-jupyter
	make setup-pre-commit

# black: https://github.com/psf/black
# flake8: https://github.com/pycqa/flake8
# isort: https://github.com/PyCQA/isort
# nbstripout: https://github.com/kynan/nbstripout
# pydocstyle: https://github.com/PyCQA/pydocstyle
# pre-commit-hooks: https://github.com/pre-commit/pre-commit-hooks
# interrogate: https://interrogate.readthedocs.io/en/latest/index.html?highlight=pre-commit

setup-pre-commit:
	poetry add --group dev flake8 isort nbstripout pydocstyle pre-commit-hooks interrogate sourcery mypy bandit black

install-pre-commit:
	poetry run pre-commit install

install-jupyter:
	poetry add ipykernel --group dev
	poetry add --group dev jupyterlab
	poetry add jupyterlab_execute_time --group dev

install-tests:
	poetry add hydra-core
	poetry add pytest allure-pytest --group dev
	poetry add pytest-cov --group dev
	poetry add pytest-clarity pytest-sugar --group dev

# https://timvink.github.io/mkdocs-git-authors-plugin/index.html
install-docs:
	poetry add --group docs mkdocs mkdocs-material
	poetry add --group docs mkdocs-git-revision-date-localized-plugin
	poetry add --group docs mkdocs-minify-plugin
	poetry add --group docs mkdocs-redirects
	poetry add --group docs mkdocs-awesome-pages-plugin
	poetry add --group docs mkdocs-git-authors-plugin
	poetry add --group docs mkdocstrings\[python\]
	poetry add --group docs mkdocs-bibtex
	poetry add --group docs mkdocs-macros-plugin
	poetry add --group docs mkdocs-jupyter
	poetry add --group docs mkdocs-callouts
	poetry add --group docs mkdocs-glightbox

test:
	@if [ -x .venv/bin/python ]; then \
		. .venv/bin/activate && python -m pytest -vs --clean-alluredir --alluredir tmp/allure_results --cov=src --no-cov-on-fail; \
	else \
		poetry run python -m pytest -vs --clean-alluredir --alluredir tmp/allure_results --cov=src --no-cov-on-fail; \
	fi

report:
	poetry run allure serve tmp/allure_results

update-dependencies:
	poetry export --without-hashes --with docs --without dev -f requirements.txt -o requirements.txt

clean:
	rm repeat_*
	rm docs/repeat_*

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
