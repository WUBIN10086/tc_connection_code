import math
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from scipy.optimize import curve_fit
import os

# =====================================
# 读取 RSS 测量数据（test.csv）
# =====================================
data = pd.read_csv("test.csv", header=None, names=['Name', 'Value'])
data['Name'] = data['Name'].str.strip()
data['Value'] = data['Value'].str.strip()
data = data[data['Value'] != 'Measurement']
data['Value'] = data['Value'].astype(float)

# =====================================
# 提取P1和Pd
# =====================================
data_ap1 = data.iloc[0:15]
P1_ap1 = data_ap1.iloc[0]['Value']
Pd_list1 = data_ap1.iloc[1:]['Value'].tolist()

data_ap2 = data.iloc[15:30]
P1_ap2 = data_ap2.iloc[0]['Value']
Pd_list2 = data_ap2.iloc[1:]['Value'].tolist()

# =====================================
# 定义AP位置和Host位置
# =====================================
ap1 = (1.5, 8.5)
hosts1 = [
    (1.5, 11.2), (1.5, 13.0), (3.5, 12.0), (4.5, 15.0),
    (8.5, 10.5), (8.5, 14.0), (12.5, 12.0), (12.5, 15.0),
    (14.0, 10.0), (15.7, 15.0), (4.5, 6.0), (5.5, 2.5),
    (6.5, 6.5), (8.5, 2.5)
]

ap2 = (8.5, 7.5)
hosts2 = [
    (1.0, 10.8), (2.0, 14.5), (5.2, 10.3), (6.5, 12.0),
    (8.5, 11.8), (8.6, 14.9), (10.5, 12.5), (12.5, 15.5),
    (14.5, 10.5), (13.5, 14.5), (4.5, 6.5), (4.5, 3.5),
    (6.5, 6.5), (7.5, 3.0)
]

# =====================================
# 计算欧氏距离
# =====================================
def euclidean_distance(p1, p2):
    return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)

distances1 = [euclidean_distance(ap1, host) for host in hosts1]
distances2 = [euclidean_distance(ap2, host) for host in hosts2]

# 打印欧氏距离
print("\n=== Distances from AP1 ===")
for idx, d in enumerate(distances1, 1):
    print(f"Host {idx}: {d:.2f} meters")

print("\n=== Distances from AP2 ===")
for idx, d in enumerate(distances2, 1):
    print(f"Host {idx}: {d:.2f} meters")

# =====================================
# 计算 alpha
# =====================================
def calculate_alpha(P1, Pd, d):
    if d <= 0:
        raise ValueError("Distance must be positive.")
    return (P1 - Pd) / (10 * math.log10(d))

alphas1 = [calculate_alpha(P1_ap1, Pd_list1[i], distances1[i]) for i in range(len(hosts1))]
alphas2 = [calculate_alpha(P1_ap2, Pd_list2[i], distances2[i]) for i in range(len(hosts2))]

dists_log1 = [math.log10(d) for d in distances1]
dists_log2 = [math.log10(d) for d in distances2]
all_logs = np.array(dists_log1 + dists_log2)
all_P1_minus_Pd = np.array([
    P1_ap1 - Pd for Pd in Pd_list1
] + [
    P1_ap2 - Pd for Pd in Pd_list2
])

A = 10 * all_logs
alpha_fit = np.sum(A * all_P1_minus_Pd) / np.sum(A * A)
all_alphas = alphas1 + alphas2
alpha_avg = sum(all_alphas) / len(all_alphas)

print("\n=== Least Squares Fitting Result ===")
print(f"Fitted Alpha (Least Squares) = {alpha_fit:.2f}")
print(f"Average Alpha = {alpha_avg:.2f}")

# 绘制 alpha 拟合图
plt.figure(figsize=(8,6))
plt.scatter(A, all_P1_minus_Pd, color='blue', label='Data points')
plt.plot(A, alpha_fit * A, color='red', label=f'Fitted line (alpha={alpha_fit:.2f})')
plt.xlabel('10 * log10(d)')
plt.ylabel('P1 - Pd')
plt.title('Least Squares Fit for Alpha')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig("alpha_fit.png")
plt.show()

# =====================================
# 读取 Sh 测量数据（test2.csv）
# =====================================
sh_data = pd.read_csv("test2.csv", names=['Name', 'Sh'])
sh_data['Name'] = sh_data['Name'].str.strip()
sh_data['Sh'] = sh_data['Sh'].astype(str).str.strip()
sh_data = sh_data[sh_data['Sh'] != 'Measurement']
sh_data['Sh'] = sh_data['Sh'].astype(float)

measured_Sh = sh_data['Sh'].values

# =====================================
# Sigmoid 曲线拟合
# =====================================
all_Pd = np.array(Pd_list1 + Pd_list2)

plt.figure(figsize=(8,6))
plt.scatter(all_Pd, measured_Sh, color='green', label='Measured Sh')
plt.xlabel('Pd')
plt.ylabel('Sh')
plt.title('Scatter of Pd vs Sh')
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.savefig("pd_vs_sh_scatter.png")
plt.show()

def sigmoid(Pd, a, b, c):
    return a / (1 + np.exp(-((120 + Pd) - b) / c))

p0 = [max(measured_Sh), 120, 10]

popt, pcov = curve_fit(sigmoid, all_Pd, measured_Sh, p0=p0, maxfev=10000)

a, b, c = popt
print("\n=== Sigmoid Curve Fitting Result ===")
print(f"a = {a:.4f}")
print(f"b = {b:.4f}")
print(f"c = {c:.4f}")

Pd_range = np.linspace(min(all_Pd), max(all_Pd), 200)
Sh_fit = sigmoid(Pd_range, *popt)

plt.figure(figsize=(8,6))
plt.scatter(all_Pd, measured_Sh, color='blue', label='Measured Sh')
plt.plot(Pd_range, Sh_fit, color='red', label='Fitted Sigmoid Curve')
plt.xlabel('Pd')
plt.ylabel('Sh')
plt.title('Sigmoid Fitting with Initial Guess')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig("sigmoid_fit.png")
plt.show()

# =====================================
# 保存结果
# =====================================
os.makedirs("output", exist_ok=True)

with open("output/fitted_parameters.txt", "w") as f:
    f.write(f"Alpha (Least Squares): {alpha_fit:.4f}\n")
    f.write(f"Alpha (Average): {alpha_avg:.4f}\n")
    f.write(f"Sigmoid a: {a:.4f}\n")
    f.write(f"Sigmoid b: {b:.4f}\n")
    f.write(f"Sigmoid c: {c:.4f}\n")

fit_data = pd.DataFrame({'Pd': Pd_range, 'Fitted_Sh': Sh_fit})
fit_data.to_csv("output/fitted_sigmoid_curve.csv", index=False)

print("\n=== All results saved in 'output/' folder ===")
