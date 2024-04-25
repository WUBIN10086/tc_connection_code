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
x2, y2 = 4, 0
d = Distance(x1, y1, x2, y2)

# P1的取值范围
P1_values = np.arange(-31, -80, -2)  # 从 -31 dBm 到 -75 dBm

# 计算每个P1下的吞吐量
throughput_values = []
P1_mW_labels = []
for P1 in P1_values:
    RSS = Rss_calculate(alpha, P1, d, nk, Wk)
    throughput = Calculate_throughput(a, b, c, RSS)
    throughput_values.append(throughput)
    mW_value = dBm_to_mW(P1)
    P1_mW_labels.append(f"{mW_value:.3f} ")
    #P1_mW_labels.append(f"{P1} dBm / {mW_value:.2f} mW")
# 计算吞吐量的一阶和二阶导数
throughput_deriv1 = np.gradient(throughput_values, P1_values)
throughput_deriv2 = np.gradient(throughput_deriv1, P1_values)

# 找到二阶导数的拐点
peaks, _ = find_peaks(np.abs(throughput_deriv2))
print([(P1_mW_labels[peak], throughput_values[peak]) for peak in peaks])

# 找到最大吞吐量对应的传输功率
max_throughput_index = np.argmax(throughput_values)
max_throughput_P1 = P1_values[max_throughput_index]
max_throughput_mW = P1_mW_labels[max_throughput_index]

# 重新计算最大吞吐量对应的 RSS 和吞吐量
max_throughput_RSS = Rss_calculate(alpha, max_throughput_P1, d, nk, Wk)
max_throughput = Calculate_throughput(a, b, c, max_throughput_RSS)

print("Max Throughput at Max Transmission:{:.2f}".format(max_throughput))

peaks, _ = find_peaks(np.abs(throughput_deriv2))


plt.rcParams['font.size'] = 14  # 可以根据需要调整大小

# 绘制图形
plt.figure(figsize=(15, 6.5))
plt.plot(P1_mW_labels, throughput_values, marker='o', label='Throughput')
plt.plot([P1_mW_labels[peak] for peak in peaks], [throughput_values[peak] for peak in peaks], 'ro', label='Inflection Points')
plt.xscale('log')
plt.title("Relationship between Transmission Power and Throughput", fontsize=25)  # 调整标题大小
plt.xlabel("Transmission Power(mW)", fontsize=20)  # 调整x轴标签大小
plt.ylabel("Throughput(Mbps)", fontsize=20)  # 调整y轴标签大小

plt.grid(True)

plt.xticks([P1_mW_labels[peak] for peak in peaks], [P1_mW_labels[peak] for peak in peaks])


plt.legend(fontsize=20)  # 调整图例大小
plt.xticks(fontsize=19.5)  # 调整x轴刻度大小
plt.yticks(fontsize=20)  # 调整y轴刻度大小

plt.show()
