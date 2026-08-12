# Model inventory — reconnaissance ledger

Factual record of what the code does, recovered before the prose was written or
revised. Every entry carries a `file:line`. Entries marked **[ASK]** are things the
code does not settle; they are questions for the author, not values to invent.

Scope: the model proper is `src/api/` (agents and environment) plus
`src/core/model.py` (the step loop). `src/app.py` is a synthetic-landscape demo, not
the published model, and is excluded. `src/workflow/` is post-hoc analysis.

Recovered against commit on `dev` at the time of writing; ABSESpy 0.11.5, Python 3.11.

---

## 1. Entities

| Entity | Class | State variables | Source |
|---|---|---|---|
| Cell | `CompetingCell(PatchCell)` | `elevation`, `slope`, `water_type`; derived `is_water`, `is_near_water`, `is_arable`, `is_rice_arable`, `dem_suitable`, `slope_suitable` | `src/api/env.py:24-148` |
| Group (base) | `SiteGroup(Actor)` | `size`, `min_size`, `max_size`, `source` | `src/api/people.py:20-28` |
| Rainfed farmer | `Farmer(SiteGroup)` | adds `area`, mutable `growth_rate` | `src/api/farmer.py:26-35` |
| Paddy farmer | `RiceFarmer(Farmer)` | inherits Farmer; overrides `convert` only | `src/api/rice_farmer.py:13-20` |
| Forager | `Hunter(SiteGroup)` | adds `is_complex`, water-dependent `max_size` | `src/api/hunter.py:21-52` |
| Environment | `Env(BaseNature)` | `dem` layer, `global_hunter_limit` | `src/api/env.py:250-316` |

One cell holds at most one group (`max_agents = 1`, `env.py:27`), enforced in
`able_to_live` (`env.py:162-167`).

## 2. Scales

| Quantity | Value | Source |
|---|---|---|
| Raster frame | 119 × 202 = 24 038 cells | `data/ohndem10.tif` |
| **Modelled cells** (after nodata masking) | **6 835** | measured at runtime |
| Resolution | 5 arc-min (0.08333°), EPSG:4326 | raster metadata |
| Cell area | 75 km² (29.1°N) to 81 km² (19.2°N); mean ≈ **78 km²** | computed from resolution and latitude |
| Extent | 104.4–121.3°E, 19.2–29.1°N | raster bounds |
| Run length | `time.end` = 500 steps | `config/config.yaml:67` |
| Replicates | `exp.repeats` = 5 | `config/config.yaml:25` |
| **What one step means in real time** | **[ASK] not in code.** No calendar, no time driver, no unit anywhere in config or code | — |

Derived landscape counts at initialisation: `is_arable` 2 620 cells,
`is_rice_arable` 885 cells, `is_near_water` 1 064 cells, `is_water` **0 cells**
(see finding F7).

## 3. Schedule

`Model.step` (`src/core/model.py:206-212`), in order:

1. `do_each("step", order=("nature","human"))` → `Env.step` (`env.py:366-374`) adds
   immigrant groups: `add_farmers(Farmer)` then `add_farmers(RiceFarmer)`.
2. `agents.shuffle_do("step")` — every group acts once in a freshly randomised order.
   **Asynchronous**: a group sees updates made earlier in the same step.
   - `SiteGroup.step` (`people.py:217-222`): `population_growth` → `convert` →
     `diffuse` → `loss`.
   - `Hunter.step` (`hunter.py:192-195`): the above, then `move_one`.
   - `Farmer.step` (`farmer.py:140-142`): the above, then **`loss` a second time**
     (finding F1). `RiceFarmer` inherits `Farmer.step`.
3. `nature.apply_global_hunter_limit()` (`env.py:324-358`) — regional forager ceiling.
4. `datacollector.collect(self)` — recording happens **after** all updates.

## 4. Parameters

Baseline values are those Hydra actually composes (verified by composition, not by
reading), `config/config.yaml` unless noted. Swept ranges come from
`run_slurm.sh:67-68` and `reports/*.ipynb`.

| Parameter | Default | Swept | Source of value |
|---|---|---|---|
| `env.lim_h` | 35 per cell | {15, 25, 35} | comment cites Binford 2001 as 31.93 per 100 km² — **[ASK]** unit mismatch, see F8 |
| `env.init_hunters` | 0.5 | — | — |
| `env.init_farmers` / `init_rice_farmers` | 0 / 0 | — | — |
| `env.lam_farmer` / `lam_ricefarmer` | 3 / 0.1 | 2–10 / 0.1–0.5 | — |
| `env.tick_farmer` / `tick_ricefarmer` | 0 / 0 | — | — |
| `Farmer.growth_rate` | 0.005 | — | inline comment says "0.1~0.25", which contradicts the value — **[ASK]** |
| `RiceFarmer.growth_rate` | 0.006 | — | as above |
| `Hunter.growth_rate` | 0.001 | — | **[ASK]** no source given |
| `min_size` (all breeds) | 6 | — | Binford 2001; Kelly 2013 |
| `Farmer.area` / `RiceFarmer.area` | 2 km | — | Shelach 1999; Wu et al. 2023 |
| `Farmer.capital_area` | 0.004 km²/person | — | Qiao 2010, halved for South China productivity |
| `RiceFarmer.capital_area` | **0.002** km²/person | — | **[ASK]** no source given; differs from Farmer |
| `Farmer.init_size` / `RiceFarmer` / `Hunter` | [60,100] / [300,400] / [0,100] | — | farmer values unused at baseline (`init_farmers`=0) |
| `new_group_size` F / R / H | [30,60] / [200,300] / [6,50] | — | — |
| `diffuse_prob` (F, R) | 0.05 | — | **[ASK]** no source |
| `complexity` (F, R) | 0.1 | — | **[ASK]** no source |
| `Farmer.convert_prob.to_hunter` (f2h) | 0.1 | 0–0.02 step 0.002 (fine); 0–0.1 (coarse) | — |
| `Hunter.convert_prob.to_farmer` (h2f) | 0.05 | 0–0.15 step 0.015 (fine) | — |
| `Farmer.convert_prob.to_rice` | 0.05 | — | — |
| `Hunter.convert_prob.to_rice` | 0.05 | — | — |
| `RiceFarmer.convert_prob.to_farmer` | 1.0 | — | — |
| `convert_threshold.to_hunter` / `.to_rice` / `.to_farmer` | 100 / 200 / 200 | — | — |
| `Hunter.max_size` / `max_size_water` | 100 / 500 | — | Kelly 2013:171 for sedentism |
| `Hunter.is_complex` | 100 | — | Kelly 2013:171 |
| `max_travel_distance` | 5 cells | — | **[ASK]** no source |
| `Hunter.loss` prob/rate | 0.05 / 0.01 | 4 nominal scenarios, **all inert** (F5) | — |
| `Farmer.loss`, `RiceFarmer.loss` prob/rate | 0.01 / 0.05 | as above | — |
| `convert.enabled` + 5 path switches | all true | on/off contrast | — |

Derived: `Farmer.max_size` = π·`area`²/`capital_area` = π·4/0.004 ≈ **3 142**;
`RiceFarmer.max_size` = π·4/0.002 ≈ **6 283** (`farmer.py:80-84`).
Global forager ceiling = 35 × 6 835 = **239 225** (measured).

## 5. Stochasticity

| Source | Call | RNG |
|---|---|---|
| Immigrant counts (Poisson) | `env.py:454` | **global NumPy** — not the seeded model RNG (F4) |
| Immigrant cell choice | `env.py:465-469` | model RNG |
| Immigrant size | `env.py:472-473` | model RNG |
| Initial forager placement | `env.py:392` | model RNG |
| Initial group size | `people.py:78` | model RNG |
| Activation order each step | `model.py:209` `shuffle_do` | model RNG |
| Conversion Bernoulli trials | `hunter.py:122,151`; `farmer.py:90,99`; `rice_farmer.py:19` | model RNG |
| Colonisation trial and colony size | `farmer.py:123`; `people.py:111` | model RNG |
| Colonisation / movement target cell | `people.py:182,208` | model RNG |
| Mortality Bernoulli | `people.py:159`; `farmer.py:137` | model RNG |
| Forager trimming order at the ceiling | `env.py:358` `shuffle_do` | model RNG |
| Cell `slope`/`elevation` constructor defaults | `env.py:31-32` | global NumPy — overwritten by rasters, so inert |

Deterministic: population growth (`people.py:85`), intensification
(`farmer.py:128-133`), the ceiling amount itself.

## 6. Existing evidence

- Unit tests: 105 passing, covering agents, environment, conversion thresholds, and
  the figure builders (`tests/`, `make test`).
- No global sensitivity analysis (no Sobol/Morris) — the sweeps are one- and
  two-factor grids. This is the abm profile's standing objection #6.
- No independent validation dataset; evaluation is pattern-oriented by design.
- Breakpoint detection (`ruptures`, `Dynp`, `n_bkps`=1, `min_size`=5,
  `src/workflow/analysis.py:15-54`) produces the `bkp_*` outputs used for heatmaps.
  It does not feed Figures 2–5.

---

## Findings — where code and the previous draft disagreed

Each was verified by execution or by a call-graph trace, not by reading alone.

**F1. Farmers and paddy farmers apply mortality twice per step; foragers once.**
`SiteGroup.step` calls `self.loss()` (`people.py:222`) and `Farmer.step` calls it
again (`farmer.py:142`). Verified: two invocations per `Farmer.step`. Two independent
Bernoulli draws at `loss.prob`, so the realised per-step survival differs from the
single draw both documents described. `RiceFarmer` inherits this. **[ASK] intended?**

**F2. Five conversion paths exist, not six.** `Hunter`→`Farmer`, `Hunter`→`RiceFarmer`,
`Farmer`→`Hunter`, `Farmer`→`RiceFarmer`, `RiceFarmer`→`Farmer`. There is no
paddy→forager path (`rice_farmer.py:16-20`). The config carries exactly five switches
(`config.yaml:17-21`). The old draft said "six" while tabulating five.

**F3. Paddy immigrants are placed on rainfed-arable cells, not paddy-arable cells.**
`add_farmers` reads the `is_arable` raster regardless of breed (`env.py:456`), whereas
`add_initial_farmers` correctly branches on breed (`env.py:414-417`). Since
paddy-arable ⊂ rainfed-arable (885 of 2 620 cells), most immigrant paddy groups land
on cells where `able_to_live` would have refused them. **[ASK] intended?**

**F4. Immigration is not seed-reproducible.** `np.random.poisson` (`env.py:454`) draws
from the global NumPy stream rather than the model's seeded generator. Every other
draw is seeded. The previous draft's claim that "a run reproduces given its parameters
and seed" is therefore too strong.

**F5. The four loss scenarios are inert.** `config/scenario/*.yaml` carry no
`# @package _global_` directive, so Hydra merges them under `cfg.scenario.*` and they
never reach `cfg.Hunter.loss`. Verified: all four scenario selections compose to
identical loss parameters. The comment at `config.yaml:4-6` states the opposite
intent. **[ASK] were any results reported from this arm?**

**F6. Group merging is dead code; splitting does not strictly conserve population.**
`Hunter.merge` (`hunter.py:55-67`) is never called anywhere in `src/` or `tests/`. In
`diffuse`, the parent's `self.size -= size` passes through the size setter
(`people.py:36-43`), which kills the parent outright if the remainder falls below
`min_size`, destroying that remainder. Both documents claimed exact conservation under
splitting and merging.

**F7. No cell is ever water at runtime.** `is_water` tests `water_type == -1`
(`env.py:59`), but the water raster only ever supplies 0 (land, 5 771 cells) and 1
(near-water land, 1 064 cells); its nodata value is 65535, which marks sea and
out-of-frame cells that ABSESpy drops from the grid entirely. Measured: `is_water` is
False for all 6 835 cells. So the sea class described in both documents is never
instantiated, the "not water" clause in both arability predicates is always satisfied,
and the ceiling denominator "non-water cells" is simply all cells. Only the
near-water distinction is live, and it acts solely through `Hunter.max_size_water`.

**F8. `lim_h` units are ambiguous.** The code multiplies `lim_h` by a cell **count**
(`env.py:316`), so 35 is people per cell; a cell is ≈ 78 km², giving ≈ 45 people per
100 km². The config comment sources the value from Binford 2001 as 31.93 people per
**100 km²**. The two readings differ by a factor of about 2.2. **[ASK] which is meant?**

**F9. Foragers start near the ceiling.** Initialisation places 3 417 forager groups
totalling ≈ 180 848 people against a ceiling of 239 225: the region begins at ~76%
of forager carrying capacity. Neither document stated this, and it is central to why
farming is suppressed.

**F10. ABSESpy version was wrong.** Both documents said 0.8.5; the project requires
`abses>=0.11.0` (`pyproject.toml:17`) and runs 0.11.5.

**F11. The terrain experiment is a 2×2 factorial, not a binary contrast.** Four arms —
real terrain, homogenised slope, homogenised DEM, fully homogenised — keyed on
(`ds.dem`, `ds.slope`) pairs (`src/workflow/figures.py:56-61`,
`reports/secondary_indicators_validation.ipynb`). Homogenised surfaces are the
constant rasters `data/ohn_value1.tif` (DEM) and `data/ohn_value0.tif` (slope). Both
documents described it as "real versus homogenised".

**F12. End state is the last 51 steps, not 50.** `_tail_mean` selects
`step >= max_step - last` with `last = 50` (`src/workflow/figures.py:260-278`),
an inclusive bound. Immaterial to results; stated precisely in the revision.

**F13. A silent fallback can disable the ceiling.** `calculate_global_hunter_limit`
wraps its body in a bare `except Exception` and falls back to 100 000
(`env.py:320-322`), which is below the true ceiling of 239 225 and would silently
change the model's behaviour rather than fail. Not triggered in the runs checked.
