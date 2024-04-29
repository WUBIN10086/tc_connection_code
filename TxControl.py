#================================================================
# Connection decision model calculation
# Last modify date: 2024 03/31
#================================================================
# Change: make main code
#         example for 80211n protocol TP-Link T4UH ver.2
#         add paramteres file for modified PC
# funcation list: 1. read file
#                 2. use function
#                 3. connection decide algorithm
# algorithm step:
# 1. Decide AP numbers and Positions in the MAP, consider RSS cover range
# 2. Decide Host numbers and positions, output the coordinates in CSV file
# 3. Give top 3 connection plans by ML model（to be updated）
# 4. calculate each connection Single and Concurrent
# 5. Calculate Fairness throughput
# 6. Sort by total throughput and fairness index
# 7. Give the best three assignments and middle, worest assignment.
#
# Upgarde:
# Accelerated computing efficiency
#=================================================================


#---------------------------------------------------------------------
# connection algorithm
import csv
import sys
import pandas as pd
import itertools
import copy
import datetime
import time
from throughput_estimation import calculate_throughput_estimate
from throughput_estimation import Rss_calculate
from throughput_estimation import Distance
from concurrent_calc import calculate_srf
from throughput_estimation import Calculate_throughput
from write_to_output import write_to_file

#---------------------------------------------------------------------

# 变量说明：
# all_matrices: 所有的连接情况
# matrix: 单个连接情况
# host_n: 主机数量
# AP_m: AP的数量
# results: 单一吞吐量计算结果
# con_results: 并发吞吐量计算结果
# all_con_results: 所有情况下的并发吞吐量计算结果
# all_fairness_index：所有连接情况的吞吐量公平性指数
# all_fair_results: 所有情况下的计算的公平吞吐量大小
# all_totals：所有连接方式下的总吞吐量大小

#---------------------------------------------------------------------
# connection solution count part
# 需要改进，暂时版

# 计算了所有的连接情况

# input number of m and n
# create matrix for connect condition:
# element X_ij represent connect(1) or disconnect(0)

# 记录开始时间
start_time = time.time()
# 输出结果到文本文件
#output_file = open("output.txt", "w")
#sys.stdout = output_file

# 获取当前日期和时间
current_datetime = datetime.datetime.now()
formatted_datetime = current_datetime.strftime("%Y-%m-%d %H:%M")
#print("Date and Time:", formatted_datetime)
write_to_file(f"Date and Time: {formatted_datetime}")
# 开始处理标志：
print("START!!!")

# 从 CSV 文件中读取 Host 和 AP 的数量
with open("coordinates.csv", newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    host_n = 0
    AP_m = 0
    for row in reader:
        if row["Type"] == "Host":
            host_n += 1
        elif row["Type"] == "AP":
            AP_m += 1

# 输出 Host 和 AP 的数量
#print("======================")
#print("Devices number")
#print("----------------------")
#print(f"Number of Hosts: {host_n}")
#print(f"Number of APs: {AP_m}")
write_to_file(f"======================")
write_to_file(f"Devices number")
write_to_file(f"----------------------")
write_to_file(f"Number of Hosts: {host_n}")
write_to_file(f"Number of APs: {AP_m}")
print("Read Devices number: Finished")

# 存储所有的连接方式
# 文件路径
file_path = 'ConnectedConfig.txt'

# 初始化矩阵列表和当前矩阵
all_matrices = []
matrix = []

# 打开并读取文件
with open(file_path, 'r') as file:
    for line in file:
        # 去除行尾的空白字符
        line = line.strip()
        if line == "":
            # 如果遇到空行且当前矩阵不为空，添加到总列表中
            if matrix:
                all_matrices.append(matrix)
                matrix = []
        else:
            # 将非空行添加到当前矩阵
            try:
                matrix.append([int(x) for x in line.split(',')])
            except ValueError:
                # 如果转换失败，打印错误消息并跳过该行
                print(f"Skipping non-numeric line: {line}")

# 检查文件末尾是否有未添加的矩阵
if matrix:
    all_matrices.append(matrix)

# 输出矩阵数量和完成状态

write_to_file(f"----------------------")
write_to_file(f"Connection number: {len(all_matrices)}")
print("Connection Assignment: Finished")
#---------------------------------------------------------------------



#---------------------------------------------------------------------
# 创建两个空数组用于存储AP和Host的坐标
ap_coordinates = []
host_coordinates = []
# 读取CSV文件
with open("coordinates.csv", newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        name = row["Name"]
        x = float(row["X"])
        y = float(row["Y"])
        entity_type = row["Type"]
        # 根据实体类型将坐标信息添加到相应的数组
        if entity_type == "AP":
            ap_coordinates.append((name, x, y))
        elif entity_type == "Host":
            host_coordinates.append((name, x, y))

write_to_file("======================")
write_to_file("Deivces Location")
write_to_file("----------------------")
# 打印AP和Host的坐标数组
write_to_file("AP Coordinates:")
for ap in ap_coordinates:
    write_to_file(f"{ap}")
write_to_file("----------------------")
write_to_file("Host Coordinates:")
for host in host_coordinates:
    write_to_file(f"{host}")
write_to_file("======================")
print("Read Devices Location: Finished")

# nk = [1, 2]  # 根据需要提供 nk 的值
# nk 为AP和Host之间各种墙面的影响数量
# corridor wall for W1, 
# the partition wall for W2, 
# the intervening wall for W3, 
# the glass wall for W4, 
# the elevator wall for W5, 
# and the door for W6.
# Roy的程序中注释掉了墙面的影响，默认就是一堵墙
write_to_file("Single Throughput")
write_to_file("----------------------")
results = []

# 初始化结果数组，填充为0
num_hosts = len(host_coordinates)
num_aps = len(ap_coordinates)
results = [[0.0] * num_aps for _ in range(num_hosts)]

# 读取墙面信息
walls_data = pd.read_csv("Walls.csv")

# 遍历每个主机和每个接入点，计算吞吐量
for matrix_index, connection_matrix in enumerate(all_matrices):
    for host_index, row in enumerate(connection_matrix):
        host_name, host_x, host_y = host_coordinates[host_index]
        for ap_index, connected in enumerate(row):
            if connected == 1:  # 如果当前主机和接入点之间存在连接
                ap_name, ap_x, ap_y = ap_coordinates[ap_index]
                wall_info = walls_data[(walls_data['AP_Name'] == ap_name) & (walls_data['Host_Name'] == host_name)]
                nk = wall_info.iloc[0, 2:].tolist()

                if ap_name.endswith(("2", "4", "6")):
                    with open("parameters2.txt", "r") as file:
                        parameters = {}
                        for line in file:
                            line = line.strip()
                            if line.startswith('#'):
                                continue
                            key_value = line.split('=')
                            if len(key_value) == 2:
                                key, value = map(str.strip, key_value)
                                if key in ['alpha', 'P_1', 'a', 'b', 'c']:
                                    parameters[key] = float(value)
                                elif key == 'Wk':
                                    parameters[key] = list(map(float, value.split()))

                    p_1_initial = parameters['P_1']
                    while p_1_initial > -80:
                        parameters['P_1'] = p_1_initial
            # 计算主机与AP的距离
                        d = Distance(host_x, host_y, ap_x, ap_y)
            # 计算接收信号强度(RSS)
                        rss = Rss_calculate(parameters['alpha'], parameters['P_1'], d, nk, parameters['Wk'])
            # 计算估计吞吐量
                        result = calculate_throughput_estimate(parameters, (host_x, host_y), (ap_x, ap_y), nk)
            # 将结果写入文件
                        write_to_file(f"{host_name} for {ap_name}: {result}, RSS: {rss}, p_1:{p_1_initial}")
            # 在结果数组中保存该结果
                        results[host_index][ap_index] = result
                        p_1_initial -= 3
                else:
                    with open("parameters.txt", "r") as file:
                        parameters = {}
                        for line in file:
                            line = line.strip()
                            if line.startswith('#'):
                                continue
                            key_value = line.split('=')
                            if len(key_value) == 2:
                                key, value = map(str.strip, key_value)
                                if key in ['alpha', 'P_1', 'a', 'b', 'c']:
                                    parameters[key] = float(value)
                                elif key == 'Wk':
                                    parameters[key] = list(map(float, value.split()))

                    p_1_initial = parameters['P_1']
                    while p_1_initial > -80:
                        parameters['P_1'] = p_1_initial
                        d = Distance(host_x, host_y, ap_x, ap_y)
                        rss = Rss_calculate(parameters['alpha'], parameters['P_1'], d, nk, parameters['Wk'])
                        result = calculate_throughput_estimate(parameters, (host_x, host_y), (ap_x, ap_y), nk)
                        write_to_file(f"{host_name} for {ap_name}: {result}, RSS: {rss}, p_1:{p_1_initial}")
                        results[host_index][ap_index] = result
                        p_1_initial -= 3

#---------------------------------------------------------------------
print("Single Throughput Calculated")

# 计算所有连接方式的数量
# 指定阈值
# 阈值根据连接数量进行调整，假设一个Host大约上下浮动3Mbps左右




#---------------------------------------------------------------------
# 输出代码运行时间
# 记录结束时间
end_time = time.time()
# 计算代码执行时间
execution_time = end_time - start_time
write_to_file(f"Code executed in {execution_time:.2f} seconds")
write_to_file("======================")
print("Procedure Finished!!!")


#---------------------------------------------------------------------
#output_file.close()
#sys.stdout = sys.__stdout__