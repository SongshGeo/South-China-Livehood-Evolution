# 🚀 部署说明 / Deployment Guide

## ✅ GitHub Actions 工作流已优化

### 主要改进

| 改进项 | 之前 | 现在 |
|--------|------|------|
| 依赖管理 | 11个单独的 pip install | ✅ `poetry install --only docs` |
| 版本控制 | ❌ 无版本锁定 | ✅ 使用 poetry.lock |
| 缓存策略 | 仅缓存 .cache | ✅ 缓存整个 .venv |
| Actions 版本 | v2, v3 | ✅ 最新 v4, v5 |
| Python 版本 | 3.x（不确定） | ✅ 3.11（明确） |
| 分支触发 | master, main | ✅ 添加 refactor.simplify |

### 新的工作流程

```yaml
name: Deploy Documentation

steps:
  1. Checkout (v4)
  2. Setup Python 3.11 (v5)
  3. Install Poetry
  4. Cache .venv
  5. poetry install --only docs
  6. poetry run mkdocs gh-deploy
```

**优势**:
- ⚡ 更快：使用缓存大幅减少安装时间
- 🔒 更稳定：版本锁定，避免兼容性问题
- 🧹 更简洁：一条命令安装所有依赖
- 🎯 更精确：只安装文档需要的依赖

---

## 🌍 双语文档支持

### 配置完成

✅ **中文版**（默认）: `https://your-site.com/`
✅ **英文版**: `https://your-site.com/en/`

### 文档结构

```
site/
├── index.html                 # 中文主页
├── UPDATES/index.html         # 中文更新说明
├── usage/
│   ├── config/index.html      # 中文配置文档
│   └── workflow/index.html    # 中文工作流
├── tech/
│   └── changelog_v2/index.html # 中文变更日志
└── en/                        # 英文版本
    ├── index.html
    ├── UPDATES/index.html
    ├── usage/
    │   ├── config/index.html
    │   └── workflow/index.html
    └── tech/
        └── changelog_v2/index.html
```

### 统计

- **中文页面**: 13个
- **英文页面**: 12个
- **总页面数**: 25个
- **总文件数**: 78个
- **构建时间**: ~2秒

### 语言切换

用户可以通过页面右上角的语言选择器在中英文之间切换。

---

## 📦 本地部署

### 查看文档

```bash
# 构建文档
poetry run mkdocs build

# 启动本地服务器
poetry run mkdocs serve

# 访问
# 中文: http://127.0.0.1:8000
# 英文: http://127.0.0.1:8000/en/
```

### 运行模型

```bash
# 单次运行
poetry run python -m src time.end=20 exp.repeats=1

# 多次重复
poetry run python -m src time.end=30 exp.repeats=3

# 参数扫描
poetry run python -m src --multirun \
    env.init_hunters=0.05,0.1,0.2 \
    env.lam_farmer=1,2,3
```

### 运行测试

```bash
# 所有测试
poetry run pytest tests/ -v

# 特定测试
poetry run pytest tests/test_hunters.py -v

# 测试覆盖率
poetry run pytest tests/ --cov=src
```

---

## 🌐 GitHub Pages 部署

### 自动部署

推送到以下分支会自动触发部署：
- `master`
- `main`
- `refactor.simplify`

### 手动部署

```bash
# 构建并部署到 gh-pages 分支
poetry run mkdocs gh-deploy --force

# 或使用 mike 进行版本管理
poetry run mike deploy --push --update-aliases v2.0 latest
```

### 部署后访问

文档将部署到：
- **中文**: `https://<username>.github.io/<repo>/`
- **英文**: `https://<username>.github.io/<repo>/en/`

---

## 🔧 依赖管理

### pyproject.toml

所有文档依赖已在 `[tool.poetry.group.docs]` 中定义：

```toml
[tool.poetry.group.docs.dependencies]
mkdocs = "^1.5.3"
mkdocs-material = "^9.4.2"
mkdocstrings = {extras = ["python"], version = "^0.23.0"}
mkdocs-static-i18n = "^1.2.0"
# ... 其他插件
```

### 当前版本

```
mkdocs: 1.6.1
mkdocs-material: latest
mkdocstrings: 0.25.0
mkdocstrings-python: 1.10.0
griffe: 0.47.0
mkdocs-static-i18n: 1.3.0
```

### 更新依赖

```bash
# 更新所有文档依赖
poetry update --only docs

# 更新特定包
poetry update mkdocs-material

# 重新生成 lock 文件
poetry lock
```

---

## 📊 GitHub Actions 工作流详情

### 触发条件

```yaml
on:
  push:
    branches:
      - master
      - main
      - refactor.simplify
```

### 构建步骤

1. **Checkout**: 获取完整历史（用于 git 信息）
2. **Setup Python 3.11**: 使用明确的 Python 版本
3. **Install Poetry**: 安装最新版 Poetry
4. **Cache**: 缓存 .venv 目录加速构建
5. **Install deps**: `poetry install --only docs`
6. **Install i18n**: 安装 mkdocs-static-i18n
7. **Deploy**: `mkdocs gh-deploy --force --clean`

### 预期执行时间

- **首次运行**: ~3-5分钟（安装所有依赖）
- **有缓存**: ~1-2分钟（仅构建文档）

### 验证部署

检查 GitHub Actions 页面：
`https://github.com/<username>/<repo>/actions`

---

## 🐛 故障排除

### 如果 GitHub Actions 失败

1. **检查分支名**：确保推送到正确的分支
2. **查看日志**：在 Actions 页面查看详细错误
3. **本地测试**：先在本地运行 `poetry run mkdocs build`
4. **依赖问题**：运行 `poetry lock` 更新锁文件

### 如果文档无法构建

```bash
# 清理并重建
rm -rf site/
poetry run mkdocs build --clean

# 检查配置
poetry run mkdocs build --strict
```

### 如果语言切换不工作

1. 确保 `.en.md` 文件与中文文件对应
2. 检查 `mkdocs.yml` 中的 i18n 配置
3. 清空浏览器缓存

---

## 📝 维护清单

### 添加新页面

1. 创建中文版：`docs/new_page.md`
2. 创建英文版：`docs/new_page.en.md`
3. 更新 `mkdocs.yml` 导航
4. 重新构建测试

### 更新现有页面

1. 同时更新中英文版本
2. 运行 `poetry run mkdocs build` 验证
3. 提交并推送触发自动部署

### 更新依赖

```bash
# 查看过时的包
poetry show --outdated --only docs

# 更新特定包
poetry update mkdocs-material

# 更新所有文档依赖
poetry update --only docs

# 提交更新的 poetry.lock
git add poetry.lock
git commit -m "chore: update docs dependencies"
```

---

## ✅ 部署验证清单

在部署前请确认：

- [ ] 所有测试通过：`poetry run pytest tests/`
- [ ] 文档本地构建成功：`poetry run mkdocs build`
- [ ] 中文页面正常
- [ ] 英文页面正常
- [ ] 语言切换正常
- [ ] 所有链接有效
- [ ] 图片正常加载
- [ ] 搜索功能正常

---

## 🎯 最佳实践

### 1. 使用 Poetry

✅ **推荐**:
```bash
poetry install --only docs
poetry run mkdocs build
```

❌ **不推荐**:
```bash
pip install mkdocs
pip install mkdocs-material
...  # 逐个安装
```

### 2. 版本管理

- 使用 `poetry.lock` 锁定版本
- 定期更新依赖
- 测试后再部署

### 3. 文档维护

- 同时维护中英文版本
- 使用一致的文档结构
- 保持 API 文档自动生成

---

**最后更新**: 2025-10-20
**文档版本**: v2.0
**部署状态**: ✅ 就绪

