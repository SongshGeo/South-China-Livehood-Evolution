# Configuration File

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

Experiment configuration: experiment name, number of repeats, processes.

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| outdir | str | out | Output root (supplied by ABSESpy's default config) |
| name | str | south_china_evolution | Experiment name; drives `out/<name>/...` |
| repeats | int | 5 | Number of repeats per parameter set |
| num_process | int | 5 | Number of parallel processes |
| logging | str | all | Logging mode (all or once) |
| save_data | bool | true | Whether to write `<run_id>_tracking.csv` |

:::note
Every key under `exp:` must have a consumer. A `plot_heatmap` key used to drive an
experiment-level heatmap; when the `MyExperiment` class it relied on was deleted
before submission, the key became a dud — present in the config, present in the docs,
read by nobody, raising nothing.
`tests/test_config.py::test_every_exp_key_still_has_a_reader` now pins each key to its
consumer: if you cannot name one for a new key, the key should not exist.
:::

### env

Environment configuration, including parameters like carrying capacity and initial agent counts.

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| lim_h | int | 28 | **Forager carrying capacity (persons per cell)**; see note below |
| init_hunters | float | 0.5 | Initial hunter ratio or count (`<1`: ratio, `≥1`: count) |
| init_farmers | int | 0 | Initial farmer agents (0 at baseline; farmers arrive as immigrants) |
| init_rice_farmers | int | 0 | Initial rice farmer agents (0 at baseline; as above) |
| lam_farmer | float | 3 | Expected value for adding farmers per step (Poisson parameter) |
| lam_ricefarmer | float | 0.1 | Expected value for adding rice farmers per step (Poisson parameter) |
| tick_farmer | int | 0 | Time step to start adding farmers (0: from beginning) |
| tick_ricefarmer | int | 0 | Time step to start adding rice farmers (0: from beginning) |

:::info `lim_h` is in persons per cell, but its value comes from an areal density
The code multiplies `lim_h` by a cell **count** (`Env.calculate_global_hunter_limit`),
so what reaches the model is always persons per cell. The value is set the other way
round — pick the density, then convert: 35 persons per 100 km² × 80 km²/cell =
**28 per cell**, and the swept arms 15/25/35 per 100 km² become 12/20/28 per cell.
The regional ceiling is therefore 28 × 6835 = **191,380**.

The 31.93 documented here previously was Binford's (2001) *areal density* being used as
a per-cell value — a factor of about 2.2 out. That default has been removed; `lim_h` is
now required and a missing value raises rather than falling back to a magic number.
:::

> **Tip**: `tick_farmer` and `tick_ricefarmer` now default to 0, meaning these agents are created at initialization rather than during runtime.

### time

Time configuration, including parameters like time steps and step length.

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| end | int | 500 | Number of time steps |

### Farmer

Farmer configuration, including parameters like growth rate and diffusion probability.

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| area | int | 2 | Farmer activity range (km) |
| growth_rate | float | 0.005 | Population growth rate (per step) |
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
| init_size | list | [0, 100] | Initial population size range; auto-adjusted to min_size if below |
| growth_rate | float | 0.001 | Population growth rate (per step) |
| min_size | int | 6 | Minimum group size; agents die below this |
| **max_size** | int | 100 | **Maximum population for unit agent (normal case)** |
| **max_size_water** | int | 500 | **Maximum population near water bodies** |
| **global_limit** | float | Auto-calculated | **Global forager ceiling = `lim_h` × modelled cells (6835; see the `lim_h` note above)** |
| new_group_size | list | [6, 50] | New group size range when diffusing |
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

### ds

Data source configuration, including parameters like data paths.

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| dem | str | - | Digital Elevation Model path |
| slope | str | - | Slope data path |
| lim_h | str | - | **Water body data path (-1=sea, 0=land, 1=near-water land)** |

