---
title: 环境类 (Environment)
description: 环境类包含 CompetingCell 和 Env，提供地理空间和主体交互环境
---

# Environment 类

环境系统由 `CompetingCell` 和 `Env` 两个主要类组成，提供地理空间环境和主体交互的舞台。

## CompetingCell 类

`CompetingCell` 代表地理空间中的一个格子，是主体竞争和交互的舞台。

### 类定义

```python
class CompetingCell(PatchCell):
    """狩猎采集者和农民竞争的舞台"""
```

### 主要属性

#### `max_agents`
- **类型**: `int`
- **值**: `1`
- **描述**: 一个格子最多只能有一个主体

#### `lim_h`
- **类型**: `float`
- **描述**: 限制高度，影响主体生存

#### `slope`
- **类型**: `float`
- **描述**: 坡度，影响农业适宜性

#### `elevation`
- **类型**: `float`
- **描述**: 海拔高度

#### `is_water`
- **类型**: `bool`
- **描述**: 是否为水体

#### `is_arable`
- **类型**: `bool`
- **描述**: 是否为可耕地

#### `is_rice_arable`
- **类型**: `bool`
- **描述**: 是否为水稻可耕地

### 主要方法

#### `able_to_live(agent: SiteGroup) -> bool`
检查主体是否能在当前格子生存。

**参数**:
- `agent`: 要检查的主体

**返回值**:
- `bool`: 是否能生存

**规则**:
- Hunter: 不能在水体上生存
- Farmer: 只能在可耕地上生存
- RiceFarmer: 只能在水稻可耕地上生存

**示例**:
```python
cell = CompetingCell()
hunter = Hunter()
farmer = Farmer()

print(cell.able_to_live(hunter))  # True (非水体)
print(cell.able_to_live(farmer))  # 取决于 is_arable
```

#### `convert(agent: SiteGroup, target_type: str) -> SiteGroup`
将主体转化为目标类型。

**参数**:
- `agent`: 要转化的主体
- `target_type`: 目标类型 (`"Hunter"`, `"Farmer"`, `"RiceFarmer"`)

**返回值**:
- `SiteGroup`: 转化后的新主体

**示例**:
```python
cell = CompetingCell()
hunter = Hunter(size=100)

# 将 Hunter 转化为 Farmer
farmer = cell.convert(hunter, "Farmer")
print(f"新农民人口: {farmer.size}")  # 100
```

#### `_count(breed: str) -> int`
统计指定类型主体的数量。

**参数**:
- `breed`: 主体类型

**返回值**:
- `int`: 主体数量

## Env 类

`Env` 类代表整个环境，管理所有格子和主体。

### 类定义

```python
class Env(BaseNature):
    """环境类"""
```

### 主要方法

#### `setup_dem()`
设置数字高程模型。

**行为**:
- 加载 DEM 数据
- 加载 Slope 数据
- 加载 lim_h 数据
- 计算水体、可耕地、水稻可耕地

**示例**:
```python
env = Env()
env.setup_dem()
print(f"总格子数: {len(env.cells)}")
```

#### `add_hunters(ratio: float = 0.05)`
添加初始狩猎采集者。

**参数**:
- `ratio`: 添加比例，默认 5%

**行为**:
- 选择非水体格子
- 创建 Hunter 主体
- 随机设置初始人口 (6-35)

**示例**:
```python
env = Env()
env.add_hunters(0.1)  # 添加10%的初始狩猎采集者
print(f"狩猎采集者数量: {len(env.agents[Hunter])}")
```

#### `add_initial_farmers(farmer_class: type, count: int)`
添加初始农民。

**参数**:
- `farmer_class`: 农民类型 (`Farmer` 或 `RiceFarmer`)
- `count`: 添加数量

**行为**:
- 选择合适的可耕地格子
- 创建农民主体
- 设置初始人口

**示例**:
```python
env = Env()
env.add_initial_farmers(Farmer, 80)      # 添加80个农民
env.add_initial_farmers(RiceFarmer, 350) # 添加350个水稻农民
```

#### `add_farmers(farmer_class: type)`
添加新的农民（运行时）。

**参数**:
- `farmer_class`: 农民类型

**行为**:
- 使用泊松分布创建新农民
- 随机选择可耕地格子

## 配置参数

### 环境参数
- `dem_file`: DEM 数据文件路径
- `slope_file`: 坡度数据文件路径
- `lim_h_file`: 限制高度数据文件路径

### 主体参数
- `init_hunters`: 初始狩猎采集者比例
- `init_farmers`: 初始农民数量
- `init_rice_farmers`: 初始水稻农民数量

### 地理参数
- `water_threshold`: 水体判断阈值
- `arable_threshold`: 可耕地判断阈值
- `rice_arable_threshold`: 水稻可耕地判断阈值

## 使用示例

```python
from src import Env, CompetingCell, Hunter, Farmer, RiceFarmer

# 创建环境
env = Env()

# 设置地理数据
env.setup_dem()

# 添加初始主体
env.add_hunters(0.05)           # 5% 狩猎采集者
env.add_initial_farmers(Farmer, 80)      # 80个农民
env.add_initial_farmers(RiceFarmer, 350) # 350个水稻农民

# 检查环境状态
print(f"总格子数: {len(env.cells)}")
print(f"水体格子数: {sum(cell.is_water for cell in env.cells)}")
print(f"可耕地格子数: {sum(cell.is_arable for cell in env.cells)}")
print(f"水稻可耕地格子数: {sum(cell.is_rice_arable for cell in env.cells)}")

# 检查主体分布
print(f"狩猎采集者数量: {len(env.agents[Hunter])}")
print(f"农民数量: {len(env.agents[Farmer])}")
print(f"水稻农民数量: {len(env.agents[RiceFarmer])}")
```

## 地理空间特性

### 地形影响
- **海拔**: 影响农业适宜性
- **坡度**: 影响耕作难度
- **限制高度**: 影响主体生存

### 土地利用
- **水体**: 不能进行农业生产
- **可耕地**: 适合一般农业
- **水稻可耕地**: 适合水稻种植

### 主体限制
- 每个格子最多一个主体
- 不同类型主体有不同的生存要求
- 主体可以相互转化

## 注意事项

1. 环境初始化时必须先调用 `setup_dem()`
2. 主体添加顺序影响初始分布
3. 地理数据文件必须存在且格式正确
4. 主体转化需要检查目标格子的适宜性
5. 水体格子不能放置任何主体