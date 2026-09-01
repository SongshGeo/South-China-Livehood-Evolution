# From Model to Manuscript

This page covers this repository's **main deliverable**: the paper's five figures, its
table workbook, and every number the prose quotes — what produces each, how to rebuild
them, and how they are stopped from going stale in silence.

For running the model itself see [Quick Start]; this page assumes you already have a
sweep on disk.

## Four layers, never blurred

| Layer | Where | Does | Never does |
| :--- | :--- | :--- | :--- |
| Core package | `src/` | constants, classes, core functions, panel builders — all tested | hard-code paths; hold one-shot experiment glue |
| Batch script | `run_slurm_rerun.sh` | one-shot batch runs → data under `out/` | touch `results.json`; hold core algorithms |
| Notebooks | `reports/*.ipynb` | one core call per cell, composing the final figure | heavy analysis inline |
| Manuscript | `paper/` + the Obsidian vault | prose, figures, `results.json`, the table workbook | analysis logic; hand-typed numbers |

Blurring them has a concrete cost: once a piece of logic exists twice, the two copies can
drift apart — and **both keep running, and neither raises**; one of them is simply using
old data. This repository has been bitten by exactly that; see the last section.

## The whole chain

```
run_slurm_rerun.sh          216 SLURM tasks, six experiment groups
        │                   directory names align with figures.py's four loaders
        ▼
out/south_china_evolution/rerun_v3/     134 MB, gitignored, fetch with make fetch-rerun
        │
        ├──▶ reports/manuscript_figures.ipynb  ──▶ reports/figure2-5.{png,pdf}
        │       composed from src/workflow/figures.py's plot_* builders
        │
        ├──▶ reports/c14_sites.ipynb           ──▶ reports/figure1.{png,pdf}
        │       from src/workflow/c14.py over data/si2_c14_sites.xlsx (the SI-2 workbook)
        │
        ├──▶ paper/build_results.py            ──▶ paper/results.json   ★ gold standard
        │       computed by src/workflow/results.py
        │
        └──▶ paper/build_tables.py             ──▶ paper/figs/SCE_Tables.xlsx
                read from the Hydra config, the input rasters and the sweep script —
                not one value is retyped

                            │  make sync-vault
                            ▼
        the vault's figs/: SCE_figure1-5.{png,pdf} + SCE_Tables.xlsx
```

One command runs the whole chain:

```bash
make figures      # re-execute both notebooks → build_tables → build_results → sync-vault
```

## The gold standard: `paper/results.json`

Figures are files, and a stale file is at least visible. The numbers **read off** them are
not: an end-state share, an effect-size ratio, an $R^2$ get copied into the prose, the
captions, `paper/model-inventory.md` and the SI, and every copy can go stale on its own.

So each number is computed once, by `src/workflow/results.py`, and frozen into
`paper/results.json`, which is committed:

```bash
make results        # recompute and rewrite results.json
make check-results  # recompute and diff without writing; names the key that moved
```

`tests/test_results_regression.py` runs the same comparison inside `make test`. The file
has two tiers:

| Tier | Keys | Verifiable |
| :--- | :--- | :--- |
| Repo | `landscape`, `parameters`, `c14` | anywhere, CI included — the rasters, the Hydra config and the SI-2 workbook are versioned here |
| Sweep | `figure2`–`figure5` | only where `rerun_v3` is present; skipped, not failed, otherwise |

Values are stored to six significant figures: far tighter than any model change worth
noticing, far looser than the last-bit noise a NumPy or pandas upgrade can introduce.

**When a revision re-runs the model**, the regression test fails and names each key with
its old value, its new value, and the percentage change. Once you have confirmed the
change is intended, rebuild the gold file and propagate it to every place that quotes it.

## Four guards, each against a failure that raises nothing

| Guard | Catches |
| :--- | :--- |
| `tests/test_manuscript_figures_source.py` | a notebook data-path constant pointed back at a superseded sweep. Those directories were deleted locally, but `make fetch-geany-data` brings them all back in one command — after which pointing at one still produces figures, just superseded ones |
| `tests/test_results_regression.py` | the data or the algorithm moved while the numbers in the prose did not |
| `tests/test_config.py::test_every_exp_key_still_has_a_reader` | a config key nobody reads |
| `make sync-vault`'s pre-flight | a half-synced vault: it validates every asset before copying any, and aborts whole rather than leaving a mix of old and new |

## The prose is not in this repository

The main text and the SI are written in the Obsidian vault's longform project.
`paper/manuscript`, `paper/si_odd_protocol` and `paper/refs.bib` are **symlinks** into it —
the same files, editable from either side; there is nothing to sync and no way not to.
All three are gitignored because they store a machine-specific absolute path.

The only genuine copies are the figures and the table workbook, moved one way by
`make sync-vault`. Details in `paper/README.md`.

## These guards were earned

During the pre-submission clean-out, `paper/model-inventory.md`'s "What the re-run changed"
section turned out to be headed `rerun_v3` while all seven of its headline values were
still the previous batch's — the re-run had happened, the section had not been updated, and
nothing anywhere raised. The end-state agricultural share is 18.0%, not the recorded 15.4%;
the terrain effect is 1.80×, not 1.91×.

`results.json` exists so that cannot happen quietly again.

<!-- Links -->
[Quick Start]: /docs/usage/quick_start
