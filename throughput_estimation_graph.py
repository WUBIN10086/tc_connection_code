import matplotlib.pyplot as plt
import numpy as np
from throughput_estimation import Calculate_throughput, Rss_calculate
from math import log10

def plot_throughput_vs_transmission_power(parameters, host_coordinates, ap_coordinates, nk):
    transmission_powers = np.linspace(-100, 0, 100)  # 假设发射功率从-100 dBm到0 dBm
    throughputs = []

    # 计算固定距离
    distance = np.sqrt((host_coordinates[0] - ap_coordinates[0])**2 + (host_coordinates[1] - ap_coordinates[1])**2)
    if distance == 0:
        print("Distance is zero, please set valid coordinates.")
        return

    for tp in transmission_powers:
        try:
            # 计算接收信号强度
            Pd = tp - (-28.9 + 10 * parameters['alpha'] * log10(distance))  # 反向计算预期的Pd
            if isinstance(Pd, str):
                continue  # 如果Pd是字符串（表示错误），跳过这个循环
            # 计算吞吐量估计
            Thr_estimation = Calculate_throughput(parameters['a'], parameters['b'], parameters['c'], Pd)
            throughputs.append(Thr_estimation)
        except Exception as e:
            print(f"Error with transmission power {tp}: {e}")
            continue

    # 初始化
    transitions = []
    last_index = 0

    # 找到8个分界点
    for i in range(8):
        if last_index < len(throughputs):
            current_throughputs = throughputs[last_index:]
            current_powers = transmission_powers[last_index:]
            derivatives = np.gradient(current_throughputs, current_powers)
            change_rates = np.abs(np.gradient(derivatives, current_powers))
            transition_index = np.argmax(change_rates)
            transition_power = current_powers[transition_index]
            transition_throughput = current_throughputs[transition_index]
            transitions.append((transition_power, transition_throughput))
            last_index += transition_index + 1  # 更新索引为当前找到的分界点后的位置
        else:
            break

    # 绘制图表
    plt.figure(figsize=(10, 5))
    plt.plot(transmission_powers, throughputs, label='Throughput vs Transmission Power')
    colors = ['red', 'green', 'blue', 'orange', 'purple', 'brown', 'pink', 'grey']
    for idx, (power, throughput) in enumerate(transitions):
        plt.scatter([power], [throughput], color=colors[idx % len(colors)],
                    label=f'Transition Point {idx+1}: {power:.2f} dBm, {throughput:.2f} Mbps')
    plt.xlabel('Transmission Power (dBm)')
    plt.ylabel('Estimated Throughput (Mbps)')
    plt.title('Throughput Estimation vs Transmission Power with Multiple Transition Points')
    plt.legend()
    plt.grid(True)
    plt.show()

    # 输出分界点信息
    for idx, (power, throughput) in enumerate(transitions):
        print(f"Transition {idx+1} occurs at Transmission Power: {power:.2f} dBm with Throughput: {throughput:.2f} Mbps")

# 示例参数
parameters = {
    'alpha': 2.2,
    'P_1': -28.9,
    'a': 59.5,
    'b': 62,
    'c': 6.78,
    'Wk': [7.21, 6.9, 3.4, 4.7, 2.11, 2.5]
}

# 使用示例
plot_throughput_vs_transmission_power(parameters, (3, 4), (0, 0), [0, 0, 0, 0, 0, 0])
