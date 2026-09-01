# 常用命令速查

依赖由 [uv](https://docs.astral.sh/uv/) 管理：运行时依赖声明在 `pyproject.toml` 的 `[project]`，开发与 notebook 工具在 `[dependency-groups]`，版本锁定在 `uv.lock`。

## 环境

```bash
uv sync                 # 运行时 + 开发依赖（pytest、black、flake8、isort、pre-commit）
uv sync --all-groups    # 额外装上 notebook 组（ipykernel、jupyterlab）
uv lock                 # 修改 pyproject.toml 后刷新锁文件
make install-pre-commit # 安装 git 钩子
```

## 运行模型

```bash
# 快速测试（20 步，不重复）
uv run python -m src time.end=20 exp.repeats=1

# 标准运行（30 步，3 次重复）
uv run python -m src time.end=30 exp.repeats=3

# 参数扫描：所有取值的笛卡尔积
uv run python -m src --multirun \
    env.init_hunters=0.05,0.1,0.2 \
    env.lam_farmer=1,2,3
```

参数含义见[参数配置](/docs/usage/config)。

## 测试

```bash
make test                                  # 全量测试 + 覆盖率（走 allure）
uv run pytest tests/ -v                    # 全量测试
uv run pytest tests/test_hunters.py -v     # 单个文件
uv run pytest tests/ --cov=src             # 覆盖率
```

## 代码风格

三个工具的版本在 `pyproject.toml` 中被钉死到与 `.pre-commit-config.yaml` 相同的版本，所以命令行与钩子的结果一定一致。

```bash
uv run black src tests
uv run isort --profile=black src tests
uv run flake8 src tests        # 配置读取仓库根的 .flake8
uv run pre-commit run --all-files
```

## 对比实验

转化机制可以整体关闭，也可以按路径单独关闭：

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

命令行覆盖同样可用：

```bash
uv run python -m src convert.enabled=true    # 实验 1：有转化机制
uv run python -m src convert.enabled=false   # 实验 2：无转化机制
```

## 文档

```bash
cd docs-docusaurus
npm ci && npm run start   # 本地预览
npm run build             # 生产构建
```

详见[部署说明](../tech/deployment.md)。
