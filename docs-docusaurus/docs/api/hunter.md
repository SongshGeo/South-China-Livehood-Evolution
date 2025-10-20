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
- 可能与其他 Hunter 合并
- 移动到合适的非水体格子

**示例**:
```python
hunter = Hunter(size=80)  # 非定居型
hunter.move_one()  # 尝试移动到更好的位置
```

### `merge(other_hunter: Hunter)`
与其他 Hunter 合并。

**参数**:
- `other_hunter`: 要合并的另一个 Hunter

**行为**:
- 人口守恒: `size = self.size + other_hunter.size`
- 当前 Hunter 死亡
- 其他 Hunter 获得合并后的人口

**示例**:
```python
hunter1 = Hunter(size=50)
hunter2 = Hunter(size=30)
hunter1.merge(hunter2)
# hunter1 死亡，hunter2 的人口变为 80
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
7. **合并**: 可能与其他 Hunter 合并

## 特殊行为

### 水体效应
- 临近水体的 Hunter 最大人口可达 500
- 水体提供更丰富的资源

### 复杂化
- 人口超过阈值时成为复杂狩猎采集者
- 复杂化影响移动和扩散行为

### 合并机制
- 移动时可能遇到其他 Hunter
- 自动合并，保持人口守恒

## 注意事项

1. Hunter 不能在水体 (`is_water=True`) 上生存
2. 转化行为受全局转化开关控制
3. 扩散时保持人口守恒
4. 移动只对非定居型有效
5. 合并时当前主体会死亡
6. 水体附近的最大人口限制更高