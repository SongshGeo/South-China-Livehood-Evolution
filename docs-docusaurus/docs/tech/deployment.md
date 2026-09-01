# 部署说明

本站点由 [Docusaurus](https://docusaurus.io/) 构建，源文件全部位于仓库的 `docs-docusaurus/` 目录。这是本项目**唯一**的文档来源——早先并存的 mkdocs 站点（`docs/` + `mkdocs.yml`）已经移除，其内容全部合并到了这里。

## 目录结构

```
docs-docusaurus/
├── docs/                 # 中文文档（默认语言）
│   ├── intro.md
│   ├── UPDATES.md
│   ├── usage/
│   ├── api/
│   └── tech/
├── i18n/en/docusaurus-plugin-content-docs/current/
│                         # 英文文档，路径与 docs/ 一一对应
├── sidebars.ts           # 侧边栏导航（新增页面必须在此登记）
├── docusaurus.config.ts  # 站点配置
└── package.json
```

## 本地预览

```bash
cd docs-docusaurus
npm ci
npm run start        # 开发服务器，热重载
npm run build        # 生产构建，等同 CI 所做的事
npm run serve        # 预览 build 产物
```

默认语言（中文）在 `/`，英文在 `/en/`。开发服务器一次只跑一个语言，要预览英文用：

```bash
npm run start -- --locale en
```

## 自动部署

两条流水线都从仓库根目录消费同一份源文件：

| 目标 | 触发 | 定义于 |
|------|------|--------|
| GitHub Pages | push 到 `main` / `master` / `dev` | `.github/workflows/docusaurus-pages.yml` |
| Vercel | Vercel 侧的 Git 集成 | `vercel.json`（`cd docs-docusaurus && npm ci && npm run build`） |

`deploy.sh` 封装了手动触发 Vercel 部署的步骤。

## 新增或修改页面

1. 在 `docs-docusaurus/docs/` 下创建中文页面。
2. 若需要英文版，在 `i18n/en/docusaurus-plugin-content-docs/current/` 下创建**同名同路径**的文件。
3. 在 `sidebars.ts` 中登记页面 ID（不含 `.md` 后缀的相对路径），否则页面不会出现在导航里。
4. 本地 `npm run build` 验证——构建会报出失效链接（`onBrokenLinks: 'warn'`）。

## 故障排除

- **页面没出现在侧边栏**：检查 `sidebars.ts` 里的 ID 是否与文件路径一致。
- **构建报失效链接**：Docusaurus 解析相对 `.md` 链接；中文锚点（如 `#结束（End）`）可能无法解析，改用英文锚点或直接链接到页面。
- **英文页面 404**：确认 `i18n/en/.../current/` 下存在同路径文件，且 `docusaurus.config.ts` 的 `i18n.locales` 包含 `'en'`。
