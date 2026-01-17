---
title: 模型重构变更日志 (v2.0)
author: Shuang Song
date: 2025-10-20
---

# 模型重构变更日志 (v2.0)

本文档记录了模型在 2025年10月20日 进行的大幅度逻辑修改。

## 主要变更概述

本次重构主要目标是简化模型逻辑，增强模型的灵活性和可控性，具体包括：

1. ✅ 增加初始农民数量设置
2. ✅ 弱化 tick 与真实时间的对应关系
3. ✅ 确保扩散机制的人口守恒
4. ✅ 添加转化机制开关
5. ✅ 修改狩猎采集者人口上限规则
6. ✅ 调整狩猎采集者单位主体人口限制
7. ✅ 删除竞争功能
8. ✅ 为狩猎采集者添加损失机制

## 详细变更说明

### 1. 初始化机制变更

#### 变更前
- 仅初始化狩猎采集者
- 农民和水稻农民在运行过程中根据泊松分布动态添加

#### 变更后
- **初始化时同时创建所有三类主体**
- 新增配置参数：
  - `env.init_farmers`: 初始普通农民数量（默认 80，推荐范围 60-100）
  - `env.init_rice_farmers`: 初始水稻农民数量（默认 350，推荐范围 300-400）
- 每类主体的初始人口规模由各自的 `init_size` 参数控制
- `tick_farmer` 和 `tick_ricefarmer` 设为 0（从第一步就开始运行）

**影响**：模型启动时就有完整的三类主体，更符合实际情况

### 2. 转化机制开关

#### 新增功能
添加了灵活的转化机制控制系统，可以独立控制不同类型的转化。

#### 配置示例
```yaml
convert:
  enabled: true  # 全局开关
  hunter_to_farmer: true  # 狩猎采集者 → 农民
  hunter_to_rice: true  # 狩猎采集者 → 水稻农民
  farmer_to_hunter: true  # 农民 → 狩猎采集者
  farmer_to_rice: true  # 农民 → 水稻农民
  rice_to_farmer: true  # 水稻农民 → 农民
```

**用途**：
- 可以通过设置 `enabled: false` 关闭所有转化
- 可以单独控制每种转化路径
- 便于对比有/无转化机制的模型行为差异

### 3. 狩猎采集者 (Hunter) 重大调整

#### 3.1 人口上限规则变更

**变更前**：
- 每个狩猎采集者的最大人口由所在格子的 `lim_h` (环境承载力) 决定

**变更后**：
- 普通情况：`max_size = 100`
- 临近水体：`max_size_water = 500`（water_type = 1 的格子）
- **全局人口上限**：`lim_h × 非水体栅格数量`（所有 Hunter 总人口不能超过此值）
- 不再受单个格子承载力限制
- **水体数据**：使用 `water_type`（-1=海，0=陆地，1=近水陆地）替代 `lim_h` 栅格异质性

**配置参数**：
```yaml
Hunter:
  max_size: 100  # 单位主体人口最大值
  max_size_water: 500  # 临近水体时的最大值
```

**注意**：超过 `is_complex` (默认100) 阈值的狩猎采集者仍不再移动

#### 3.2 删除竞争机制

**移除的功能**：
- `moving()` 方法 - 不再处理与其他主体的竞争
- `compete()` 方法 - 删除所有竞争逻辑
- `loss_in_competition()` 方法 - 删除竞争失败的处理
- `intensified_coefficient` 参数 - 删除竞争系数

**影响**：
- 不同主体不能再占据同一格子（每格唯一主体规则）
- 狩猎采集者遇到其他 Hunter 时仍会合并
- 移动逻辑更简单清晰
- **`search_cell()` 函数简化**：不再使用适宜度加权选择，改为简单随机选择

#### 3.3 新增损失机制

**新增功能**：
狩猎采集者现在也会像农民一样经历随机损失（如疾病、灾害等）

**配置参数**：
```yaml
Hunter:
  loss:
    prob: 0.05  # 损失发生概率
    rate: 0.1   # 损失时人口减少比率
```

**实现**：每个时间步，有 `prob` 概率发生损失，损失时人口减少 `rate` 比例

#### 3.4 合并机制改进

**变更前**：
```python
size = max(other_hunter.size + self.size, lim_h)
```

**变更后**：
```python
size = other_hunter.size + self.size  # 严格人口守恒
```

**影响**：合并后的总人口 = 两个群体人口之和，确保人口守恒

### 4. 每格唯一主体规则

#### 新规则
- **一个格子只能有一个主体**（任何类型）
- 主体移动或扩散时会检查目标格子是否已有其他主体
- 已有主体的格子不能作为移动或扩散的目标

#### 实现位置
`CompetingCell.able_to_live()` 方法中添加了检查逻辑

#### 例外情况
- 狩猎采集者之间仍可合并（移动到有其他 Hunter 的格子会触发合并）
- 主体检查自己当前位置时不受此限制

### 5. 人口守恒保证

#### 扩散机制改进 (`SiteGroup.diffuse()`)

**变更前**：
先创建新主体，再减少原主体人口，可能导致人口总数不守恒

**变更后**：
```python
# 1. 先减少原主体人口
self.size -= new_group_size
# 2. 如果原主体还活着，创建新主体
if self.alive:
    new = create_new_agent(size=new_group_size)
```

**保证**：扩散前后总人口数严格相等（原主体人口 = 原主体减少后 + 新主体）

### 6. 配置文件新增参数

#### Farmer 配置
```yaml
Farmer:
  init_size: [60, 100]  # 初始人口规模范围
```

#### RiceFarmer 配置
```yaml
RiceFarmer:
  init_size: [300, 400]  # 初始人口规模范围
```

## 测试验证

所有修改已通过完整的测试套件验证：

- ✅ 84 个单元测试全部通过
- ✅ 单次运行测试正常
- ✅ 多次重复运行测试正常
- ✅ 并行处理正常工作
- ✅ 输出文件（转化数据、动态图、热图）正常生成

## 向后兼容性

### 不兼容变更

1. **配置文件必须更新**：
   - 添加 `convert` 部分
   - Hunter 中删除 `intensified_coefficient`
   - Hunter 中添加 `max_size`, `max_size_water`, `loss`
   - 添加 `env.init_farmers`, `env.init_rice_farmers`
   - Farmer 和 RiceFarmer 添加 `init_size`

2. **API 变更**：
   - `Hunter.compete()` 方法已删除
   - `Hunter.loss_in_competition()` 方法已删除
   - `Hunter.moving()` 方法已删除
   - `Hunter.max_size` 属性计算逻辑改变

### 迁移指南

如果您使用旧版本的配置文件，请参考 `config/config.yaml` 更新您的配置：

1. 在根级别添加 `convert` 配置部分
2. 更新 Hunter 配置参数
3. 添加初始农民相关参数
4. 添加各主体的 `init_size` 参数

## 未来计划

以下功能在本次重构中被提及但未实现，可能在未来版本中添加：

- [ ] 全局狩猎采集者人口上限（`lim_h * 非水体栅格数`）
- [ ] 更灵活的时间-空间尺度映射机制

## 参考文档

- [配置文件说明](../usage/config.md)
- [工作流程](../usage/workflow.md)
- [Hunter API](../api/hunter.md)
- [Environment API](../api/env.md)

