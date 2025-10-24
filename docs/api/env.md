---
title: 狩猎采集者与农民的交互环境
author: Shuang Song
---

环境包括了两个类，即[斑块（CompetingCell）](#斑块)和[环境（Env）](#环境)。环境会自动根据输入的栅格文件创建足够数量的斑块，每一个斑块是主体具体所在的位置。

## 主要特性

### 2.0 版本核心规则
- **每格一主体**：每个格子只能有一个主体，严格遵守空间约束
- **水体类型系统**：支持 -1（海）、0（陆地）、1（近水陆地）三种水体类型
- **全局人口上限**：Hunter 人口有全局上限控制机制
- **无竞争机制**：主体不能移动到已有其他主体的格子

### 水体类型定义
- `water_type = -1`：海（`is_water = True`，所有主体都不能到达）
- `water_type = 0`：陆地（`is_water = False`，`is_near_water = False`）
- `water_type = 1`：近水陆地（`is_water = False`，`is_near_water = True`）

### 主体生存规则
- **Hunter**：可以到陆地和近水陆地，在近水陆地有更高人口上限
- **Farmer**：只能在可耕地生存（坡度<10°，海拔<200m，非水体）
- **RiceFarmer**：只能在水稻可耕地生存（坡度≤0.5°，海拔<200m，非水体）

## 斑块

:::src.api.env.CompetingCell

## 环境

:::src.api.env.Env
