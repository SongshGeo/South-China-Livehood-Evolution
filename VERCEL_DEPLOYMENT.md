# 🚀 Vercel 部署指南

## ✅ 已配置文件

项目现已完全配置好 Vercel 部署：

| 文件 | 用途 | 状态 |
|------|------|------|
| `vercel.json` | Vercel 配置 | ✅ 已创建 |
| `requirements-docs.txt` | Python 依赖 | ✅ 已导出 |
| `mkdocs.yml` | 文档配置 | ✅ 已优化 |
| `.github/workflows/gh_page.yml` | GitHub Actions | ✅ 备用方案 |

---

## 🎯 部署步骤

### 方式1：通过 Vercel Dashboard（推荐）

1. **登录 Vercel**
   - 访问 https://vercel.com
   - 使用 GitHub 账号登录

2. **导入项目**
   - 点击 "Add New..." → "Project"
   - 选择你的 GitHub 仓库
   - Vercel 会自动检测到 `vercel.json`

3. **配置项目**（应该自动检测）
   - **Framework Preset**: Other
   - **Build Command**: `pip install -r requirements-docs.txt && mkdocs build --clean`
   - **Output Directory**: `site`
   - **Install Command**: `pip install --upgrade pip`

4. **部署**
   - 点击 "Deploy"
   - 等待构建完成（约 2-3 分钟）

5. **访问**
   - 中文版: `https://your-project.vercel.app/`
   - 英文版: `https://your-project.vercel.app/en/`

### 方式2：通过 Vercel CLI

```bash
# 安装 Vercel CLI
npm install -g vercel

# 登录
vercel login

# 部署
vercel

# 部署到生产环境
vercel --prod
```

---

## 🔧 配置说明

### vercel.json

```json
{
  "buildCommand": "pip install -r requirements-docs.txt && mkdocs build --clean",
  "outputDirectory": "site",
  "installCommand": "pip install --upgrade pip",
  "framework": null,
  "routes": [
    {
      "src": "/en/(.*)",
      "dest": "/en/$1"
    },
    {
      "src": "/(.*)",
      "dest": "/$1"
    }
  ]
}
```

**关键配置**:
- ✅ 使用 `requirements-docs.txt`（从 poetry 导出）
- ✅ 输出到 `site/` 目录
- ✅ 路由配置支持中英双语

### requirements-docs.txt

通过 Poetry 自动生成：

```bash
poetry export -f requirements.txt --only docs --output requirements-docs.txt --without-hashes
```

**优势**:
- 🔒 版本锁定（来自 poetry.lock）
- 📦 只包含文档依赖
- 🚀 构建更快

---

## 🐛 常见问题

### Q: Node.js 版本错误

**错误信息**: `Node.js Version "18.x" is discontinued`

**解决方案**:
Vercel 会自动检测项目不需要 Node.js（因为是 Python/MkDocs 项目）。如果仍提示错误，在 Vercel Dashboard 中设置：

- Project Settings → General → Node.js Version → 22.x

### Q: 构建失败

**检查步骤**:

1. 本地测试构建：
```bash
pip install -r requirements-docs.txt
mkdocs build --clean
```

2. 检查 `requirements-docs.txt` 是否最新：
```bash
poetry export -f requirements.txt --only docs --output requirements-docs.txt --without-hashes
```

3. 提交更新后的文件：
```bash
git add requirements-docs.txt vercel.json
git commit -m "chore: update Vercel config"
git push
```

### Q: 双语切换不工作

**检查**:
- 确保 `mkdocs-static-i18n` 在 `requirements-docs.txt` 中
- 确保 `.en.md` 文件存在
- 清空浏览器缓存

---

## 📊 部署对比

### Vercel vs GitHub Pages

| 特性 | Vercel | GitHub Pages |
|------|--------|--------------|
| 部署速度 | ⚡ 2-3分钟 | 🐢 5-8分钟 |
| 自动部署 | ✅ 推送即部署 | ✅ 推送即部署 |
| 自定义域名 | ✅ 免费 | ✅ 免费 |
| HTTPS | ✅ 自动 | ✅ 自动 |
| 预览部署 | ✅ PR 自动预览 | ❌ 无 |
| 边缘网络 | ✅ 全球 CDN | ✅ GitHub CDN |
| 构建日志 | ✅ 详细 | ✅ 详细 |
| **推荐** | 🌟🌟🌟🌟🌟 | 🌟🌟🌟🌟 |

**建议**:
- Vercel 用于生产部署（更快、PR 预览）
- GitHub Pages 作为备用

---

## 🔄 更新流程

### 自动部署

推送到任何分支都会触发 Vercel 构建：

```bash
git add .
git commit -m "docs: 更新文档"
git push
```

Vercel 会：
1. 自动检测到代码变更
2. 安装依赖（使用 requirements-docs.txt）
3. 构建文档（中英双语）
4. 部署到 CDN
5. 提供预览链接

### 手动触发

在 Vercel Dashboard 中：
- Deployments → 选择部署 → Redeploy

---

## 📝 环境变量（可选）

如果需要配置环境变量，在 Vercel Project Settings 中添加：

| 变量名 | 值 | 说明 |
|--------|-----|------|
| `PYTHON_VERSION` | `3.11` | Python 版本（可选） |
| `MKDOCS_STRICT` | `false` | 是否严格模式 |

---

## ✅ 部署检查清单

部署前请确认：

- [ ] `requirements-docs.txt` 已更新
- [ ] `vercel.json` 配置正确
- [ ] 本地构建成功：`mkdocs build --clean`
- [ ] 所有文档文件已提交
- [ ] 中英文文档都已准备
- [ ] 时序图正常显示

---

## 🎊 部署后验证

### 检查项目

- [ ] 访问主页正常
- [ ] 中文版显示正常（默认）
- [ ] 英文版显示正常（/en/路径）
- [ ] 语言切换器工作正常
- [ ] 所有页面可访问
- [ ] 时序图正常渲染（Mermaid）
- [ ] 搜索功能正常
- [ ] 图片加载正常

### 性能检查

访问 Vercel Dashboard 查看：
- 构建时间
- 部署大小
- 访问速度
- 错误日志

---

## 🌟 最佳实践

### 1. 保持依赖更新

定期更新并重新导出：

```bash
poetry update --only docs
poetry export -f requirements.txt --only docs --output requirements-docs.txt --without-hashes
git add requirements-docs.txt
git commit -m "chore: update docs dependencies"
```

### 2. 使用 PR 预览

Vercel 会为每个 PR 创建预览环境：
- 在 PR 中自动评论预览链接
- 可以在合并前验证文档变更

### 3. 监控部署状态

在 Vercel Dashboard 中：
- 查看构建日志
- 监控访问统计
- 设置告警通知

---

## 📞 获取帮助

### Vercel 相关
- 📖 文档: https://vercel.com/docs
- 💬 社区: https://github.com/vercel/vercel/discussions

### 项目相关
- 📧 邮箱: songshgeo@gmail.com
- 📖 文档: 本项目 docs 目录

---

**创建日期**: 2025-10-20
**状态**: ✅ 配置完成，随时可部署
**部署方式**: Vercel + GitHub Pages（双重保险）

