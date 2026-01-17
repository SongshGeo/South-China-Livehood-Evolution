# 参数配置

## 基本配置

模型支持通过配置文件进行参数设置，主要配置文件位于 `config/config.yaml`。

## 主要参数

### 环境参数
- `env.init_hunters`: 初始狩猎采集者比例
- `env.lam_farmer`: 农民转化参数
- `env.demographic`: 人口统计参数

### 模拟参数
- `simulation.steps`: 模拟步数
- `simulation.seed`: 随机种子

## 配置示例

```yaml
env:
  init_hunters: 0.1
  lam_farmer: 2.0
  demographic:
    birth_rate: 0.02
    death_rate: 0.01
```

## 更多信息

详细的参数说明请参考 [API 文档](/docs/api/env)。
