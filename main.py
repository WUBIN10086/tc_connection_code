#================================================================
# Connection decision model calculation
# Last modify date: 2023 11/12
#================================================================
# Change: make main code
#         example for 80211n protocol TP-Link T4UH ver.2
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
from concurrent_calc import calculate_srf
from fairness_calc import Fairness_calc
from fairness_index import calculate_fairness_index

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
output_file = open("output.txt", "w")
sys.stdout = output_file

# 获取当前日期和时间
current_datetime = datetime.datetime.now()
formatted_datetime = current_datetime.strftime("%Y-%m-%d %H:%M")
print("Date and Time:", formatted_datetime)



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
print("======================")
print("Devices number")
print("----------------------")
print(f"Number of Hosts: {host_n}")
print(f"Number of APs: {AP_m}")

# 存储所有的连接方式
all_matrices = []

for combination in itertools.product([0, 1], repeat=host_n * AP_m):
    matrix = [list(combination[i:i+AP_m]) for i in range(0, host_n * AP_m, AP_m)]

    # 筛选条件1：删除包含 1 多于一个的行
    if all(row.count(1) <= 1 for row in matrix):
        # 筛选条件2：检查每一列是否至少有一个 1
        if all(any(row[j] == 1 for row in matrix) for j in range(AP_m)):
            # 筛选条件3：检查每一行是否至少有一个 1
            if all(1 in row for row in matrix):
                all_matrices.append(matrix)

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

print("======================")
print("Deivces Location")
print("----------------------")
# 打印AP和Host的坐标数组
print("AP Coordinates:")
for ap in ap_coordinates:
    print(ap)
print("----------------------")
print("Host Coordinates:")
for host in host_coordinates:
    print(host)
print("======================")

# nk = [1, 2]  # 根据需要提供 nk 的值
# nk 为AP和Host之间各种墙面的影响数量
# corridor wall for W1, 
# the partition wall for W2, 
# the intervening wall for W3, 
# the glass wall for W4, 
# the elevator wall for W5, 
# and the door for W6.
# Roy的程序中注释掉了墙面的影响，默认就是一堵墙
print("Single Throughput")
print("----------------------")
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
        if ap_name.endswith("2"):
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
                result = calculate_throughput_estimate(parameters, (host_x, host_y), (ap_x, ap_y), nk)
                print(f"{host_name} for {ap_name}: {result}")
                results[i][j] = result

            except ValueError as e:
                print(e)
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
                result = calculate_throughput_estimate(parameters, (host_x, host_y), (ap_x, ap_y), nk)
                print(f"{host_name} for {ap_name}: {result}")
                results[i][j] = result

            except ValueError as e:
                print(e)
#---------------------------------------------------------------------


#---------------------------------------------------------------------
# 决定连接方案从而决定同时连接的数量m
# concurrent throughput calc.
# calc signal/success rate factor
print("======================")
print("Connection assignments")
print("----------------------")
for i, matrix in enumerate(all_matrices):
    print(f"Connection {i + 1}:")
    for row in matrix:
        print(row)

# print(results)
print("======================")
print("Concurret throughput")
print("----------------------")
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
    print(f"Connection {i + 1} Results:")
    print(all_con_results[i])
    print()
#---------------------------------------------------------------------

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

print("======================")
print("Fairness connection results")
print("----------------------")
for i, fair_results in enumerate(all_fair_results):
    print(f"Connection {i + 1} Results:")
    print(all_fair_results[i])
    print()

#---------------------------------------------------------------------



#---------------------------------------------------------------------
# 计算fairness index

# 初始化记录公平性指数的列表
all_fairness_index =[]

for i, fair_results in enumerate(all_fair_results):
    print(f"Connection {i + 1} fairness index:")
    calc_value = all_fair_results[i]
    fairness_index = calculate_fairness_index(calc_value)
    fairness_index = round(fairness_index, 6)
    print(fairness_index)
    all_fairness_index.append(fairness_index)
#---------------------------------------------------------------------



#---------------------------------------------------------------------
# 排序寻找最佳的连接方式
# 因为fairness index和总吞吐量之间的单位相差过大，
# 因此使用归一化方法，将总吞吐量转化为和fairness index一样的单位范围，
# 然后通过设计权重去判断合适的最佳组合。

best_connections = []

# 根据结果确定权重，初始化权重
W_1 = 0
W_2 = 0

# 判断总吞吐量的离散程度
# 由于吞吐量在实际测量中存在上下波动，
# 如果总吞吐量相差只有1或者2的话实际上不同的连接方式最后测量的结果相差不大
# 若吞吐量相差不大的话则优先考虑公平性指数，如果总吞吐量相差过大则优先考虑吞吐量大小
'''
総スループットの分散を判断する
実際の測定ではスループットは上下に変動するため、
たとえば、総スループットの差が1か2しかない場合、異なる接続方法の間で最終的な測定値に大きな差は生じない。
スループットの差が小さい場合は公平性指標を優先し、
総スループットの差が大きすぎる場合はスループットサイズを優先する。
'''


# 计算每种连接方式下的总吞吐量大小
all_totals =[]
for i, fair_results in enumerate(all_fair_results):
    total = 0
    for sub_list in fair_results:
        total += sum(sub_list)
    all_totals.append(total)

# 指定阈值
impact_threshold = 10
# 计算所有连接方式的数量
connection_num = len(all_matrices)

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
    # 如果大部分（1/2）的连接情况下，吞吐量相差不大，则优先考虑公平性指数
    if cont >= connection_num / 2:
        return True

# 调用均值计算函数
throughput_data = all_totals
if categorize_throughput(throughput_data, impact_threshold):
    W_2 = 0.3
else:
    W_2 = 0.7

W_1 = 1 - W_2

print()
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

print("======================")
print()
print("Top 3 Best Connections:")

# 输出最佳的三个连接方式
for i, (index, score, fairness_index, total) in enumerate(best_connections[:3]):
    print(f"Rank {i + 1}: Connection[{index+1}], Total Score: {score:.2f}, Fairness Index: {fairness_index:.6f}, Total Throughput: {total:.2f}")
    print("Connection Details:")
    print(f"Connection {index + 1}:")
    for row in all_matrices[index]:
        print(row)
    print()
print("======================")

if middle_index >= 0:
    print("Middle Connection:")
    mid_index, mid_score, mid_fairness, mid_total = best_connections[middle_index]
    print(f"Rank {middle_index + 1}: Connection[{mid_index + 1}], Total Score: {mid_score:.2f}, Fairness Index: {mid_fairness:.6f}, Total Throughput: {mid_total:.2f}")
    print("Connection Details:")
    print(f"Connection {mid_index + 1}:")
    for row in all_matrices[mid_index]:
        print(row)
    print("======================")

if worst_index == -1:
    worst_index, worst_score, worst_fairness, worst_total = best_connections[-1]
    print("Worst Connection:")
    print(f"Rank {len(best_connections)}: Connection[{worst_index + 1}], Total Score: {worst_score:.2f}, Fairness Index: {worst_fairness:.6f}, Total Throughput: {worst_total:.2f}")
    print("Connection Details:")
    print(f"Connection {worst_index + 1}:")
    for row in all_matrices[worst_index]:
        print(row)
    print("======================")

#---------------------------------------------------------------------
# 输出代码运行时间
# 记录结束时间
end_time = time.time()
# 计算代码执行时间
execution_time = end_time - start_time
print(f"Code executed in {execution_time:.2f} seconds")
print("======================")

#---------------------------------------------------------------------
output_file.close()
sys.stdout = sys.__stdout__