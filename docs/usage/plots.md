---
title: 实验结果的展示
author: Shuang Song
---

## 绘制热图

通过调整[绘制热图的变量参数]`plot_heatmap`，可以绘制不同的模拟结果：

- 当`plot_heatmap`为`None`时，不绘制热图。
- 当`plot_heatmap`为`bkp_farmer`时，绘制[农民]的断点平均所在位置。
- ... 还可以设置为[运行结束时]保存的其它可用变量，如`bkp_rice`、`len_farmers`、`len_rice`等。

如下图中，热力图代表[农民]的断点平均所在位置，无论 `env.lam_farmer` 和 `env.init_hunters` 两个实验的参数值怎样变化，断点平均位置（记住每个实验重复5次）基本不变，都出现在 `tick=5` 附近。

<img src="https://songshgeo-picgo-1302043007.cos.ap-beijing.myqcloud.com/uPic/WechatIMG6621.jpg" alt="Drawing" style="width: 400px;”/>

<!-- Links -->
  [绘制热图的变量参数]: ./config.md#exp
  [运行结束时]: ./workflow.md#结束（End）
