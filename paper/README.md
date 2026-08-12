# paper/

Manuscript prose for the South China livelihood-evolution study.

- `model-inventory.md` — **reconnaissance ledger**, written before the prose. A
  factual record of entities, scales, schedule, parameters, stochasticity, and
  existing evidence, every entry carrying a `file:line`. Its "Findings" section
  lists the places where the code and an earlier draft disagreed, and the open
  questions that only the author can settle (marked `[ASK]`). Re-derive it before
  editing the two documents below; they are downstream of it.
- `methods.md` — **main-text Methods**. Concise and overview-level: model
  purpose, landscape and agents, the core processes, and the four simulation
  experiments organised by figure (Figure 2–5), plus a compact key-parameter
  table. Points to the SI for the full specification.
- `si_odd_protocol.md` — **Supplementary Information**. The full, protocol-
  conformant model description following ODD+D (Overview, Design concepts,
  Details, and human Decision-making). Contains every submodel equation, the
  design-concept subsections, initialisation, input data, and the full parameter
  list (Table S1).

## Tables live in the workbook, not in the prose

Every table the manuscript needs is a sheet in the one workbook,
`figs/SCE_Tables.xlsx`; the prose carries only an `xlsx-table` block pointing at
the sheet, and refers to it as `Table \ref{tbl:…}`. Never write a markdown table
into `methods.md` or `si_odd_protocol.md` — it would carry hand-typed numbers
whose only copy is the prose, and it would be typeset outside the house style.

| Sheet | Label | In |
|---|---|---|
| `Table 1` | `tbl:key-params` | Methods |
| `Table S1` | `tbl:stochasticity` | SI, Design concepts |
| `Table S2` | `tbl:conversion-paths` | SI, Submodels |
| `Table S3` | `tbl:symbol-map` | SI, end |
| `Table S4` | `tbl:parameters` | SI, end |

The `_index` sheet registers each table's label, caption, and the source of its
numbers. Rebuild the workbook with `uv run python build_tables.py` from the
repository root: it reads defaults from the composed Hydra config, landscape
counts from the input rasters, and swept ranges from `run_slurm.sh`, so no value
is retyped. Edit the script, not the spreadsheet — a hand-edit is lost on the
next rebuild. Formulas are never written into cells: the export reads cached
values, so a formula renders blank in the PDF with no error.

`model-inventory.md` keeps its markdown tables. It is a working ledger, not a
manuscript, and is never exported.

Both manuscript files follow the `project-to-paper` conventions for ABM writing
(`references/abm-writing.md`): a two-layer split where the **main text uses
mathematical symbols** ($\lambda_F$, $p_{F\to H}$, $k_H$, …) and the **SI ODD+D
uses the implementation parameter names** (`env.lam_farmer`,
`Farmer.convert_prob.to_hunter`, `env.lim_h`, …) so the model can be replicated.
Both write the per-step schedule as an explicit ordered sequence, declare the
model class (heuristic, pattern-validated), and enumerate every stochastic
source. Same equations and parameters in both layers; only the notation differs.

Figures referenced by number (Figure 2–5) are produced by
`reports/manuscript_figures.ipynb`, which composes them from the core builders in
`src/workflow/figures.py`. Figure 1 (study-area map) is out of scope here.
