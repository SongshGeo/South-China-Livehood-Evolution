# Model Updates (v2.0)

## Quick Overview

This update is a major refactoring of the model, focusing on **simplifying logic, enhancing flexibility, and ensuring accuracy**.

### 🎯 Core Changes

| Change Type | Description | Impact |
|------------|-------------|--------|
| ✅ Initialization | All agent types present from start | More realistic |
| ✅ Conversion Switches | Independent control of 6 conversion paths | Easier comparative experiments |
| ❌ Remove Competition | Removed inter-agent competition | Clearer logic |
| ✅ Population Conservation | Strict conservation in diffusion/merger | More accurate |
| ✅ Hunter Improvements | New population limits + loss mechanism | More reasonable behavior |
| ✅ One Agent Per Cell | Only one agent allowed per cell | Clear spatial rules |

## ⚠️ Important: Configuration File Must Be Updated

If you've used this model before, **you MUST update your configuration file** to run the new version!

### Required New Configurations

```yaml
# 1. Add conversion switches (root level)
convert:
  enabled: true
  hunter_to_farmer: true
  hunter_to_rice: true
  farmer_to_hunter: true
  farmer_to_rice: true
  rice_to_farmer: true

# 2. Update env configuration
env:
  init_farmers: 80  # NEW
  init_rice_farmers: 350  # NEW
  tick_farmer: 0  # Changed to 0
  tick_ricefarmer: 0  # Changed to 0

# 3. Update Hunter configuration
Hunter:
  # DELETE: intensified_coefficient
  max_size: 100  # NEW
  max_size_water: 500  # NEW
  loss:  # NEW
    prob: 0.05
    rate: 0.1

# 4. Add initial population sizes
Farmer:
  init_size: [60, 100]  # NEW

RiceFarmer:
  init_size: [300, 400]  # NEW
```

## 📝 Configuration Migration Steps

1. Backup your old configuration file
2. Copy `config/config.yaml` as a template
3. Update your configuration based on changes above
4. Run tests to ensure configuration is correct

## 🧪 Verification

All changes have been thoroughly tested:

```bash
# Run test suite
uv run pytest tests/ -v

# Run model
uv run python -m src time.end=20 exp.repeats=1
```

Expected results:
- ✅ All 84 unit tests pass
- ✅ Model runs normally and generates output
- ✅ Generates conversion data, dynamic charts, heatmaps

## 📚 Detailed Documentation

- **Changelog**: [changelog_v2.md](tech/changelog_v2.md) - Detailed change descriptions
- **Configuration**: [config.md](usage/config.md) - Complete parameter documentation
- **Workflow**: [workflow.md](usage/workflow.md) - Updated model process

## 🔄 Major API Changes

### Removed Methods

```python
# ❌ The following methods have been removed
Hunter.compete()
Hunter.loss_in_competition()
Hunter.moving()
```

### Modified Methods

```python
# ✅ Current implementation
Hunter.max_size  # Returns 100 or 500 (near water)
Hunter.loss()  # New loss mechanism
Hunter.merge()  # Strict population conservation

SiteGroup.diffuse()  # Strict population conservation
```

### New Methods

```python
# ✅ New methods
Hunter.is_near_water()  # Check if near water body
Env.add_initial_farmers()  # Initialize farmers
```

## 💡 Usage Suggestions

### Comparative Experiment Design

Use the new conversion switch feature for easy comparative experiments:

```yaml
# Experiment 1: With conversion
convert:
  enabled: true

# Experiment 2: Without conversion
convert:
  enabled: false
```

### Recommended Parameters

Based on test results, the following parameter combination works well:

```yaml
env:
  init_hunters: 0.05
  init_farmers: 80
  init_rice_farmers: 350

Hunter:
  max_size: 100
  max_size_water: 500
  loss:
    prob: 0.05
    rate: 0.1
```

## 🐛 Known Issues

Currently, no critical issues are known. If you encounter problems:

1. Ensure configuration file is correctly updated
2. Check all tests pass
3. Review log files for error messages

## 📞 Getting Help

If you have questions, please refer to:

1. [Complete Documentation](intro.md)
2. [Configuration Guide](usage/config.md)
3. [Changelog](tech/changelog_v2.md)

Or contact: songshgeo[at]gmail.com

