import math
import numpy as np
import matplotlib.pyplot as plt

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
P1_values = np.arange(-31, -75, -5)  # 从 -31 dBm 到 -80 dBm

# 计算每个P1下的吞吐量
throughput_values = []
P1_mW_labels = []
for P1 in P1_values:
    RSS = Rss_calculate(alpha, P1, d, nk, Wk)
    throughput = Calculate_throughput(a, b, c, RSS)
    throughput_values.append(throughput)
    mW_value = dBm_to_mW(P1)
    P1_mW_labels.append(f"{P1} dBm / {mW_value:.2f} mW")
    #P1_mW_labels.append(f"{mW_value:.2f} mW")
    #P1_mW_labels.append(f"{P1} dBm ")

# 绘制 P1 与吞吐量的关系图
plt.figure(figsize=(20, 10))
plt.plot(P1_mW_labels, throughput_values, marker='o')
plt.title("Relationship between P1 and Throughput")
plt.xlabel("P1 (dBm / mW)")
plt.ylabel("Throughput")
plt.grid(True)
#plt.xticks(rotation=90)  #旋转标签以提高可读性
plt.show()
