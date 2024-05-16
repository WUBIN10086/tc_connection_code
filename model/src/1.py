#================================================================
# Connection decision model calculation
# Last modify date: 2024 05/31
#================================================================
"""
+ 采用字典形式更新了AP和Host的数据
+ 对最佳组合的寻找方式不在进行遍历，因为数量太多
+ 采用遗传算法进行最佳组合的多目标优化
+ 优化的目标为：更加公平的吞吐量以及总吞吐量大小
+ 对于决定两个优化目标的权重问题，采用模糊逻辑进行判断
+ 对于遗传算法随机生成的连接组合，通过预处理减少搜索空间,在初始化连接分配时
+ 预处理包括：AP最大数量连接限制，距离筛选
"""
#=================================================================
import csv
import time
import datetime
import random
from throughput_estimation import calculate_throughput_estimate, Distance
from concurrent_calc import calculate_srf
from fairness_calc import Fairness_calc
from fairness_index import calculate_fairness_index
from write_to_output import write_to_file, clear_output_file
import numpy as np
import pandas as pd
import math

# 设置数据结构
class AP:
    def __init__(self, name, x, y):
        self.name = name
        self.x = x
        self.y = y
        self.connected_hosts = []
        self.connect_list = []
    def connect_host(self, host_id):
        self.connected_hosts.append(host_id)
    def __repr__(self):
        return f"AP({self.name}, X={self.x}, Y={self.y}, Connected Hosts={self.connected_hosts})"

class Host:
    def __init__(self, name, x, y):
        self.name = name
        self.x = x
        self.y = y
        self.connected_ap = None
        self.speed = None
    def connect_to_ap(self, ap_id):
        self.connected_ap = ap_id
    def __repr__(self):
        return f"Host({self.name}, X={self.x}, Y={self.y}, Connected AP={self.connected_ap}, speed={self.speed})"

# 设定循环次数
POPULATION_NUM = 1000
PRO_OF_MUTATION = 0.12
GENERATION_COUNT = 2000
#============================================================================
# Read command-line arguments
# Location_csv_path = sys.argv[1]
# output_filename = sys.argv[2]
# Walls_csv_path = sys.argv[3]
# Location_csv_path = 'model/Location/Exp2/After avtive AP/Eng_Location.csv'
Location_csv_path = 'model/Location/Exp4/After avtive AP/Gra_Location.csv'
output_filename = "Topology_4_4.txt"
Walls_csv_path = 'model/Location/Exp4/After avtive AP/Walls.csv'
# random.seed = 50
#============================================================================



# 函数部分
#============================================================================
# 读取AP以及Host的信息：
# 修改后的读取位置数据的函数
def read_locations(csv_path):
    aps = {}
    hosts = {}
    
    with open(csv_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            name = row["Name"]
            x = float(row["X"])
            y = float(row["Y"])
            entity_type = row["Type"]
            
            if entity_type == "AP":
                aps[name] = AP(name, x, y)
            elif entity_type == "Host":
                hosts[name] = Host(name, x, y)
    
    return aps, hosts

def get_wall_info(walls_data, ap_name, host_name):
    """
    查询并返回指定AP和Host之间的墙面信息。

    参数:
    - walls_data: pandas DataFrame，包含墙面信息的数据。
    - ap_name: 字符串，接入点的名称。
    - host_name: 字符串，主机的名称。

    返回:
    - list: 包含墙面信息的列表，如果没有找到信息，则返回默认值。
    """
    wall_info = walls_data[(walls_data['AP_Name'] == ap_name) & (walls_data['Host_Name'] == host_name)]
    if not wall_info.empty:
        return wall_info.iloc[0, 2:].tolist()  # 获取除前两列之外的所有数据
    else:
        print(f"No wall data found for AP {ap_name} and Host {host_name}")
        return [0] * (walls_data.shape[1] - 2)  # 返回与列数相匹配的零列表

def load_parameters(file_path):
    """
    从给定的文件路径读取网络参数。

    参数:
    - file_path: 字符串，指向含有网络参数的文件的路径。

    返回:
    - dict: 包含所有参数的字典。
    """
    parameters = {}
    with open(file_path, "r") as file:
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

    return parameters

# 初始化连接分配：
# 初始化连接分配中加入了预筛选减少搜索空间：
# 1. 距离准则，排除距离太远的连接
# 2. 排除每个AP连接过多的host
# 3. 保证每个Host只连接到一个AP
# 4. 保证每个AP都有Host连接
def initialize_population(size, hosts, aps, max_ap_connection_num):
    # Size为初始循环次数
    # hosts和aps为存储信息的字典
    population = []
    max_hosts_per_ap = max_ap_connection_num # AP能连接的最大的host数量
    # 计算每个AP与所有Host的距离，然后确定最远的Host
    distance_matrix = {ap_name: {} for ap_name in aps.keys()}
    max_distance_host = {}
    for ap_name, ap in aps.items():
        for host_name, host in hosts.items():
            # 假设Distance函数返回两点之间的距离
            distance = Distance(ap.x, ap.y, host.x, host.y)
            distance_matrix[ap_name][host_name] = distance
        # 找到与此AP距离最远的Host
        # 找到与此AP距离最远的Host，并存储host名和距离
        furthest_host = max(distance_matrix[ap_name], key=distance_matrix[ap_name].get)
        max_distance = distance_matrix[ap_name][furthest_host]
        max_distance_host[ap_name] = (furthest_host, max_distance)
    # 初始化种群
    for _ in range(size):
        individual = {ap_name: [] for ap_name in aps.keys()}  # 每个AP初始化空列表
        available_hosts = list(hosts.keys())  # 所有可用的Hosts

        # 移除每个AP的最远Host
        for ap_name in aps.keys():
            if max_distance_host[ap_name] in available_hosts:
                available_hosts.remove(max_distance_host[ap_name])

        # 随机打乱Host列表和AP列表
        random.shuffle(available_hosts)
        ap_order = list(aps.keys()) * max_hosts_per_ap
        random.shuffle(ap_order)

        # 优先保证每个AP至少连接一个Host
        for ap_name in aps.keys():
            for host in available_hosts:
                if len(individual[ap_name]) < 1:  # 确保至少有一个Host
                    individual[ap_name].append(host)
                    available_hosts.remove(host)
                    break

        # 继续分配剩余的Host
        for host in available_hosts:
            for ap_name in ap_order:
                if len(individual[ap_name]) < max_hosts_per_ap:
                    individual[ap_name].append(host)
                    available_hosts.remove(host)
                    break

        population.append(individual)
    return population,distance_matrix,max_distance_host,max_distance
# 这里返回值是是所有连接方式的种群
# 其中的individual形式是字典，一代里面包含每个AP的名字，以及对应连接的Host的名字 

# 计算个体的适应度
# 個々の適性の計算
def fitness(individual, Single_throughput, hosts):
    total_throughput = 0
    throughput_list = []
    # 计算fairness target大小
    # 1. 计算同时连接数量：
    for ap, connected_hosts in individual.items():
        concurrent_num = len(connected_hosts)
        srf = calculate_srf(concurrent_num)
        S = []
        C = []
        # 2. 计算fairness target大小
        for index, host in enumerate(connected_hosts):
            S.append(Single_throughput[(host, ap)])
            concurrent_throughput = srf * Single_throughput[(host, ap)]
            C.append(concurrent_throughput)
        Fairness_target = Fairness_calc(concurrent_num,S,C)
        sum = concurrent_num * Fairness_target
        for index, host in enumerate(connected_hosts):
            hosts[host].speed = Fairness_target
            hosts[host].connected_ap = ap
            throughput_list.append(hosts[host].speed) 
        total_throughput += sum
    # 计算Fairness index
    fairness_index = calculate_jains_fairness_index(throughput_list)

    return fairness_index, total_throughput

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

def calculate_variance(values):
    mean = sum(values) / len(values)
    return sum((x - mean) ** 2 for x in values) / len(values)

# 归一化函数
# 正規化関数
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

def calculate_jains_fairness_index(throughputs):
    if not throughputs:  # Ensure the list is not empty
        return 0
    num_users = len(throughputs)
    sum_of_throughputs = sum(throughputs)
    sum_of_squares = sum(x ** 2 for x in throughputs)
    if sum_of_squares == 0:  # Prevent division by zero
        return 0
    fairness_index = (sum_of_throughputs ** 2) / (num_users * sum_of_squares)
    return fairness_index

def crossover(parent1, parent2, aps, hosts, distance_matrix, max_hosts_per_ap):
    child = {ap: [] for ap in aps}
    unassigned_hosts = set(hosts)  # 初始化所有host

    # 首先，根据父代的综合偏好确定主机分配的优先次序
    for ap in aps:
        preferred_hosts = list(set(parent1[ap] + parent2[ap]))
        random.shuffle(preferred_hosts)  # 洗牌，引入一些随机选择

        for host in preferred_hosts:
            if host in unassigned_hosts and len(child[ap]) < max_hosts_per_ap:
                child[ap].append(host)
                unassigned_hosts.remove(host)

    # 保证每个AP连接至少一个Host
    for ap in aps:
        if not child[ap]:  # 如果AP未连接任何Host
            if unassigned_hosts:
                # 分配最近的可用Host，确保距离位置优先
                nearest_host = min(unassigned_hosts, key=lambda host: distance_matrix[ap][host])
                child[ap].append(nearest_host)
                unassigned_hosts.remove(nearest_host)

    # 如果仍有未分配的Host，则将其分配给能接收更多Host的AP
    for host in list(unassigned_hosts):  # 迭代列表副本 Iterate over a list copy since we're modifying the set
        aps_with_capacity = [ap for ap in aps if len(child[ap]) < max_hosts_per_ap]
        if aps_with_capacity:
            # 根据容量和邻近程度将Host分配给适合的接入点
            ap_to_assign = min(aps_with_capacity, key=lambda ap: distance_matrix[ap][host])
            child[ap_to_assign].append(host)
            unassigned_hosts.remove(host)

    # 再次检查
    if any(len(child[ap]) == 0 for ap in aps):
        for ap in aps:
            if len(child[ap]) == 0:
                # Find an AP to borrow a host from; choose the one with the most hosts
                donor_ap = max((a for a in aps if len(child[a]) > 1), key=lambda a: len(child[a]), default=None)
                if donor_ap:
                    # Move one host from the donor to the needy AP
                    host_to_move = child[donor_ap].pop()
                    child[ap].append(host_to_move)

    return child

def mutate(individual, hosts, aps, distance_matrix, max_hosts_per_ap, max_distance_host):
    if random.random() < PRO_OF_MUTATION:
        muta_individual = {ap_name: [] for ap_name in aps.keys()}  # 每个AP初始化空列表
        available_hosts = list(hosts.keys())  # 所有可用的Hosts
        individual = muta_individual
        # 移除每个AP的最远Host
        for ap_name in aps.keys():
            if max_distance_host[ap_name] in available_hosts:
                available_hosts.remove(max_distance_host[ap_name])

        # 随机打乱Host列表和AP列表
        random.shuffle(available_hosts)
        ap_order = list(aps.keys()) * max_hosts_per_ap
        random.shuffle(ap_order)

        # 优先保证每个AP至少连接一个Host
        for ap_name in aps.keys():
            for host in available_hosts:
                if len(individual[ap_name]) < 1:  # 确保至少有一个Host
                    individual[ap_name].append(host)
                    available_hosts.remove(host)
                    break

        # 继续分配剩余的Host
        for host in available_hosts:
            for ap_name in ap_order:
                if len(individual[ap_name]) < max_hosts_per_ap:
                    individual[ap_name].append(host)
                    available_hosts.remove(host)
                    break
    muta_individual = individual
    return muta_individual


# 遗传算法函数
def genetic_algorithm(hosts, aps, population_size, generations, max_ap_connetion_num, Single_throughput):
    distance_matrix = {ap_name: {host_name: Distance(aps[ap_name].x, aps[ap_name].y, hosts[host_name].x, hosts[host_name].y) for host_name in hosts} for ap_name in aps}
    max_distance_host = {ap: max(distance_matrix[ap], key=distance_matrix[ap].get) for ap in aps}
    population,distance_matrix,max_distance_host,max_distance = initialize_population(population_size, hosts, aps, max_ap_connetion_num)

    for _ in range(generations):
        print("Generation: ",_)
        print("------------------")
        scores = []
        throughput_values = [fitness(ind, Single_throughput, hosts)[1] for ind in population]
        normalized_throughput = normalize(throughput_values)
        variance = calculate_variance(throughput_values)
        low_threshold = host_n * 1.5
        high_threshold = host_n * 8
        # 使用模糊逻辑进行得分权重的判断
        # # ファジーロジックを用いた得点の重み付け
        W_1, W_2 = fuzzy_weight(variance, high_threshold, low_threshold)
        # W_1 = 0.9 
        # W_2 = 0.3
        for ind, norm_tp in zip(population, normalized_throughput):
            fi, _ = fitness(ind, Single_throughput, hosts)
            score = W_1 * fi + W_2 * norm_tp
            scores.append((ind, score))

        # 根据计算得出的得分进行排序 
        # 算出された得点に基づくランキング
        scores.sort(key=lambda x: x[1], reverse=True)
        population = [x[0] for x in scores]  # 更新population为排序后的个体
        next_generation = population[:2]  # 精英主义
        while len(next_generation) < population_size:
            parent1, parent2 = random.sample(population[:10], 2)  # 锦标赛选择
            child = crossover(parent1, parent2, aps, hosts, distance_matrix, max_ap_connetion_num)
            mutate(child, hosts, aps, distance_matrix, max_ap_connetion_num, max_distance_host)
            next_generation.append(child)
        population = next_generation

    return population[0]


# Main函数部分
#============================================================================
def main():
    # 记录开始时间
    start_time = time.time()
    global host_n
    global AP_m
    host_n = 0 # 初始化
    AP_m = 0
    # np.random.seed(0)
    # random.seed(50)
    # 清理并写入初始数据到输出文件
    clear_output_file(output_filename)
    current_datetime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    write_to_file(f"Date and Time: {current_datetime}", output_filename)
    # 开始处理标志：
    print("START!!!")

    # 从 CSV 文件中读取 Host 和 AP 的数量
    with open(Location_csv_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row["Type"] == "Host":
                host_n += 1
            elif row["Type"] == "AP":
                AP_m += 1
    write_to_file(f"======================", output_filename)
    write_to_file(f"Devices number", output_filename)
    write_to_file(f"----------------------", output_filename)
    write_to_file(f"Number of Hosts: {host_n}", output_filename)
    write_to_file(f"Number of APs: {AP_m}", output_filename)
    print("Read Devices number: Finished")

    # 加载位置
    write_to_file(f"======================", output_filename)
    APInfo, HostInfo = read_locations(Location_csv_path)
    # print(APInfo,HostInfo)

    # 读取墙面信息
    walls_data = pd.read_csv(Walls_csv_path)
   
    # 读取参数地址
    parameters_24_path = "model/etc/parameters.txt"
    parameters_5_path = "model/etc/parameters2.txt"

    # 计算单一吞吐量
    # 初始化Single Throughput存储字典
    Single_throughput = {}
    # 输出Single
    write_to_file("Single Throughput", output_filename)
    # 遍历AP和Host字典的键和值
    for ap_name, ap in APInfo.items():
        write_to_file("----------------------", output_filename)
        write_to_file(f"{ap_name}:", output_filename)
        for host_name, host in HostInfo.items():
            if ap_name.endswith("_1"):  # 判断是否为2.4G接口
                parameters = load_parameters(parameters_24_path)
                ap_coordinates = (ap.x, ap.y)
                host_coordinates = (host.x, host.y)
                nk = get_wall_info(walls_data, ap_name, host_name)
                result = calculate_throughput_estimate(parameters, host_coordinates, ap_coordinates, nk)
                Single_throughput[(host_name, ap_name)] = result
                write_to_file(f"{host_name}: {result}", output_filename)
            else:
                parameters = load_parameters(parameters_5_path)
                ap_coordinates = (ap.x, ap.y)
                host_coordinates = (host.x, host.y)
                nk = get_wall_info(walls_data, ap_name, host_name)
                result = calculate_throughput_estimate(parameters, host_coordinates, ap_coordinates, nk)
                Single_throughput[(host_name, ap_name)] = result
                write_to_file(f"{host_name}: {result}", output_filename)
    print("Single Throughput Calculated")

    # 设定每个AP的最大连接Host数量： 
    max_ap_connetion_num = math.floor(host_n * 0.8)
    generations = GENERATION_COUNT
    population_size = POPULATION_NUM
    best_setup = genetic_algorithm(HostInfo, APInfo, population_size, generations, max_ap_connetion_num, Single_throughput)
    execution_time = time.time() - start_time
    # 将最佳设置写入输出文件
    write_to_file("----------------------", output_filename)
    write_to_file(f"Best Setup:", output_filename)
    # 输出结果：
    throughput_list = []
    a = 0
    for ap, connected_hosts in best_setup.items():
        concurrent_num = len(connected_hosts)
        srf = calculate_srf(concurrent_num)
        S = []
        C = []
        for host in connected_hosts:
            S.append(Single_throughput[(host, ap)])
            concurrent_throughput = srf * Single_throughput[(host, ap)]
            C.append(concurrent_throughput)
        Fairness_target = Fairness_calc(concurrent_num, S, C)
        sum_throughput = concurrent_num * Fairness_target
        a += sum_throughput
        write_to_file(f"AP: {ap} connects to hosts {connected_hosts}\n"
                       f"Fairness_target: {Fairness_target:.3f}\n", output_filename)
        for index, host in enumerate(connected_hosts):
            throughput_list.append(HostInfo[host].speed) 
    # 计算Fairness index
    write_to_file("----------------------", output_filename)
    fairness_index = calculate_jains_fairness_index(throughput_list)
    write_to_file(f"Fairness index: {fairness_index}", output_filename)
    write_to_file("----------------------", output_filename)
    write_to_file(f"Total throughput: {a}", output_filename)
    write_to_file(f"Code executed in {execution_time:.2f} seconds", output_filename)
    print("Procedure Finished!!!")

if __name__ == "__main__":
    main()