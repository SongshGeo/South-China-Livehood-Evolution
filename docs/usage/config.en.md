---
title: Configuration File
author: Shuang Song
---

Configuration files are an essential part of model execution. The model runs simulations based on parameters in the configuration file. Configuration files use YAML format, and users can modify model parameters in the configuration file.

The default location for the configuration file is `config/config.yaml`. Users can also specify the configuration file location through command-line arguments when running the model.

## Configuration Structure

The configuration file is divided into the following sections:

### convert

Conversion mechanism switches that control conversion behavior between different agent types.

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| enabled | bool | true | Global conversion switch; all conversions disabled when off |
| hunter_to_farmer | bool | true | Whether hunters can convert to farmers |
| hunter_to_rice | bool | true | Whether hunters can convert to rice farmers |
| farmer_to_hunter | bool | true | Whether farmers can convert to hunters |
| farmer_to_rice | bool | true | Whether farmers can convert to rice farmers |
| rice_to_farmer | bool | true | Whether rice farmers can convert to farmers |

> **Note**: This feature allows you to disable conversion mechanisms to compare model behavior with/without conversion.

### exp

Experiment configuration, including experiment name, number of repeats, processes, plotting variables, etc.

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| name | str | - | Experiment name |
| repeats | int | 1 | Number of repeats per parameter set |
| num_process | int | 1 | Number of parallel processes |
| plot_heatmap | str | - | Variable for heatmap plotting |

### model

Model configuration, including model parameters like population loss coefficient and breakpoint detection method.

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| save_plots | bool | True | Whether to save plots |
| loss_rate | float | 0.5 | Population loss coefficient for competition losers (deprecated) |
| n_bkps | int | 1 | Number of breakpoints |
| detect_bkp_by | str | 'size' | Breakpoint detection method |

### env

Environment configuration, including parameters like carrying capacity and initial agent counts.

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| lim_h | float | 31.93 | Carrying capacity (persons/100km²) |
| init_hunters | float | 0.05 | Initial hunter ratio or count (<1: ratio, ≥1: count) |
| init_farmers | int | 80 | Initial number of farmer agents (recommended: 60-100) |
| init_rice_farmers | int | 350 | Initial number of rice farmer agents (recommended: 300-400) |
| lam_farmer | float | 1 | Expected value for adding farmers per step (Poisson parameter) |
| lam_ricefarmer | float | 1 | Expected value for adding rice farmers per step (Poisson parameter) |
| tick_farmer | int | 0 | Time step to start adding farmers (0: from beginning) |
| tick_ricefarmer | int | 0 | Time step to start adding rice farmers (0: from beginning) |

> **Tip**: `tick_farmer` and `tick_ricefarmer` now default to 0, meaning these agents are created at initialization rather than during runtime.

### time

Time configuration, including parameters like time steps and step length.

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| end | int | 10 | Number of time steps |

### Farmer

Farmer configuration, including parameters like growth rate and diffusion probability.

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| area | int | 2 | Farmer activity range (km) |
| growth_rate | float | 0.004 | Population growth rate (per step) |
| min_size | int | 6 | Minimum group size; agents die below this |
| **init_size** | list | [60, 100] | **Initial population size range** (random value at initialization) |
| new_group_size | list | [30, 60] | New group size range when diffusing |
| diffuse_prob | float | 0.05 | Diffusion probability per step |
| complexity | float | 0.1 | Growth rate reduction ratio after complexification |
| convert_prob | dict | - | Conversion probabilities (to_hunter, to_rice) |
| convert_threshold | dict | - | Conversion thresholds (to_hunter: max, to_rice: min) |
| max_travel_distance | int | 5 | Maximum search distance when diffusing |
| capital_area | float | 0.004 | Per capita arable land (km²) |
| loss | dict | - | Loss mechanism (prob: probability, rate: loss ratio) |

### Hunter

Hunter-gatherer configuration, including parameters like growth rate and movement rules.

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| init_size | list | [0, 35] | Initial population size range; auto-adjusted to min_size if below |
| growth_rate | float | 0.0008 | Population growth rate (per step) |
| min_size | int | 6 | Minimum group size; agents die below this |
| **max_size** | int | 100 | **Maximum population for unit agent (normal case)** |
| **max_size_water** | int | 500 | **Maximum population near water bodies** |
| new_group_size | list | [6, 31] | New group size range when diffusing |
| convert_prob | dict | - | Conversion probabilities (to_farmer, to_rice) |
| max_travel_distance | int | 5 | Maximum search distance when moving |
| is_complex | int | 100 | Threshold for settled hunters (stop moving) |
| **loss** | dict | - | **Loss mechanism (prob: probability, rate: loss ratio)** |

> **Important Changes**:
> - ❌ Removed `intensified_coefficient` parameter (no competition mechanism)
> - ✅ Added `max_size` and `max_size_water` parameters
> - ✅ Added `loss` parameter; hunters now also experience random losses

### RiceFarmer

Rice farmer configuration, including parameters like growth rate and diffusion probability.

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| area | int | 2 | Rice farmer activity range (km) |
| growth_rate | float | 0.005 | Population growth rate (per step) |
| min_size | int | 6 | Minimum group size; agents die below this |
| **init_size** | list | [300, 400] | **Initial population size range** (random value at initialization) |
| new_group_size | list | [200, 300] | New group size range when diffusing |
| diffuse_prob | float | 0.05 | Diffusion probability per step |
| complexity | float | 0.1 | Growth rate reduction ratio after complexification |
| convert_prob | dict | - | Conversion probabilities (to_farmer); cannot convert to hunters |
| convert_threshold | dict | - | Conversion thresholds (to_farmer: must be below this) |
| max_travel_distance | int | 5 | Maximum search distance when diffusing |
| capital_area | float | 0.002 | Per capita arable land (km²) |
| loss | dict | - | Loss mechanism (prob: probability, rate: loss ratio) |

### db

Database configuration, including parameters like database paths and types.

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| dem | str | - | Digital Elevation Model path |
| slo | str | - | Slope data path |
| asp | str | - | Aspect data path |
| farmland | str | - | Farmland data path |
| lim_h | str | - | Carrying capacity data path |

