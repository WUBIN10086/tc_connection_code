import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.interpolate import UnivariateSpline

# 读取CSV文件，假设文件名为"data.csv"，并指定没有头部（header=None）
data = pd.read_csv("data.csv", header=None, names=['H4', 'p_t'])

# 确保数据被正确解析为数值类型

data['H4'] = pd.to_numeric(data['H4'], errors='coerce')
data['p_t'] = pd.to_numeric(data['p_t'], errors='coerce')

# 删除因转换错误可能产生的任何NaN值
data.dropna(inplace=True)

# 提取H4和p_t的数据
h4_values = data['H4']
pt_values = data['p_t']

# 排序数据以确保p_t是递增的
sorted_indices = np.argsort(pt_values)
sorted_pt = pt_values.iloc[sorted_indices].values
sorted_h4 = h4_values.iloc[sorted_indices].values

# 使用四次样条函数拟合数据
spline_sorted = UnivariateSpline(sorted_pt, sorted_h4, s=0, k=4)

# 计算并绘制拟合曲线及其二阶导数
#pt_fine_sorted = np.linspace(min(sorted_pt), max(sorted_pt), 300)
pt_fine_sorted = np.linspace(min(sorted_pt), max(sorted_pt), 300)
h4_spline_sorted = spline_sorted(pt_fine_sorted)

# 找出二阶导数的极值点，即转折点
h4_second_derivative_sorted = spline_sorted.derivative(n=2)(sorted_pt)
extrema_indices = np.where(np.diff(np.sign(np.diff(h4_second_derivative_sorted))) != 0)[0] + 1

for idx in extrema_indices:
    print(f"转折点坐标: p_t = {sorted_pt[idx]}, H4 = {sorted_h4[idx]}")
# 绘制结果
plt.figure(figsize=(8, 6))
plt.scatter(sorted_pt, sorted_h4, color='blue', label='data')
plt.plot(sorted_pt, spline_sorted(sorted_pt), 'r-', label='Curve fitting')
plt.scatter(sorted_pt[extrema_indices], spline_sorted(sorted_pt)[extrema_indices],
            color='green', s=100, label='turning point', zorder=5)
plt.xlabel('Transmission Power [dbm]', fontsize=16)
plt.ylabel('Throughput (Mb/s)', fontsize=16)
plt.title('AP1 at 2.4Ghz', fontsize=20)
plt.tick_params(axis='x', labelsize=14)  # 设置x轴刻度标签的字体大小
plt.tick_params(axis='y', labelsize=14)  # 设置y轴刻度标签的字体大小
plt.legend(fontsize=12)
plt.grid(True)
plt.show()
