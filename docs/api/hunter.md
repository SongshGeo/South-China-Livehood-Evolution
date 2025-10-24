---
title: 狩猎采集者
author: Shuang Song
---

## 狩猎采集者

:::src.api.hunter.Hunter

## 主要特性

### 2.0 版本核心功能
- **全局人口上限**：支持全局 Hunter 人口上限控制
- **近水优势**：在近水陆地有更高的人口上限（500 vs 100）
- **无竞争机制**：不再有竞争功能，简化移动逻辑
- **通用方法**：使用统一的 `loss()` 和 `search_cell()` 方法

### 人口上限规则
- **普通陆地**：最大人口 100
- **近水陆地**：最大人口 500
- **全局上限**：总人口不超过 `lim_h * 非水体栅格数量`

### 移动规则
- **复杂主体**：人口超过 `is_complex` 阈值后不再移动
- **简单主体**：可以移动和搜索新位置
- **空间约束**：严格遵守"每格一主体"规则

### 损失机制
- 支持配置驱动的损失参数
- 每个时间步按概率减少人口
- 与全局人口上限控制协同工作

## 配置示例

```yaml
Hunter:
  init_size: [0, 35]  # 初始人口范围
  growth_rate: 0.0008  # 人口增长率
  min_size: 6  # 最小人口数
  max_size: 100  # 普通陆地最大人口
  max_size_water: 500  # 近水陆地最大人口
  is_complex: 100  # 复杂化阈值
  max_travel_distance: 5  # 最大移动距离
  loss:
    prob: 0.05  # 损失概率
    rate: 0.1   # 损失率
```

## 使用示例

### 基本使用
```python
# 创建 Hunter
hunter = model.agents.new(Hunter, size=20)

# 检查是否复杂
if hunter.is_complex:
    print("复杂主体，不再移动")

# 检查近水优势
if hunter.is_near_water:
    print("在近水陆地，人口上限更高")

# 移动
hunter.move_one()
```

### 全局人口控制
```python
# 环境会自动应用全局人口上限
env.apply_global_hunter_limit()
```
