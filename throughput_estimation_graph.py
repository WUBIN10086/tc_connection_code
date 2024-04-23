import math
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks

# 定义距离计算函数
def Distance(x1, y1, x2, y2):
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

# 定义 RSS 计算函数
def Rss_calculate(alpha, P_1, d, nk, Wk):
    sum_nk_Wk = sum(nk_i * Wk_i for nk_i, Wk_i in zip(nk, Wk))
    RSS = P_1 - 10 * alpha * math.log10(d) - sum_nk_Wk
    return RSS

# 定义吞吐量计算函数
def Calculate_throughput(a, b, c, Pd):
    exponent = -(120 + Pd - b) / c
    throughput = a / (1 + math.exp(exponent))
    return throughput

# 定义 dBm 到 mW 的转换函数
def dBm_to_mW(dBm):
    return 10 ** ((dBm) / 10)*100000

# 参数设置
alpha = 2.15
a = 133
b = 58
c = 6.3
nk = [0]
Wk = [0]

# 设备坐标
x1, y1 = 0, 0
x2, y2 = 3, 0
d = Distance(x1, y1, x2, y2)

# P1的取值范围
P1_values = np.arange(-31, -66, -1.5)  # 从 -31 dBm 到 -75 dBm

# 计算每个P1下的吞吐量
throughput_values = []
P1_mW_labels = []
for P1 in P1_values:
    RSS = Rss_calculate(alpha, P1, d, nk, Wk)
    throughput = Calculate_throughput(a, b, c, RSS)
    throughput_values.append(throughput)
    mW_value = dBm_to_mW(P1)
    P1_mW_labels.append(f"{mW_value:.2f} ")
    #P1_mW_labels.append(f"{P1} dBm / {mW_value:.2f} mW")
# 计算吞吐量的一阶和二阶导数
throughput_deriv1 = np.gradient(throughput_values, P1_values)
throughput_deriv2 = np.gradient(throughput_deriv1, P1_values)

# 找到二阶导数的拐点
peaks, _ = find_peaks(np.abs(throughput_deriv2))
print([(P1_mW_labels[peak], throughput_values[peak]) for peak in peaks])

# 绘制图形
plt.figure(figsize=(20, 10))
plt.plot(P1_mW_labels, throughput_values, marker='o', label='Throughput')
plt.plot([P1_mW_labels[peak] for peak in peaks], [throughput_values[peak] for peak in peaks], 'ro', label='Inflection Points')
plt.title("Relationship between Transmission Power and Throughput")
plt.xlabel("Transmission Power(mW)")
plt.ylabel("Throughput")
plt.grid(True)
plt.legend()
plt.show()
