# 华南生计演变模型

## 模型功能

本模型目前包含以下主要功能：

1. 模拟狩猎采集者、普通农民和水稻农民三类人群的互动。
2. 考虑地形因素(如海拔、坡度)对人群分布的影响。
3. 支持人口增长、迁移和转化等动态过程。
4. 提供多种数据可视化方法，如人口分布热力图、人口变化趋势图等。
5. 灵活的转化机制控制，可独立开关不同类型的转化。
6. 严格的人口守恒机制，确保扩散和合并过程的准确性。

> **最新更新 (v2.0)**：模型经过大幅度重构，删除了竞争机制，增加了转化控制开关，优化了初始化流程。详见 [变更日志](tech/changelog_v2.md)。

## 开始使用

- 首先参照[快速开始]安装并使用模型
- 接下来仔细阅读[模型工作流]确认模型运行逻辑
- 然后参考[参数配置]调试模型参数，运行自己的实验
- 最后使用[数据输出与分析]中的方法分析实验结果

## 方法说明

- [模型工作流](api/model.md)
- [模型时序图](tech/sequence_diagram.md) - 🆕 可视化流程图
- [农民主体方法](api/farmer.md)
- [狩猎采集者主体方法](api/hunter.md)
- [斑块与环境](api/env.md)

## 关于作者

- 作者：[宋爽]
- 邮箱：songshgeo[at]gmail.com

## 部署状态

- 📚 文档已通过 GitHub Actions 自动部署到 Vercel
- 🔄 每次文档更新都会自动触发重新部署
- 🌐 访问地址：[https://south-china-livehood-evolution.vercel.app](https://south-china-livehood-evolution.vercel.app)
- ✅ Vercel secrets 已配置完成，测试部署中...

<!-- Links -->
[快速开始]: usage/quick_start.md
[模型工作流]: usage/workflow.md
[参数配置]: usage/config.md
[数据输出与分析]: usage/plots.md
[宋爽]: https://cv.songshgeo.com/
