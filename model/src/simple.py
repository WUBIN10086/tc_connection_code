#================================================================
# Connection decision model calculation
# Last modify date: 2024 05/31
#================================================================
import pandas as pd
import csv
from write_to_output import write_to_file, clear_output_file
from throughput_estimation import calculate_throughput_estimate, Distance
import numpy as np
from concurrent_calc import calculate_srf
from fairness_calc import Fairness_calc
from fairness_index import calculate_fairness_index
import copy

# Load the CSV file
Location_csv_path = 'model/Location/Exp4/Orignal Location/Gra_Location.csv'
Walls_csv_path = 'model/Location/Exp4/Orignal Location/Walls.csv'
output_filename = "Topology_4.txt"

# 初始化输出文件
clear_output_file(output_filename)

# Define the active AP
specified_aps = ["AP4_1", "AP4_2", "AP5_2"]
specified_hosts = ["H1", "H2", "H3", "H4", "H5", "H6", "H7", "H8", "H9", 'H10']

# 假设每个AP连接的Host名称的映射
ap_to_hosts = {
"AP4_1": ["H3","H5"],
"AP4_2": ["H1","H7","H8","H9"],
"AP5_2": ["H2","H4","H6","H10"]
}

# 从 CSV 文件中读取 Host 和 AP 的数量
with open(Location_csv_path, newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    host_n = 0
    AP_m = 0
    for row in reader:
        if row["Type"] == "Host":
            host_n += 1

# Initialize dictionaries to store coordinates
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
        if entity_type == "AP" and name in specified_aps:
            ap_coordinates.append((name, x, y))
        elif entity_type == "Host":
            host_coordinates.append((name, x, y))

# 打印结果
# print("AP Coordinates:", ap_coordinates)
# print("Host Coordinates:", host_coordinates)
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

# set connection
num = len(specified_aps)
connection_matrix = np.zeros((host_n, num), dtype=int)

# 填充连接矩阵
for ap_index, ap in enumerate(specified_aps):
    for host_index, host in enumerate(specified_hosts):
        if host in ap_to_hosts.get(ap, []):
            connection_matrix[host_index, ap_index] = 1

# 让连接矩阵以更加直观的方式输出
connection_matrix_str = '\n'.join([' '.join(map(str, row)) for row in connection_matrix])

write_to_file("Connection", output_filename)
write_to_file("----------------------", output_filename)
write_to_file(f"{connection_matrix_str}", output_filename)
write_to_file("======================", output_filename)

# calculate single throughput
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
        nk = get_wall_info(ap_name, host_name)
        # 双括号表示参数是一个元组（tuple），而非单个字符串
        if ap_name.endswith(("_2")):
            # 如果是结尾为_2的接口代表着TP-Link T4UH
            # 使用parameter2的数据
            # 5Ghz频段 带宽40Mhz
            with open("model/etc/parameters2.txt", "r") as file:
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
        else:
            # 其他的时候使用普通的板载参数
            # 2.4GHz 80211n协议 40Mhz信道绑定
            with open("model/etc/parameters.txt", "r") as file:
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

print("Single Throughput Calculated")

# Decision connection plan to determine the number of concurrent connections m
# write_to_file("======================", output_filename)
# write_to_file("Connection assignments", output_filename)
# write_to_file("----------------------", output_filename)

filtered_matrices = [connection_matrix]  # This example assumes only one connection matrix; adapt as needed

# for i, matrix in enumerate(filtered_matrices):
#     write_to_file(f"Connection {i + 1}:", output_filename)
#     for row in matrix:
#         write_to_file(f"{row}", output_filename)

write_to_file("======================", output_filename)
write_to_file("Concurrent throughput", output_filename)
write_to_file("----------------------", output_filename)
all_con_results = []
# 遍历所有的链接情况
# 更新results
for matrix in filtered_matrices:
    con_results = copy.deepcopy(results)
    # 对于一种连接方式的每一列
    # 代表着遍历每个AP连接的Host数量
    for j in range(len(specified_aps)):
        Host_index = []  # 同时连接的Host的序号
        con_num = 0
        for i in range(host_n):
            if matrix[i][j] == 1:
                con_num = con_num + 1
                Host_index.append(i)
            elif matrix[i][j] == 0:
                con_results[i][j] = 0
        # 计算同时连接的数量
        srf = calculate_srf(con_num)
        if con_num == 1:
            continue
        else:
            for i in Host_index:
                concurrent = con_results[i][j]
                con_results[i][j] = round(concurrent * srf, 2)
    all_con_results.append(con_results)

for i, con_results in enumerate(all_con_results):
    write_to_file(f"Connection {i + 1} Results:", output_filename)
    for row in con_results:
        write_to_file(f"{row}", output_filename)

#---------------------------------------------------------------------
print("Concurrent Throughput Calculated")

all_fairness_index =[]

for i, fair_results in enumerate(all_con_results):
    write_to_file(f"Connection {i + 1} fairness index:", output_filename)
    calc_value = all_con_results[i]
    fairness_index = calculate_fairness_index(calc_value)
    fairness_index = round(fairness_index, 6)
    write_to_file(f"{fairness_index}", output_filename)
    all_fairness_index.append(fairness_index)

# 计算Fairness target throughput
connect_index = 0
all_fair_results = []
for matrix in filtered_matrices:
    fair_results = [[0] * len(specified_aps) for _ in range(host_n)]
    for j in range(len(specified_aps)):
        fair_S = []
        fair_C = []
        n = 0
        for i in range(host_n):
            if matrix[i][j] == 1:
                n += 1
                fair_S.append(results[i][j])
                fair_C.append(all_con_results[connect_index][i][j])
        target = Fairness_calc(n, fair_S, fair_C)
        # 用计算完的Fairness target更新预估结果
        for i in range(host_n):
            if matrix[i][j] == 1:
                fair_results[i][j] = target
    all_fair_results.append(fair_results)
    connect_index += 1

write_to_file("======================", output_filename)
write_to_file("Fairness connection results", output_filename)
write_to_file("----------------------", output_filename)
for i, fair_results in enumerate(all_fair_results):
    write_to_file(f"Connection {i + 1} Results:", output_filename)
    for row in fair_results:
        write_to_file(f"{row}", output_filename)

print("Fairness throughput Calculated")

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
