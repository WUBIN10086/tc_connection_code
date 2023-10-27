#================================================================
# Connection decision model calculation
# Last modify date: 2023 10/20
#================================================================
# Change: make main code
#         example for 80211n protocol TP-Link T4UH ver.2
# funcation list: 1. read file
#                 2. use function
#                 3. connection decide algorithm
# algorithm step:
# 1. Decide AP numbers and Positions in the MAP, consider RSS cover range
# 2. Decide Host numbers and positions, output the coordinates in CSV file
# 3. Give top 3 connection plans by ML model
# 4. 
#=================================================================


#---------------------------------------------------------------------
# connection algorithm
import csv
import itertools
from throughput_estimation import calculate_throughput_estimate
from concurrent_calc import calculate_srf
#---------------------------------------------------------------------


#---------------------------------------------------------------------
# connection solution count part
# 需要改进，暂时版

# 计算了所有的连接情况

# input number of m and n
# create matrix for connect condition:
# element X_ij represent connect(1) or disconnect(0)

n = int(input("请输入行数 n: "))
m = int(input("请输入列数 m: "))

all_matrices = []

for combination in itertools.product([0, 1], repeat=n * m):
    matrix = [list(combination[i:i+m]) for i in range(0, n * m, m)]

    # 筛选条件1：删除包含 1 多于一个的行
    if all(row.count(1) <= 1 for row in matrix):
        # 筛选条件2：检查每一列是否至少有一个 1
        if all(any(row[j] == 1 for row in matrix) for j in range(m)):
            # 筛选条件3：检查每一行是否至少有一个 1
            if all(1 in row for row in matrix):
                all_matrices.append(matrix)

for i, matrix in enumerate(all_matrices):
    print(f"Matrix {i + 1}:")
    for row in matrix:
        print(row)
    print()
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
results = {}
# 遍历每个主机和每个接入点，计算吞吐量
for host_name, host_x, host_y in host_coordinates:
    for ap_name, ap_x, ap_y in ap_coordinates:
        nk = [0, 0, 0, 0, 0, 0]  # Update this with the appropriate nk values
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
                # 创建二维索引，把结果存入数组，并设置索引为对应的Host和AP
                if host_name not in results:
                    results[host_name] = {}
                results[host_name][ap_name] = result

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

                if host_name not in results:
                    results[host_name] = {}
                results[host_name][ap_name] = result

            except ValueError as e:
                print(e)
print("======================")
print(results)
#---------------------------------------------------------------------



#---------------------------------------------------------------------
# 决定连接方案从而决定同时连接的数量m




#---------------------------------------------------------------------
# concurrent throughput calc.
# calc signal/success rate factor


srf = calculate_srf(m)

concurrent_H[i]= single_thr[i] * srf
