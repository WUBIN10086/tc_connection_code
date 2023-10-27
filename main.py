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
# 3. 
#
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
# single throughput calc. part
# 示例用法
# 读取参数文件




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

 # 读取坐标文件
with open("coordinates.csv", newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    coordinates = list(reader)



#interface_i = int(input("Enter the target interface i (1, 2, 3, ...): "))
#Host_j = int(input("Enter the target Host j (1, 2, 3, ...): "))


# nk = [1, 2]  # 根据需要提供 nk 的值
# nk 为AP和Host之间各种墙面的影响数量
# corridor wall for W1, 
# the partition wall for W2, 
# the intervening wall for W3, 
# the glass wall for W4, 
# the elevator wall for W5, 
# and the door for W6.
# Roy的程序中注释掉了墙面的影响，默认就是一堵墙
nk = [0, 0, 0, 0, 0, 0]

#try:
    #result = calculate_throughput_estimate(parameters, coordinates, interface_i, Host_j, nk)
    #print(f"Single Thr_estimation of Host_j is: {result}")
#except ValueError as e:
    #print(e)


for i, host in enumerate(coordinates):
    for j, ap in enumerate(coordinates):
        try:
            result = calculate_throughput_estimate(parameters, coordinates, i, j, nk)
            print(f"Host_{i} for AP_{j}: {result}")
        except ValueError as e:
            print(e)
#---------------------------------------------------------------------


#---------------------------------------------------------------------
# concurrent throughput calc.
# calc signal/success rate factor
i = int(input("Enter the target AP i (1, 2, 3, ...): "))
j = int(input("Enter the target Host j (1, 2, 3, ...): "))
srf = calculate_srf(m)
thr = calculate_throughput_estimate(parameters, coordinates, i, j, nk)
concurrent = thr * srf
