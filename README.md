# 华南生计演变模型 / South China Livelihood Evolution Model

[![Docs](https://github.com/SongshGeo/South-China-Livehood-Evolution/actions/workflows/docusaurus-pages.yml/badge.svg)](https://github.com/SongshGeo/South-China-Livehood-Evolution/actions/workflows/docusaurus-pages.yml)
[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/)
[![uv](https://img.shields.io/badge/uv-managed-blue)](https://docs.astral.sh/uv/)

[中文](#中文) | [English](#english)

---

## 中文

基于主体的华南地区史前生计演变模拟模型。

### ✨ 主要特性

- 🏹 三类主体模拟：狩猎采集者、普通农民、水稻农民
- 🗺️ 地形因素考虑：海拔、坡度对人群分布的影响
- 🔄 动态过程：人口增长、迁移、转化
- 📊 数据可视化：热力图、趋势图、断点分析
- 🎛️ 灵活控制：独立的转化机制开关
- 📐 严格守恒：扩散和合并过程的人口守恒

### 🆕 最新更新 (v2.0)

本次重构完成了 8 项重大模型逻辑修改：

| 修改 | 描述 |
|------|------|
| ✅ 初始化优化 | 所有主体类型从开始就存在 |
| ✅ 转化开关 | 可独立控制 6 种转化路径 |
| ❌ 删除竞争 | 移除主体间竞争机制 |
| ✅ 人口守恒 | 严格保证扩散/合并守恒 |
| ✅ Hunter 改进 | 新的人口上限规则 + 损失机制 |
| ✅ 每格唯一 | 一个格子只能有一个主体 |

详见[更新说明](https://south-china-livehood-evolution.vercel.app/docs/UPDATES)和[变更日志](https://south-china-livehood-evolution.vercel.app/docs/tech/changelog_v2)。

### 🚀 快速开始

依赖由 [uv](https://docs.astral.sh/uv/) 管理，声明在 `pyproject.toml`、锁定在 `uv.lock`。

```bash
# 安装运行时 + 开发依赖
uv sync
# 需要 Jupyter 时，额外装上 notebook 依赖组
uv sync --all-groups

# 运行测试
make test

# 运行模型
uv run python -m src time.end=20 exp.repeats=1

# 本地预览文档
cd docs-docusaurus && npm ci && npm run start
```

### 📚 文档

- 🌐 **在线文档**: <https://south-china-livehood-evolution.vercel.app>
- 📖 **本地预览**: `cd docs-docusaurus && npm run start`
- 🇨🇳 **中文文档**: 默认语言
- 🇬🇧 **英文文档**: 点击语言选择器切换

文档源文件全部位于 `docs-docusaurus/`，中文在 `docs/`、英文在 `i18n/en/`。

### 🗂️ 目录结构

| 路径 | 内容 |
|------|------|
| `src/` | 模型源码（`api/` 主体、`core/` 模型、`workflow/` 分析与绘图） |
| `tests/` | pytest 测试 |
| `config/` | Hydra 配置与情景文件 |
| `reports/` | 分析与出图 notebook |
| `paper/` | 手稿相关：Methods、ODD+D 协议、参考文献 |
| `docs-docusaurus/` | 文档站点（唯一文档来源） |

### 🛠️ 技术栈

- Python 3.11
- ABSESpy 0.11 (Agent-Based Modeling Framework)
- Hydra (Configuration Management)
- Docusaurus (Documentation)
- uv (Dependency Management)

### 📝 引用

如果您使用了本模型，请引用：

```bibtex
@software{song2025sce,
  author = {Song, Shuang},
  title = {South China Livelihood Evolution Model},
  year = {2025},
  url = {https://github.com/SongshGeo/South-China-Livehood-Evolution}
}
```

### 📧 联系

- **作者**: Shuang (Twist) Song
- **邮箱**: songshgeo@gmail.com
- **网站**: https://cv.songshgeo.com/

---

## English

An agent-based model simulating prehistoric livelihood evolution in South China.

### ✨ Key Features

- 🏹 Three agent types: hunter-gatherers, farmers, rice farmers
- 🗺️ Terrain factors: elevation and slope impact on population distribution
- 🔄 Dynamic processes: population growth, migration, conversion
- 📊 Data visualization: heatmaps, trend charts, breakpoint analysis
- 🎛️ Flexible control: independent conversion mechanism switches
- 📐 Strict conservation: population conservation in diffusion and merger

### 🆕 Latest Update (v2.0)

This refactoring completed 8 major model logic modifications:

| Change | Description |
|--------|-------------|
| ✅ Initialization | All agent types present from start |
| ✅ Conversion Switches | Independent control of 6 conversion paths |
| ❌ Remove Competition | Removed inter-agent competition |
| ✅ Conservation | Strict diffusion/merger conservation |
| ✅ Hunter Improvements | New population limits + loss mechanism |
| ✅ One Per Cell | Only one agent allowed per cell |

See [Updates](https://south-china-livehood-evolution.vercel.app/en/docs/UPDATES) and [Changelog](https://south-china-livehood-evolution.vercel.app/en/docs/tech/changelog_v2) for details.

### 🚀 Quick Start

Dependencies are managed by [uv](https://docs.astral.sh/uv/), declared in `pyproject.toml` and pinned in `uv.lock`.

```bash
# Install runtime + dev dependencies
uv sync
# Add the notebook group when you need Jupyter
uv sync --all-groups

# Run tests
make test

# Run the model
uv run python -m src time.end=20 exp.repeats=1

# Preview the docs locally
cd docs-docusaurus && npm ci && npm run start
```

### 📚 Documentation

- 🌐 **Online Docs**: <https://south-china-livehood-evolution.vercel.app>
- 📖 **Local Preview**: `cd docs-docusaurus && npm run start`
- 🇨🇳 **Chinese**: Default language
- 🇬🇧 **English**: Switch via language selector

All documentation sources live under `docs-docusaurus/` — Chinese in `docs/`, English in `i18n/en/`.

### 🗂️ Layout

| Path | Contents |
|------|----------|
| `src/` | Model source (`api/` agents, `core/` model, `workflow/` analysis and plotting) |
| `tests/` | pytest suite |
| `config/` | Hydra configuration |
| `reports/` | Analysis and figure notebooks |
| `paper/` | Manuscript material: Methods, ODD+D protocol, references |
| `docs-docusaurus/` | Documentation site (single source of truth) |

### 🛠️ Tech Stack

- Python 3.11
- ABSESpy 0.11 (Agent-Based Modeling Framework)
- Hydra (Configuration Management)
- Docusaurus (Documentation)
- uv (Dependency Management)

### 📝 Citation

If you use this model, please cite:

```bibtex
@software{song2025sce,
  author = {Song, Shuang},
  title = {South China Livelihood Evolution Model},
  year = {2025},
  url = {https://github.com/SongshGeo/South-China-Livehood-Evolution}
}
```

### 📧 Contact

- **Author**: Shuang (Twist) Song
- **Email**: songshgeo@gmail.com
- **Website**: https://cv.songshgeo.com/

---

## License

[Add your license here]

## Acknowledgments

This model is built with [ABSESpy](https://github.com/ABSESpy/ABSESpy), a Python framework for agent-based modeling.
