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
# 1. Determine the number of interfaces and hosts in the network
# 2. 
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
# input number of m and n
n = int(input("Please input number of Host n: "))
m = int(input("Please input number of AP m: "))

host_list = list(range(n))
ap_list = list(range(m))

connection_combinations = list(itertools.permutations(ap_list, n))

all_matrices = []


for connection in connection_combinations:
    matrix_X = [[0 for _ in range(m)] for _ in range(n)]  # 初始化矩阵X

    for i, ap in enumerate(connection):
        matrix_X[i][ap] = 1

    all_matrices.append(matrix_X)

n = 0
for i, matrix in enumerate(all_matrices):
    n = n+1
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

i = int(input("Enter the target AP i (1, 2, 3, ...): "))
j = int(input("Enter the target Host j (1, 2, 3, ...): "))
nk = [1, 2]  # 根据需要提供 nk 的值

try:
    result = calculate_throughput_estimate(parameters, coordinates, i, j, nk)
    print(f"Thr_estimation is: {result}")
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
