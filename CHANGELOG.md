
<a id='changelog-0.6.2'></a>
# 0.6.2 — 2024-10-08

## New Features

- [x] #feat✨ 绘制两组参数对应结果的热力图

## Documentation changes

- [x] #docs📄 根据最新的模型重写文档架构

## Fixed bugs

- [x] #bug🐛 修复了不能改变初始狩猎采集者数量的问题
- [x] #bug🐛 折线图改回主体人数

## Refactoring

- [x] #refactor♻ 采用ABSESpy 0.6.9 版本的框架
- [x] 将源代码分组以便于管理

## New Features

- [x] #feat✨ 记录断点前后的增长率
- [x] #feat✨ 放宽了依赖的版本要求

<a id='changelog-0.6.1'></a>
# 0.6.1 — 2024-07-02

## Fixed bugs

- [x] #bug🐛 修复了在服务器上不能切换root的bug

<a id='changelog-0.6.0'></a>
# 0.6.0 — 2024-05-12

## Performance improvements

- [x] #zap⚡️ 可以并行运算，所以重复实验的速度提升了很多

## New Features

- [x] #feat✨ 现在可以根据多组实验结果画出带误差范围的变化曲线
- [x] #feat✨ 现在可以绘制不同重复实验后，各类主体数量的断点分布
- [x] #feat✨ 绘制对数变化后的主体数量分布热力图

## Fixed bugs

- [x] #bug🐛 修复了水体范围不正确的 bug

## Refactoring

- [x] #refactor♻️ 适配0.6.x版本的`ABSESpy`框架
- [x] #refactor♻️ 删除了新版本下过去多余的代码

<a id='changelog-0.5.0'></a>
# 0.5.0 — 2024-03-27

## Fixed bugs

- [x] #bug🐛 修复了竞争中失败者可能意外损失的 bug

## Refactoring

- [x] #refactor♻️ 适配到最近的 ABSESpy 版本 0.5.x

<a id='changelog-0.4.2'></a>
# 0.4.2 — 2024-03-20

## Fixed bugs

- [x] #bug🐛 修正为外部农民进入时间的调整

<a id='changelog-0.4.1'></a>
# 0.4.1 — 2024-03-10

## New Features

- [x] #feat✨ 现在可以检测人数哪一年发生了变化
- [x] #feat✨ 水稻农民可以设定为某个时间之前不出现（参数 `farmer.tick`）
- [x] #feat✨ 农民现在每个时间步会以一定概率按比例损失人数 （参数 `farmer.loss`）

## Documentation changes

- [x] #docs📄 在`demo.ipynb`里展示有多少适合的斑块

<a id='changelog-0.4.0'></a>
# 0.4.0 — 2024-02-04

## Fixed bugs

- [x] #bug🐛 fix(project): :rotating_light: fixing random int deprecation warning
- [x] #bug🐛 修改 mkdocs vercel 部署文档的 CI

## New Features

- [x] #feat✨ 绘制展示人口和族群数量随时间变化的堆积图
- [x] #feat✨ feat(analysis): :sparkles: 绘制聚合多个实验结果的分析图

<a id='changelog-0.3.2'></a>
# 0.3.2 — 2024-01-12

## New Features

- [x] #feat✨ inspect conversions between different breeds

## Fixed bugs

- [x] #bug🐛 fixed competing without rice farmer bug
- [x] #bug🐛 plot rice farmers' heatmap correctly

## Refactoring

- [x]  #refactor♻️ improve code format by sourcery

<a id='changelog-0.3.1'></a>
# 0.3.1 — 2024-01-11

## Performance improvements

- [x]  #zap⚡️ upgrade `seaborn` to mute the future warnings from `pandas`

## Fixed bugs

- [x]  #bug🐛 Fixing plotting for rice farmer

## New Features

- [x]  #feat✨ Add rice farmers in each step

## Documentation changes

- [x] #docs📄 update paths for `mkdocs-strings`

<a id='changelog-0.3.0'></a>
# 0.3.0 — 2024-01-05

## New Features

- [x] #feat✨ 增加种植水稻的农民

## Refactoring

- [x] #refactor♻️ 删除坡向的影响
- [x] #refactor♻️ 把适宜度改成内部代码而不是数据
- [x] #refactor♻️ 水稻和普通农民的人口上限改成参数

<a id='changelog-0.2.3'></a>
# 0.2.3 — 2023-12-11

## Fixed bugs

- [x] #bug🐛 修改两个`histplot`图一样

<a id='changelog-0.2.2'></a>
# 0.2.2 — 2023-12-11

- [x] #bug🐛 `histplot` 分布直方图修正

<a id='changelog-0.2.1'></a>
# 0.2.1 — 2023-12-09

## New Features

- [x] #feat✨ 两个新的折线图，表示农民和狩猎采集者群体的数量，而不是人数

## Refactoring

- [x] #refactor♻️ 将所有的画图功能转移到 `ModelViz` 类

<a id='changelog-0.2.0'></a>
# 0.2.0 — 2023-12-03

## New Features

- [x] #feat✨ 初始添加狩猎采集者，单个agent人数范围设置在【0,35】的区间内，即仍不存在复杂狩猎采集者
- [x] #feat✨ 农民人数超过100后就不会convert为狩猎采集者
- [x] #feat✨ 批量测试（1）init_hunters （2）convert_prob （3）loss_rate （4）intensified_coefficient

<a id='changelog-0.1.0'></a>
# 0.1.0 — 2023-11-25

## Fixed bugs

- [x] #bug🐛 修复了农民主体出生在已有主体斑块的情况
- [x] #bug🐛 修复了失败的狩猎采集者因为复杂化不会逃跑的情况
- [x] #bug🐛 修复了人口不会自然增长的问题

## New Features

- [x] #feat✨ 使用外部数据作为狩猎采集者的人口承载力上限

- [x] #feat✨ 农民只于可耕种区域定居，并会在搜索范围内优先选择可耕适宜度更高的地块（具体适宜度待细化）；

- [x] #feat✨ 开局设置存在部分狩猎采集者，其群体个数可以按地块数1％-5％来设置，数量在范围内（6-地块上限）随机；

- [x] #feat✨ 生成模拟结果中人群具体分布的热力图
- [x] #feat✨ 汇报每个agent具体的数量、位置等属性

## Documentation changes

- [x] #docs📄 更新文档并发布
- [x] #docs📄 更新版本日志
