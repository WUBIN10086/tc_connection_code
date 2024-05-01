#================================================================
# Rewrite the code from Roy: active AP algorithm
# Last modify date: 2024 05/1
# Author: WU BIN
#================================================================
import random
import csv
import sys
from throughput_estimation import Distance

# Default paramerter
Default_RandomSeed = 50
Location_csv_path = 'model\Location\Exp1\Eng_Location.csv'
# Custom_RandomSeed = sys.argv[2]

# Generate random number
random.seed(50) # Default seed = 50

APCoverageRm = 110 # APcoverage(m)
Max_Host = 50 # max capacity of host numbers

# read AP and Host number from CSV
with open(Location_csv_path, newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    Num_AP = 0
    Num_Host = 0
    for row in reader:
        if row["Type"] == "Host":
            Num_Host += 1
        elif row["Type"] == "AP":
            Num_AP += 1


# main start
Num_APAll = 0
Num_APReal = 0
Num_MobAP = 0
Num_VirtualAP = 0
Num_DefectAP = 0

# for i in range(Num_AP):
#     if AI[i].type == 0:
#         Num_APAll += 1
#         Num_APReal += 1
#         AI[i].participateInSelection = 1
#     elif AI[i].type == 1:
#         Num_VirtualAP += 1
#         AI[i].participateInSelection = 0
#     elif AI[i].type == 2:
#         Num_MobAP += 1
#         AI[i].participateInSelection = 0
#     else:
#         Num_DefectAP += 1
#         AI[i].participateInSelection = 0

linkSpeedThreshold = float(1)
AverageHostThroughputThreshold = float(1.5)
LOOP_COUNT_LB_TX_TIME = int(365)
LOOP_COUNT_HILL_CLIMB_LB_TX_TIME = int(90)
LOOP_COUNT_AP_SELECTION_OPTIMIZATION = int(18)
HILL_CLIMB_MUTATION_FACTOR = int(0.9)
AP_SELECTION_HILL_CLIMBING_RATIO = int(.5)
THROUGHPUT_IMPROVE_MARGIN = float(.1)
totalBandwidth = float(1000)

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

# 遍历每个主机和每个接入点，计算距离
# 初始化结果数组，填充为0
num_hosts = len(host_coordinates)
num_aps = len(ap_coordinates)
results = [[0.0] * num_aps for _ in range(num_hosts)]
# 计算每个Host到每个AP的距离
for i, (host_name, host_x, host_y) in enumerate(host_coordinates):
    for j, (ap_name, ap_x, ap_y) in enumerate(ap_coordinates):
        result = Distance(host_x, host_y, ap_x, ap_y)
        results[i][j] = round(result,3)

print(results)