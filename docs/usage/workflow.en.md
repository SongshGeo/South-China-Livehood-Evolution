---
title: Model Workflow
author: Shuang Song
---

A typical agent-based model experiment has the structure shown below, with [Experiment Process] on the left and [Model Process] on the right.

![workflow](https://songshgeo-picgo-1302043007.cos.ap-beijing.myqcloud.com/uPic/workflow.png)

## Experiment Process

In each experiment, this library automatically completes the following steps:

1. Get combinations of different parameters and determine the number of experimental configurations (jobs)
2. Batch run models, saving results for each run
3. Plot comparison charts for all jobs (heatmaps, breakpoint charts, dynamic charts)
4. Store summary data (`summary.csv`)

## Model Process

For each run in an experiment, the library automatically completes the following steps:

### Initialize

Environment loads according to `env` parameters, including:

1. Load terrain data (DEM)
2. Load slope data (SLO)
3. Load hunter population limit raster data (LIM_H)

### Setup

Add initial agents of all three types:

1. **Hunters**: Created in random non-water cells based on `env.init_hunters` parameter. Each hunter's initial population is randomly selected from the `Hunter.init_size` range.

2. **Farmers**: Created in random arable cells based on `env.init_farmers` parameter (default 80). Each farmer's initial population is randomly selected from the `Farmer.init_size` range (default 60-100).

3. **Rice Farmers**: Created in random rice-arable cells based on `env.init_rice_farmers` parameter (default 350). Each rice farmer's initial population is randomly selected from the `RiceFarmer.init_size` range (default 300-400).

> [!important]
> **Important Change**: All three agent types are now created at initialization. No need to wait for specific time steps. `tick_farmer` and `tick_ricefarmer` parameters default to 0.

### Step

As the run progresses (tick increases), the model repeatedly performs the following steps:

#### Environment Step

1. Add new Farmers based on `env.lam_farmer` parameter using Poisson distribution
2. Add new Rice Farmers based on `env.lam_ricefarmer` parameter using Poisson distribution

#### Agent Step

Sequentially **randomly** select all agents and execute their `step` methods:

##### Common Behaviors for All Agents

1. **Population Growth**: Update population based on `<breed>.growth_rate` parameter
2. **Conversion**: Attempt to convert to other agent types based on `<breed>.convert_prob` probability
   - Must meet conversion conditions (nearby target type, population within thresholds, etc.)
   - Subject to global switch `convert.enabled` and specific switches (e.g., `convert.hunter_to_farmer`)
3. **Diffusion**: Attempt to split into new groups in suitable nearby locations
   - Farmers and Rice Farmers: Based on `<breed>.diffuse_prob` probability
   - Hunters: Automatically diffuse when population reaches `max_size`
4. **Loss**: All agents may experience population loss with certain probability
   - Occurs with `<breed>.loss.prob` probability
   - Population decreases by `<breed>.loss.rate` ratio when occurs

##### Hunter-Specific Behaviors

- **Movement**: Non-settled hunters (population ≤ `is_complex`) actively search for and move to more suitable locations
- **Merger**: When encountering other hunters, they merge; merged population = sum of both (population conservation)

> [!warning]
> **Important Rule Changes**:
> - ❌ **Competition mechanism removed**: No competition between different agent types
> - ✅ **One agent per cell**: Only one agent (any type) allowed per cell
> - ✅ **Population conservation**: Diffusion and merger operations strictly conserve total population

#### Death Check

At each step, checks if current population is below the minimum threshold (determined by `<breed>.min_size`). If below, the `die` method is executed and the group perishes.

### End

The model ends when the number of steps reaches the `time.end` parameter, saving the following data for comparison with other runs:

1. All agent information (population, position, state, etc.)
2. Conversion matrices
3. Visualization charts

<!-- Links -->
[Experiment Process]: #experiment-process
[Model Process]: #model-process

