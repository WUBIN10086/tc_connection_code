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
from math import log10
def dBm_to_mW(dBm):
    return 10 ** (dBm / 10)

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
for i, (host_name, host_x, host_y) in enumerate(host_coordinates):
    for j, (ap_name, ap_x, ap_y) in enumerate(ap_coordinates):
        # 查找墙面信息
        wall_info = walls_data[(walls_data['AP_Name'] == ap_name) & (walls_data['Host_Name'] == host_name)]
        nk = wall_info.iloc[0, 2:].tolist()  # 从第三列开始是墙面信息
        # 双括号表示参数是一个元组（tuple），而非单个字符串
        if ap_name.endswith(("2", "4", "6")):
            # 如果是结尾为偶数的接口代表着TP-Link T4UH
            # 使用parameter2的数据
            # 5Ghz频段 带宽40Mhz
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
            try:
                d = Distance(host_x, host_y, ap_x, ap_y)
                rss = Rss_calculate(parameters['alpha'], parameters['P_1'], d, nk,parameters['Wk'])
                result = calculate_throughput_estimate(parameters, (host_x, host_y), (ap_x, ap_y), nk)
                write_to_file(f"{host_name} for {ap_name}: {result}, RSS: {rss}")
                results[i][j] = result

            except ValueError as e:
                write_to_file(e)

        else:
            # 其他的时候使用普通的板载参数
            # 2.4GHz 80211n协议 40Mhz信道绑定
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
            try:
                d = Distance(host_x, host_y, ap_x, ap_y)
                rss = Rss_calculate(parameters['alpha'], parameters['P_1'], d, nk, parameters['Wk'])
                result = calculate_throughput_estimate(parameters, (host_x, host_y), (ap_x, ap_y), nk)
                mW_value = dBm_to_mW(rss)
                write_to_file(f"{host_name} for {ap_name}: {result}, RSS: {rss},mW:{mW_value}")
                results[i][j] = result

            except ValueError as e:
                write_to_file(e)
#---------------------------------------------------------------------
print("Single Throughput Calculated")

#---------------------------------------------------------------------
# 决定连接方案从而决定同时连接的数量m
# concurrent throughput calc.
# calc signal/success rate factor
write_to_file("======================")
write_to_file("Connection assignments")
write_to_file("----------------------")
for i, matrix in enumerate(all_matrices):
    write_to_file(f"Connection {i + 1}:")
    for row in matrix:
        write_to_file(f"{row}")

# print(results)
write_to_file("======================")
write_to_file("Concurret throughput")
write_to_file("----------------------")
all_con_results = []
# 遍历所有的链接情况
# 更新results
for matrix in all_matrices:
    con_results = copy.deepcopy(results)
    # 对于一种连接方式的每一列
    # 代表着遍历每个AP连接的Host数量
    for j in range(AP_m):
        Host_index = [] # 同时连接的Host的序号
        con_num = 0
        for i in range(host_n):
            if matrix[i][j] == 1:
                con_num = con_num + 1
                Host_index.append(i)
            elif matrix[i][j] == 0:
                con_results[i][j] = 0
        # print("同时连接数量: ", con_num)
        srf = calculate_srf(con_num)#同时链接的
        if con_num == 1:
            continue
        else:
            for i in Host_index:
                concurrent = con_results[i][j]
                con_results[i][j] = round(concurrent * srf, 2)
                # print("并发通信吞吐量: " , results[i][j])
    all_con_results.append(con_results)

for i, con_results in enumerate(all_con_results):
    write_to_file(f"Connection {i + 1} Results:\n")
    for result in con_results:
        # 将结果列表转换为字符串，并用逗号和空格隔开各个元素，最后添加换行符
        result_str = ', '.join(map(str, result))
        write_to_file(f"[{result_str}]\n")

#---------------------------------------------------------------------
print("Concurrent Throughput Calculated")







# 计算所有连接方式的数量
connection_num = len(all_matrices)

# 指定阈值
# 阈值根据连接数量进行调整，假设一个Host大约上下浮动3Mbps左右
impact_threshold = host_n * 3



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