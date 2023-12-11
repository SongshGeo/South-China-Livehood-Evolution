
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
