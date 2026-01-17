---
title: 农民
author: Shuang Song
---

## 农民

:::src.api.farmer.Farmer

## 水稻农民

:::src.api.farmer.RiceFarmer

## 主要特性

### 2.0 版本核心功能
- **初始农民**：支持在环境初始化时添加初始农民
- **通用方法**：使用统一的 `loss()` 和 `search_cell()` 方法
- **空间约束**：严格遵守"每格一主体"规则
- **转换机制**：支持可配置的转换开关

### 农民类型
- **Farmer**：普通农民，在可耕地生存
- **RiceFarmer**：水稻农民，在水稻可耕地生存

### 生存规则
- **Farmer**：坡度<10°，海拔<200m，非水体
- **RiceFarmer**：坡度≤0.5°，海拔<200m，非水体

### 转换机制
- 支持全局转换开关控制
- 支持特定类型转换开关控制
- 可配置转换概率和阈值

## 配置示例

```yaml
# 全局转换控制
convert:
  enabled: true  # 全局开关
  farmer_to_hunter: true
  farmer_to_rice: true
  rice_to_farmer: true

# 农民配置
Farmer:
  growth_rate: 0.004
  min_size: 6
  init_size: [60, 100]
  new_group_size: [30, 60]
  diffuse_prob: 0.05
  convert_prob:
    to_hunter: 0.08
    to_rice: 0.05
  convert_threshold:
    to_hunter: 100
    to_rice: 200
  loss:
    prob: 0.05
    rate: 0.1

# 水稻农民配置
RiceFarmer:
  growth_rate: 0.005
  min_size: 6
  init_size: [300, 400]
  new_group_size: [200, 300]
  diffuse_prob: 0.05
  convert_prob:
    to_farmer: 1
  convert_threshold:
    to_farmer: 200
  loss:
    prob: 0.05
    rate: 0.1
```

## 使用示例

### 基本使用
```python
# 创建农民
farmer = model.agents.new(Farmer, size=50)

# 创建水稻农民
rice_farmer = model.agents.new(RiceFarmer, size=200)

# 检查生存条件
if farmer.at.is_arable:
    print("在可耕地")

if rice_farmer.at.is_rice_arable:
    print("在水稻可耕地")
```

### 转换机制
```python
# 检查转换开关
if model.params.convert.enabled:
    if model.params.convert.farmer_to_rice:
        # 执行转换逻辑
        pass
```
