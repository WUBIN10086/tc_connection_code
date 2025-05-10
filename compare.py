import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

# m ？
m_values = np.array([1, 2, 3, 4, 5, 6, 7])

# 原始数据
data = np.array([
    [394, 394, 391, 384.9, 383.66, 361.59, 347.26],
    [398, 395, 393, 387,   377.85, 357,    345.42],
    [395, 393, 390, 388.29,379.3,  355.07, 336.5 ]
])

# 平均？
tp_mean = data.mean(axis=0)

# SRF公式（？个 host 的？吐量）
def srf(m):
    return (1 / (m + 0.1 * (m - 1) / 4)) * (1 - (0.1 * (m - 1)))

# 估？的？？吐量（乘上 m）
srf_values = srf(m_values)
srf_scaled_total = srf_values * tp_mean[0] * m_values

# ？？？差和相？？差（百分比）
error = tp_mean - srf_scaled_total
percent_error = (error / tp_mean) * 100

# 画？
plt.figure(figsize=(10, 6))
plt.plot(m_values, tp_mean, 'o-', label='Measured Total Throughput')
plt.plot(m_values, srf_scaled_total, 's--', label='SRF Estimated Total Throughput')
plt.xlabel('Number of Hosts (m)', fontsize=16)
plt.ylabel('Throughput (Mbps)', fontsize=16)
plt.title('Measured vs SRF Estimated Total Throughput', fontsize=18)
plt.xticks(fontsize=14)
plt.yticks(fontsize=14)
plt.legend(fontsize=14)
plt.grid(True)
plt.tight_layout()
plt.show()

# ？出？差表格
df = pd.DataFrame({
    'm': m_values,
    'Measured Mean': tp_mean,
    'SRF Estimated (Total)': srf_scaled_total,
    'Error (Measured - Estimated)': error,
    'Relative Error (%)': percent_error
})
print(df.round(2))
