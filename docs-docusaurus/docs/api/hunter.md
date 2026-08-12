---
title: 狩猎采集者类 (Hunter)
description: 狩猎采集者主体类，代表从事狩猎采集活动的群体
---

# Hunter 类

`Hunter` 类代表从事狩猎采集活动的群体，继承自 `SiteGroup`，具有移动、转化、扩散等行为。

## 类定义

```python
class Hunter(SiteGroup):
    """狩猎采集者"""
```

## 主要属性

### `max_size`
- **类型**: `int`
- **描述**: 单位主体人口最大值
- **规则**:
  - 普通情况: 100
  - 临近水体: 500
- **示例**:
```python
hunter = Hunter()
print(f"最大人口: {hunter.max_size}")

# 移动到水体附近
hunter.move_to_water_area()
print(f"水体附近最大人口: {hunter.max_size}")  # 500
```

### `is_complex`
- **类型**: `bool`
- **描述**: 是否为复杂狩猎采集者
- **判断条件**: 人口超过定居规模阈值
- **示例**:
```python
hunter = Hunter(size=150)
print(f"是否为复杂狩猎采集者: {hunter.is_complex}")  # True
```

### `is_near_water()`
- **类型**: `bool`
- **描述**: 检查是否临近水体
- **判断条件**: 相邻格子（包括对角线）有水体
- **示例**:
```python
hunter = Hunter()
if hunter.is_near_water():
    print("临近水体，最大人口可达500")
else:
    print("普通区域，最大人口为100")
```

## 主要方法

### `population_growth()`
执行人口增长。

**行为**:
- 根据固定增长率计算人口增长
- 增长公式: `size = size * (1 + 0.0008)`

**示例**:
```python
hunter = Hunter(size=100)
hunter.population_growth()
print(f"增长后人口: {hunter.size}")  # 约100.08
```

### `convert()`
检查并执行转化行为。

**转化条件**:
1. **转化为 Farmer**: 周围有农民 + 当前可耕地 + 随机触发
2. **转化为 RiceFarmer**: 周围有水稻农民 + 水稻可耕地 + 随机触发

**示例**:
```python
hunter = Hunter(size=80)
hunter.convert()  # 可能转化为 Farmer 或 RiceFarmer
```

### `diffuse()`
执行扩散行为。

**触发条件**: 人口 >= `max_size`

**行为**:
- 自动触发扩散
- 创建新的 Hunter 主体
- 保持人口守恒

**示例**:
```python
hunter = Hunter(size=120)  # 超过普通最大人口
hunter.diffuse()  # 自动扩散
```

### `loss()`
执行人口损失。

**行为**:
- 随机触发损失 (概率: 5%)
- 损失率: 10%
- 计算公式: `size = size * (1 - 0.1)`

**示例**:
```python
hunter = Hunter(size=100)
hunter.loss()  # 5% 概率减少到90
```

### `move_one()`
执行移动行为。

**移动条件**: 非定居型 (人口 ≤ 100)

**行为**:
- 搜索周围更好的格子
- 移动到合适的非水体格子（每格最多一个主体，已占据的格子会被拒绝）

**示例**:
```python
hunter = Hunter(size=80)  # 非定居型
hunter.move_one()  # 尝试移动到更好的位置
```

## 配置参数

### 基础参数
- `min_size`: 最小人口规模 (默认: 6)
- `max_size`: 最大人口规模 (默认: 100)
- `max_size_water`: 水体附近最大人口 (默认: 500)
- `growth_rate`: 人口增长率 (默认: 0.0008)

### 转化参数
- `convert.hunter_to_farmer`: 猎人转农民开关
- `convert.hunter_to_rice`: 猎人转水稻农民开关

### 移动参数
- `max_travel_distance`: 最大移动距离
- `search_radius`: 搜索半径

## 使用示例

```python
from src import Hunter

# 创建狩猎采集者实例
hunter = Hunter(
    size=80,
    growth_rate=0.0008
)

# 模拟一个时间步
hunter.population_growth()  # 人口增长
hunter.convert()           # 检查转化
hunter.diffuse()           # 检查扩散
hunter.loss()              # 检查损失
hunter.move_one()          # 移动

print(f"最终人口: {hunter.size}")
print(f"是否复杂: {hunter.is_complex}")
print(f"是否临近水体: {hunter.is_near_water()}")
```

## 生命周期

1. **初始化**: 设置初始人口和位置
2. **人口增长**: 根据固定增长率增加人口
3. **转化检查**: 根据环境条件转化为其他类型
4. **扩散**: 当人口超过阈值时自动扩散
5. **损失**: 随机减少人口
6. **移动**: 非定居型会尝试移动到更好的位置

## 特殊行为

### 水体效应
- 临近水体的 Hunter 最大人口可达 500
- 水体提供更丰富的资源

### 复杂化
- 人口超过阈值时成为复杂狩猎采集者
- 复杂化影响移动和扩散行为

## 2.0 版本规则要点

### 人口上限规则
- **普通陆地**：最大人口 100
- **近水陆地**：最大人口 500
- **全局上限**：所有 Hunter 总人口不超过 `lim_h * 非水体栅格数量`，由环境在每个时间步结束时统一施加

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

全局人口上限由环境自动应用：

```python
env.apply_global_hunter_limit()
```

## 注意事项

1. Hunter 不能在水体 (`is_water=True`) 上生存
2. 转化行为受全局转化开关控制
3. 扩散时人口基本守恒，但母体残余低于 `min_size` 时会随母体一起消失
4. 移动只对非定居型有效
5. 模型不含合并机制：每格最多一个主体，两个 Hunter 不会同处一格
6. 水体附近的最大人口限制更高