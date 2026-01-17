---
title: Model Refactoring Changelog (v2.0)
author: Shuang Song
date: 2025-10-20
---

# Model Refactoring Changelog (v2.0)

This document records the major logical modifications made to the model on October 20, 2025.

## Overview of Major Changes

This refactoring primarily aims to simplify model logic, enhance model flexibility and controllability, specifically including:

1. ✅ Add initial farmer population settings
2. ✅ Weaken correspondence between ticks and real time
3. ✅ Ensure population conservation in diffusion mechanism
4. ✅ Add conversion mechanism switches
5. ✅ Modify hunter population limit rules
6. ✅ Adjust hunter unit population constraints
7. ✅ Remove competition functionality
8. ✅ Add loss mechanism for hunters

## Detailed Change Descriptions

### 1. Initialization Mechanism Changes

#### Before
- Only hunters initialized
- Farmers and rice farmers dynamically added during runtime via Poisson distribution

#### After
- **All three agent types created at initialization**
- New configuration parameters:
  - `env.init_farmers`: Initial farmer count (default 80, recommended range 60-100)
  - `env.init_rice_farmers`: Initial rice farmer count (default 350, recommended range 300-400)
- Each agent type's initial population controlled by their respective `init_size` parameters
- `tick_farmer` and `tick_ricefarmer` set to 0 (active from first step)

**Impact**: Model starts with complete set of all three agent types, more realistic

### 2. Conversion Mechanism Switches

#### New Feature
Added flexible conversion control system with independent control over 6 conversion paths.

#### Configuration Example
```yaml
convert:
  enabled: true  # Global switch
  hunter_to_farmer: true  # Hunter → Farmer
  hunter_to_rice: true  # Hunter → Rice Farmer
  farmer_to_hunter: true  # Farmer → Hunter
  farmer_to_rice: true  # Farmer → Rice Farmer
  rice_to_farmer: true  # Rice Farmer → Farmer
```

**Purpose**:
- Can disable all conversions by setting `enabled: false`
- Can independently control each conversion path
- Facilitates comparison of model behavior with/without conversion

### 3. Major Hunter Adjustments

#### 3.1 Population Limit Rule Changes

**Before**:
- Each hunter's maximum population determined by cell's `lim_h` (carrying capacity)

**After**:
- Normal case: `max_size = 100`
- Near water: `max_size_water = 500` (water_type = 1 cells)
- **Global population limit**: `lim_h × non-water cells` (total Hunter population cannot exceed this)
- No longer limited by individual cell capacity
- **Water body data**: Use `water_type` (-1=sea, 0=land, 1=near-water land) instead of `lim_h` grid heterogeneity

**Configuration**:
```yaml
Hunter:
  max_size: 100  # Unit agent max population
  max_size_water: 500  # Max population near water
```

**Note**: Hunters exceeding `is_complex` threshold (default 100) still stop moving

#### 3.2 Remove Competition Mechanism

**Removed Features**:
- `moving()` method - No longer handles competition with other agents
- `compete()` method - All competition logic removed
- `loss_in_competition()` method - Competition failure handling removed
- `intensified_coefficient` parameter - Competition coefficient removed

**Impact**:
- Different agents cannot occupy same cell (one agent per cell rule)
- Hunters still merge when encountering other hunters
- Simpler, clearer movement logic
- **`search_cell()` function simplified**: No longer uses suitability-weighted selection, changed to simple random selection

#### 3.3 New Loss Mechanism

**New Feature**:
Hunters now also experience random losses like farmers (e.g., disease, disasters)

**Configuration**:
```yaml
Hunter:
  loss:
    prob: 0.05  # Loss occurrence probability
    rate: 0.1   # Population reduction ratio when loss occurs
```

**Implementation**: Each time step, loss occurs with `prob` probability, reducing population by `rate` ratio

#### 3.4 Merger Mechanism Improvement

**Before**:
```python
size = max(other_hunter.size + self.size, lim_h)
```

**After**:
```python
size = other_hunter.size + self.size  # Strict population conservation
```

**Impact**: Merged population = sum of both groups, ensuring population conservation

### 4. One Agent Per Cell Rule

#### New Rule
- **Only one agent (any type) allowed per cell**
- Checks if target cell has other agents when moving or diffusing
- Cells with existing agents cannot be movement or diffusion targets

#### Implementation
Added check logic in `CompetingCell.able_to_live()` method

#### Exception
- Hunters can still merge (moving to cell with another hunter triggers merger)
- Agents checking their own position not subject to this restriction

### 5. Population Conservation Guarantee

#### Diffusion Mechanism Improvement (`SiteGroup.diffuse()`)

**Before**:
Create new agent first, then decrease original population, potentially violating conservation

**After**:
```python
# 1. Create new agent first (ensure it exists even if original dies)
new = create_new_agent(size=new_group_size)
# 2. Decrease original population
self.size -= new_group_size
```

**Guarantee**: Total population strictly equal before and after diffusion (original = reduced original + new)

### 6. New Configuration Parameters

#### Farmer Configuration
```yaml
Farmer:
  init_size: [60, 100]  # Initial population size range
```

#### RiceFarmer Configuration
```yaml
RiceFarmer:
  init_size: [300, 400]  # Initial population size range
```

## Test Verification

All modifications verified through complete test suite:

- ✅ All 84 unit tests pass
- ✅ Single run test normal
- ✅ Multiple repeat runs normal
- ✅ Parallel processing works correctly
- ✅ Output files (conversion data, dynamic charts, heatmaps) generated normally

## Backward Compatibility

### Breaking Changes

1. **Configuration file must be updated**:
   - Add `convert` section
   - Remove `intensified_coefficient` from Hunter
   - Add `max_size`, `max_size_water`, `loss` to Hunter
   - Add `env.init_farmers`, `env.init_rice_farmers`
   - Add `init_size` to Farmer and RiceFarmer

2. **API Changes**:
   - `Hunter.compete()` method removed
   - `Hunter.loss_in_competition()` method removed
   - `Hunter.moving()` method removed
   - `Hunter.max_size` property calculation logic changed

### Migration Guide

If using old version configuration files, please refer to `config/config.yaml` to update your configuration:

1. Add `convert` configuration section at root level
2. Update Hunter configuration parameters
3. Add initial farmer-related parameters
4. Add `init_size` parameters for each agent type

## Future Plans

The following features were mentioned in this refactoring but not implemented; may be added in future versions:

- [ ] Global hunter population limit (`lim_h * number of non-water cells`)
- [ ] More flexible time-space scale mapping mechanism

## Reference Documentation

- [Configuration Guide](../usage/config.en.md)
- [Workflow](../usage/workflow.en.md)
- [Hunter API](../api/hunter.md)
- [Environment API](../api/env.md)

