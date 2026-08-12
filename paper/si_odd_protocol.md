---
title: "Supplementary Information — Model description (ODD+D)"
acronym: "SCE"
date: "2026-08-12"
csl: "nature"
# TODO before first export: authors, affiliations, and a mybib.bib for the
# literature cited in the parameter provenance (Table S4).
---

```{=latex}
%% Supplementary numbering: prefix figures and tables with "S".
\renewcommand{\thefigure}{S\arabic{figure}}
\renewcommand{\thetable}{S\arabic{table}}
```

This description follows the ODD+D protocol (Overview, Design concepts, Details,
and human Decision-making; Müller et al. 2013), an extension of ODD for
agent-based models that make behavioural decisions. It is written for
replication, so it names the implementation parameters directly, in
monospace; the main-text Methods gives the same quantities as mathematical
symbols, and Table \ref{tbl:symbol-map} maps one onto the other. Baseline values,
tested ranges, and their provenance are collected in Table \ref{tbl:parameters}.
The model produces main-text Figures 2–5.

Where the implemented behaviour differs from what a reader would naturally assume,
this description reports the implemented behaviour, so that the description matches
the code that can be run. Those places are marked and collected in section IV.
Figures 2–5 were generated before the mortality submodel was corrected to one draw
per step; they are being regenerated, and this description follows the corrected
code rather than the version that produced them.

---

## I. Overview

### I.i Purpose and patterns

The model represents the entry and spread of agriculture into prehistoric South
China, a region already occupied by hunter-gatherers. Its purpose is to explain a
qualitative pattern: agriculture arrived from the north yet remained suppressed
for a long period rather than expanding quickly. It is a heuristic, process-based
model used to identify which mechanism holds farming down and to rank the
candidate mechanisms by effect size. No parameter is fitted to an observed time
series. Evaluation is pattern-oriented: the target patterns are (i) a low and
slowly rising agricultural share of the total population under baseline
conditions, and (ii) the ordering of mechanisms by how strongly each releases or
suppresses farming. Both patterns were fixed as the evaluation criteria before the
sweeps were run.

### I.ii Entities, state variables, and scales

The model contains two entity types: spatial cells and settlement groups.

**Cells** form a raster grid of South China. Each cell stores an elevation
(`elevation`), a slope (`slope`), and a water class (`water_type`). It derives
binary land-use predicates. A cell is rainfed-arable (`is_arable`) when `slope` ≤
10°, 0 < `elevation` < 200 m, and it is not open water. A cell is paddy-arable
(`is_rice_arable`) when `slope` ≤ 0.5° under the same elevation and water
conditions; paddy-arable cells are therefore a subset of rainfed-arable cells. A
cell is near-water (`is_near_water`) when `water_type` = 1, which raises the
forager capacity it can support. Each cell holds at most one group
(`max_agents` = 1).

**Settlement groups** are the agents; individuals are not represented. Three
breeds inherit one group class: rainfed farmers (`Farmer`), paddy farmers
(`RiceFarmer`), and hunter-gatherers (`Hunter`). Every group has a size (`size`,
= $N$), a minimum viable size (`min_size` = 6), and a carrying capacity
(`max_size`). Farmers additionally hold a cultivated area (`area`) and a mutable
growth rate (`growth_rate`); foragers hold a sedentism flag, set when `size`
exceeds the threshold `Hunter.is_complex` = 100. A group whose `size` drops below
`min_size` is removed.

**Scales.** Space is the fixed extent of the input raster: 104.4–121.3° E,
19.2–29.1° N at 5 arc-minute resolution (EPSG:4326). After nodata masking this
gives **6835 modelled cells**, each covering about **78 km²** (75 km² at the
northern edge, 81 km² at the southern). Of these, 2620 are rainfed-arable, 885 are
paddy-arable, and 1064 are near-water. Time advances in discrete steps and each run
lasts `time.end` = 500 steps. **The model defines no mapping from a step to
calendar time**: there is no time driver and no unit in the configuration, so all
results are reported in step number and interpreted as an abstract
generation-scale interval. There is no exogenous temporal input.

### I.iii Process overview and scheduling

One step (`Model.step`) executes the following ordered sequence.

1. **Immigration** (`Env.step`). Two independent inflows of farming groups are
   added. The count of new rainfed groups is drawn as
   `Poisson(env.lam_farmer)` and of paddy groups as
   `Poisson(env.lam_ricefarmer)`, provided the current tick is at least
   `tick_farmer` / `tick_ricefarmer` (both 0 by default). Each new group is placed
   on a uniformly random empty **rainfed-arable** cell — for both breeds — and
   given a size drawn from `new_group_size`.
2. **Group updates** (`agents.shuffle_do("step")`). All existing groups act once
   in a freshly randomised order. Each group, in its turn, performs the following
   sub-sequence:
   - (a) **Growth** (`population_growth`): `size` ← `size` × (1 + `growth_rate`).
   - (b) **Conversion** (`convert`): a two-stage attempt to change breed (below).
   - (c) **Colonization** (`diffuse`): a farming group attempts to split off a
     colony with probability `diffuse_prob`; a forager group attempts to split
     only when it is at `max_size`.
   - (d) **Mortality** (`loss`): a Bernoulli loss event, executed once per tick by
     every breed.
   - (e) **Movement** (`move_one`, `Hunter` only): a mobile forager steps to a
     random suitable empty cell within `max_travel_distance`.
3. **Regional forager ceiling** (`apply_global_hunter_limit`). If the summed
   forager population exceeds the ceiling `global_hunter_limit`, forager groups
   are trimmed in random order until it no longer does.
4. **Observation** (`datacollector.collect`). For each breed the summed `size`
   and the group count are recorded, after all updates for the step have completed.

Updates are asynchronous within a step: a group acts on the state left by groups
that acted earlier in the same step.

---

## II. Design concepts

### II.i Basic principles

The model instantiates the frontier view of the Neolithic transition, in which
farming spreads into occupied land by demic diffusion and by local adoption at the
contact zone, rather than into empty space. Two principles carry the design. First,
livelihoods compete for a shared, finite landscape: because a cell holds at most one
group, a standing forager population is not merely a demographic background but an
occupier of the very cells farming needs. Second, the boundary between livelihoods
is permeable in both directions, so the frontier can retreat as well as advance. The
model addresses these principles at the level of the settlement group, which is the
scale at which archaeological sites are observed, and it deliberately omits the
individual and the household. The central hypothesis under test is that the
two-directional conversion rate between livelihoods, rather than environmental
suitability, governs how fast agriculture takes hold.

### II.ii Theoretical and empirical background

The arability thresholds, the per-cell forager carrying capacity, the per-group
farming capacity, and the spacing of settlements are parameterised from published
archaeological and ethnographic estimates for the region and period: forager
densities from Binford (2001) and Tallavaara et al. (2017), minimum viable group
size from Binford (2001) and Kelly (2013), the sedentism threshold from Kelly
(2013: 171), per-person cultivated area from Qiao (2010) adjusted for South China
productivity, and settlement spacing from Wu et al. (2023) and Shelach (1999).
Several behavioural parameters carry no empirical source and are stated as expert
judgement: the colonisation probability `diffuse_prob`, the intensification factor
`complexity`, the travel range `max_travel_distance`, and all growth rates. They are
identified as such in Table S1 rather than given an implied provenance.

### II.iii Individual decision-making

Groups do not maximise an explicit objective; behaviour is governed by
condition-and-probability rules, and persistence is emergent. Every behavioural
decision is a two-stage test: a set of deterministic conditions must hold, and
then a random Bernoulli draw at the relevant probability must succeed; the
randomness is a stand-in for the many local circumstances the model does not
represent, and each of its sources is enumerated with a reason in II.x below.
This applies to
conversion (`convert_prob`, gated by size thresholds, land suitability, and
neighbour presence), colonization (`diffuse_prob`, gated by having enough people
for a colony and an empty suitable cell), and movement (gated by the sedentism
threshold). The rule is heuristic rather than optimising or satisficing: no
alternative is evaluated and no utility is compared. The decision horizon is one
step; decisions are made at the scale of the group and its immediate neighbourhood
and are re-evaluated every step. Immigrant placement is a model-level draw over
eligible cells, not a decision by the immigrating group. Social norms, institutions,
preferences, and explicit representations of uncertainty are not modelled.

### II.iv Learning

Not implemented. No rule or parameter is updated from past experience, and no group
carries a memory of previous steps. The only adaptive feedback is density-dependent
intensification of farming groups (see Submodels), which is a fixed functional
response to current size rather than a learned strategy.

### II.v Individual sensing

A group senses its own cell (its arable predicates and water class) and the
contents of its immediate neighbourhood. Forager-to-farmer conversion senses a
`Farmer` neighbour; forager-to-paddy conversion senses a `RiceFarmer` neighbour.
Colonising and moving groups sense which nearby cells are suitable and empty, out to
`max_travel_distance`. Sensing is local and error-free, which is an assumption: no
group has regional information, and no group is ever mistaken about a cell.

### II.vi Prediction

Not implemented. No decision uses an estimate of a future state, and no group holds
even a tacit internal model of how conditions will change. All rules act on present
conditions only.

### II.vii Interaction

Interaction is indirect and spatial. Because `max_agents` = 1, groups compete for
space by occupancy: a colonising or moving group can settle only on an empty
suitable cell, so a cell held by a forager is unavailable to a farmer and the
reverse. Conversion is a contact interaction, since a forager adopts farming only
next to an existing farming group. There is no direct conflict, predation, trade, or
resource transfer between groups; an earlier competition mechanism was removed from
the model. A group-merging routine exists in the code but is never invoked, so no
merging occurs.

### II.viii Collectives

The settlement group is itself the collective unit, and it is imposed rather than
emergent: individuals are not represented, so a group never forms or dissolves by
aggregation of members. Groups do form and disappear through colonisation, conversion
and death, but there are no higher-order collectives such as tribes, alliances, or
regional polities, and no group-level property is inherited from a parent group other
than population and its `source` label.

### II.ix Heterogeneity

Cells are heterogeneous in `elevation`, `slope`, and `water_type`, and therefore
in their arable predicates. Groups are heterogeneous **in state values, not in
decision rules**: every group of a given breed runs the identical rule set, and
differs only in `size`, position, and — for farmers — `area` and current
`growth_rate`. Heterogeneity between breeds is structural: the two farming breeds
load onto the landscape differently, since rainfed groups arrive frequently and
small (`new_group_size` 30–60) and use a wide range of cells, whereas paddy groups
arrive rarely and large (`new_group_size` 200–300) and can persist only on the
scarce near-flat cells.

### II.x Stochasticity

The model is stochastic throughout. Table \ref{tbl:stochasticity} lists every random
source with the reason it is random rather than fixed; the ones authors most often
omit — initial placement, activation order, and the order in which groups absorb the
ceiling adjustment — are among them.

```xlsx-table
file: SCE_Tables.xlsx
sheet: Table S1
caption: Every source of randomness in the model, with the reason each is random rather than fixed.
label: tbl:stochasticity
skip_n: 1
```

Growth, intensification, and the size of the ceiling adjustment are deterministic.
Because of these sources, every parameter combination is run in replicate
(`exp.repeats` = 5) and reported as a distribution across replicates.

### II.xi Observation

At each step the model records, for each breed, the summed `size` and the number
of groups, together with their shares of the totals. From these emergent series we
compute the agricultural share of total population and the end-state summaries. The
end state of a run is the mean over steps ≥ `time.end` − 50 (the final 51 recorded
steps); the end state of a parameter combination is the mean of those values across
the five replicates. The quantities of interest — the suppressed agricultural share,
the conversion response surface, and the leverage of each immigration stream — are
emergent properties. What is imposed rather than emergent is stated explicitly: the
regional forager ceiling, the per-group capacities, the arability thresholds, and the
immigration rates are parameters, not outcomes.

---

## III. Details

### III.i Implementation details

The model is implemented in Python 3.11 on the ABSESpy agent-based modelling
framework (0.11). A hierarchical Hydra configuration (`config/`) stores the
baseline parameters and defines the sweeps, so model structure and parameters are
separated and a sweep changes configuration only. Each combination runs as an
independent batch of `exp.repeats` = 5 replicates. A base seed in the configuration
(`seed`) fixes the whole batch: each replicate derives a distinct seed from it
(`base + 1000 × job_id + run_id`, where `job_id` is the combination's position in the
sweep), and every random draw — including the Poisson immigration counts — uses the
resulting seeded generators. A replicate therefore reproduces **exactly** given its
configuration, sweep position, and repeat index. The runs reported here predate the
introduction of the base seed and so reproduce in distribution rather than exactly.
Each replicate writes a full time series (`<run>_tracking.csv`) of
summed `size` and group count per breed, which is the sole input to the analysis.
Code and configuration are version-controlled; sweeps are dispatched as SLURM job
arrays (`run_slurm.sh`).

### III.ii Initialisation

At the start of a run, a fraction `env.init_hunters` = 0.5 of the land cells is
seeded with a `Hunter` group, each with a `size` drawn uniformly between
`min_size` = 6 and 100. In the baseline landscape this places **3417 forager groups
holding about 180 800 people, roughly 76% of the regional ceiling**, so the region
begins close to forager saturation. No farming groups are present initially
(`env.init_farmers` = 0, `env.init_rice_farmers` = 0), and consequently the
`init_size` ranges for the two farming breeds are unused at baseline. Agriculture
appears only through immigration, so any farming population observed in a run is
generated by the model's own dynamics. Results depend on the initial forager
saturation, which is why `env.lim_h` is treated as an experimental factor.

### III.iii Input data

The model uses static spatial input only: a digital elevation model of South
China (sets `elevation`), a matching slope surface (sets `slope`), and a
water-body layer (sets `water_type`). These rasters are read once and do not
change during a run. The model uses **no dynamic external drivers** such as a
climate, vegetation, or population series; this is a modelling choice, and it means
that every trend in the output is generated internally.

Water enters the model as a productivity property of land, not as impassable
terrain. The sea lies outside the modelled grid by construction: it is the water
layer's nodata value and is masked out with the rest of the frame, so every one of
the 6835 modelled cells is land. Over that land the layer supplies two classes,
inland (5771 cells) and near-water (1064 cells), and the distinction acts through
carrying capacity: a near-water cell supports a forager group of
`Hunter.max_size_water` = 500 against `Hunter.max_size` = 100 inland, which
represents the richer aquatic and riparian resources such cells offer. Because no
modelled cell is itself water, the "not water" clause of the two arability predicates
is always satisfied in practice, and the denominator of the regional forager ceiling
is the full 6835 cells.

In the terrain experiment (Figure 4) the elevation and slope surfaces are each
replaced, independently, by a spatially uniform raster, giving a 2 × 2 factorial:
real terrain, homogenised slope only, homogenised elevation only, and fully
homogenised.

### III.iv Submodels

**Growth and intensification.** Each step, `size` ← `size` × (1 + `growth_rate`),
with `Farmer.growth_rate` = 0.005, `RiceFarmer.growth_rate` = 0.006, and
`Hunter.growth_rate` = 0.001. A farming group's per-group capacity is
`max_size` = π · `area`² / `capital_area`. With the initial cultivated radius
`area` = 2 km this gives ≈ 3142 for `Farmer` (`capital_area` = 0.004 km² per person)
and ≈ 6283 for `RiceFarmer` (`capital_area` = 0.002 km² per person). When a group
would exceed its capacity it intensifies (`complicate`): `area` grows by
`area` × (1 − `complexity`) and `growth_rate` is multiplied by (1 − `complexity`),
with `complexity` = 0.1. This produces saturating population curves.

**Immigration.** The number of new rainfed groups per step is
`Poisson(env.lam_farmer)` and of paddy groups `Poisson(env.lam_ricefarmer)`, once
the tick reaches `tick_farmer` / `tick_ricefarmer` (both 0). Each group is placed
on a uniformly random empty rainfed-arable cell at a `size` drawn from
`new_group_size` (30–60 for `Farmer`, 200–300 for `RiceFarmer`). Placement uses the
rainfed-arable mask for both breeds, so an immigrant paddy group may be seeded on a
cell that does not meet the paddy slope criterion. Defaults are
`env.lam_farmer` = 3 and `env.lam_ricefarmer` = 0.1; these set how hard
agriculture presses on the region and are swept in Figure 5
(`env.lam_farmer` ∈ {2,4,6,8,10}, `env.lam_ricefarmer` ∈ {0.1,…,0.5}).

**Colonization.** With probability `diffuse_prob` = 0.05 per step a farming group
attempts to split off a colony; a `Hunter` group attempts only when at
`max_size`. The colony takes a block drawn from `new_group_size` and the parent
keeps the rest. The colony searches outward ring by ring, in a von Neumann
neighbourhood, for a suitable empty cell within `max_travel_distance` = 5 cells,
choosing uniformly among the eligible cells in the nearest ring that has any; if
none is found within range, no colony forms. Population is conserved by the split
itself, with one exception: if the parent is left below `min_size` it dies, and its
remaining population is lost with it.

**Conversion.** A group changes breed in place when a path's conditions hold and a
Bernoulli draw at its probability succeeds; the group's `size` and its `source`
label are preserved. A global switch (`convert.enabled`) and per-path switches
(`convert.farmer_to_hunter`, `convert.hunter_to_farmer`, `convert.hunter_to_rice`,
`convert.farmer_to_rice`, `convert.rice_to_farmer`) can disable any path. There are
**five** directed paths, set out in Table \ref{tbl:conversion-paths}; there is no
paddy-to-forager path.

```xlsx-table
file: SCE_Tables.xlsx
sheet: Table S2
caption: The five directed conversion paths, with the conditions and probability gating each; only the two paths linking rainfed farmers and foragers are swept.
label: tbl:conversion-paths
skip_n: 1
notes: Conditions are evaluated first; the probability is a Bernoulli draw taken only when they hold. A dash marks a path held at its default in every experiment.
```

A forager evaluates the rainfed path first and the paddy path only if the first
fails; a rainfed farmer evaluates the forager path first and the paddy path only if
the first fails. The `Farmer` → `Hunter` path drains small farming groups back into
the much larger foraging pool and is the dominant suppressor of farming; the
`Hunter` → `Farmer` path is the contact channel by which farming spreads. These two
probabilities are swept in Figure 3, coarsely over {0, 0.02, …, 0.10} and finely
over `Farmer.convert_prob.to_hunter` ∈ [0, 0.02] (step 0.002) ×
`Hunter.convert_prob.to_farmer` ∈ [0, 0.15] (step 0.015).

**Mortality.** With probability `loss.prob` a group's `size` is scaled by
(1 − `loss.rate`). Foragers face frequent small losses (`Hunter.loss.prob` = 0.05,
`Hunter.loss.rate` = 0.01); farmers face rarer larger losses (`Farmer.loss.prob` =
`RiceFarmer.loss.prob` = 0.01, rate 0.05). Every breed executes this submodel
**once per step**, so each group draws exactly one loss trial per tick. A group
driven below `min_size` dies.

**Forager carrying capacity.** The total forager population is bounded by
`global_hunter_limit` = `env.lim_h` × (number of modelled cells), with
`env.lim_h` = 35 people per cell, giving a baseline ceiling of 35 × 6835 =
**239 225 people**. At the end of each step, if the total exceeds this ceiling,
forager groups are visited in random order and each is reduced by as much as it can
give without falling below `min_size`, dissolving groups that reach that floor,
until the total returns to the ceiling. Per-group forager capacity is also bounded
(`Hunter.max_size` = 100 inland, `Hunter.max_size_water` = 500 next to water). The
ceiling parameter `env.lim_h` is swept in Figure 4 over {15, 25, 35}.

**Movement.** A forager group below the sedentism threshold
(`Hunter.is_complex` = 100) moves each step to a suitable empty cell, chosen
uniformly from the nearest ring that offers one, out to `max_travel_distance` = 5;
above the threshold it becomes sedentary and stops moving. Farmers never move and
spread only by colonization.

### III.v Model output and analysis

Every parameter combination is run for `exp.repeats` = 5 replicates of
`time.end` = 500 steps. Trajectories are reported as the replicate mean with a
95% confidence interval; a scalar outcome is the end state, the mean over the final
51 recorded steps across replicates. Because replicate count is a design choice,
effect sizes and the replicate count are reported rather than significance tests.
For the conversion surface (Figure 3) we fit a separable additive model in log
space, log N ≈ α(f2h) + β(h2f) + γ, and report its coefficient of determination
($R^2 = 0.992$) and residual structure as a measure of interaction. For the
leverage comparison (Figure 5) each swept intensity is normalised to a multiple of
its baseline and the slope of the end-state response is compared between the two
streams. A separate breakpoint detector (the ruptures library, `Dynp` algorithm, one breakpoint,
minimum segment 5 steps) produces the `bkp_*` diagnostics used in exploratory
heatmaps; it does not feed Figures 2–5.

---

## IV. Additional elements (ODD+D)

**Implemented behaviour that departs from the natural reading.** These are recorded
so that a reimplementation reproduces this model rather than an idealised one.
(i) Immigrant paddy groups are placed using the rainfed-arable mask, so some are
seeded on cells that fail the paddy slope criterion. (ii) A colony split loses the
parent's residual population when that residual falls below `min_size`. (iii) A
group-merging routine exists in the code but is never called.

**Model testing and validation.** Validation is pattern-oriented. The model is
judged by whether it reproduces the qualitative patterns named in I.i — a
persistently low agricultural share and the relative ranking of mechanisms —
rather than by point prediction of specific historical events. No independent
dataset was available for validation, so calibration and validation are not
separated: the parameters are sourced from the literature and the patterns are
qualitative. The core submodels (agent state transitions, conversion thresholds,
mortality, and boundary cases) are covered by 114 unit tests. No global
variance-based sensitivity analysis was run; the sweeps are one- and two-factor
grids around the mechanism of interest.

**Model replication.** The model structure and its parameters are separated, and the
base seed is part of the configuration, so a run reproduces exactly from its
configuration, sweep position, and repeat index. The code and configurations are
version-controlled and the sweep scripts are included.

**Computational requirements.** Each replicate is a single-process run of 500
steps. Sweeps are embarrassingly parallel across parameter combinations and
replicates, and are dispatched as independent batch jobs (121 combinations × 5
replicates for the fine conversion grid).

---

Table \\ref{tbl:symbol-map} maps the main-text symbols onto the implementation
parameter names one for one, and Table \\ref{tbl:parameters} lists every parameter
with its provenance.

```xlsx-table
file: SCE_Tables.xlsx
sheet: Table S3
caption: One-to-one mapping between the main-text symbols and the implementation parameter names, so that the two descriptions of the model cannot drift apart.
label: tbl:symbol-map
skip_n: 1
```

```xlsx-table
file: SCE_Tables.xlsx
sheet: Table S4
caption: Every model parameter with its baseline value, the range over which it was swept, and whether the value is taken from the literature or set by expert judgement.
label: tbl:parameters
skip_n: 1
longtable: true
notes: Provenance is one of *Literature*, *Expert judgement*, or *Derived*. A parameter marked *Expert judgement* has no empirical source; it is named as such rather than given an implied one.
```


*Reference: Müller B. et al. (2013) Describing human decisions in agent-based
models — ODD+D, an extension of the ODD protocol. Environmental Modelling &
Software 48, 37–48.*
