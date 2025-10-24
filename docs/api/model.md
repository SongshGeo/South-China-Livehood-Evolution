---
title: 模型工作流
author: Shuang Song
---

## 模型

:::src.core.model.Model

## 主要特性

### 2.0 版本核心功能
- **全局人口上限控制**：在每个时间步结束时自动应用 Hunter 人口上限
- **断点检测**：支持自动检测人口发展中的拐点
- **数据收集**：自动收集模型运行数据
- **可视化**：支持动态图和热图生成

### 工作流程
1. **环境更新**：`nature.step()`
2. **主体行为**：所有主体执行 `step()` 方法
3. **全局控制**：应用全局 Hunter 人口上限
4. **数据收集**：收集当前时间步的数据

### 断点检测
- 支持多种检测依据：`size`、`ratio`、`group`、`group_ratio`
- 自动计算断点前后的增长率
- 支持断点前后的数据分析

## 配置示例

```yaml
model:
  save_plots: True  # 保存绘图
  n_bkps: 1  # 断点数量
  detect_bkp_by: 'size'  # 断点检测依据

reports:
  model:
    num_farmers: "farmers size ratio"
    num_hunters: "hunters size ratio"
    num_rice: "rice size ratio"
  final:
    bkp_farmer: "bkp_farmers"
    pre_farmer: "pre_farmers"
    post_farmer: "post_farmers"
```

## 使用示例

### 基本使用
```python
# 创建模型
model = Model()

# 运行模型
model.run()

# 获取断点信息
bkp = model.detect_breakpoints("farmers")

# 获取增长率
pre_rate, post_rate = model.calc_rate("farmers")
```

### 数据分析
```python
# 获取数据
data = model.datacollector.get_model_vars_dataframe()

# 绘制图表
model.plot.dynamic()  # 动态图
model.plot.heatmap()  # 热图
```
