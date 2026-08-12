# Supplementary Information — Model description (ODD+D protocol)

This description follows the ODD+D protocol (Overview, Design concepts, Details,
and human Decision-making; Müller et al. 2013), an extension of ODD for
agent-based models that make behavioural decisions. It is written for
replication, so it names the implementation parameters directly (in
`monospace`); the main-text Methods gives the same quantities as mathematical
symbols. Baseline values, tested ranges, and their rationale are collected in
Table S1. The model produces main-text Figures 2–5.

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
suppresses farming.

### I.ii Entities, state variables, and scales

The model contains two entity types: spatial cells and settlement groups.

**Cells** form a raster grid of South China. Each cell stores an elevation
(`elevation`), a slope (`slope`), and a water class (`water_type` ∈ {sea, land,
near-water}). It derives binary land-use predicates. A cell is rainfed-arable
(`is_arable`) when `slope` ≤ 10°, 0 < `elevation` < 200 m, and it is not water. A
cell is paddy-arable (`is_rice_arable`) when `slope` ≤ 0.5° under the same
elevation and water conditions; paddy-arable cells are a subset of rainfed-arable
cells. Each cell holds at most one group (`max_agents = 1`).

**Settlement groups** are the agents; individuals are not represented. Three
breeds inherit one group class: rainfed farmers (`Farmer`), paddy farmers
(`RiceFarmer`), and hunter-gatherers (`Hunter`). Every group has a size (`size`,
= $N$), a minimum viable size (`min_size` = 6), and a carrying capacity
(`max_size`). Farmers additionally hold a cultivated area (`area`) and a mutable
growth rate (`growth_rate`). A group whose `size` drops below `min_size` is
removed.

**Scales.** Time advances in discrete steps with no calendar; each run lasts
`time.end` = 500 steps. Space is the fixed extent of the input raster, and each
cell is a patch of constant area. There is no exogenous temporal input.

### I.iii Process overview and scheduling

One step (`Model.step`) executes the following ordered sequence.

1. **Immigration** (`Env.step`). Two independent inflows of farming groups are
   added. The count of new rainfed groups is drawn as
   `Poisson(env.lam_farmer)` and of paddy groups as
   `Poisson(env.lam_ricefarmer)`, provided the current tick is at least
   `tick_farmer` / `tick_ricefarmer` (both 0 by default). Each new group is placed
   on a uniformly random empty arable cell of the matching type and given a size
   drawn from `new_group_size`.
2. **Group updates** (`agents.shuffle_do("step")`). All existing groups act once
   in a freshly randomised order. Each group, in its turn, performs the following
   sub-sequence:
   - (a) **Growth** (`population_growth`): `size` ← `size` × (1 + `growth_rate`).
   - (b) **Conversion** (`convert`): a two-stage attempt to change breed (below).
   - (c) **Colonization** (`diffuse`): a farming group attempts to split off a
     colony with probability `diffuse_prob`; a forager group attempts to split
     only when it is at `max_size`.
   - (d) **Mortality** (`loss`): a Bernoulli loss event.
   - (e) **Movement** (`move_one`, `Hunter` only): a mobile forager steps to a
     random suitable empty neighbour.
3. **Regional forager ceiling** (`apply_global_hunter_limit`). If the summed
   forager population exceeds the ceiling `global_hunter_limit`, forager groups
   are trimmed in random order until it no longer does.
4. **Observation** (`datacollector.collect`). For each breed the summed `size`
   and the group count are recorded.

Updates are asynchronous within a step: a group acts on the state left by groups
that moved earlier in the same step. Group splitting and merging conserve total
population exactly.

---

## II. Design concepts

### II.i Theoretical and empirical background

The model rests on competition between livelihoods for a shared, finite
landscape. The standing forager population sets the resistance that incoming
farmers meet. The arability thresholds, the per-cell forager carrying capacity,
the per-group farming capacity, and the spacing of settlements are parameterised
from published archaeological and ethnographic estimates for the region and
period. Livelihood conversion encodes the central hypothesis that switching
between ways of life, rather than the physical environment, governs the spread of
agriculture.

### II.ii Individual decision-making

Groups do not maximise an explicit objective; behaviour is governed by
condition-and-probability rules, and persistence is emergent. Every behavioural
decision is a two-stage test: a set of deterministic conditions must hold, and
then a Bernoulli draw at the relevant probability must succeed. This applies to
conversion (`convert_prob`, gated by size thresholds, land suitability, and
neighbour presence), colonization (`diffuse_prob`, gated by having enough people
for a colony and an empty suitable cell), and movement (gated by the sedentism
threshold). Immigrant placement is a model-level draw over eligible cells.
Decisions are made at the scale of the group and its immediate neighbourhood and
are re-evaluated every step. Social norms, institutions, preferences, and
explicit representations of uncertainty are not modelled.

### II.iii Learning

Not implemented. No rule or parameter is updated from past experience. The only
adaptive feedback is density-dependent intensification of farming groups (see
Submodels), a fixed response rather than a learned strategy.

### II.iv Individual sensing

A group senses its own cell (its arable predicates and water class) and the
contents of its immediate neighbourhood. Forager-to-farmer conversion senses a
`Farmer` neighbour; forager-to-paddy conversion senses a `RiceFarmer` neighbour.
Colonising and moving groups sense which neighbouring cells are suitable and
empty. Sensing is local and error-free.

### II.v Prediction

Not implemented. No decision uses an expectation of a future state.

### II.vi Interaction

Interaction is indirect and spatial. Because `max_agents = 1`, groups compete for
space by occupancy: a colonising or moving group can settle only on an empty
suitable cell. Conversion is a contact interaction, since a forager adopts farming
only next to an existing farming group. There is no direct conflict, predation, or
resource transfer between groups; an earlier competition mechanism was removed.

### II.vii Collectives

The settlement group is itself the collective unit. Individual people are not
represented, and there are no higher-order collectives such as tribes or
alliances.

### II.viii Heterogeneity

Cells are heterogeneous in `elevation`, `slope`, and `water_type`, and therefore
in their arable predicates. Groups are heterogeneous in breed, in `size`, and —
for farmers — in `area` and current `growth_rate`. The two farming breeds load
onto the landscape differently: rainfed groups arrive frequently and small
(`new_group_size` 30–60) and use a wide range of cells, whereas paddy groups
arrive rarely and large (`new_group_size` 200–300) and need the scarce near-flat
cells.

### II.ix Stochasticity

The model is stochastic throughout. The random sources are: the Poisson
immigration counts (`env.lam_farmer`, `env.lam_ricefarmer`); the uniform choice
of empty cells for immigrants and colonies; the initial group sizes (drawn
uniformly within bounds); the Bernoulli conversion trials (`convert_prob`); the
Bernoulli colonization trial (`diffuse_prob`) and the drawn colony size; the
Bernoulli mortality trial (`loss.prob`); the random neighbour chosen in forager
movement; the randomised order of group updates each step; and the random order
in which forager groups are trimmed at the ceiling. Growth and intensification
are deterministic. Because of these sources, every parameter combination is run
in replicate (`exp.repeats` = 5).

### II.x Observation

At each step the model records, for each breed, the summed `size` and the number
of groups. From these emergent series we compute the agricultural share of total
population and the end-state summaries. The end state of a run is the mean over
the last 50 steps; the end state of a parameter combination is the mean of those
values across the five replicates. The quantities of interest — the suppressed
agricultural share, the conversion response surface, and the leverage of each
immigration stream — are emergent properties, not imposed.

---

## III. Details

### III.i Implementation details

The model is implemented in Python (3.11) on the ABSESpy agent-based modelling
framework (0.8.5). A hierarchical configuration system (`config`) stores the
baseline parameters and defines the sweeps, so model structure and parameters are
separated and a sweep changes configuration only. Each combination runs as an
independent batch of `exp.repeats` = 5 replicates. Random draws use the
framework's seeded generators, so a run reproduces given its parameters and seed.
Each replicate writes a full time series (`<run>_tracking.csv`) of summed `size`
and group count per breed, which is the sole input to the analysis.

### III.ii Initialisation

At the start of a run, a fraction `env.init_hunters` = 0.5 of the non-water cells
is seeded with a `Hunter` group, each with a `size` drawn uniformly between
`min_size` and 100. No farming groups are present initially (`env.init_farmers` =
0, `env.init_rice_farmers` = 0). Agriculture appears only through immigration, so
any farming population observed in a run is generated by the model's own dynamics.

### III.iii Input data

The model uses static spatial input only: a digital elevation model of South
China (sets `elevation`), a matching slope surface (sets `slope`), and a
water-body layer (sets `water_type`). These rasters are read once and do not
change during a run. The model uses no dynamic external drivers such as a climate
or population series. In the terrain experiment (Figure 4) the elevation and slope
surfaces are replaced by spatially uniform rasters to remove landscape
heterogeneity.

### III.iv Submodels

**Growth and intensification.** Each step, `size` ← `size` × (1 + `growth_rate`),
with `Farmer.growth_rate` = 0.005, `RiceFarmer.growth_rate` = 0.006, and
`Hunter.growth_rate` = 0.001. A farming group's per-group capacity is
`max_size` = π · `area`² / `capital_area`, with `capital_area` = 0.004 km² per
person; the initial cultivated radius `area` = 2 km gives `max_size` ≈ 3142. When
a group would exceed its capacity it intensifies (`complicate`): `area` grows and
`growth_rate` is multiplied by (1 − `complexity`), with `complexity` = 0.1. This
produces saturating population curves.

**Immigration.** The number of new rainfed groups per step is
`Poisson(env.lam_farmer)` and of paddy groups `Poisson(env.lam_ricefarmer)`, once
the tick reaches `tick_farmer` / `tick_ricefarmer` (both 0). Each group is placed
on a uniformly random empty arable cell of the matching type, at a `size` drawn
from `new_group_size` (30–60 for `Farmer`, 200–300 for `RiceFarmer`). Defaults are
`env.lam_farmer` = 3 and `env.lam_ricefarmer` = 0.1; these set how hard
agriculture presses on the region and are swept in Figure 5
(`env.lam_farmer` ∈ {2,4,6,8,10}, `env.lam_ricefarmer` ∈ {0.1,…,0.5}).

**Colonization.** With probability `diffuse_prob` = 0.05 per step a farming group
attempts to split off a colony; a `Hunter` group attempts only when at
`max_size`. The colony takes a block from `new_group_size` and the parent keeps
the rest, conserving population. The colony searches outward for the nearest
suitable empty cell within `max_travel_distance` = 5 cells; if none is found, no
colony forms.

**Conversion.** A group changes breed in place when a path's conditions hold and a
Bernoulli draw at its probability succeeds; the group's `size` is preserved. A
global switch (`convert.enabled`) and per-path switches
(`convert.farmer_to_hunter`, `convert.hunter_to_farmer`, `convert.hunter_to_rice`,
`convert.farmer_to_rice`, `convert.rice_to_farmer`) can disable any path. The six
paths:

| Path | Conditions | Probability (default) | Tested range |
|---|---|---|---|
| `Farmer` → `Hunter` (f2h) | `size` ≤ `convert_threshold.to_hunter` (100) | `Farmer.convert_prob.to_hunter` = 0.1 | 0–0.1 |
| `Hunter` → `Farmer` (h2f) | a `Farmer` neighbour; cell `is_arable` | `Hunter.convert_prob.to_farmer` = 0.05 | 0–0.15 |
| `Farmer` → `RiceFarmer` | `size` ≥ `convert_threshold.to_rice` (200); cell `is_rice_arable` | `Farmer.convert_prob.to_rice` = 0.05 | — |
| `Hunter` → `RiceFarmer` | a `RiceFarmer` neighbour; cell `is_rice_arable` | `Hunter.convert_prob.to_rice` = 0.05 | — |
| `RiceFarmer` → `Farmer` | `size` < `convert_threshold.to_farmer` (200) | `RiceFarmer.convert_prob.to_farmer` = 1.0 | — |

The `Farmer` → `Hunter` path drains small farming groups back into the much larger
foraging pool and is the dominant suppressor of farming; the `Hunter` → `Farmer`
path is the contact channel by which farming spreads. These two probabilities are
swept in Figure 3, coarsely over {0, 0.02, …, 0.10} and finely over
`Farmer.convert_prob.to_hunter` ∈ [0, 0.02] (step 0.002) ×
`Hunter.convert_prob.to_farmer` ∈ [0, 0.15] (step 0.015).

**Mortality.** With probability `loss.prob` a group's `size` is scaled by
(1 − `loss.rate`). Foragers face frequent small losses (`Hunter.loss.prob` = 0.05,
`Hunter.loss.rate` = 0.01); farmers face rarer larger losses (`Farmer.loss.prob` =
0.01, `Farmer.loss.rate` = 0.05). A group driven below `min_size` dies.

**Forager carrying capacity.** The total forager population is bounded by
`global_hunter_limit` = `env.lim_h` × (number of non-water cells), with
`env.lim_h` = 35 people per cell. At the end of each step, if the total exceeds
this ceiling, forager groups are trimmed in random order — reducing the largest
reducible groups first and dissolving groups that reach `min_size` — until the
total returns to the ceiling. Per-group forager capacity is also bounded
(`Hunter.max_size` = 100 inland, `Hunter.max_size_water` = 500 next to water). The
ceiling `env.lim_h` is swept in Figure 4 over {15, 25, 35}.

**Movement.** A forager group below the sedentism threshold
(`Hunter.is_complex` = 100) steps to a uniformly random suitable empty neighbour
each step; above the threshold it becomes sedentary and stops moving. Farmers never
move and spread only by colonization.

### III.v Model output and analysis

Every parameter combination is run for `exp.repeats` = 5 replicates of
`time.end` = 500 steps. Trajectories are reported as the replicate mean with a
95% confidence interval; a scalar outcome is the end state, the mean over the last
50 steps across replicates. For the conversion surface (Figure 3) we fit a
separable additive model in log space,
log N ≈ α(f2h) + β(h2f) + γ, and report its coefficient of determination
($R^2 = 0.992$) and residual structure as a measure of interaction. For the
leverage comparison (Figure 5) each swept intensity is normalised to a multiple of
its baseline and the slope of the end-state response is compared between the two
streams.

---

## IV. Additional elements (ODD+D)

**Model testing and validation.** Validation is pattern-oriented. The model is
judged by whether it reproduces the qualitative patterns of interest — a
persistently low agricultural share and the relative ranking of mechanisms —
rather than by point prediction of specific historical events. The core submodels
(agent state transitions, conversion thresholds, mortality, and boundary cases)
are covered by unit tests.

**Model replication.** The model structure and its parameters are separated, and
all randomness uses seeded generators, so any reported run reproduces from its
configuration and seed. The code and configurations are version-controlled.

**Computational requirements.** Each replicate is a single-process run of 500
steps. Sweeps are embarrassingly parallel across parameter combinations and
replicates, and are dispatched as independent batch jobs.

---

## Table S1. Full parameter list

| Parameter | Meaning | Default (range tested) |
|---|---|---|
| `time.end` | steps per run | 500 |
| `exp.repeats` | replicates per combination | 5 |
| `min_size` | minimum viable group size | 6 |
| `Farmer.growth_rate` / `RiceFarmer.growth_rate` / `Hunter.growth_rate` | growth rates | 0.005 / 0.006 / 0.001 |
| `Farmer.area` | initial cultivated radius | 2 km |
| `Farmer.capital_area` | land per person | 0.004 km² |
| — | initial per-group farming capacity | ≈ 3142 |
| `Farmer.complexity` | intensification factor | 0.1 |
| `env.lam_farmer` / `env.lam_ricefarmer` | immigration intensity | 3 / 0.1 (2–10; 0.1–0.5) |
| `new_group_size` (Farmer / RiceFarmer) | immigrant/colony size | 30–60 / 200–300 |
| `diffuse_prob` | colonization probability | 0.05 |
| `max_travel_distance` | colonization/movement range | 5 cells |
| `Farmer.convert_prob.to_hunter` (f2h) | rainfed → forager | 0.1 (0–0.1) |
| `Hunter.convert_prob.to_farmer` (h2f) | forager → rainfed | 0.05 (0–0.15) |
| `Farmer.convert_prob.to_rice` | rainfed → paddy | 0.05 |
| `Hunter.convert_prob.to_rice` | forager → paddy | 0.05 |
| `RiceFarmer.convert_prob.to_farmer` | paddy → rainfed | 1.0 |
| `convert_threshold.to_hunter` / `.to_rice` / `.to_farmer` | size thresholds | 100 / 200 / 200 |
| `Hunter.max_size` / `Hunter.max_size_water` | per-group forager capacity | 100 / 500 |
| `Hunter.is_complex` | forager sedentism threshold | 100 |
| `env.lim_h` | forager carrying capacity per cell | 35 (15, 25, 35) |
| `Farmer.loss.prob` / `.rate` | farmer mortality | 0.01 / 0.05 |
| `Hunter.loss.prob` / `.rate` | forager mortality | 0.05 / 0.01 |
| `env.init_hunters` | initial forager cover | 0.5 (50% of non-water cells) |
| `env.init_farmers` / `env.init_rice_farmers` | initial farmers | 0 / 0 |
| `convert.enabled` and per-path switches | conversion on/off controls | all on |

*Reference: Müller B. et al. (2013) Describing human decisions in agent-based
models — ODD+D, an extension of the ODD protocol. Environmental Modelling &
Software 48, 37–48.*
