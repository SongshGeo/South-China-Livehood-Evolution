# 华南生计演变模型 / South China Livelihood Evolution Model

[![Tests](https://github.com/SongshGeo/SC-20230710-SCE/actions/workflows/test.yml/badge.svg)](https://github.com/SongshGeo/SC-20230710-SCE/actions/workflows/test.yml)
[![Documentation](https://github.com/SongshGeo/SC-20230710-SCE/actions/workflows/gh_page.yml/badge.svg)](https://github.com/SongshGeo/SC-20230710-SCE/actions/workflows/gh_page.yml)
[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/)
[![Poetry](https://img.shields.io/badge/poetry-managed-blue)](https://python-poetry.org/)

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

### 🆕 最新更新 (v2.0 - 2025-10-20)

本次重构完成了8项重大模型逻辑修改：

| 修改 | 描述 |
|------|------|
| ✅ 初始化优化 | 所有主体类型从开始就存在 |
| ✅ 转化开关 | 可独立控制6种转化路径 |
| ❌ 删除竞争 | 移除主体间竞争机制 |
| ✅ 人口守恒 | 严格保证扩散/合并守恒 |
| ✅ Hunter改进 | 新的人口上限规则 + 损失机制 |
| ✅ 每格唯一 | 一个格子只能有一个主体 |

详见 [更新说明](docs/UPDATES.md) 和 [变更日志](docs/tech/changelog_v2.md)

### 🚀 快速开始

```bash
# 安装依赖
poetry install

# 运行测试
poetry run pytest tests/

# 运行模型
poetry run python -m src time.end=20 exp.repeats=1

# 查看文档
poetry run mkdocs serve
# 访问 http://127.0.0.1:8000
```

### 📚 文档

- 🌐 **在线文档**: [GitHub Pages](https://songshgeo.github.io/SC-20230710-SCE/) *(即将部署)*
- 📖 **本地文档**: `poetry run mkdocs serve`
- 🇨🇳 **中文文档**: 默认语言
- 🇬🇧 **英文文档**: 点击语言选择器切换

### ✅ 项目状态

- **代码**: ✅ 全部重构完成
- **测试**: ✅ 84/84 通过
- **文档**: ✅ 中英双语
- **部署**: ✅ GitHub Actions 配置完成

### 🛠️ 技术栈

- Python 3.11
- ABSESpy 0.8.5 (Agent-Based Modeling Framework)
- Hydra (Configuration Management)
- MkDocs Material (Documentation)
- Poetry (Dependency Management)

### 📝 引用

如果您使用了本模型，请引用：

```bibtex
@software{song2025sce,
  author = {Song, Shuang},
  title = {South China Livelihood Evolution Model},
  year = {2025},
  url = {https://github.com/SongshGeo/SC-20230710-SCE}
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

### 🆕 Latest Update (v2.0 - 2025-10-20)

This refactoring completed 8 major model logic modifications:

| Change | Description |
|--------|-------------|
| ✅ Initialization | All agent types present from start |
| ✅ Conversion Switches | Independent control of 6 conversion paths |
| ❌ Remove Competition | Removed inter-agent competition |
| ✅ Conservation | Strict diffusion/merger conservation |
| ✅ Hunter Improvements | New population limits + loss mechanism |
| ✅ One Per Cell | Only one agent allowed per cell |

See [Updates](docs/UPDATES.en.md) and [Changelog](docs/tech/changelog_v2.en.md) for details.

### 🚀 Quick Start

```bash
# Install dependencies
poetry install

# Run tests
poetry run pytest tests/

# Run model
poetry run python -m src time.end=20 exp.repeats=1

# View documentation
poetry run mkdocs serve
# Visit http://127.0.0.1:8000
```

### 📚 Documentation

- 🌐 **Online Docs**: [GitHub Pages](https://songshgeo.github.io/SC-20230710-SCE/) *(coming soon)*
- 📖 **Local Docs**: `poetry run mkdocs serve`
- 🇨🇳 **Chinese**: Default language
- 🇬🇧 **English**: Switch via language selector

### ✅ Project Status

- **Code**: ✅ Fully refactored
- **Tests**: ✅ 84/84 passing
- **Documentation**: ✅ Bilingual (Chinese/English)
- **Deployment**: ✅ GitHub Actions configured

### 🛠️ Tech Stack

- Python 3.11
- ABSESpy 0.8.5 (Agent-Based Modeling Framework)
- Hydra (Configuration Management)
- MkDocs Material (Documentation)
- Poetry (Dependency Management)

### 📝 Citation

If you use this model, please cite:

```bibtex
@software{song2025sce,
  author = {Song, Shuang},
  title = {South China Livelihood Evolution Model},
  year = {2025},
  url = {https://github.com/SongshGeo/SC-20230710-SCE}
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

- [模型工作流](docs/api/model.md)
- [农民主体方法](docs/api/farmer.md)
- [狩猎采集者主体方法](docs/api/hunter.md)
- [斑块与环境](docs/api/env.md)
