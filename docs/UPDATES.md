---
title: 模型更新说明
author: Shuang Song
date: 2025-10-20
---

# 模型更新说明 (v2.0)

## 快速概览

本次更新是模型的重大重构，主要目标是**简化逻辑、增强灵活性、确保准确性**。

### 🎯 核心变更

| 变更类型 | 描述 | 影响 |
|---------|------|------|
| ✅ 初始化优化 | 所有主体类型从开始就存在 | 更符合实际情况 |
| ✅ 转化开关 | 可独立控制6种转化路径 | 便于对比实验 |
| ❌ 删除竞争 | 移除主体间竞争机制 | 逻辑更清晰 |
| ✅ 人口守恒 | 严格保证扩散/合并守恒 | 数值更准确 |
| ✅ Hunter 改进 | 新的人口上限规则 + 损失机制 | 行为更合理 |
| ✅ 每格唯一 | 一个格子只能有一个主体 | 空间规则明确 |

## ⚠️ 重要：必须更新配置文件

如果您之前使用过本模型，**必须更新配置文件**才能运行新版本！

### 必须添加的新配置

```yaml
# 1. 添加转化开关（根级别）
convert:
  enabled: true
  hunter_to_farmer: true
  hunter_to_rice: true
  farmer_to_hunter: true
  farmer_to_rice: true
  rice_to_farmer: true

# 2. 更新 env 配置
env:
  init_farmers: 80  # 新增
  init_rice_farmers: 350  # 新增
  tick_farmer: 0  # 修改为 0
  tick_ricefarmer: 0  # 修改为 0

# 3. 更新 Hunter 配置
Hunter:
  # 删除: intensified_coefficient
  max_size: 100  # 新增
  max_size_water: 500  # 新增
  loss:  # 新增
    prob: 0.05
    rate: 0.1

# 4. 添加初始人口规模
Farmer:
  init_size: [60, 100]  # 新增

RiceFarmer:
  init_size: [300, 400]  # 新增
```

## 📝 配置文件迁移步骤

1. 备份您的旧配置文件
2. 复制 `config/config.yaml` 作为模板
3. 根据上述变更更新您的配置
4. 运行测试确保配置正确

## 🧪 验证

所有修改已通过全面测试：

```bash
# 运行测试套件
poetry run pytest tests/ -v

# 运行模型
poetry run python -m src time.end=20 exp.repeats=1
```

预期结果：
- ✅ 84 个单元测试全部通过
- ✅ 模型正常运行并生成输出
- ✅ 生成转化数据、动态图、热图

## 📚 详细文档

- **变更日志**：[changelog_v2.md](tech/changelog_v2.md) - 详细的变更说明
- **配置说明**：[config.md](usage/config.md) - 完整的参数文档
- **工作流程**：[workflow.md](usage/workflow.md) - 更新的模型流程

## 🔄 主要 API 变更

### 删除的方法

```python
# ❌ 以下方法已删除
Hunter.compete()
Hunter.loss_in_competition()
Hunter.moving()
```

### 修改的方法

```python
# ✅ 现在的实现
Hunter.max_size  # 返回 100 或 500（临近水体）
Hunter.loss()  # 新增损失机制
Hunter.merge()  # 严格人口守恒

SiteGroup.diffuse()  # 严格人口守恒
```

### 新增的方法

```python
# ✅ 新增方法
Hunter.is_near_water()  # 检查是否临近水体
Env.add_initial_farmers()  # 初始化农民
```

## 💡 使用建议

### 对比实验设计

利用新的转化开关功能，您可以轻松设计对比实验：

```yaml
# 实验1：有转化机制
convert:
  enabled: true

# 实验2：无转化机制
convert:
  enabled: false
```

### 参数调整建议

基于测试结果，以下参数组合表现良好：

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

## 🐛 已知问题

目前没有已知的严重问题。如果遇到问题，请：

1. 确认配置文件已正确更新
2. 检查所有测试是否通过
3. 查看日志文件中的错误信息

## 📞 获取帮助

如有问题，请参考：

1. [完整文档](index.md)
2. [配置说明](usage/config.md)
3. [变更日志](tech/changelog_v2.md)

或联系：songshgeo[at]gmail.com

