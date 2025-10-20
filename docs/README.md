---
title: 文档说明
author: Shuang Song
date: 2025-10-20
---

# 文档说明

本目录包含华南生计演变模型的完整文档。

## 📚 文档结构

```
docs/
├── index.md                    # 📖 文档主页
├── UPDATES.md                  # 🆕 v2.0 更新说明（快速指南）
├── README.md                   # 📝 本文件
│
├── usage/                      # 📘 使用指南
│   ├── quick_start.md         # 快速开始
│   ├── config.md              # 参数配置（已更新）
│   ├── workflow.md            # 模拟流程（已更新）
│   └── plots.md               # 结果分析
│
├── tech/                       # 🔧 技术文档
│   ├── changelog_v2.md        # 🆕 v2.0 详细变更日志
│   └── breakpoint.md          # 断点检测方法
│
├── api/                        # 📚 API 参考
│   ├── model.md               # Model 类
│   ├── hunter.md              # Hunter 类
│   ├── farmer.md              # Farmer 类
│   └── env.md                 # Environment 类
│
└── demo.ipynb                  # 💻 使用示例（Jupyter Notebook）
```

## 🆕 最新更新 (2025-10-20)

本次更新对应模型 **v2.0** 重构，主要文档更新包括：

### 新增文档

- **`UPDATES.md`** - v2.0 快速更新指南
  - 核心变更快速概览表
  - 配置文件迁移步骤
  - API 变更对照
  - 使用建议

- **`tech/changelog_v2.md`** - 详细变更日志
  - 8项核心修改的详细说明
  - 变更前后代码对比
  - 配置示例
  - 向后兼容性说明

### 更新的文档

- **`index.md`** - 主页
  - ✅ 添加新功能列表
  - ✅ 添加更新提示
  - ✅ 链接到变更日志

- **`usage/config.md`** - 参数配置
  - ✅ 新增 `convert` 部分（转化机制开关）
  - ✅ 更新 `env` 部分（初始农民参数）
  - ✅ 重写 `Hunter` 部分（删除竞争参数，新增人口上限和损失参数）
  - ✅ 更新 `Farmer` 和 `RiceFarmer` 部分（添加 init_size）
  - ✅ 所有参数都有详细说明

- **`usage/workflow.md`** - 工作流程
  - ✅ 更新初始化说明（现在创建三类主体）
  - ✅ 重写步骤说明（删除竞争，添加损失）
  - ✅ 添加重要规则变更说明
  - ✅ 强调人口守恒机制

## 🔍 关键变更速查

### 配置文件必须更新

如果您使用旧版本配置，请添加以下内容：

```yaml
# 1. 转化开关
convert:
  enabled: true
  hunter_to_farmer: true
  hunter_to_rice: true
  farmer_to_hunter: true
  farmer_to_rice: true
  rice_to_farmer: true

# 2. 初始农民
env:
  init_farmers: 80
  init_rice_farmers: 350
  tick_farmer: 0
  tick_ricefarmer: 0

# 3. Hunter 更新
Hunter:
  max_size: 100
  max_size_water: 500
  loss:
    prob: 0.05
    rate: 0.1
  # 删除: intensified_coefficient

# 4. 初始人口
Farmer:
  init_size: [60, 100]

RiceFarmer:
  init_size: [300, 400]
```

### API 变更

**删除的方法**：
- `Hunter.compete()`
- `Hunter.loss_in_competition()`
- `Hunter.moving()`

**新增的方法**：
- `Hunter.is_near_water()` - 检查是否临近水体
- `Hunter.loss()` - 损失机制
- `Env.add_initial_farmers()` - 初始化农民

**修改的方法**：
- `Hunter.max_size` - 现在返回固定值（100或500）
- `Hunter.merge()` - 严格人口守恒
- `SiteGroup.diffuse()` - 严格人口守恒
- `CompetingCell.able_to_live()` - 每格唯一主体
- `CompetingCell.convert()` - 支持转化开关

## 🛠️ 构建文档

### 本地预览

```bash
# 安装依赖（如果尚未安装）
poetry install

# 构建文档
poetry run mkdocs build

# 启动本地服务器
poetry run mkdocs serve
```

然后在浏览器中访问 `http://127.0.0.1:8000`

### 构建状态

- ✅ 文档构建成功
- ✅ 生成 14 个 HTML 页面
- ✅ 所有主要页面正常渲染
- ⚠️ 部分内部链接锚点待优化（不影响使用）

### 已生成的文档

- 主页 (index.html)
- 更新说明 (UPDATES/index.html)
- 使用指南 (usage/)
  - 快速开始
  - 参数配置
  - 模拟流程
  - 结果分析
- 技术文档 (tech/)
  - 变更日志 v2.0
  - 断点检测
- API 参考 (api/)
  - Model
  - Hunter
  - Farmer
  - Environment
- 演示示例 (demo/)

## 📖 阅读建议

### 对于新用户

1. 从 [主页](index.md) 了解模型概况
2. 阅读 [快速开始](usage/quick_start.md) 安装和运行
3. 学习 [模拟流程](usage/workflow.md) 理解模型逻辑
4. 参考 [参数配置](usage/config.md) 调整实验参数

### 对于已有用户

1. **必读**：[更新说明](UPDATES.md) - 快速了解变更和迁移步骤
2. **详细**：[变更日志](tech/changelog_v2.md) - 完整的变更说明
3. **更新**：[参数配置](usage/config.md) - 新的参数说明
4. **更新**：[模拟流程](usage/workflow.md) - 新的工作流程

### 对于开发者

1. 查阅 [API 参考](api/) 了解类和方法
2. 阅读 [变更日志](tech/changelog_v2.md) 了解实现细节
3. 参考源代码中的 docstring（Google 风格）

## 🔗 相关资源

- **源代码**：`src/` 目录
- **配置文件**：`config/config.yaml`
- **测试代码**：`tests/` 目录
- **示例输出**：`out/south_china_evolution/` 目录

## 📝 文档维护

### 自动生成部分

- API 参考文档通过 `mkdocstrings` 从源代码自动生成
- 需要保持代码 docstring 的完整性和准确性

### 手动维护部分

- 使用指南
- 配置说明
- 工作流程说明
- 技术文档

### 更新文档

修改 Markdown 文件后，重新构建：

```bash
poetry run mkdocs build
```

## ⚠️ 已知问题

部分内部链接的中文锚点可能无法正常工作，这是 MkDocs 对中文字符的处理限制。不影响文档的整体阅读和使用。

## 📞 反馈

如发现文档中的错误或需要补充的内容，请联系：songshgeo[at]gmail.com

