#================================================================
# Rewrite the code from Roy: active AP algorithm
# Last modify date: 2024 05/1
# Author: WU BIN
#================================================================
import random
import csv
import sys
import pandas as pd
from throughput_estimation import Distance
from throughput_estimation import calculate_throughput_estimate

# Default paramerter
Default_RandomSeed = 50
Location_csv_path = 'model\Location\Exp1\Eng_Location.csv'
# Custom_RandomSeed = sys.argv[2]
# Walls_csv_path = sys.argv[3]
Walls_csv_path = 'model\Location\Exp1\Walls.csv'

# Generate random number
random.seed(50) # Default seed = 50

APCoverageRm = 110 # APcoverage(m)
Max_Host = 50 # max capacity of host numbers

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

# 例如结果为
# [3.607, 3.607], 
# [1.789, 1.789], 
# [3.970, 3.970]
# 上边的列代表AP，行代表Host

# print(results)

#-------------------------------------------------------------------
# 判断距离是否在AP的覆盖范围内，初步创建连接关系
# 对应APCms272.cpp中的determineAssociabilityOfAP_HostUsingOnlyCoverageRadius()函数
# 创建一个空白的连接
# i索引是Host
# j索引是AP
# 在Roy的代码里这个Connection_Results应该是Aggr[i][j]
Connection_Results = [[0.0] * num_aps for _ in range(num_hosts)]
for i in range(num_hosts):
    for j in range(num_aps):
        if results[i][j] <= APCoverageRm:
            Connection_Results[i][j] = 1
# print(Connection_Results)
#-------------------------------------------------------------------


#-------------------------------------------------------------------
# 通过最大连接速度更新AP和Host之间的临接关系
# 对应APCms272.cpp中的phase_initialization()函数
# function phase_initialization()
#     初始化数组以存储每个主机的最大链接速度和对应的AP索引
#     初始化每个主机和AP的基本信息和连接状态

#     遍历每个AP：
#         对于每个AP，遍历它所连接的每个主机：
#             如果该主机和AP属于允许互联的组：
#                 计算并更新该主机与当前AP的链接速度
#                 如果链接速度高于当前记录的最大速度：
#                     更新该主机的最大链接速度和对应的AP索引
#                 如果链接速度超过预设阈值：
#                     在AINew和HINew中记录该连接

#     遍历每个主机：
#         如果某主机没有任何连接：
#             将该主机连接到之前计算出的最大速度的AP
#             更新连接信息
#     初始化所有AP为非激活状态

# 初始化每个AP以及Host之间的最大连接速度
num_hosts = len(host_coordinates)
num_aps = len(ap_coordinates)
Max_speed_results = [[0.0] * num_aps for _ in range(num_hosts)]
# 目前每个AP和Host之间的连接状态为Connection_Results
# 读取墙面信息
walls_data = pd.read_csv(Walls_csv_path)

# 遍历每个主机和每个接入点，计算吞吐量
for i, (host_name, host_x, host_y) in enumerate(host_coordinates):
    for j, (ap_name, ap_x, ap_y) in enumerate(ap_coordinates):
        # 根据上边的范围判定结果判断是否在连接范围内
        if Connection_Results[i][j] == 1:
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
                    Max_speed_results[i][j] = result

                except ValueError as e:
                    print("Error! Please check the ActiveAP.py while calculate the single throughput!")
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
                    Max_speed_results[i][j] = result

                except ValueError as e:
                    print("Error! Please check the ActiveAP.py while calculate the single throughput!")
        else:
            Max_speed_results[i][j] = 0
            print("The Host",i+1,"is not in the AP",j+1,"coverage!")

# 对于Max_speed_results，找出其中每一行（也就是每个Host）对应的最大速度的AP
# Max_speed_results存放的是每个Host连接到每个AP的最大速度


# init_Connection_Results代表经过最大化计算速度之后的连接方案
init_Connection_Results = [[0] * num_aps for _ in range(num_hosts)]
init_Max_speed = [[0.0] * num_aps for _ in range(num_hosts)]

# 遍历每个Host
for i in range(num_hosts):
    # 获取当前Host对所有AP的最大速度值
    max_speed = max(Max_speed_results[i])
    # 找到最大速度对应的AP的索引
    max_index = Max_speed_results[i].index(max_speed)
    if max_speed >= linkSpeedThreshold:
        # 在Connection_Results中设置该AP为1
        init_Connection_Results[i][max_index] = 1
        init_Max_speed[i][max_index] = max_speed

for i in range(num_hosts):
    # 如果Host没有连接任何AP：
    # 则分配给之前计算的最大速度的AP
    connect_index = max(init_Connection_Results[i])
    if connect_index == 0:
        max_speed = max(Max_speed_results[i])
        max_index = Max_speed_results[i].index(max_speed)
        # 在Connection_Results中设置该AP为1
        init_Connection_Results[i][max_index] = 1
        init_Max_speed[i][max_index] = max_speed

# print(init_Connection_Results)
# print(init_Max_speed)
# 到这一步已经找到每个Host连接速度最快的AP了
# 最快连接速度和连接方案写在init_Connection_Results和init_Max_speed
#-------------------------------------------------------------------


#-------------------------------------------------------------------
# 筛选有链接的AP的总数
# 初始化
sumLinkCandidate = []
# 遍历每行（每个Host）
for row in init_Connection_Results:
    # 遍历每列（每个AP）
    for col_index, value in enumerate(row):
        # 检查是否存在连接
        if value == 1:
            # 如果这个AP的编号尚未加入列表，则加入
            if col_index not in sumLinkCandidate:
                sumLinkCandidate.append(col_index)
sumLinkCandidate = sorted(sumLinkCandidate)
# print(sumLinkCandidate)

# 累加每个AP的连接总速度
AP_HostLinkSpeed = []
# 遍历所有有链接的AP
for index, ap_index in enumerate(sumLinkCandidate):
    sumLinkSpeed = 0  # 初始化该AP的连接速度总和
    # 遍历每个Host
    for i in range(num_hosts):
        # 累加这个AP的连接速度，只对有连接的AP进行计算
        if init_Connection_Results[i][ap_index] == 1:
            sumLinkSpeed += init_Max_speed[i][ap_index]
    # 将累加结果存储
    AP_HostLinkSpeed.append(sumLinkSpeed)
# print(AP_HostLinkSpeed)
#-------------------------------------------------------------------


#-------------------------------------------------------------------
# 对应phase_initial_solution_search();
# 总觉得这段有点多余呢
# 但是因为以前的代码也写了所以我就加上了
# --------05.04---------------------------
# 好像也不是很多余，这段应该是假设只激活一个AP的情况下，找到只激活
# 一个AP时最大的总吞吐量AP的索引


def phase_initial_solution_search(Connection_Results, Max_speed_results, num_hosts, num_aps):
    # 初始化激活AP的索引
    ifActive_AP = [0] * num_aps
    maxAPThroughput = [0] * num_aps
    # 遍历所有的AP
    for j in range(num_aps): # 当且仅当一个AP激活的时候
        total_throughput = 0
        for i in range(num_hosts):
            if Connection_Results[i][j] == 1:  # 这里是根据第一步，通过范围判定AP能否连接的结果
                total_throughput += Max_speed_results[i][j] # 这里的Max_speed_results指的是每个Host连接AP的最大速度
        maxAPThroughput[j] = total_throughput
    # 寻找总吞吐量最高的那个
    best_ap_index = maxAPThroughput.index(max(maxAPThroughput))
    ifActive_AP[best_ap_index] = 1  # 激活这个AP
    return ifActive_AP

ifActive_AP = phase_initial_solution_search(Connection_Results, Max_speed_results, num_hosts, num_aps)
# print("Initial Active APs:", ifActive_AP)

# 更新数据信息：
best_ap_index = ifActive_AP.index(max(ifActive_AP))
# print(best_ap_index)
init_Connection_Results = [[0] * num_aps for _ in range(num_hosts)]
for i in range(num_hosts):
        init_Connection_Results[i][best_ap_index] = 1
# print(init_Connection_Results)
#-------------------------------------------------------------------


#-------------------------------------------------------------------
# 对应phase_AP_host_association_optimization()
# 迭代所有主机并根据定义的指标评估切换当前 AP 连接是否可以提高网络性能
def phase_AP_host_association_optimization(init_Connection_Results, init_Max_speed, num_hosts, num_aps):
    improved = True
    while improved:
        improved = False
        for i in range(num_hosts):
            current_ap = None
            current_max_speed = 0
            # 确定当前的连接方案下的速度
            for j in range(num_aps):
                if init_Connection_Results[i][j] == 1:
                    current_ap = j
                    current_max_speed = init_Max_speed[i][j]
                    break

            # 寻找是否有更合适的连接
            for j in range(num_aps):
                if j != current_ap and init_Connection_Results[i][j] == 1:
                    potential_new_speed = init_Max_speed[i][j]
                    # 比较切换之后的吞吐量是否更加优秀
                    if potential_new_speed > current_max_speed:
                        # 更新连接方案
                        init_Connection_Results[i][current_ap] = 0
                        init_Connection_Results[i][j] = 1
                        improved = True
                        # print(f"Host {i} switched from AP {current_ap} to AP {j} for better throughput.")
                        break
    return init_Connection_Results

# 执行函数
optimized_Connection_Results = phase_AP_host_association_optimization(Connection_Results, Max_speed_results, num_hosts, num_aps)
print("Optimized Host-AP Associations:", optimized_Connection_Results)
#-------------------------------------------------------------------


#-------------------------------------------------------------------
# 对应calculateMaxTxTimeAmongAPs()
def calculate_max_tx_time_among_aps(AIActive):
    max_tx_time = -0.1
    global_max_tx_time_ap = None
    for ap in AIActive:
        if ap['ifActive']:
            ap_tx_time = calculate_tx_time_for_ap(ap)  # Define this function based on C++ logic
            if ap_tx_time > max_tx_time:
                global_max_tx_time_ap = ap  # assuming ap is a dict or identifier
                max_tx_time = ap_tx_time
    return max_tx_time
#-------------------------------------------------------------------
# 对应calculateTxTimeForAP
def calculate_tx_time_for_ap(ap_index, AIActive, HIActive):
    sum_tx_time = 0.0
    tmp_map_speed = 30.00
    tmp_map_speed_accum = 0

    # 遍历连接到指定接入点的所有主机
    for j in range(AIActive[ap_index]['NoConHost']):
        host_index = AIActive[ap_index]['ConHost'][j] - 1  # Adjust index since Python uses 0-based indexing
        host_active_rate = HIActive[host_index]['HostActiveRate']
        assoc_ap_host_link_speed = HIActive[host_index]['AssocAP_HostLinkSpeed']

        if AIActive[ap_index]['type'] == 2:
            # Type 2 AP calculation
            sum_tx_time += host_active_rate / assoc_ap_host_link_speed
            tmp_map_speed_accum += host_active_rate / tmp_map_speed
        else:
            # Other AP types calculation
            sum_tx_time += host_active_rate / assoc_ap_host_link_speed

        # After processing all hosts, if the AP type is 2, compare and possibly update sum_tx_time
        if AIActive[ap_index]['type'] == 2:
            if tmp_map_speed_accum >= sum_tx_time:
                sum_tx_time = tmp_map_speed_accum

    return sum_tx_time



#-------------------------------------------------------------------




#-------------------------------------------------------------------
# 对应phase_additional_AP_activation();
def phase_additional_AP_activation(AIActive, HIActive, NoAP, NoHost, LOOP_COUNT_AP_SELECTION_OPTIMIZATION):
    no_of_active_ap = sum(1 for ap in AIActive if ap['ifActive'])
    best_found_no_of_active_ap = no_of_active_ap
    best_found_max_tx_time = calculate_max_tx_time_among_aps(AIActive)

    for ap in AIActive:
        if ap['participateInSelection'] == 0:
            continue
        ap['APSelectionflag'] = 0

    # Assuming AIActive is a list of dictionaries with keys like 'ifActive', 'participateInSelection', etc.
    # More processing needed here based on the actual data structure
    for loop_count in range(LOOP_COUNT_AP_SELECTION_OPTIMIZATION):
        # Your logic for optimizing AP selection and host distribution goes here
        pass

    return AIActive  # or any other relevant data to return



