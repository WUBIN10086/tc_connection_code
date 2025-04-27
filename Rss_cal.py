import math
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

# 读取测量数据，没有表头，自己设定列名
data = pd.read_csv("test.csv", header=None, names=['Name', 'Value'])

# 去除字符串前后空白并清理非数字行
data['Name'] = data['Name'].str.strip()
data['Value'] = data['Value'].str.strip()
data = data[~data['Value'].isin(['Measurement'])]

# 把Value列转成float
data['Value'] = data['Value'].astype(float)

# 重新提取P1和Pd列表
# AP1部分
data_ap1 = data.iloc[0:15]
P1_ap1 = data_ap1.iloc[0]['Value']
Pd_list1 = data_ap1.iloc[1:]['Value'].tolist()

# AP2部分
data_ap2 = data.iloc[15:30]
P1_ap2 = data_ap2.iloc[0]['Value']
Pd_list2 = data_ap2.iloc[1:]['Value'].tolist()

# 第1组 AP 和 Hosts
ap1 = (1.5, 8.5)
hosts1 = [
    (1.5, 11.2), (1.5, 13.0), (3.5, 12.0), (4.5, 15.0),
    (8.5, 10.5), (8.5, 14.0), (12.5, 12.0), (12.5, 15.0),
    (14.0, 10.0), (15.7, 15.0), (4.5, 6.0), (5.5, 2.5),
    (6.5, 6.5), (8.5, 2.5)
]

# 第2组 AP 和 Hosts
ap2 = (8.5, 7.5)
hosts2 = [
    (1.0, 10.8), (2.0, 14.5), (5.2, 10.3), (6.5, 12.0),
    (8.5, 11.8), (8.6, 14.9), (10.5, 12.5), (12.5, 15.5),
    (14.5, 10.5), (13.5, 14.5), (4.5, 6.5), (4.5, 3.5),
    (6.5, 6.5), (7.5, 3.0)
]

# 计算欧氏距离
def euclidean_distance(p1, p2):
    return math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)

# 计算各组距离
distances1 = [euclidean_distance(ap1, host) for host in hosts1]
distances2 = [euclidean_distance(ap2, host) for host in hosts2]

# 计算alpha
def calculate_alpha(P1, Pd, d):
    if d <= 0:
        raise ValueError("Distance must be positive.")
    return (P1 - Pd) / (10 * math.log10(d))

# 计算所有alpha
alphas1 = [calculate_alpha(P1_ap1, Pd_list1[i], distances1[i]) for i in range(len(hosts1))]
alphas2 = [calculate_alpha(P1_ap2, Pd_list2[i], distances2[i]) for i in range(len(hosts2))]

# 合并所有log10(d)和(P1-Pd)
dists_log1 = [math.log10(d) for d in distances1]
dists_log2 = [math.log10(d) for d in distances2]
all_logs = np.array(dists_log1 + dists_log2)
all_P1_minus_Pd = np.array([
    P1_ap1 - Pd for Pd in Pd_list1
] + [
    P1_ap2 - Pd for Pd in Pd_list2
])

# 最小二乘拟合 (y = 10 * alpha * log10(d))
A = 10 * all_logs
alpha_fit = np.sum(A * all_P1_minus_Pd) / np.sum(A * A)

# 计算所有alpha的平均值
all_alphas = alphas1 + alphas2
alpha_avg = sum(all_alphas) / len(all_alphas)

print("\n=== Least Squares Fitting Result ===")
print(f"Fitted Alpha (Least Squares) = {alpha_fit:.2f}")
print(f"Average Alpha = {alpha_avg:.2f}")

# 绘图
plt.figure(figsize=(8,6))
plt.scatter(A, all_P1_minus_Pd, color='blue', label='Data points')
plt.plot(A, alpha_fit * A, color='red', label=f'Fitted line (alpha={alpha_fit:.2f})')
plt.xlabel('10 * log10(d)')
plt.ylabel('P1 - Pd')
plt.title('Least Squares Fit for Alpha')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()
