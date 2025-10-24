---
title: 模型类 (Model)
description: 华南生计演变模型的主要类，负责协调整个模拟过程
---

# Model 类

`Model` 类是华南生计演变模型的核心，继承自 `abses.MainModel`，负责协调整个模拟过程。

## 类定义

```python
class Model(MainModel):
    """运行的模型"""
```

## 主要属性

### `grid`
- **类型**: `PatchCell`
- **描述**: 数字高程模型，提供地形信息
- **示例**:
```python
model = Model()
elevation = model.grid.elevation
```

### `farmers`
- **类型**: `ActorsList[Farmer]`
- **描述**: 农民主体列表
- **示例**:
```python
farmers = model.farmers
print(f"农民数量: {len(farmers)}")
```

### `hunters`
- **类型**: `ActorsList[Hunter]`
- **描述**: 狩猎采集者主体列表
- **示例**:
```python
hunters = model.hunters
print(f"狩猎采集者数量: {len(hunters)}")
```

### `rice`
- **类型**: `ActorsList[RiceFarmer]`
- **描述**: 水稻农民主体列表
- **示例**:
```python
rice_farmers = model.rice
print(f"水稻农民数量: {len(rice_farmers)}")
```

## 主要方法

### `get_data_col(actor: ActorType) -> pd.Series`
获取指定主体的数据列。

**参数**:
- `actor` (str): 主体类型，可选值: `"farmers"`, `"hunters"`, `"rice"`

**返回值**:
- `pd.Series`: 包含主体数据的 pandas Series

**示例**:
```python
# 获取农民的人口数据
farmer_data = model.get_data_col("farmers")
print(farmer_data.head())
```

### `detect_breakpoints(actor: ActorType) -> int`
检测指定主体的断点。

**参数**:
- `actor` (str): 主体类型

**返回值**:
- `int`: 断点位置

**示例**:
```python
# 检测农民的断点
breakpoint = model.detect_breakpoints("farmers")
print(f"农民断点位置: {breakpoint}")
```

## 动态属性

模型支持通过属性名动态计算各种统计指标：

### 计数属性
- `farmers size num`: 农民总人口数
- `hunters size num`: 狩猎采集者总人口数
- `rice size num`: 水稻农民总人口数
- `farmers group num`: 农民群体数量
- `hunters group num`: 狩猎采集者群体数量
- `rice group num`: 水稻农民群体数量

### 比例属性
- `farmers size ratio`: 农民人口比例
- `hunters size ratio`: 狩猎采集者人口比例
- `rice size ratio`: 水稻农民人口比例
- `farmers group ratio`: 农民群体比例
- `hunters group ratio`: 狩猎采集者群体比例
- `rice group ratio`: 水稻农民群体比例

### 断点相关属性
- `bkp_farmers`: 农民断点位置
- `bkp_hunters`: 狩猎采集者断点位置
- `bkp_rice`: 水稻农民断点位置
- `pre_farmers`: 农民断点前增长率
- `post_farmers`: 农民断点后增长率

## 使用示例

```python
from src import Model

# 创建模型实例
model = Model()

# 运行模拟
for step in range(100):
    model.step()

# 获取统计信息
print(f"农民总人口: {model.farmers_size_num}")
print(f"狩猎采集者总人口: {model.hunters_size_num}")
print(f"农民断点: {model.bkp_farmers}")

# 获取详细数据
farmer_data = model.get_data_col("farmers")
print(farmer_data.describe())
```

## 配置参数

模型支持以下配置参数：

- `detect_bkp_by`: 断点检测依据 (`"size"`, `"ratio"`, `"group"`, `"group_ratio"`)
- `min_size`: 主体最小人口规模
- `max_size`: 主体最大人口规模
- `growth_rate`: 人口增长率
- `area`: 耕地面积

## 注意事项

1. 模型继承自 `abses.MainModel`，具有所有基础模型功能
2. 动态属性通过 `__getattr__` 方法实现，支持灵活的统计计算
3. 断点检测使用 `@lru_cache` 装饰器缓存结果，提高性能
4. 所有统计计算都基于 `datacollector` 收集的数据