---
title: 模型时序图
author: Shuang Song
date: 2025-10-20
---

# 模型详细时序图

本文档通过时序图详细说明华南生计演变模型的运行流程。

## 完整运行时序

```mermaid
sequenceDiagram
    participant User as 用户
    participant Exp as MyExperiment
    participant Model as Model
    participant Env as Environment
    participant H as Hunter
    participant F as Farmer
    participant RF as RiceFarmer
    participant Cell as CompetingCell

    Note over User,Cell: 初始化阶段

    User->>Exp: 运行实验 (batch_run)
    Exp->>Model: 创建模型实例
    Model->>Env: initialize()

    Note over Env,Cell: 环境初始化
    Env->>Env: setup_dem()
    Env->>Cell: 加载 DEM 数据
    Env->>Cell: 加载 Slope 数据
    Env->>Cell: 加载 lim_h 数据

    Note over Env,H: 添加初始 Hunters
    Env->>Env: add_hunters(0.05)
    Env->>Cell: 选择非水体格子
    Env->>H: 创建 Hunter (init_size: 6-35)
    H->>Cell: 移动到格子

    Note over Env,F: 添加初始 Farmers (新增)
    Env->>Env: add_initial_farmers(80)
    Env->>Cell: 选择可耕地
    Env->>F: 创建 Farmer (init_size: 60-100)
    F->>Cell: 移动到格子

    Note over Env,RF: 添加初始 RiceFarmers (新增)
    Env->>Env: add_initial_farmers(350)
    Env->>Cell: 选择水稻可耕地
    Env->>RF: 创建 RiceFarmer (init_size: 300-400)
    RF->>Cell: 移动到格子

    Note over User,Cell: 运行阶段 (每个 Tick)

    loop 每个时间步 (tick)
        Model->>Env: env.step()

        Note over Env,F: 环境步骤：添加新主体
        Env->>Env: add_farmers(Farmer)
        Env->>F: 泊松分布创建新 Farmers
        Env->>Env: add_farmers(RiceFarmer)
        Env->>RF: 泊松分布创建新 RiceFarmers

        Note over Model,RF: 主体步骤：随机执行
        Model->>Model: agents.shuffle_do("step")

        alt 选中 Hunter
            Model->>H: step()
            H->>H: population_growth()
            H->>H: convert() [检查转化开关]
            opt 转化开关开启 & 满足条件
                H->>Cell: convert(to="Farmer")
                Cell->>Cell: 检查 convert.hunter_to_farmer
                Cell->>F: 创建新 Farmer
                Cell->>H: 死亡
            end
            H->>H: diffuse()
            opt 人口 >= max_size
                H->>H: 创建新 Hunter
                H->>Cell: 搜索合适格子
                Cell-->>H: 返回目标格子
            end
            H->>H: loss() [新增]
            opt 随机损失触发
                H->>H: size *= (1 - loss.rate)
            end
            H->>H: move_one()
            opt 不是定居型 (size <= 100)
                H->>Cell: 搜索更好的格子
                opt 遇到另一个 Hunter
                    H->>H: merge(other_hunter)
                    Note over H: 人口守恒：size = size1 + size2
                end
            end
        else 选中 Farmer
            Model->>F: step()
            F->>F: population_growth()
            F->>F: convert() [检查转化开关]
            opt 转化开关开启 & 满足条件
                alt 人口 <= 100 & 随机
                    F->>Cell: convert(to="Hunter")
                    Cell->>H: 创建新 Hunter
                else 人口 >= 200 & 在水稻地
                    F->>Cell: convert(to="RiceFarmer")
                    Cell->>RF: 创建新 RiceFarmer
                end
            end
            F->>F: diffuse()
            opt 随机扩散触发
                F->>F: 创建新 Farmer
                Note over F: 人口守恒：原主体先减人口
                F->>Cell: 搜索可耕地
            end
            F->>F: loss()
            opt 随机损失触发
                F->>F: size *= (1 - loss.rate)
            end
        else 选中 RiceFarmer
            Model->>RF: step()
            RF->>RF: population_growth()
            RF->>RF: convert() [检查转化开关]
            opt 人口 < 200 & 随机
                RF->>Cell: convert(to="Farmer")
                Cell->>F: 创建新 Farmer
            end
            RF->>RF: diffuse()
            RF->>RF: loss()
        end

        Note over Model: 检查死亡条件
        alt 主体人口 < min_size
            Model->>H: die()
            Model->>F: die()
            Model->>RF: die()
        end

        Model->>Model: datacollector.collect()
    end

    Note over User,Cell: 结束阶段

    Model->>Model: end()
    Model->>Model: plot.dynamic()
    Model->>Model: plot.heatmap()
    Model->>Model: export_conversion_data()
    Model-->>Exp: 返回结果
    Exp-->>User: 保存结果文件
```

## 初始化详细流程

```mermaid
sequenceDiagram
    participant Model
    participant Env
    participant DEM as DEM Layer
    participant Cell as CompetingCells
    participant H as Hunters
    participant F as Farmers
    participant RF as RiceFarmers

    Model->>Env: initialize()

    Note over Env,Cell: 1. 设置地形
    Env->>Env: setup_dem()
    Env->>DEM: create_module(dem_file)
    DEM->>Cell: 创建 CompetingCell 数组
    loop 每个格子
        Cell->>Cell: 设置 elevation
        Cell->>Cell: 设置 slope
        Cell->>Cell: 设置 lim_h
        Cell->>Cell: 计算 is_water
        Cell->>Cell: 计算 is_arable
        Cell->>Cell: 计算 is_rice_arable
    end

    Note over Env,H: 2. 添加初始狩猎采集者
    Env->>Env: add_hunters(ratio=0.05)
    Env->>Cell: 选择非水体格子
    Cell-->>Env: 返回可用格子列表
    Env->>Env: 计算数量 (5% 或固定数)
    loop 每个初始 Hunter
        Env->>H: 创建 Hunter
        H->>H: random_size(0, 35)
        H->>Cell: 移动到格子
        Cell->>Cell: agents.add(hunter)
    end

    Note over Env,F: 3. 添加初始农民 (v2.0 新增)
    Env->>Env: add_initial_farmers(Farmer, 80)
    Env->>Cell: 选择可耕地 & 无主体的格子
    Cell-->>Env: 返回可用格子列表
    loop 每个初始 Farmer
        Env->>F: 创建 Farmer
        F->>F: random_size(60, 100)
        F->>Cell: 移动到格子
        Cell->>Cell: 检查 able_to_live()
        Cell->>Cell: agents.add(farmer)
    end

    Note over Env,RF: 4. 添加初始水稻农民 (v2.0 新增)
    Env->>Env: add_initial_farmers(RiceFarmer, 350)
    Env->>Cell: 选择水稻可耕地 & 无主体的格子
    Cell-->>Env: 返回可用格子列表
    loop 每个初始 RiceFarmer
        Env->>RF: 创建 RiceFarmer
        RF->>RF: random_size(300, 400)
        RF->>Cell: 移动到格子
        Cell->>Cell: 检查 able_to_live()
        Cell->>Cell: agents.add(rice_farmer)
    end

    Env-->>Model: 初始化完成
```

## Hunter 行为详细流程

```mermaid
sequenceDiagram
    participant Model
    participant H as Hunter
    participant Cell as Current Cell
    participant NewCell as Target Cell
    participant Other as Other Hunter

    Model->>H: step()

    Note over H: 1. 人口增长
    H->>H: population_growth(rate=0.0008)
    H->>H: size = size * (1 + growth_rate)

    Note over H,Cell: 2. 转化检查 (v2.0: 可关闭)
    H->>H: convert()

    alt 转化开关开启
        H->>H: _convert_to_farmer()
        opt 周围有 Farmer & 当前可耕地 & 随机
            H->>Cell: 检查 convert.hunter_to_farmer
            alt 开关开启
                Cell->>Cell: convert(hunter, "Farmer")
                Cell->>Model: 创建 Farmer(size=hunter.size)
                Cell->>H: die()
            end
        end

        opt 未转化为 Farmer
            H->>H: _convert_to_rice()
            opt 周围有 RiceFarmer & 水稻地 & 随机
                H->>Cell: 检查 convert.hunter_to_rice
                alt 开关开启
                    Cell->>Cell: convert(hunter, "RiceFarmer")
                    Cell->>Model: 创建 RiceFarmer(size=hunter.size)
                    Cell->>H: die()
                end
            end
        end
    end

    Note over H: 3. 扩散 (人口守恒)
    H->>H: diffuse()

    alt 人口 >= max_size
        H->>H: 计算 max_size
        alt 临近水体
            H->>H: max_size = 500
        else 普通情况
            H->>H: max_size = 100
        end

        H->>Model: 创建新 Hunter
        Note over H: 人口守恒：先减后创建
        H->>H: size -= new_size

        opt 原 Hunter 仍存活
            H->>Cell: search_cell(new_hunter)
            Cell-->>H: 返回合适格子
            H->>NewCell: 新 Hunter 移动到目标格子
        else 原 Hunter 死亡
            H->>H: 新 Hunter 也死亡
        end
    end

    Note over H: 4. 损失 (v2.0 新增)
    H->>H: loss()

    alt 随机触发 (prob=0.05)
        H->>H: size *= (1 - 0.1)
        Note over H: 人口减少 10%
    end

    Note over H,NewCell: 5. 移动
    H->>H: move_one()

    alt 非定居型 (size <= 100)
        H->>Cell: neighboring(radius=1)
        Cell-->>H: 返回周围格子

        loop 搜索合适格子
            H->>NewCell: 检查 able_to_live(hunter)

            alt 格子有其他 Hunter
                H->>Other: 合并
                Note over H,Other: merge(): size = h1.size + h2.size
                Other->>Other: size = self.size + h.size
                H->>H: die()
            else 格子有其他主体
                NewCell-->>H: False (不能进入)
            else 格子为空 & 非水体
                H->>NewCell: 移动到新格子
            end
        end
    end

    opt 人口 < min_size (6)
        H->>H: die()
    end

    H-->>Model: step 完成
```

## Farmer 行为详细流程

```mermaid
sequenceDiagram
    participant Model
    participant F as Farmer
    participant Cell as Current Cell
    participant NewCell as Target Cell

    Model->>F: step()

    Note over F: 1. 人口增长
    F->>F: population_growth(rate=0.004)
    F->>F: size = size * (1 + growth_rate)

    Note over F,Cell: 2. 转化检查
    F->>F: convert()

    alt 转化开关开启
        F->>F: _convert_to_hunter()
        opt size <= 100 & 随机
            F->>Cell: 检查 convert.farmer_to_hunter
            alt 开关开启
                Cell->>Cell: convert(farmer, "Hunter")
                Cell->>Model: 创建 Hunter(size=farmer.size)
                Cell->>F: die()
            end
        end

        opt 未转化 & size >= 200
            F->>F: _convert_to_rice()
            opt 在水稻地 & 随机
                F->>Cell: 检查 convert.farmer_to_rice
                alt 开关开启
                    Cell->>Cell: convert(farmer, "RiceFarmer")
                    Cell->>Model: 创建 RiceFarmer(size=farmer.size)
                    Cell->>F: die()
                end
            end
        end
    end

    Note over F: 3. 扩散 (人口守恒)
    F->>F: diffuse(diffuse_prob=0.05)

    alt 随机触发扩散
        F->>F: random_size(30, 60)
        Note over F: 人口守恒：先创建后减少
        F->>Model: 创建新 Farmer(size=new_size)
        F->>F: size -= new_size

        opt 原 Farmer 仍存活
            F->>Cell: search_cell(new_farmer)
            Cell-->>F: 返回可耕地
            F->>NewCell: 新 Farmer 移动
            NewCell->>NewCell: 检查 able_to_live()
        end
    end

    Note over F: 4. 损失
    F->>F: loss()
    alt 随机触发 (prob=0.05)
        F->>F: size *= (1 - 0.1)
    end

    Note over F: 5. 复杂化检查
    opt size > max_size
        F->>F: complicate()
        F->>F: growth_rate *= (1 - 0.1)
        F->>F: area += 2 * (1 - 0.1)
    end

    opt size < min_size (6)
        F->>F: die()
    end

    F-->>Model: step 完成
```

## 转化机制详细流程 (v2.0 新增开关控制)

```mermaid
flowchart TD
    Start([主体尝试转化]) --> CheckGlobal{全局开关<br/>convert.enabled?}

    CheckGlobal -->|False| NoConvert[不转化]
    CheckGlobal -->|True| CheckType{检查主体类型}

    CheckType -->|Hunter| HunterConvert[Hunter 转化逻辑]
    CheckType -->|Farmer| FarmerConvert[Farmer 转化逻辑]
    CheckType -->|RiceFarmer| RiceConvert[RiceFarmer 转化逻辑]

    HunterConvert --> CheckH2F{hunter_to_farmer<br/>开关?}
    CheckH2F -->|True| H2FCond{周围有 Farmer &<br/>当前可耕地 &<br/>随机触发?}
    CheckH2F -->|False| CheckH2R{hunter_to_rice<br/>开关?}
    H2FCond -->|Yes| ConvertH2F[转化为 Farmer]
    H2FCond -->|No| CheckH2R

    CheckH2R -->|True| H2RCond{周围有 RiceFarmer &<br/>水稻可耕地 &<br/>随机触发?}
    CheckH2R -->|False| NoConvert
    H2RCond -->|Yes| ConvertH2R[转化为 RiceFarmer]
    H2RCond -->|No| NoConvert

    FarmerConvert --> CheckF2H{farmer_to_hunter<br/>开关?}
    CheckF2H -->|True| F2HCond{人口 <= 100 &<br/>随机触发?}
    CheckF2H -->|False| CheckF2R{farmer_to_rice<br/>开关?}
    F2HCond -->|Yes| ConvertF2H[转化为 Hunter]
    F2HCond -->|No| CheckF2R

    CheckF2R -->|True| F2RCond{人口 >= 200 &<br/>在水稻地 &<br/>随机触发?}
    CheckF2R -->|False| NoConvert
    F2RCond -->|Yes| ConvertF2R[转化为 RiceFarmer]
    F2RCond -->|No| NoConvert

    RiceConvert --> CheckR2F{rice_to_farmer<br/>开关?}
    CheckR2F -->|True| R2FCond{人口 < 200 &<br/>随机触发?}
    CheckR2F -->|False| NoConvert
    R2FCond -->|Yes| ConvertR2F[转化为 Farmer]
    R2FCond -->|No| NoConvert

    ConvertH2F --> Create[创建新主体<br/>保持人口数]
    ConvertH2R --> Create
    ConvertF2H --> Create
    ConvertF2R --> Create
    ConvertR2F --> Create

    Create --> Die[旧主体死亡]
    Die --> End([转化完成])
    NoConvert --> End

    style CheckGlobal fill:#ff9999
    style Create fill:#99ff99
    style Die fill:#ffcc99
```

## 扩散机制与人口守恒 (v2.0 改进)

```mermaid
sequenceDiagram
    participant Agent as 原主体<br/>(size=100)
    participant Model
    participant NewAgent as 新主体
    participant Cell as 原格子
    participant NewCell as 目标格子

    Note over Agent: 触发扩散条件
    Agent->>Agent: 检查扩散条件

    alt Hunter: size >= max_size
        Agent->>Agent: 自动扩散
    else Farmer/RiceFarmer: 随机
        Agent->>Agent: random() < diffuse_prob
    end

    Note over Agent,Model: 人口守恒关键步骤

    rect rgb(255, 220, 220)
        Note over Agent,NewAgent: 步骤1: 先创建新主体
        Agent->>Agent: new_size = random(min, max)
        Agent->>Agent: new_size = min(new_size, self.size)
        Agent->>Model: 创建新主体(size=new_size)
        Model->>NewAgent: 新主体诞生
    end

    rect rgb(220, 255, 220)
        Note over Agent: 步骤2: 减少原主体人口
        Agent->>Agent: self.size -= new_size
        Note over Agent: 🔒 人口守恒检查点<br/>原人口 = 现人口 + 新人口
    end

    alt 原主体人口 < min_size
        Agent->>Agent: die()
        Note over Agent: 原主体死亡
    end

    rect rgb(220, 220, 255)
        Note over NewAgent,NewCell: 步骤3: 新主体寻找位置
        NewAgent->>Cell: search_cell(radius=1)
        Cell->>NewCell: 检查周围格子

        loop 扩大搜索半径
            NewCell->>NewCell: able_to_live(new_agent)?
            alt 找到合适格子
                NewAgent->>NewCell: 移动到新格子
            else 未找到
                NewCell->>Cell: 扩大半径继续搜索
            end
        end

        alt 搜索失败 (半径 > max_travel_distance)
            NewAgent->>NewAgent: die()
            Note over NewAgent: 新主体死亡<br/>但人口已从原主体减少<br/>总人口守恒
        end
    end

    Note over Agent,NewAgent: 最终结果：<br/>总人口 = 原主体剩余 + 新主体
```

## 格子规则检查流程 (v2.0 新增每格唯一主体)

```mermaid
flowchart TD
    Start([主体尝试进入格子]) --> HasAgent{格子有主体?}

    HasAgent -->|No| CheckType{检查主体类型}
    HasAgent -->|Yes| SameAgent{是同一个主体?}

    SameAgent -->|Yes| CheckType
    SameAgent -->|No| Reject[拒绝: 每格只能有一个主体]

    CheckType -->|Hunter| CheckWater{是水体?}
    CheckType -->|Farmer| CheckArable{是可耕地?}
    CheckType -->|RiceFarmer| CheckRiceArable{是水稻可耕地?}

    CheckWater -->|No| Allow[允许进入]
    CheckWater -->|Yes| Reject

    CheckArable -->|Yes| Allow
    CheckArable -->|No| Reject

    CheckRiceArable -->|Yes| Allow
    CheckRiceArable -->|No| Reject

    Allow --> Success([成功])
    Reject --> Fail([失败])

    style HasAgent fill:#ffcccc
    style CheckType fill:#ccccff
    style Allow fill:#ccffcc
    style Reject fill:#ffcccc
```

## 数据收集与可视化流程

```mermaid
sequenceDiagram
    participant Model
    participant DC as DataCollector
    participant Agents as All Agents
    participant Plot as ModelViz
    participant File as Output Files

    Note over Model,DC: 每个时间步
    loop 每个 tick
        Model->>DC: collect(model)
        DC->>Agents: 统计各类主体
        DC->>DC: 计算 num_farmers
        DC->>DC: 计算 num_hunters
        DC->>DC: 计算 num_rice
        DC->>DC: 计算 len_farmers (群体数)
        DC->>DC: 计算 len_hunters
        DC->>DC: 计算 len_rice
        DC->>DC: 存储到 DataFrame
    end

    Note over Model,File: 运行结束
    Model->>Model: end()

    Model->>Plot: plot.dynamic()
    Plot->>DC: 获取时间序列数据
    Plot->>Plot: 绘制人口变化趋势
    Plot->>File: 保存 repeat_X_dynamic.jpg

    Model->>Plot: plot.heatmap()
    Plot->>DC: 获取断点数据
    Plot->>Plot: 绘制空间热图
    Plot->>File: 保存 repeat_X_heatmap.jpg

    Model->>Model: export_conversion_data()
    Model->>Agents: 统计来源转化矩阵
    Model->>File: 保存 repeat_X_conversion.csv

    File-->>Model: 所有文件已保存
```

## 使用说明

### 在文档中嵌入时序图

这些时序图使用 Mermaid 语法编写，会自动在文档中渲染成可交互的图表。

### 查看时序图

1. 启动文档服务器：`poetry run mkdocs serve`
2. 访问此页面查看完整的交互式时序图
3. 可以缩放、导出 SVG/PNG

### 修改时序图

直接编辑本文件中的 Mermaid 代码块，保存后自动更新。

## 关键流程说明

### v2.0 重要变更在时序图中的体现

1. **转化机制开关**：每个转化操作都会检查对应的开关
2. **人口守恒**：扩散时先创建新主体，再减少原主体人口
3. **损失机制**：Hunter 现在也有 loss() 步骤
4. **每格唯一**：able_to_live() 检查格子是否已有其他主体
5. **初始化**：同时创建三类主体，不再等待特定 tick

### 关键时间点

- **tick=0**：初始化，创建所有三类主体
- **每个 tick**：
  1. 环境步骤（添加新主体）
  2. 主体步骤（随机执行所有主体的 step）
  3. 数据收集
- **tick=end**：结束，绘图和导出数据

## 参考文档

- [工作流程](../usage/workflow.md) - 文字描述
- [变更日志](changelog_v2.md) - 详细变更说明
- [配置文件](../usage/config.md) - 参数说明

