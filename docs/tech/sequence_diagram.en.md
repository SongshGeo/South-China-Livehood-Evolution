---
title: Model Sequence Diagrams
author: Shuang Song
date: 2025-10-20
---

# Model Detailed Sequence Diagrams

This document illustrates the running process of the South China Livelihood Evolution Model through sequence diagrams.

## Complete Run Sequence

```mermaid
sequenceDiagram
    participant User
    participant Exp as MyExperiment
    participant Model
    participant Env as Environment
    participant H as Hunter
    participant F as Farmer
    participant RF as RiceFarmer
    participant Cell as CompetingCell

    Note over User,Cell: Initialization Phase

    User->>Exp: Run experiment (batch_run)
    Exp->>Model: Create model instance
    Model->>Env: initialize()

    Note over Env,Cell: Environment Initialization
    Env->>Env: setup_dem()
    Env->>Cell: Load DEM data
    Env->>Cell: Load Slope data
    Env->>Cell: Load lim_h data

    Note over Env,H: Add Initial Hunters
    Env->>Env: add_hunters(0.05)
    Env->>Cell: Select non-water cells
    Env->>H: Create Hunter (init_size: 6-35)
    H->>Cell: Move to cell

    Note over Env,F: Add Initial Farmers (NEW)
    Env->>Env: add_initial_farmers(80)
    Env->>Cell: Select arable land
    Env->>F: Create Farmer (init_size: 60-100)
    F->>Cell: Move to cell

    Note over Env,RF: Add Initial RiceFarmers (NEW)
    Env->>Env: add_initial_farmers(350)
    Env->>Cell: Select rice-arable land
    Env->>RF: Create RiceFarmer (init_size: 300-400)
    RF->>Cell: Move to cell

    Note over User,Cell: Running Phase (Each Tick)

    loop Each time step (tick)
        Model->>Env: env.step()

        Note over Env,F: Environment Step: Add New Agents
        Env->>Env: add_farmers(Farmer)
        Env->>F: Create Farmers via Poisson
        Env->>Env: add_farmers(RiceFarmer)
        Env->>RF: Create RiceFarmers via Poisson

        Note over Model,RF: Agent Step: Random Execution
        Model->>Model: agents.shuffle_do("step")

        alt Hunter selected
            Model->>H: step()
            H->>H: population_growth()
            H->>H: convert() [Check switches]
            opt Switch ON & conditions met
                H->>Cell: convert(to="Farmer")
                Cell->>Cell: Check convert.hunter_to_farmer
                Cell->>F: Create new Farmer
                Cell->>H: Die
            end
            H->>H: diffuse()
            opt population >= max_size
                H->>H: Create new Hunter
                H->>Cell: Search suitable cell
                Cell-->>H: Return target cell
            end
            H->>H: loss() [NEW]
            opt Random loss triggered
                H->>H: size *= (1 - loss.rate)
            end
            H->>H: move_one()
            opt Not settled (size <= 100)
                H->>Cell: Search better cell
                opt Meet another Hunter
                    H->>H: merge(other_hunter)
                    Note over H: Conservation: size = size1 + size2
                end
            end
        else Farmer selected
            Model->>F: step()
            F->>F: population_growth()
            F->>F: convert() [Check switches]
            F->>F: diffuse()
            F->>F: loss()
        else RiceFarmer selected
            Model->>RF: step()
            RF->>RF: population_growth()
            RF->>RF: convert() [Check switches]
            RF->>RF: diffuse()
            RF->>RF: loss()
        end

        Note over Model: Check Death Conditions
        alt Agent population < min_size
            Model->>H: die()
            Model->>F: die()
            Model->>RF: die()
        end

        Model->>Model: datacollector.collect()
    end

    Note over User,Cell: End Phase

    Model->>Model: end()
    Model->>Model: plot.dynamic()
    Model->>Model: plot.heatmap()
    Model->>Model: export_conversion_data()
    Model-->>Exp: Return results
    Exp-->>User: Save result files
```

## Conversion Mechanism (v2.0 with Switch Control)

```mermaid
flowchart TD
    Start([Agent Attempts Conversion]) --> CheckGlobal{Global Switch<br/>convert.enabled?}

    CheckGlobal -->|False| NoConvert[No Conversion]
    CheckGlobal -->|True| CheckType{Check Agent Type}

    CheckType -->|Hunter| HunterConvert[Hunter Conversion Logic]
    CheckType -->|Farmer| FarmerConvert[Farmer Conversion Logic]
    CheckType -->|RiceFarmer| RiceConvert[RiceFarmer Conversion Logic]

    HunterConvert --> CheckH2F{hunter_to_farmer<br/>switch?}
    CheckH2F -->|True| H2FCond{Near Farmer &<br/>On arable land &<br/>Random trigger?}
    CheckH2F -->|False| CheckH2R{hunter_to_rice<br/>switch?}
    H2FCond -->|Yes| ConvertH2F[Convert to Farmer]
    H2FCond -->|No| CheckH2R

    CheckH2R -->|True| H2RCond{Near RiceFarmer &<br/>On rice-arable land &<br/>Random trigger?}
    CheckH2R -->|False| NoConvert
    H2RCond -->|Yes| ConvertH2R[Convert to RiceFarmer]
    H2RCond -->|No| NoConvert

    FarmerConvert --> CheckF2H{farmer_to_hunter<br/>switch?}
    CheckF2H -->|True| F2HCond{Population <= 100 &<br/>Random trigger?}
    CheckF2H -->|False| CheckF2R{farmer_to_rice<br/>switch?}
    F2HCond -->|Yes| ConvertF2H[Convert to Hunter]
    F2HCond -->|No| CheckF2R

    CheckF2R -->|True| F2RCond{Population >= 200 &<br/>On rice-arable land &<br/>Random trigger?}
    CheckF2R -->|False| NoConvert
    F2RCond -->|Yes| ConvertF2R[Convert to RiceFarmer]
    F2RCond -->|No| NoConvert

    RiceConvert --> CheckR2F{rice_to_farmer<br/>switch?}
    CheckR2F -->|True| R2FCond{Population < 200 &<br/>Random trigger?}
    CheckR2F -->|False| NoConvert
    R2FCond -->|Yes| ConvertR2F[Convert to Farmer]
    R2FCond -->|No| NoConvert

    ConvertH2F --> Create[Create new agent<br/>Keep population]
    ConvertH2R --> Create
    ConvertF2H --> Create
    ConvertF2R --> Create
    ConvertR2F --> Create

    Create --> Die[Old agent dies]
    Die --> End([Conversion Complete])
    NoConvert --> End

    style CheckGlobal fill:#ff9999
    style Create fill:#99ff99
    style Die fill:#ffcc99
```

## Diffusion & Population Conservation (v2.0 Improved)

```mermaid
sequenceDiagram
    participant Agent as Original Agent<br/>(size=100)
    participant Model
    participant NewAgent as New Agent
    participant Cell as Current Cell
    participant NewCell as Target Cell

    Note over Agent: Trigger Diffusion
    Agent->>Agent: Check diffusion conditions

    alt Hunter: size >= max_size
        Agent->>Agent: Auto diffuse
    else Farmer/RiceFarmer: Random
        Agent->>Agent: random() < diffuse_prob
    end

    Note over Agent,Model: Population Conservation Key Steps

    rect rgb(255, 220, 220)
        Note over Agent,NewAgent: Step 1: Create new agent first
        Agent->>Agent: new_size = random(min, max)
        Agent->>Agent: new_size = min(new_size, self.size)
        Agent->>Model: Create new agent(size=new_size)
        Model->>NewAgent: New agent born
    end

    rect rgb(220, 255, 220)
        Note over Agent: Step 2: Decrease original population
        Agent->>Agent: self.size -= new_size
        Note over Agent: 🔒 Conservation Check<br/>Original = Current + New
    end

    alt Original population < min_size
        Agent->>Agent: die()
        Note over Agent: Original agent dies
    end

    rect rgb(220, 220, 255)
        Note over NewAgent,NewCell: Step 3: New agent finds location
        NewAgent->>Cell: search_cell(radius=1)
        Cell->>NewCell: Check nearby cells

        loop Expand search radius
            NewCell->>NewCell: able_to_live(new_agent)?
            alt Found suitable cell
                NewAgent->>NewCell: Move to new cell
            else Not found
                NewCell->>Cell: Expand radius and continue
            end
        end

        alt Search failed (radius > max_travel_distance)
            NewAgent->>NewAgent: die()
            Note over NewAgent: New agent dies<br/>But population already reduced<br/>Total conserved
        end
    end

    Note over Agent,NewAgent: Final Result:<br/>Total = Remaining + New
```

## Cell Rule Check (v2.0: One Agent Per Cell)

```mermaid
flowchart TD
    Start([Agent Attempts to Enter Cell]) --> HasAgent{Cell has agent?}

    HasAgent -->|No| CheckType{Check Agent Type}
    HasAgent -->|Yes| SameAgent{Same agent?}

    SameAgent -->|Yes| CheckType
    SameAgent -->|No| Reject[Reject: Only one agent per cell]

    CheckType -->|Hunter| CheckWater{Is water?}
    CheckType -->|Farmer| CheckArable{Is arable?}
    CheckType -->|RiceFarmer| CheckRiceArable{Is rice-arable?}

    CheckWater -->|No| Allow[Allow Entry]
    CheckWater -->|Yes| Reject

    CheckArable -->|Yes| Allow
    CheckArable -->|No| Reject

    CheckRiceArable -->|Yes| Allow
    CheckRiceArable -->|No| Reject

    Allow --> Success([Success])
    Reject --> Fail([Failed])

    style HasAgent fill:#ffcccc
    style CheckType fill:#ccccff
    style Allow fill:#ccffcc
    style Reject fill:#ffcccc
```

## Usage

### Embedding Sequence Diagrams in Documentation

These sequence diagrams are written in Mermaid syntax and will be automatically rendered as interactive charts in the documentation.

### Viewing Diagrams

1. Start documentation server: `poetry run mkdocs serve`
2. Visit this page to view complete interactive sequence diagrams
3. Can zoom, export to SVG/PNG

### Modifying Diagrams

Directly edit the Mermaid code blocks in this file; changes update automatically.

## Key Process Descriptions

### v2.0 Important Changes Reflected in Diagrams

1. **Conversion Switches**: Each conversion operation checks corresponding switch
2. **Population Conservation**: Create new agent first, then decrease original population during diffusion
3. **Loss Mechanism**: Hunter now has loss() step
4. **One Per Cell**: able_to_live() checks if cell already has other agents
5. **Initialization**: All three agent types created simultaneously, no waiting for specific ticks

### Key Time Points

- **tick=0**: Initialize, create all three agent types
- **Each tick**:
  1. Environment step (add new agents)
  2. Agent step (randomly execute all agents' steps)
  3. Data collection
- **tick=end**: End, plot and export data

## Reference Documentation

- [Workflow](../usage/workflow.en.md) - Text description
- [Changelog](changelog_v2.en.md) - Detailed changes
- [Configuration](../usage/config.en.md) - Parameter descriptions

