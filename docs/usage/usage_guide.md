# 📖 使用指南

## ✅ 现在可以做的事

### 1. 查看双语文档

```bash
poetry run mkdocs serve
```

然后访问：
- **中文版**: http://127.0.0.1:8000
- **英文版**: http://127.0.0.1:8000/en/

在页面右上角可以切换语言！

### 2. 运行模型

```bash
# 快速测试（20步）
poetry run python -m src time.end=20 exp.repeats=1

# 标准运行（30步，3次重复）
poetry run python -m src time.end=30 exp.repeats=3

# 参数扫描
poetry run python -m src --multirun \
    env.init_hunters=0.05,0.1,0.2 \
    env.lam_farmer=1,2,3
```

### 3. 运行测试

```bash
poetry run pytest tests/ -v
```

预期：**84 passed** ✅

### 4. 部署文档到 GitHub Pages

```bash
# 方式1：推送代码自动部署
git push origin refactor.simplify  # 或 main/master

# 方式2：手动部署
poetry run mkdocs gh-deploy --force
```

---

## 🎯 重大变更（v2.0）

### 配置文件必须更新！

如果你有旧的配置文件，请添加：

```yaml
convert:
  enabled: true
  hunter_to_farmer: true
  hunter_to_rice: true
  farmer_to_hunter: true
  farmer_to_rice: true
  rice_to_farmer: true

env:
  init_farmers: 80
  init_rice_farmers: 350
  tick_farmer: 0
  tick_ricefarmer: 0

Hunter:
  max_size: 100
  max_size_water: 500
  loss:
    prob: 0.05
    rate: 0.1
  # 删除: intensified_coefficient

Farmer:
  init_size: [60, 100]

RiceFarmer:
  init_size: [300, 400]
```

### 核心变更

- ❌ **删除竞争机制**
- ✅ **添加转化开关**
- ✅ **每格只能有一个主体**
- ✅ **严格人口守恒**
- ✅ **Hunter 新增损失机制**

---

## 📚 文档资源

### 中文文档
- 🏠 主页: [docs/index.md](docs/index.md)
- 🆕 更新说明: [docs/UPDATES.md](docs/UPDATES.md)
- ⚙️ 参数配置: [docs/usage/config.md](docs/usage/config.md)
- 🔄 工作流程: [docs/usage/workflow.md](docs/usage/workflow.md)
- 📝 变更日志: [docs/tech/changelog_v2.md](docs/tech/changelog_v2.md)

### 英文文档
- 🏠 Home: [docs/index.en.md](docs/index.en.md)
- 🆕 Updates: [docs/UPDATES.en.md](docs/UPDATES.en.md)
- ⚙️ Configuration: [docs/usage/config.en.md](docs/usage/config.en.md)
- 🔄 Workflow: [docs/usage/workflow.en.md](docs/usage/workflow.en.md)
- 📝 Changelog: [docs/tech/changelog_v2.en.md](docs/tech/changelog_v2.en.md)

### 技术文档
- 🚀 部署说明: [DEPLOYMENT.md](DEPLOYMENT.md)
- 📊 项目说明: [README.md](README.md)

---

## 🔧 常用命令

```bash
# 测试
poetry run pytest tests/ -v                    # 运行测试
poetry run pytest tests/test_hunters.py -v     # 运行特定测试

# 文档
poetry run mkdocs build --clean                # 构建文档
poetry run mkdocs serve                        # 启动文档服务器
poetry run mkdocs gh-deploy --force            # 部署到 GitHub Pages

# 模型
poetry run python -m src                       # 运行模型（默认参数）
poetry run python -m src time.end=50           # 运行50步
poetry run python -m src exp.repeats=5         # 5次重复

# 依赖
poetry install                                 # 安装所有依赖
poetry install --only docs                     # 只安装文档依赖
poetry update                                  # 更新依赖
```

---

## ✨ 特性亮点

### 🎛️ 转化机制控制

```yaml
# 完全关闭转化
convert:
  enabled: false

# 只允许特定转化
convert:
  enabled: true
  hunter_to_farmer: true
  hunter_to_rice: false  # 关闭 Hunter → RiceFarmer
```

### 📊 对比实验

```bash
# 实验1：有转化机制
poetry run python -m src convert.enabled=true

# 实验2：无转化机制
poetry run python -m src convert.enabled=false
```

### 🌍 双语文档

- 中文为默认语言
- 英文版在 `/en/` 路径下
- 自动生成语言切换器

---

## 📊 项目状态

| 项目 | 状态 |
|------|------|
| 代码重构 | ✅ 完成 |
| 单元测试 | ✅ 84/84 通过 |
| 中文文档 | ✅ 13页 |
| 英文文档 | ✅ 12页 |
| GitHub Actions | ✅ 已优化 |
| 依赖管理 | ✅ Poetry 管理 |

---

## 🎊 全部就绪！

项目已经完全可以使用了：

- ✅ 代码经过完整测试
- ✅ 文档支持中英双语
- ✅ 自动部署已配置
- ✅ 所有依赖通过 Poetry 管理

开始你的研究吧！🚀

