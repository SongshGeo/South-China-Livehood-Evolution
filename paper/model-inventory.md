# Model inventory — reconnaissance ledger

Factual record of what the code does, recovered before the prose was written or
revised. Every entry carries a `file:line`. Entries marked **[ASK]** are things the
code does not settle; they are questions for the author, not values to invent.

Scope: the model proper is `src/api/` (agents and environment) plus
`src/core/model.py` (the step loop). `src/app.py` is a synthetic-landscape demo, not
the published model, and is excluded. `src/workflow/` is post-hoc analysis.

Recovered against commit on `dev` at the time of writing; ABSESpy 0.11.5, Python 3.11.

---

## ⚠️ Pending re-run

The stored runs under `out/` — and therefore Figures 2–5 — were produced **before**
the fixes now landing on `dev`. Two consequences, both to be cleared by one re-run:

1. **No stored run is exactly reproducible.** They were generated with no base seed at
   all (F14), so they reproduce in distribution only. `methods.md` and
   `si_odd_protocol.md` say so explicitly; delete those sentences once the sweeps are
   re-run under the seeded code.
2. **The stored numbers are stale.** Fixes that change model behaviour have landed
   since they were generated, so the figures must be rebuilt:
   - **F1 / #28** — farming breeds drew mortality twice per step; now once. This
     halves the expected per-step mortality of both farming breeds. Arithmetic only:
     the expected per-step survival multiplier moves from 0.999 to 0.9995, which
     compounds to ≈1.28× over 500 steps. The realised effect has not been measured
     and the direction is not asserted here — the re-run is the measurement.
   - **F3 / #29** — immigrant paddy groups were placed on the rainfed-arable mask;
     now on the paddy-arable mask. Before the fix 31% of paddy groups sat on cells
     that fail the paddy slope test and were never evicted, so Figure 5's
     `env.lam_ricefarmer` sweep carried their contribution inside the measured paddy
     effect. Every figure that involves paddy agents is affected, Figure 5 most
     directly.

Until the sweeps are re-run, `methods.md` and `si_odd_protocol.md` describe the
**current code**, which is not the code that produced the current figures.

**How to clear this block.** `run_slurm_rerun.sh` dispatches all six sweeps as one
216-task SLURM array into the stable root `out/south_china_evolution/rerun_v2/`
(`sbatch run_slurm_rerun.sh`; it skips combinations that already have all five
`*_tracking.csv`). Two sweeps are deliberately run to their full design rather than
to what the old directories happen to contain: the broad conversion grid becomes 6×6
(was 25 of 36) and the immigration sweep 5×5 (was 23 of 25). Afterwards:

| `reports/manuscript_figures.ipynb` constant | repoint to `rerun_v2/` |
|---|---|
| `BASELINE_DIR` | `convert3/22_Farmer.convert_prob.to_hunter=0.1,Hunter.convert_prob.to_farmer=0.05,Hunter.convert_prob.to_rice=0.05` |
| `OFF_DIR` | `convert3/0_Farmer.convert_prob.to_hunter=0.0,Hunter.convert_prob.to_farmer=0.0,Hunter.convert_prob.to_rice=0.0` |
| `LAM_ROOT` | `lam` |
| `LIMH_ROOT` | `limh` |
| `TERRAIN_ROOT` | `terrain` |
| `BROAD_GRID` / `FINE_GRID` | `grid_broad` / `grid_fine` |

Then delete this block, the seed and correction caveats in `methods.md` §Software and
`si_odd_protocol.md` §III.i, and the paragraph about Figures 2–5 in that file's
preamble. All replicate seeds derive from `seed` = 42, and every array task sees
`job_id` = 0, so the sweep uses common random numbers — combinations are paired,
which is what a sweep wants, but grid-wide intervals are not independent across cells.

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
| **What one step means in real time** | **Nothing — deliberately.** No calendar, no time driver, no unit anywhere in config or code; confirmed by the author as an abstract generation-scale interval (#36) | — |

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
   - `Farmer` and `RiceFarmer` inherit `SiteGroup.step` unchanged. `Farmer` used to
     override it to call `loss` a second time (finding F1, now fixed).
3. `nature.apply_global_hunter_limit()` (`env.py:324-358`) — regional forager ceiling.
4. `datacollector.collect(self)` — recording happens **after** all updates.

## 4. Parameters

Baseline values are those Hydra actually composes (verified by composition, not by
reading), `config/config.yaml` unless noted. Swept ranges come from
`run_slurm.sh:67-68` and `reports/*.ipynb`.

| Parameter | Default | Swept | Source of value |
|---|---|---|---|
| `env.lim_h` | 35 per cell | {15, 25, 35} | **[exp]** people per cell, confirmed by the author; Binford 2001's 31.93 per 100 km² is an order-of-magnitude reference only, see F8 |
| `env.init_hunters` | 0.5 | — | — |
| `env.init_farmers` / `init_rice_farmers` | 0 / 0 | — | — |
| `env.lam_farmer` / `lam_ricefarmer` | 3 / 0.1 | 2–10 / 0.1–0.5 | — |
| `env.tick_farmer` / `tick_ricefarmer` | 0 / 0 | — | — |
| `Farmer.growth_rate` | 0.005 | — | **[exp]** per step; the contradictory "0.1~0.25" comment is removed (#37) |
| `RiceFarmer.growth_rate` | 0.006 | — | **[exp]** per step, as above |
| `Hunter.growth_rate` | 0.001 | — | **[exp]** no source; marked as such in the config |
| `min_size` (all breeds) | 6 | — | Binford 2001; Kelly 2013 |
| `Farmer.area` / `RiceFarmer.area` | 2 km | — | Shelach 1999; Wu et al. 2023 |
| `Farmer.capital_area` | 0.004 km²/person | — | Qiao 2010, halved for South China productivity |
| `RiceFarmer.capital_area` | **0.002** km²/person | — | **[exp]** half of `Farmer`'s, on the reasoning that paddy yields more per unit area; the factor of 2 itself is unsourced (#37) |
| `Farmer.init_size` / `RiceFarmer` / `Hunter` | [60,100] / [300,400] / [0,100] | — | farmer values unused at baseline (`init_farmers`=0) |
| `new_group_size` F / R / H | [30,60] / [200,300] / [6,50] | — | — |
| `diffuse_prob` (F, R) | 0.05 | — | **[exp]** no source; marked as such in the config |
| `complexity` (F, R) | 0.1 | — | **[exp]** no source; marked as such in the config |
| `Farmer.convert_prob.to_hunter` (f2h) | 0.1 | 0–0.02 step 0.002 (fine); 0–0.1 (coarse) | — |
| `Hunter.convert_prob.to_farmer` (h2f) | 0.05 | 0–0.15 step 0.015 (fine) | — |
| `Farmer.convert_prob.to_rice` | 0.05 | — | — |
| `Hunter.convert_prob.to_rice` | 0.05 | — | — |
| `RiceFarmer.convert_prob.to_farmer` | 1.0 | — | — |
| `convert_threshold.to_hunter` / `.to_rice` / `.to_farmer` | 100 / 200 / 200 | — | — |
| `Hunter.max_size` / `max_size_water` | 100 / 500 | — | Kelly 2013:171 for sedentism |
| `Hunter.is_complex` | 100 | — | Kelly 2013:171 |
| `max_travel_distance` | 5 cells | — | **[exp]** no source; marked as such in the config |
| `Hunter.loss` prob/rate | 0.05 / 0.01 | — (a nominal 4-scenario arm existed but was inert; removed, F5) | — |
| `Farmer.loss`, `RiceFarmer.loss` prob/rate | 0.01 / 0.05 | as above | — |
| `convert.enabled` + 5 path switches | all true | on/off contrast | — |

Derived: `Farmer.max_size` = π·`area`²/`capital_area` = π·4/0.004 ≈ **3 142**;
`RiceFarmer.max_size` = π·4/0.002 ≈ **6 283** (`farmer.py:80-84`).
Global forager ceiling = 35 × 6 835 = **239 225** (measured).

## 5. Stochasticity

| Source | Call | RNG |
|---|---|---|
| Immigrant counts (Poisson) | `env.py:457` | model RNG (`model.rng`) — was global NumPy until F4/F14 were fixed |
| Immigrant cell choice | `env.py:468-472` | model RNG |
| Immigrant size | `env.py:475-476` | model RNG |
| Initial forager placement | `env.py:394` | model RNG |
| Initial group size | `people.py:78` | model RNG |
| Activation order each step | `model.py:209` `shuffle_do` | model RNG |
| Conversion Bernoulli trials | `hunter.py:122,151`; `farmer.py:90,99`; `rice_farmer.py:19` | model RNG |
| Colonisation trial and colony size | `farmer.py:123`; `people.py:111` | model RNG |
| Colonisation / movement target cell | `people.py:182,208` | model RNG |
| Mortality Bernoulli | `people.py:159`; `farmer.py:137` | model RNG |
| Forager trimming order at the ceiling | `env.py:360` `shuffle_do` | model RNG |
| Cell `slope`/`elevation` constructor defaults | `env.py:31-34` | constants (0.0) — overwritten by rasters |

Deterministic: population growth (`people.py:85`), intensification
(`farmer.py:128-133`), the ceiling amount itself.

## 6. Existing evidence

- Unit tests: 134 passing, covering agents, environment, conversion thresholds, seed
  reproducibility, and the figure builders (`tests/`, `make test`).
- No global sensitivity analysis (no Sobol/Morris) — the sweeps are one- and
  two-factor grids. This is the abm profile's standing objection #6.
- No independent validation dataset; evaluation is pattern-oriented by design.
- Breakpoint detection (`ruptures`, `Dynp`, `n_bkps`=1, `min_size`=5,
  `src/workflow/analysis.py:15-54`) produces the `bkp_*` outputs used for heatmaps.
  It does not feed Figures 2–5.

---

## Findings — where code and the previous draft disagreed

Each was verified by execution or by a call-graph trace, not by reading alone.

**F1. Farmers and paddy farmers applied mortality twice per step — FIXED.**
`SiteGroup.step` called `self.loss()` (`people.py:222`) and `Farmer.step` called it
again (`farmer.py:142`), giving two independent Bernoulli draws at `loss.prob` per
tick for both farming breeds while foragers got one.

Git history settles the "[ASK] intended?" that stood here: `e66a0ec` added
`Farmer.step` → `super().step(); self.loss()` at a time when `SiteGroup.step`
contained **no** `loss()` call, so farmers correctly lost once. The later refactor
`beedcf5` ("streamline population management") added `self.loss()` to
`SiteGroup.step` to give foragers a mortality mechanism, without removing the
farmer-side call. A leftover, not a modelling choice.

Fixed by deleting the `Farmer.step` override entirely (it then held nothing but
`super().step()`); `RiceFarmer`, which inherited it, is fixed with it.
`tests/test_people.py::TestStepSchedule` locks all four breeds to one draw per step.
**This changed model behaviour: the stored runs and Figures 2–5 predate the fix and
must be regenerated — see "Pending re-run" at the top.**

**F2. Five conversion paths exist, not six.** `Hunter`→`Farmer`, `Hunter`→`RiceFarmer`,
`Farmer`→`Hunter`, `Farmer`→`RiceFarmer`, `RiceFarmer`→`Farmer`. There is no
paddy→forager path (`rice_farmer.py:16-20`). The config carries exactly five switches
(`config.yaml:17-21`). The old draft said "six" while tabulating five.

**F3. Paddy immigrants were placed on rainfed-arable cells — FIXED.**
`add_farmers` read the `is_arable` raster regardless of breed, whereas
`add_initial_farmers` correctly branched on breed. Since paddy-arable ⊂ rainfed-arable
(885 of 2 620 cells), most immigrant paddy groups landed on cells where
`able_to_live` would have refused them.

Measured over 10 seeded replicates (baseline config, seeds 1–10, 30 steps each, now
reproducible since F14): **22 of 71 surviving paddy groups (31.0%)** sat on cells
failing the paddy slope test. As a share of paddy population per replicate the mean is
**31.1%** (median 34.2%), but the spread is wide — 0.0% to 52.8% — so no single number
characterises it; one replicate in ten had no misplaced group at all.

Misplacement is not transient. A paddy group only converts back to `Farmer` below
`convert_threshold.to_farmer` = 200, while immigrants arrive at `new_group_size`
200–300 and then grow, so most never cross back. `able_to_live` is consulted only when
searching for a cell (`people.py:184,210`), never as a recurring survival check, so a
misplaced group is never evicted either.

**Fixed** by giving both placement paths one breed-aware helper,
`Env._vacant_arable_cells`, so an immigrant can only be seeded where `able_to_live`
would admit it. Re-measured after the fix over 5 seeded replicates: **0 of 31**
paddy groups on non-paddy-arable cells, against 22 of 71 before.
`tests/test_env.py::TestImmigrantPlacement` locks it; reverting the branch fails the
three paddy cases while the rainfed case passes as a control.

**This changed model behaviour.** Figure 5's `env.lam_ricefarmer` sweep previously
mixed the paddy mechanism with a contribution from paddy groups living where paddy
cannot be grown; it must be re-run. See "Pending re-run" at the top.

**F4. Immigration was not seed-reproducible — FIXED.** `np.random.poisson` (then at
`env.py:454`) drew from the global NumPy stream rather than the model's seeded
generator. Now `self.model.rng.poisson` at `env.py:457`. Note that F4 alone never explained the
irreproducibility: see F14, which showed that no seed was ever set in the first
place. Both were fixed together; `tests/test_reproducibility.py` locks the behaviour.

**F14. No seed was ever set for any run — FIXED.** `src/__main__.py` constructed
`MyExperiment(Model, cfg=cfg, nature_class=Env)` without a `seed`, so ABSESpy's
`Experiment._base_seed` stayed `None` and `_get_seed()` returned `None` for every
replicate, leaving mesa to seed from OS entropy. Measured before the fix:

```
Experiment._base_seed = None
_get_seed(1..5) = [None, None, None, None, None]
```

So *nothing* was seeded, not merely the Poisson draw of F4. Both `methods.md` and
`si_odd_protocol.md` claimed "replicate draws are seeded except for the Poisson
immigration counts", which was false in the more permissive direction. Fixed by
adding a top-level `seed` to `config/config.yaml` and passing it through as
`Experiment`'s named `seed` argument; both documents were corrected in the same
commit. This finding came out of the issue audit and never had its own issue number
in the original F1–F13 sweep.

**F5. The four loss scenarios were inert — ARM REMOVED.** `config/scenario/*.yaml`
carried no `# @package _global_` directive, so Hydra merged them under
`cfg.scenario.*` and they never reached `cfg.Hunter.loss`. Verified: all four
scenario selections composed to identical loss parameters, namely the inline values
in `config.yaml`. The comment in the `defaults` list stated the opposite intent.

The "[ASK] were any results reported from this arm?" is answered: **no.** Of 383 run
directories under `out/`, only 8 carry a `scenario=` override, all under
`out/south_china_evolution/2026-03-22/`. `reports/manuscript_figures.ipynb` reads
2026-04-14 (baseline and conversion-off), 2026-01-18 (`lam`), 2026-03-10 (`lim_h`),
2026-03-09 (terrain) and the `grid_*` sweeps — none of them touch 2026-03-22. So the
four nominally distinct runs really were parameter-identical, but nothing in the
manuscript rests on them.

The author chose to drop the arm rather than repair it. `config/scenario/` and the
`defaults` entry are deleted; the loss parameters now come solely from the inline
blocks in `config.yaml`, whose values are unchanged, so every published run's
parameters are unaffected. `tests/test_config.py` pins the composed baseline loss
values and asserts no `scenario` key survives composition. Note the scope of that
second check: it is name-specific, so it would not catch an inert group introduced
under a different name — the values assertion is the general guard. The 8 orphaned
run directories are left in place; they feed nothing.

**F6a. Group merging was dead code — REMOVED.** `Hunter.merge` (`hunter.py:55-67`)
was never called anywhere in `src/` or `tests/`. It could not have fired even if it
had been called from the movement logic: `max_agents = 1` and `able_to_live` refuses
an occupied cell, so two foragers never share a cell and no occasion to merge arises.
Deleted, along with `SiteGroup.loss_in_competition` (`people.py:224-227`), the other
call-less remnant of the removed competition mechanism. The SI no longer describes a
merging routine at all; it states that groups do not merge and why.

**F6b. Splitting does not strictly conserve population — see #32.** In `diffuse`,
the parent's `self.size -= size` passes through the size setter (`people.py:36-43`),
which kills the parent outright if the remainder falls below `min_size`, destroying
that remainder. Bounds derivable from the code alone: at most `min_size − 1` = 5
people per event, and only for farming breeds — a forager only splits at `max_size`
(100, or 500 near water) and its colony is at most `new_group_size` = 50, so its
remainder is always ≥ 50 and it can never trigger the leak. The docstring claiming
conservation is the defect, not the arithmetic.

**F7. Water is modelled as a land property, not as terrain (confirmed by author, not
a defect).** `is_water` tests `water_type == -1`, which the input never supplies: the
sea is the water layer's nodata value and is masked out with the rest of the frame,
so all 6835 modelled cells are land. Water's effect enters through carrying capacity
instead, via the 1064 near-water cells (`water_type` = 1) that raise
`Hunter.max_size` from 100 to `Hunter.max_size_water` = 500. Consequences to state in
the write-up: the "not water" clause of both arability predicates is always satisfied,
and the ceiling denominator is the full 6835 cells.

**F8. `lim_h` units are ambiguous.** The code multiplies `lim_h` by a cell **count**
(`env.py:316`), so 35 is people per cell; a cell is ≈ 78 km², giving ≈ 45 people per
100 km². The config comment sources the value from Binford 2001 as 31.93 people per
**100 km²**. The two readings differ by a factor of about 2.2.

**Answered by the author: people per cell is what is meant.** 35 is an expert
judgement at the right order of magnitude, not a conversion of Binford's density, and
no area conversion is intended. The code is unchanged; `config.yaml` now states the
unit explicitly and labels the literature figures as an order-of-magnitude reference,
and Table S1 already carried "people per cell". The stale `31.93` default in
`calculate_global_hunter_limit` — the areal density used as a per-cell fallback, which
is where the confusion came from — is gone with F13.

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

**F13. A silent fallback could have disabled the ceiling — FIXED.**
`calculate_global_hunter_limit` wrapped its body in a bare `except Exception` and
fell back to 100 000 (`env.py:320-322`). The comment called that "a large default
that will not constrain", but the true ceiling is 239 225, so the fallback was less
than half of it — it would have tightened the forager ceiling, not lifted it, and
silently. Worse, `lim_h` = 15 is a swept value in Figure 4 and 15 × 6835 = 102 525
sits within 3% of the magic number, so a triggered fallback would have been nearly
invisible in the results.

Never triggered in any run checked (measured `global_hunter_limit` = 239 225 = 35 ×
6835 throughout). Fixed by removing the `try`/`except` so an initialisation-time
configuration or data fault fails loudly. `lim_h` is now required rather than
defaulted: its old default, 31.93, was the **areal density** from Binford 2001 being
used as a **per-cell** value, which is exactly the unit confusion of F8.
`tests/test_env.py::TestGlobalHunterLimit` covers both the value and the raise.

---

## Tracked issues

Findings that need a decision or a code change are filed on GitHub. F2, F9–F12 were
documentation defects and are already fixed in `methods.md` / `si_odd_protocol.md`;
F7 is confirmed intended behaviour and needs no change.

| Finding | Issue | Title | Status |
|---|---|---|---|
| F1 | [#28](https://github.com/SongshGeo/South-China-Livehood-Evolution/issues/28) | Farmer/RiceFarmer 每步执行两次 `loss()` | **fixed** — changed model behaviour; needs re-run |
| F3 | [#29](https://github.com/SongshGeo/South-China-Livehood-Evolution/issues/29) | 水稻移民用 `is_arable` 掩膜放置 | **fixed** — changed model behaviour; needs re-run |
| F4 | [#30](https://github.com/SongshGeo/South-China-Livehood-Evolution/issues/30) | 移民 Poisson 抽样走全局 NumPy RNG | **fixed** |
| F14 | [#38](https://github.com/SongshGeo/South-China-Livehood-Evolution/issues/38) | 项目从未设过随机种子 | **fixed** |
| F5 | [#31](https://github.com/SongshGeo/South-China-Livehood-Evolution/issues/31) | `config/scenario/*.yaml` 全部失效 | **fixed** — arm removed; no published result used it |
| F6b | [#32](https://github.com/SongshGeo/South-China-Livehood-Evolution/issues/32) | `diffuse()` 分裂时母体残余人口丢失 | **closed, code unchanged** — ≤ `min_size − 1` per event, farming breeds only; docstring corrected and behaviour pinned by tests |
| F6a | [#33](https://github.com/SongshGeo/South-China-Livehood-Evolution/issues/33) | `Hunter.merge()` 是死代码 | **fixed** — removed |
| F13 | [#34](https://github.com/SongshGeo/South-China-Livehood-Evolution/issues/34) | `calculate_global_hunter_limit()` 的裸 except | **fixed** |
| F8 | [#35](https://github.com/SongshGeo/South-China-Livehood-Evolution/issues/35) | `env.lim_h` 单位歧义 | **closed, code unchanged** — people per cell, confirmed; unit stated in config |
| §2 [ASK] | [#36](https://github.com/SongshGeo/South-China-Livehood-Evolution/issues/36) | 一个时间步对应多少现实时间 | **closed, code unchanged** — abstract by design; misleading comments removed |
| §4 [ASK] | [#37](https://github.com/SongshGeo/South-China-Livehood-Evolution/issues/37) | 参数出处缺失；`growth_rate` 注释矛盾 | **closed** — every behavioural parameter tagged [lit]/[exp] in the config, with a legend; contradictory comments removed |
