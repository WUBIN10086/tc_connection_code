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
import numpy as np
from itertools import product
import copy
import datetime
import time
from throughput_estimation import calculate_throughput_estimate, Distance
from concurrent_calc import calculate_srf
from fairness_calc import Fairness_calc
from fairness_index import calculate_fairness_index
from write_to_output import write_to_file, clear_output_file

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

# Read command-line arguments
# Location_csv_path = sys.argv[1]
# output_filename = sys.argv[2]
# Walls_csv_path = sys.argv[3]
Location_csv_path = 'model/Location/Exp1/After avtive AP/Eng_Location.csv'
output_filename = "Topology_1.txt"
Walls_csv_path = 'model/Location/Exp1/After avtive AP/Walls.csv'

# 记录开始时间
start_time = time.time()
# 输出结果到文本文件
#output_file = open("output.txt", "w")
#sys.stdout = output_file

# 获取当前日期和时间
current_datetime = datetime.datetime.now()
formatted_datetime = current_datetime.strftime("%Y-%m-%d %H:%M")
#print("Date and Time:", formatted_datetime)

# 初始化输出文件
clear_output_file(output_filename)

write_to_file(f"Date and Time: {formatted_datetime}", output_filename)
# 开始处理标志：
print("START!!!")

# 从 CSV 文件中读取 Host 和 AP 的数量
with open(Location_csv_path, newline='') as csvfile:
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
write_to_file(f"======================", output_filename)
write_to_file(f"Devices number", output_filename)
write_to_file(f"----------------------", output_filename)
write_to_file(f"Number of Hosts: {host_n}", output_filename)
write_to_file(f"Number of APs: {AP_m}", output_filename)
print("Read Devices number: Finished")

# 创建两个空数组用于存储AP和Host的坐标
ap_coordinates = []
host_coordinates = []
# 读取CSV文件
with open(Location_csv_path, newline='') as csvfile:
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

write_to_file("======================", output_filename)
write_to_file("Deivces Location", output_filename)
write_to_file("----------------------", output_filename)
# 打印AP和Host的坐标数组
write_to_file("AP Coordinates:", output_filename)
for ap in ap_coordinates:
    write_to_file(f"{ap}", output_filename)
write_to_file("----------------------", output_filename)
write_to_file("Host Coordinates:", output_filename)
for host in host_coordinates:
    write_to_file(f"{host}", output_filename)
write_to_file("======================", output_filename)
print("Read Devices Location: Finished")

# 更新了筛选方式：
# 初始化存储所有的连接方式
# def valid_matrix(matrix):
#     # 筛选条件1: 每行最多一个1
#     if np.all(matrix.sum(axis=1) <= 1):
#         # 筛选条件2: 每列至少一个1
#         if np.all(matrix.sum(axis=0) >= 1):
#             # 筛选条件3: 每行至少一个1
#             if np.all(matrix.sum(axis=1) >= 1):
#                 return True
#     return False

# def generate_valid_matrices(host_n, AP_m):
#     all_matrices = []
#     for combination in product([0, 1], repeat=host_n * AP_m):
#         matrix = np.array(combination).reshape(host_n, AP_m)
#         if valid_matrix(matrix):
#             all_matrices.append(matrix)
#     return all_matrices

# all_matrices = generate_valid_matrices(host_n, AP_m)
# write_to_file(f"----------------------", output_filename)
# write_to_file(f"Connection number: {len(all_matrices)}", output_filename)
# print("Inti Connection Assignment: Finished")
# #---------------------------------------------------------------------

# def calculate_all_distances_and_find_max(hosts, aps):
#     distances = {}
#     max_distance = 0
#     max_pair = None

#     for host_name, host_x, host_y in hosts:
#         for ap_name, ap_x, ap_y in aps:
#             key = (host_name, ap_name)
#             dist = Distance(host_x, host_y, ap_x, ap_y)
#             distances[key] = dist
#             if dist > max_distance:
#                 max_distance = dist
#                 max_pair = key

#     return distances, max_distance, max_pair

# # 寻找最远距离的组合:
# distances, max_distance, max_pair = calculate_all_distances_and_find_max(host_coordinates, ap_coordinates)
# print(f"The maximum distance is {max_distance:.2f} units between {max_pair[0]} and {max_pair[1]}.")

# # 删除最远距离的组合:
# host_names = [name for name, x, y in host_coordinates]  # List of host names
# ap_names = [name for name, x, y in ap_coordinates]  # List of AP names
# host_name, ap_name = max_pair
# host_index = host_names.index(host_name)
# ap_index = ap_names.index(ap_name)
# filtered_matrices = [
#     matrix for matrix in all_matrices if matrix[host_index][ap_index] == 0
# ]
# print(f"Number of valid matrices after filtering: {len(filtered_matrices)}")
# write_to_file(f"New Connection number after Distance filter: {len(filtered_matrices)}", output_filename)
# def calculate_distances(hosts, aps):
#     distances = {}
#     for host_name, host_x, host_y in hosts:
#         for ap_name, ap_x, ap_y in aps:
#             key = (host_name, ap_name)
#             dist = np.sqrt((host_x - ap_x)**2 + (host_y - ap_y)**2)
#             distances[key] = dist
#     return distances

# 设置一个距离阈值

def calculate_all_distances_and_find_max(hosts, aps):
    distances = {}
    max_distance = 0

    for host_name, host_x, host_y in hosts:
        for ap_name, ap_x, ap_y in aps:
            key = (host_name, ap_name)
            dist = Distance(host_x, host_y, ap_x, ap_y)
            distances[key] = dist
            if dist > max_distance:
                max_distance = dist
    return distances,max_distance

distances, distance_threshold = calculate_all_distances_and_find_max(host_coordinates, ap_coordinates)
print(f"The maximum distance and threshold is {distance_threshold:.2f}.")

def generate_valid_matrices(hosts, aps, distances, max_conn_ratio):
    host_n = len(hosts)
    AP_m = len(aps)
    max_host_per_ap = int(host_n * max_conn_ratio)
    all_matrices = []
    for combination in product([0, 1], repeat=host_n * AP_m):
        matrix = np.array(combination).reshape(host_n, AP_m)
        # print("Inti Connection Assignment: Finished")
        # 检查每个AP的连接数是否符合限制
        if np.all(matrix.sum(axis=0) <= max_host_per_ap):
            # 检查是否每个连接都在距离阈值内
            valid = True
            for i in range(host_n):
                for j in range(AP_m):
                    if matrix[i][j] == 1:
                        host_name = hosts[i][0]
                        ap_name = aps[j][0]
                        if distances[(host_name, ap_name)] >= distance_threshold:
                            valid = False
                            break
                if not valid:
                    break
            
            if valid:
                all_matrices.append(matrix)
                
    return all_matrices

# 使用修改后的函数
filtered_matrices = generate_valid_matrices(host_coordinates, ap_coordinates, distances, 0.8)
write_to_file(f"----------------------", output_filename)
print(f"Number of valid matrices after filtering: {len(filtered_matrices)}")
write_to_file(f"New Connection number after Distance filter: {len(filtered_matrices)}", output_filename)

#---------------------------------------------------------------------
# nk = [1, 2]  # 根据需要提供 nk 的值
# nk 为AP和Host之间各种墙面的影响数量
# corridor wall for W1, 
# the partition wall for W2, 
# the intervening wall for W3, 
# the glass wall for W4, 
# the elevator wall for W5, 
# and the door for W6.
# Roy的程序中注释掉了墙面的影响，默认就是一堵墙
write_to_file("Single Throughput", output_filename)
write_to_file("----------------------", output_filename)
results = []

# 初始化结果数组，填充为0
num_hosts = len(host_coordinates)
num_aps = len(ap_coordinates)
results = [[0.0] * num_aps for _ in range(num_hosts)]

# 读取墙面信息
walls_data = pd.read_csv(Walls_csv_path)

def get_wall_info(ap_name, host_name):
    # print(walls_data['AP_Name'].dtype)
    # print(walls_data['AP_Name'])
    wall_info = walls_data[(walls_data['AP_Name'] == ap_name) & (walls_data['Host_Name'] == host_name)]
    if not wall_info.empty:
        nk = wall_info.iloc[0, 2:].tolist()  # Accessing columns directly
        return nk
    else:
        print(f"No wall data found for AP {ap_name} and Host {host_name}")
        return [0] * (walls_data.shape[1] - 2)  # Default no impact

# 遍历每个主机和每个接入点，计算吞吐量
for i, (host_name, host_x, host_y) in enumerate(host_coordinates):
    for j, (ap_name, ap_x, ap_y) in enumerate(ap_coordinates):
        # 查找墙面信息
        # print(type(ap_name))
        nk = get_wall_info(ap_name, host_name)
        # 双括号表示参数是一个元组（tuple），而非单个字符串
        if ap_name.endswith(("_2")):
            # 如果是结尾为_2的接口代表着TP-Link T4UH
            # 使用parameter2的数据
            # 5Ghz频段 带宽40Mhz
            with open("model\etc\parameters2.txt", "r") as file:
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
                result = calculate_throughput_estimate(parameters, (host_x, host_y), (ap_x, ap_y), nk)
                write_to_file(f"{host_name} for {ap_name}: {result}", output_filename)
                results[i][j] = result

            except ValueError as e:
                write_to_file(e, output_filename)
        # elif ap_name.endswith("3"):
        #     # 加入一个新的parameters3，作为当主机吞吐量与其他主机相差较大时，调整仿真到符合现实测量
        #     with open("parameters3.txt", "r") as file:
        #         parameters = {}
        #         for line in file:
        #             line = line.strip()
        #             if line.startswith('#'):
        #                 continue
        #             key_value = line.split('=')
        #             if len(key_value) == 2:
        #                 key, value = map(str.strip, key_value)
        #                 if key in ['alpha', 'P_1', 'a', 'b', 'c']:
        #                     parameters[key] = float(value)
        #                 elif key == 'Wk':
        #                     parameters[key] = list(map(float, value.split()))
        #     try:
        #         result = calculate_throughput_estimate(parameters, (host_x, host_y), (ap_x, ap_y), nk)
        #         print(f"{host_name} for {ap_name}: {result}")
        #         results[i][j] = result
        #     except ValueError as e:
        #         print(e)
        else:
            # 其他的时候使用普通的板载参数
            # 2.4GHz 80211n协议 40Mhz信道绑定
            with open("model\etc\parameters.txt", "r") as file:
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
                result = calculate_throughput_estimate(parameters, (host_x, host_y), (ap_x, ap_y), nk)
                write_to_file(f"{host_name} for {ap_name}: {result}", output_filename)
                results[i][j] = result

            except ValueError as e:
                write_to_file(e, output_filename)
#---------------------------------------------------------------------
print("Single Throughput Calculated")




#---------------------------------------------------------------------
# 决定连接方案从而决定同时连接的数量m
# concurrent throughput calc.
# calc signal/success rate factor
write_to_file("======================", output_filename)
write_to_file("Connection assignments", output_filename)
write_to_file("----------------------", output_filename)
for i, matrix in enumerate(filtered_matrices):
    write_to_file(f"Connection {i + 1}:", output_filename)
    for row in matrix:
        write_to_file(f"{row}", output_filename)

# print(results)
write_to_file("======================", output_filename)
write_to_file("Concurret throughput", output_filename)
write_to_file("----------------------", output_filename)
all_con_results = []
# 遍历所有的链接情况
# 更新results
for matrix in filtered_matrices:
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
        srf = calculate_srf(con_num)
        if con_num == 1:
            continue
        else:
            for i in Host_index:
                concurrent = con_results[i][j]
                con_results[i][j] = round(concurrent * srf, 2)
                # print("并发通信吞吐量: " , results[i][j])
    all_con_results.append(con_results)

for i, con_results in enumerate(all_con_results):
    write_to_file(f"Connection {i + 1} Results:", output_filename)
    write_to_file(f"{all_con_results[i]}", output_filename)
    #write_to_file()
#---------------------------------------------------------------------
print("Concurrent Throughput Calculated")


#---------------------------------------------------------------------
# 计算Fairness target throughput
connect_index = 0
all_fair_results = []
for matrix in filtered_matrices:
    fair_results = [[0] * AP_m for _ in range(host_n)]
    for j in range(AP_m):
        fair_S = []
        fair_C = []
        n = 0
        for i in range(host_n):
            if matrix[i][j] == 1:
                n += 1
                fair_S.append(results[i][j])
                fair_C.append(all_con_results[connect_index][i][j])
        target = Fairness_calc(n,fair_S,fair_C)
        # print(target)
        # 用计算完的Fairness target更新预估结果
        for i in range(host_n):
            if matrix[i][j] == 1:
                fair_results [i][j] = target
    # print(fair_results)
    all_fair_results.append(fair_results)
    connect_index += 1

write_to_file("======================", output_filename)
write_to_file("Fairness connection results", output_filename)
write_to_file("----------------------", output_filename)
for i, fair_results in enumerate(all_fair_results):
    write_to_file(f"Connection {i + 1} Results:", output_filename)
    write_to_file(f"{all_fair_results[i]}", output_filename)
    #write_to_file()
#---------------------------------------------------------------------
print("Fairness throughput Calculated")



#---------------------------------------------------------------------
# 计算fairness index
# 初始化记录公平性指数的列表
all_fairness_index =[]

for i, fair_results in enumerate(all_fair_results):
    write_to_file(f"Connection {i + 1} fairness index:", output_filename)
    calc_value = all_fair_results[i]
    fairness_index = calculate_fairness_index(calc_value)
    fairness_index = round(fairness_index, 6)
    write_to_file(f"{fairness_index}", output_filename)
    all_fairness_index.append(fairness_index)
#---------------------------------------------------------------------
print("Fairness index Calculated")

#---------------------------------------------------------------------
# 删除fairness index小于0.8的组合
# Filtering fairness index less than 0.8
filtered_matrices_by_fairness = []
filtered_fairness_indexes = []
filtered_fair_results = []

for i, fairness_value in enumerate(all_fairness_index):
    if fairness_value >= 0.8:
        filtered_matrices_by_fairness.append(filtered_matrices[i])
        filtered_fairness_indexes.append(fairness_value)
        filtered_fair_results.append(all_fair_results[i])

# Update filtered_matrices to only include those that passed the fairness filter
filtered_matrices = filtered_matrices_by_fairness
all_fair_results = filtered_fair_results
all_fairness_index = filtered_fairness_indexes

print(f"Number of valid matrices after filtering by fairness index: {len(filtered_matrices)}")
write_to_file(f"Filtered Connection number after Fairness filter: {len(filtered_matrices)}", output_filename)
#---------------------------------------------------------------------


#---------------------------------------------------------------------
# 排序寻找最佳的连接方式
# 因为fairness index和总吞吐量之间的单位相差过大，
# 因此使用归一化方法，将总吞吐量转化为和fairness index一样的单位范围，
# 然后通过设计权重去判断合适的最佳组合。

best_connections = []

# W_1 = 0
# W_2 = 0

# 计算每种连接方式下的总吞吐量大小
all_totals = []
for fair_results in filtered_fair_results:
    total = sum(sum(sub_list) for sub_list in fair_results)
    all_totals.append(total)

# # 计算均值和差异，调整权重
# mean_throughput = sum(all_totals) / len(all_totals)
# deviations = [abs(total - mean_throughput) for total in all_totals]

# # 判断吞吐量差异是否在阈值内
# threshold = host_n * 3  # 假设一个Host大约上下浮动3Mbps左右
# if all(deviation <= threshold for deviation in deviations):
#     W_2 = 0.3
# else:
#     W_2 = 0.7
# W_1 = 1 - W_2

def calculate_variance(data):
    return np.var(data)

def fuzzy_weight(variance, high_threshold, low_threshold):
    # Determine degrees of membership
    if variance < low_threshold:
        fairness_high = 1
        throughput_high = 0
    elif variance > high_threshold:
        fairness_high = 0
        throughput_high = 1
    else:
        # Linear interpolation between thresholds
        fairness_high = (high_threshold - variance) / (high_threshold - low_threshold)
        throughput_high = (variance - low_threshold) / (high_threshold - low_threshold)
    
    # Use the membership values to set weights
    W_1 = fairness_high  # Weight for fairness
    W_2 = throughput_high  # Weight for throughput
    return W_1, W_2

# Calculate variance of the throughput data
variance = calculate_variance(all_totals)

# Set thresholds for what you consider low and high variance
low_threshold = host_n * 1.5  # Adjust as needed
high_threshold = host_n * 5  # Adjust as needed

# Get weights using the fuzzy logic function
W_1, W_2 = fuzzy_weight(variance, high_threshold, low_threshold)

write_to_file(f"Judgement weight: Fairness index: {W_1:.2f}, Total throughput: {W_2:.2f}", output_filename)
print("Judgement weigth: Fairness index: {:.2f}, Total throughput: {:.2f}".format(W_1, W_2))

def normalize(data):
    """
    Normalize the data to make it range between 0 and 1.
    :param data: List of numeric values.
    :return: List of normalized values.
    """
    min_val = min(data)
    max_val = max(data)
    if max_val - min_val == 0:  # Avoid division by zero if all values are the same
        return [1] * len(data)
    return [(x - min_val) / (max_val - min_val) for x in data]

# 归一化总吞吐量
normalized_totals = normalize(all_totals)

# 综合评分
for i, (fairness_index, total, normalized_total) in enumerate(zip(filtered_fairness_indexes, all_totals, normalized_totals)):
    score = (W_1 * fairness_index + W_2 * normalized_total) * 100
    best_connections.append((i, score, fairness_index, total))

# 排序
best_connections.sort(key=lambda x: x[1], reverse=True)

# 处理中间和最差连接
middle_index = len(best_connections) // 2
worst_index = -1

write_to_file("======================", output_filename)
#write_to_file()
write_to_file("Top 3 Best Connections:", output_filename)

# 输出最佳的三个连接方式
for i, (index, score, fairness_index, total) in enumerate(best_connections[:3]):
    write_to_file(f"Rank {i + 1}: Connection[{index+1}], Total Score: {score:.2f}, Fairness Index: {fairness_index:.6f}, Total Throughput: {total:.2f}", output_filename)
    write_to_file("Connection Details:", output_filename)
    write_to_file(f"Connection {index + 1}:", output_filename)
    for row in all_matrices[index]:
        write_to_file(f"{row}", output_filename)
    write_to_file(f"Connection {index + 1} Results:", output_filename)
    write_to_file(f"{all_fair_results[index]}", output_filename)
    write_to_file("--------------------------", output_filename)
    #write_to_file()
write_to_file("======================", output_filename)

if middle_index >= 0:
    write_to_file("Middle Connection:", output_filename)
    mid_index, mid_score, mid_fairness, mid_total = best_connections[middle_index]
    write_to_file(f"Rank {middle_index + 1}: Connection[{mid_index + 1}], Total Score: {mid_score:.2f}, Fairness Index: {mid_fairness:.6f}, Total Throughput: {mid_total:.2f}", output_filename)
    write_to_file("Connection Details:", output_filename)
    write_to_file(f"Connection {mid_index + 1}:", output_filename)
    for row in all_matrices[mid_index]:
        write_to_file(f"{row}", output_filename)
    write_to_file("======================", output_filename)

if worst_index == -1:
    worst_index, worst_score, worst_fairness, worst_total = best_connections[-1]
    write_to_file("Worst Connection:", output_filename)
    write_to_file(f"Rank {len(best_connections)}: Connection[{worst_index + 1}], Total Score: {worst_score:.2f}, Fairness Index: {worst_fairness:.6f}, Total Throughput: {worst_total:.2f}", output_filename)
    write_to_file("Connection Details:", output_filename)
    write_to_file(f"Connection {worst_index + 1}:", output_filename)
    for row in all_matrices[worst_index]:
        write_to_file(f"{row}", output_filename)
    write_to_file("======================", output_filename)

# 结束程序，输出执行时间
end_time = time.time()
execution_time = end_time - start_time
write_to_file("======================", output_filename)
write_to_file(f"Code executed in {execution_time:.2f} seconds", output_filename)
print("Procedure Finished!!!")
#---------------------------------------------------------------------
#output_file.close()
#sys.stdout = sys.__stdout__