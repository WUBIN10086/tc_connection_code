import matplotlib.pyplot as plt
import numpy as np
from throughput_estimation import calculate_throughput_estimate, Calculate_throughput, Rss_calculate

def plot_throughput_vs_signal_strength(parameters, host_coordinates, ap_coordinates, nk, max_distance):
    distances = np.linspace(0, max_distance, 100)
    signal_strengths = []
    throughputs = []

    x1, y1 = host_coordinates
    x2, y2 = ap_coordinates

    for distance in distances:
        try:
            adjusted_ap_coordinates = (x2, y2 + distance)
            Pd = Rss_calculate(parameters['alpha'], parameters['P_1'], distance, nk, parameters['Wk'])
            if isinstance(Pd, str):
                continue  # 如果Pd是字符串（表示错误），跳过这个循环
            Thr_estimation = Calculate_throughput(parameters['a'], parameters['b'], parameters['c'], Pd)
            signal_strengths.append(Pd)
            throughputs.append(Thr_estimation)
        except Exception as e:
            print(f"Error at distance {distance}: {e}")
            continue

    plt.figure(figsize=(10, 5))
    plt.plot(signal_strengths, throughputs, label='Throughput vs Signal Strength')
    plt.xlabel('Signal Strength (dBm)')
    plt.ylabel('Estimated Throughput (Mbps)')
    plt.title('Throughput Estimation vs Signal Strength')
    plt.legend()
    plt.grid(True)
    plt.show()

# 示例参数
parameters = {
    'alpha': 2.2,
    'P_1': -28.9,
    'a': 59.5,
    'b': 62,
    'c': 6.78,
    'Wk': [7.21,6.9,3.4,4.7,2.11,2.5]
}

# 使用示例
plot_throughput_vs_signal_strength(parameters, (0, 0), (0, 0), [1, 1, 1, 1, 1, 1], 5)
