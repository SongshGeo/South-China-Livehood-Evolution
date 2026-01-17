---
title: 断点检测
author: Shuang Song
---

## 断点检测方法

断点检测使用[`ruptures`]库实现。

本模型中，断点检测方法 `detect_breakpoints` 默认调用 [`Dynp` 算法]，用户必须指定 `n_bkps` 参数，即期望有多少个断点，在这里默认 `n_bkps=1`，即只检测一个断点。同时，用户还需要指定 `min_size` 参数，即每个断点之间至少包含多少个数据点，在这里默认 `min_size=5`，这意味着在检测断点时若少于5个数据点（比如模型只运行了4年），则不进行断点检测。

可替代的断点检测方法包括：

- `Dynp` 算法
- `Binseg` 算法
- `BottomUp` 算法
- `Window` 算法

:::src.workflow.analysis.detect_breakpoints

## 检测目标变量

检测会对所有三类主体（狩猎采集者、农民、水稻）进行断点检测，检测目标变量有四种，分别是：

1. 人口绝对数量：size
2. 人口占总人口的相对比例：ratio
3. 人口群体数量：group
4. 人口群体占总人口的相对比例：group_ratio

<!-- Links -->
  [`ruptures`]: https://centre-borelli.github.io/ruptures-docs/
  [Dynp 算法]: https://centre-borelli.github.io/ruptures-docs/user-guide/detection/dynp/?h=dynp#dynamic-programming-dynp
