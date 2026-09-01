# South China Livelihood Evolution Model

## Model Features

This model currently includes the following main features:

1. Simulates interactions among three groups: hunter-gatherers, farmers, and rice farmers.
2. Considers terrain factors (elevation, slope) impact on population distribution.
3. Supports dynamic processes like population growth, migration, and conversion.
4. Provides various data visualization methods (heatmaps, trend charts, etc.).
5. Flexible conversion mechanism control with independent switches for different conversion types.
6. Diffusion mostly conserves population (a parent left below `min_size` is removed with its remainder); the model has no merging mechanism.

> **This repository's main deliverable is a paper**: five figures, one table workbook, and
> every number the prose quotes are produced by the two notebooks under `reports/` and the
> two scripts under `paper/` — see [From Model to Manuscript].
> The model itself was substantially refactored in v2.0 (competition removed, conversion
> switches added, initialisation reworked); see [Changelog](tech/changelog_v2.md).

## Getting Started

- First, refer to [Quick Start] to install and use the model
- Then carefully read [Model Workflow] to understand the running logic
- Next, consult [Configuration] to adjust model parameters and run your experiments
- Finally, use methods in [Data Analysis] to analyze experimental results
- To rebuild the paper's figures, tables and numbers, see [From Model to Manuscript]

## Method Documentation

- [Model Workflow](api/model.md)
- [Sequence Diagrams](tech/sequence_diagram.md) - 🆕 Visual Process Flows
- [Farmer Agent Methods](api/farmer.md)
- [Hunter Agent Methods](api/hunter.md)
- [Patches and Environment](api/env.md)

## About the Author

- Author: [Shuang Song]
- Email: songshgeo[at]gmail.com

<!-- Links -->
[Quick Start]: usage/quick_start.md
[Model Workflow]: usage/workflow.md
[Configuration]: usage/config.md
[From Model to Manuscript]: /docs/usage/manuscript_pipeline
[Data Analysis]: usage/plots.md
[Shuang Song]: https://cv.songshgeo.com/

