# 结果分析

## 数据输出

模型运行后会生成多种数据文件，用于后续分析。

## 主要输出文件

### CSV 数据文件
- `conversion.csv`: 转化数据
- `population.csv`: 人口数据
- `summary.csv`: 汇总数据

### 图像文件
- `dynamic.jpg`: 动态变化图
- `heatmap.jpg`: 热力图

## 分析方法

### 1. 人口分布分析
通过热力图分析不同人群的空间分布特征。

### 2. 时间序列分析
分析人口变化的时间趋势和转化模式。

### 3. 统计指标
- 总人口变化
- 转化率统计
- 空间聚集度

## 可视化工具

推荐使用以下工具进行数据分析：
- Python: pandas, matplotlib, seaborn
- R: ggplot2, dplyr
- 其他: Excel, Origin

## 示例代码

```python
import pandas as pd
import matplotlib.pyplot as plt

# 读取数据
data = pd.read_csv('conversion.csv')

# 绘制时间序列图
plt.plot(data['step'], data['hunters'])
plt.xlabel('时间步')
plt.ylabel('狩猎采集者数量')
plt.title('狩猎采集者数量变化')
plt.show()
```

## 绘制热图

通过调整[配置文件](/docs/usage/config)中 `exp` 部分的 `plot_heatmap` 参数，可以绘制不同的模拟结果：

- 当 `plot_heatmap` 为 `None` 时，不绘制热图。
- 当 `plot_heatmap` 为 `bkp_farmer` 时，绘制农民的断点平均所在位置。
- 还可以设置为运行结束时保存的其它可用变量，如 `bkp_rice`、`len_farmers`、`len_rice` 等。

如下图中，热力图代表农民的断点平均所在位置。无论 `env.lam_farmer` 和 `env.init_hunters` 两个实验参数的取值怎样变化，断点平均位置（每个实验重复 5 次）基本不变，都出现在 `tick=5` 附近。

<img src="https://songshgeo-picgo-1302043007.cos.ap-beijing.myqcloud.com/uPic/WechatIMG6621.jpg" alt="断点位置热图" style={{width: 400}} />
