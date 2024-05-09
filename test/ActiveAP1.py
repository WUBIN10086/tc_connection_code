#================================================================
# Rewrite the code from Roy: active AP algorithm
# Last modify date: 2024 05/1
# Author: WU BIN
#================================================================
import random
import csv
import copy
import numpy as np
from itertools import product
import datetime
import time
from throughput_estimation import calculate_throughput_estimate

#---------------------------------------
# 数据结构
class APInfo:
    def __init__(self, apid, xpos, ypos):
        self.apid = apid
        self.xpos = xpos
        self.ypos = ypos
        self.throughput = 0
class HostInfo:
    def __init__(self, hostid, xpos, ypos):
        self.hostid = hostid
        self.xpos = xpos
        self.ypos = ypos

#-------------------------------------------
# 恒量定义
# CSV文件地址
Location_csv_path = 'model\Location\Exp1\Eng_Location.csv'
Walls_csv_path = 'model\Location\Exp1\Walls.csv'



#-------------------------------------------------
# 最小化AP数量算法
# 贪婪算法初始化：
# 采用贪婪算法初步选出能满足最小吞吐量需求的AP集合。
#
# 局部搜索优化：
# 通过局部搜索技术优化AP的选择，
# 找到在满足主机最小吞吐量的同时，
# 能使得活跃AP数量最小的配置

# 读取CSV信息
def read_network_info_from_csv(csv_path):
    aps = []
    hosts = []
    with open(csv_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row['Type'] == 'AP':
                ap = APInfo(apid=row['Name'], xpos=float(row['X']), ypos=float(row['Y']))
                aps.append(ap)
            elif row['Type'] == 'Host':
                host = HostInfo(hostid=row['Name'], xpos=float(row['X']), ypos=float(row['Y']))
                hosts.append(host)
    return aps, hosts










#-------------------------------------------------
# 寻找最佳连接方式并计算预估公平吞吐量
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

def get_active_aps(AIActive, NoAP):
    active_aps = []
    for i in range(NoAP):
        if AIActive[i].ifActive == 1:
            active_aps.append(AIActive[i].APID)
    return active_aps

active_aps = get_active_aps(AIActive, NoAP)
active_ap_data = []
# 从 CSV 文件中读取 Host 和 AP 的数量
with open(Location_csv_path, newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    host_n = 0
    AP_m = 0
    for row in reader:
        if row["Type"] == "Host":
            host_n += 1
        elif row["Type"] == "AP":
            if row["Name"] in active_aps:
                    active_ap_data.append(row)
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

# -------------------------------------------------------------
# 更新了筛选方式：
# 存储所有的连接方式
def valid_matrix(matrix):
    # 筛选条件1: 每行最多一个1
    if np.all(matrix.sum(axis=1) <= 1):
        # 筛选条件2: 每列至少一个1
        if np.all(matrix.sum(axis=0) >= 1):
            # 筛选条件3: 每行至少一个1
            if np.all(matrix.sum(axis=1) >= 1):
                return True
    return False

def generate_valid_matrices(host_n, AP_m):
    all_matrices = []
    for combination in product([0, 1], repeat=host_n * AP_m):
        matrix = np.array(combination).reshape(host_n, AP_m)
        if valid_matrix(matrix):
            all_matrices.append(matrix)
    return all_matrices

all_matrices = generate_valid_matrices(host_n, AP_m)
write_to_file(f"----------------------", output_filename)
write_to_file(f"Connection number: {len(all_matrices)}", output_filename)
print("Connection Assignment: Finished")
#---------------------------------------------------------------------



#---------------------------------------------------------------------
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
            if row["Name"] in active_aps:
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

write_to_file("Single Throughput", output_filename)
write_to_file("----------------------", output_filename)
results = []

# 初始化结果数组，填充为0
num_hosts = len(host_coordinates)
num_aps = len(ap_coordinates)
results = [[0.0] * num_aps for _ in range(num_hosts)]

# 读取墙面信息
walls_data = pd.read_csv(Walls_csv_path)

# 遍历每个主机和每个接入点，计算吞吐量
for i, (host_name, host_x, host_y) in enumerate(host_coordinates):
    for j, (ap_name, ap_x, ap_y) in enumerate(ap_coordinates):
        # 查找墙面信息
        wall_info = walls_data[(walls_data['AP_Name'] == ap_name) & (walls_data['Host_Name'] == host_name)]
        nk = wall_info.iloc[0, 2:].tolist()  # 从第三列开始是墙面信息
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
for i, matrix in enumerate(all_matrices):
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
for matrix in all_matrices:
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



best_connections = []

W_1 = 0
W_2 = 0

# 计算每种连接方式下的总吞吐量大小
all_totals =[]
for i, fair_results in enumerate(all_fair_results):
    total = 0
    for sub_list in fair_results:
        total += sum(sub_list)
    all_totals.append(total)

# 计算所有连接方式的数量
connection_num = len(all_matrices)

# 指定阈值
# 阈值根据连接数量进行调整，假设一个Host大约上下浮动3Mbps左右
impact_threshold = host_n * 3

def categorize_throughput(data, threshold):
    # 计算均值
    mean_throughput = sum(data) / len(data)
    cont = 0
    # 遍历吞吐量数据
    for value in data:
        # 计算吞吐量与均值的差值
        difference = abs(value - mean_throughput)
        # 根据阈值判断类别
        if difference <= threshold:
            cont += 1
        else:
            cont -= 1
    # 如果大部分（80%）的连接情况下，吞吐量相差不大，则优先考虑公平性指数
    if cont >= connection_num * 0.8:
        return True

# 调用均值计算函数
throughput_data = all_totals
if categorize_throughput(throughput_data, impact_threshold):
    W_2 = 0.3
else:
    W_2 = 0.7

W_1 = 1 - W_2

#write_to_file()
write_to_file(f"Judgement weight: Fairness index: {W_1:.2f}, Total throughput: {W_2:.2f}", output_filename)
print("Judgement weigth: Fairness index: {:.2f}, Total throughput: {:.2f}".format(W_1, W_2))

# 归一化函数
def normalize(data):
    """
    对数据进行归一化处理，使其范围在0到1之间。
    :param data: 一个数字列表。
    :return: 归一化后的数据列表。
    """
    min_val = min(data)
    max_val = max(data)
    return [(x - min_val) / (max_val - min_val) for x in data]

# 归一化总吞吐量
normalized_totals = normalize(all_totals)

for i, fair_results in enumerate(all_fair_results):
    total = 0
    for sub_list in fair_results:
        total += sum(sub_list)
    
    # 使用归一化的总吞吐量
    normalized_total = normalized_totals[i]
    fair_index = all_fairness_index[i]
    # 计算综合得分，使用归一化的总吞吐量
    score = ( W_1 * fair_index + W_2 * normalized_total) * 100
    best_connections.append((i, score, fair_index, total))

# 根据得分降序排序
best_connections.sort(key=lambda x: x[1], reverse=True)  

middle_index = len(best_connections) // 2  # 中间索引
worst_index = -1  # 最差连接索引

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

#---------------------------------------------------------------------
# 输出代码运行时间
# 记录结束时间
end_time = time.time()
# 计算代码执行时间
execution_time = end_time - start_time
write_to_file(f"Code executed in {execution_time:.2f} seconds", output_filename)
write_to_file("======================", output_filename)
print("Procedure Finished!!!")

#---------------------------------------------------------------------
#output_file.close()
#sys.stdout = sys.__stdout__