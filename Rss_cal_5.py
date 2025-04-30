import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os
import math
from scipy.optimize import curve_fit

# =====================================
# 手动指定 P1（单位：dBm）
# =====================================
p1_value = -28.31

# =====================================
# 读取用于 α 计算的 Pd（all_rss.csv）
# =====================================
Pd_alpha = pd.read_csv("all_rss.csv", header=None).iloc[:, 0].values

# =====================================
# 指定距离（每4个样本一组：3m、5m、10m）
# =====================================
distances = [
    3, 3, 3, 3,    # 3米
    5, 5, 5, 5,    # 5米
    10, 10, 10, 10 # 10米
]
assert len(distances) == len(Pd_alpha), "distances长度必须等于all_rss.csv行数"

# =====================================
# 计算每个α
# =====================================
A = 10 * np.log10(distances)
alpha_list = []
print("\n=== Individual α values ===")
for i, (pd1, a, d) in enumerate(zip(Pd_alpha, A, distances), 1):
    α = (p1_value - pd1) / a
    print(f"Sample {i} (d={d}m): α = {α:.2f}")
    alpha_list.append(α)

valid = ~np.isnan(alpha_list)
P1_minus_Pd = p1_value - Pd_alpha
alpha_fit = np.sum(A[valid] * P1_minus_Pd[valid]) / np.sum(A[valid] * A[valid])
alpha_avg = np.nanmean(alpha_list)

print(f"\nFitted α (Least Squares): {alpha_fit:.2f}")
print(f"Average α               : {alpha_avg:.2f}")

# =====================================
# 读取用于Sigmoid的Pd（all_rsss.csv）和Sh（all_thr.csv）
# =====================================
Pd_sigmoid = pd.read_csv("all_rsss.csv", header=None).iloc[:, 0].values
Sh_array   = pd.read_csv("all_thr.csv",  header=None).iloc[:, 0].values
assert len(Pd_sigmoid) == len(Sh_array), "all_rsss和all_thr长度必须一致"

# =====================================
# Sigmoid拟合
# =====================================
def sigmoid(Pd1, a, b, c):
    return a / (1 + np.exp(-((120 + Pd1) - b) / c))

p0 = [max(Sh_array), 120, 10]
popt, _ = curve_fit(sigmoid, Pd_sigmoid, Sh_array, p0=p0, maxfev=10000)
a, b, c = popt

print("\n=== Sigmoid Fit Result ===")
print(f"a = {a:.4f}")
print(f"b = {b:.4f}")
print(f"c = {c:.4f}")

# =====================================
# 绘图
# =====================================
os.makedirs("output", exist_ok=True)

# α拟合图
plt.figure(figsize=(6,4))
plt.scatter(A, P1_minus_Pd, label='Data points')
plt.plot(A, alpha_fit*A, label=f'Fit α={alpha_fit:.2f}')
plt.xlabel('10·log10(d)')
plt.ylabel('P1 - Pd')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig("output/alpha_fit.png")
plt.close()

# Sigmoid拟合图
Pd_range = np.linspace(Pd_sigmoid.min(), Pd_sigmoid.max(), 200)
Sh_fit   = sigmoid(Pd_range, *popt)
plt.figure(figsize=(6,4))
plt.scatter(Pd_sigmoid, Sh_array, label='Measured Sh')
plt.plot(Pd_range, Sh_fit, label='Fitted Sigmoid')
plt.xlabel('Pd (RSS from all_rsss)')
plt.ylabel('Sh (Throughput)')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig("output/sigmoid_fit.png")
plt.close()

# 保存参数
with open("output/fitted_parameters.txt", "w") as f:
    f.write(f"P1 (manual)          : {p1_value:.4f} dBm\n")
    f.write(f"Alpha (LeastSquares) : {alpha_fit:.4f}\n")
    f.write(f"Alpha (Average)      : {alpha_avg:.4f}\n")
    f.write(f"Sigmoid a            : {a:.4f}\n")
    f.write(f"Sigmoid b            : {b:.4f}\n")
    f.write(f"Sigmoid c            : {c:.4f}\n")

print("\n=== Results saved in 'output/' folder ===")
