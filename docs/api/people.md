---
title: 主体基类
author: Shuang Song
---

## 主体基类

:::src.api.people.SiteGroup

## 主要特性

### 2.0 版本通用方法
- **通用 `loss()` 方法**：所有主体类型都可以使用统一的损失机制
- **通用 `search_cell()` 方法**：所有主体类型都可以使用统一的格子搜索逻辑
- **配置驱动**：通过 `params.loss` 配置参数控制损失行为

### 损失机制
```yaml
# 配置示例
loss:
  prob: 0.05  # 损失概率
  rate: 0.1   # 损失率
```

### 搜索机制
- 支持递归搜索，逐步扩大搜索范围
- 最大搜索距离由 `max_travel_distance` 参数控制
- 严格遵守"每格一主体"规则

### 扩散机制
- 先检查是否有可用格子，再创建新主体
- 如果没有可用格子，扩散不会发生
- 确保人口守恒和空间约束

## 使用示例

### 基本使用
```python
# 创建主体
hunter = model.agents.new(Hunter, size=20)

# 搜索可用格子
new_cell = hunter.search_cell(radius=2)

# 移动
if new_cell:
    hunter.move.to(new_cell)

# 扩散
new_hunter = hunter.diffuse([10, 20])
```

### 配置驱动
```python
# 通过配置文件控制损失
hunter.params.loss = {"prob": 0.05, "rate": 0.1}
```
