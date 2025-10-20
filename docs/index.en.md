# South China Livelihood Evolution Model

## Model Features

This model currently includes the following main features:

1. Simulates interactions among three groups: hunter-gatherers, farmers, and rice farmers.
2. Considers terrain factors (elevation, slope) impact on population distribution.
3. Supports dynamic processes like population growth, migration, and conversion.
4. Provides various data visualization methods (heatmaps, trend charts, etc.).
5. Flexible conversion mechanism control with independent switches for different conversion types.
6. Strict population conservation for diffusion and merger processes.

> **Latest Update (v2.0)**: The model underwent major refactoring, removing competition mechanisms, adding conversion control switches, and optimizing initialization. See [Changelog](tech/changelog_v2.en.md) for details.

## Getting Started

- First, refer to [Quick Start] to install and use the model
- Then carefully read [Model Workflow] to understand the running logic
- Next, consult [Configuration] to adjust model parameters and run your experiments
- Finally, use methods in [Data Analysis] to analyze experimental results

## Method Documentation

- [Model Workflow](api/model.md)
- [Sequence Diagrams](tech/sequence_diagram.en.md) - 🆕 Visual Process Flows
- [Farmer Agent Methods](api/farmer.md)
- [Hunter Agent Methods](api/hunter.md)
- [Patches and Environment](api/env.md)

## About the Author

- Author: [Shuang Song]
- Email: songshgeo[at]gmail.com

<!-- Links -->
[Quick Start]: usage/quick_start.md
[Model Workflow]: usage/workflow.en.md
[Configuration]: usage/config.en.md
[Data Analysis]: usage/plots.md
[Shuang Song]: https://cv.songshgeo.com/

