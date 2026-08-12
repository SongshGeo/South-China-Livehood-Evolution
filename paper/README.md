# paper/

Manuscript prose for the South China livelihood-evolution study.

- `methods.md` — **main-text Methods**. Concise and overview-level: model
  purpose, landscape and agents, the core processes, and the four simulation
  experiments organised by figure (Figure 2–5), plus a compact key-parameter
  table. Points to the SI for the full specification.
- `si_odd_protocol.md` — **Supplementary Information**. The full, protocol-
  conformant model description following ODD+D (Overview, Design concepts,
  Details, and human Decision-making). Contains every submodel equation, the
  design-concept subsections, initialisation, input data, and the full parameter
  list (Table S1).

Both follow the `project-to-paper` conventions for ABM writing
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
