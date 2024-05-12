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
    def connect_to_ap(self, ap_id):
        self.connected_ap = ap_id
    def __repr__(self):
        return f"Host({self.name}, X={self.x}, Y={self.y}, Connected AP={self.connected_ap})"

#============================================================================
# Read command-line arguments
# Location_csv_path = sys.argv[1]
# output_filename = sys.argv[2]
# Walls_csv_path = sys.argv[3]
Location_csv_path = 'model/Location/Exp1/After avtive AP/Eng_Location.csv'
output_filename = "Topology_1.txt"
Walls_csv_path = 'model/Location/Exp1/After avtive AP/Walls.csv'
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
        max_distance_host[ap_name] = max(distance_matrix[ap_name], key=distance_matrix[ap_name].get)
    # 初始化种群
    for _ in range(size):
        individual = {}
        for ap_name in aps.keys():
            available_hosts = list(hosts.keys())
            # 排除最远的Host
            available_hosts.remove(max_distance_host[ap_name])
            # 随机选择一定数量的Host连接到此AP，但不超过max_hosts_per_ap
            individual[ap_name] = random.sample(available_hosts, min(len(available_hosts), max_hosts_per_ap))
        population.append(individual)
    return population

# # 计算个体的适应度


# 遗传算法函数
def genetic_algorithm(hosts, aps, population_size, generations, max_ap_connetion_num):
    population = initialize_population(population_size, hosts, aps, max_ap_connetion_num)
    
    return population[0]

# Main函数部分
#============================================================================
def main():
    global host_n
    global AP_m
    host_n = 0 # 初始化
    AP_m = 0
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
            if ap_name.endswith("_2"):  # 判断是否为5G接口
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
    generations = 100
    population_size = LOOP_COUNT
    best_setup = genetic_algorithm(HostInfo, APInfo, population_size, generations, max_ap_connetion_num )
    # 设定循环次数
    LOOP_COUNT = 1000




if __name__ == "__main__":
    main()