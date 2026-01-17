---
title: 农民类 (Farmer)
description: 农民主体类，代表从事农业生产的群体
---

# Farmer 类

`Farmer` 类代表从事农业生产的群体，继承自 `SiteGroup`，具有人口增长、转化、扩散等行为。

## 类定义

```python
class Farmer(SiteGroup):
    """农民"""
```

## 主要属性

### `growth_rate`
- **类型**: `float`
- **描述**: 人口增长率，默认值可在配置文件中调节，也可因复杂化而下降
- **约束**: 不能为负值
- **示例**:
```python
farmer = Farmer()
print(f"当前增长率: {farmer.growth_rate}")
farmer.growth_rate = 0.05  # 设置5%的增长率
```

### `area`
- **类型**: `float`
- **描述**: 耕地面积。复杂化时会增加土地面积
- **计算公式**: `area = 2 * 2 * (1 - 0.1)` (复杂化时)
- **示例**:
```python
farmer = Farmer()
print(f"耕地面积: {farmer.area} km²")
```

### `size`
- **类型**: `int`
- **描述**: 人口规模，自动转换为整数
- **约束**: 必须在 `min_size` 和 `max_size` 之间
- **示例**:
```python
farmer = Farmer(size=50)
print(f"人口规模: {farmer.size}")
```

## 主要方法

### `population_growth()`
执行人口增长。

**行为**:
- 根据 `growth_rate` 计算人口增长
- 增长公式: `size = size * (1 + growth_rate)`

**示例**:
```python
farmer = Farmer(size=100, growth_rate=0.02)
farmer.population_growth()
print(f"增长后人口: {farmer.size}")  # 约102
```

### `convert()`
检查并执行转化行为。

**转化条件**:
1. **转化为 Hunter**: 人口 ≤ 100 且随机触发
2. **转化为 RiceFarmer**: 人口 ≥ 200 且在水稻可耕地

**示例**:
```python
farmer = Farmer(size=80)
farmer.convert()  # 可能转化为 Hunter
```

### `diffuse(diffuse_prob: float = 0.05)`
执行扩散行为。

**参数**:
- `diffuse_prob`: 扩散概率，默认 0.05

**行为**:
- 随机触发扩散
- 创建新的 Farmer 主体
- 保持人口守恒

**示例**:
```python
farmer = Farmer(size=100)
farmer.diffuse(0.1)  # 10% 概率扩散
```

### `loss()`
执行人口损失。

**行为**:
- 随机触发损失
- 损失率: 10%
- 计算公式: `size = size * (1 - 0.1)`

**示例**:
```python
farmer = Farmer(size=100)
farmer.loss()  # 可能减少到90
```

### `complicate()`
执行复杂化过程。

**行为**:
- 降低增长率: `growth_rate *= (1 - 0.1)`
- 增加耕地面积: `area += 2 * (1 - 0.1)`

**示例**:
```python
farmer = Farmer(growth_rate=0.05, area=4.0)
farmer.complicate()
print(f"新增长率: {farmer.growth_rate}")  # 约0.045
print(f"新面积: {farmer.area}")  # 约5.8
```

## 配置参数

### 基础参数
- `min_size`: 最小人口规模 (默认: 6)
- `max_size`: 最大人口规模 (默认: 200)
- `growth_rate`: 人口增长率 (默认: 0.004)
- `area`: 耕地面积 (默认: 4.0)

### 转化参数
- `convert.farmer_to_hunter`: 农民转猎人开关
- `convert.farmer_to_rice`: 农民转水稻农民开关

### 扩散参数
- `diffuse_prob`: 扩散概率 (默认: 0.05)
- `diffuse.min_size`: 扩散最小人口 (默认: 30)
- `diffuse.max_size`: 扩散最大人口 (默认: 60)

## 使用示例

```python
from src import Farmer

# 创建农民实例
farmer = Farmer(
    size=100,
    growth_rate=0.02,
    area=4.0
)

# 模拟一个时间步
farmer.population_growth()  # 人口增长
farmer.convert()           # 检查转化
farmer.diffuse()           # 检查扩散
farmer.loss()              # 检查损失

print(f"最终人口: {farmer.size}")
print(f"最终增长率: {farmer.growth_rate}")
print(f"最终面积: {farmer.area}")
```

## 生命周期

1. **初始化**: 设置初始人口、增长率、面积
2. **人口增长**: 根据增长率增加人口
3. **转化检查**: 根据条件转化为其他类型
4. **扩散**: 随机创建新的农民群体
5. **损失**: 随机减少人口
6. **复杂化**: 当人口超过阈值时触发

## 注意事项

1. 农民只能在可耕地 (`is_arable=True`) 上生存
2. 转化行为受全局转化开关控制
3. 扩散时保持人口守恒
4. 复杂化会降低增长率但增加耕地面积
5. 人口规模会自动转换为整数