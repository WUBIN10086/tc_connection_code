from throughput_estimation import calculate_throughput_estimate
import random
import copy
from math import exp
import csv

# 初始化参数
POPULATION_SIZE = 100
GENERATIONS = 50
CROSSOVER_RATE = 0.9
MUTATION_RATE = 0.1
LOOP_COUNT = 1000  # 模拟退火迭代次数
TEMPERATURE = 100  # 初始温度
COOLING_RATE = 0.95  # 冷却率

# 定义 APInfo 和 HostInfo 类
class APInfo:
    def __init__(self, apid, xpos, ypos):
        self.apid = apid
        self.xpos = xpos
        self.ypos = ypos
        self.active = False

class HostInfo:
    def __init__(self, hostid, xpos, ypos):
        self.hostid = hostid
        self.xpos = xpos
        self.ypos = ypos

# 读取网络信息和参数
def read_network_info(csv_path):
    aps = []
    hosts = []
    with open(csv_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row['Type'] == 'AP':
                aps.append(APInfo(apid=row['Name'], xpos=float(row['X']), ypos=float(row['Y'])))
            elif row['Type'] == 'Host':
                hosts.append(HostInfo(hostid=row['Name'], xpos=float(row['X']), ypos=float(row['Y'])))
    return aps, hosts

Walls_csv_path = 'model\Location\Exp1\Walls.csv'
walls_data = pd.read_csv(Walls_csv_path)
# 计算吞吐量
def calculate_throughput(aps, hosts):
    for ap in enumerate(aps):
        for host in enumerate(hosts):
            wall_info = walls_data[(walls_data['AP_Name'] == ap_name) & (walls_data['Host_Name'] == host_name)]
            nk = wall_info.iloc[0, 2:].tolist()
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
            throughput_values = calculate_throughput_estimate(parameters, (host.xpos,host.ypos), (ap.xpos,ap.ypos), nk)
    
    return throughput_values

def calculate_network_performance(activated_aps, hosts):
    # 这里仅为示例，需要实际的吞吐量计算逻辑
    throughput = sum(host.throughput for host in hosts if any(ap.active for ap in activated_aps))
    fairness = calculate_fairness(activated_aps, hosts)  # 假设存在此函数

    return throughput, fairness

# NSGA-II算法
def NSGA_II(aps, hosts):
    # 初始化种群
    population = initialize_population(POPULATION_SIZE, aps, hosts)
    for generation in range(GENERATIONS):
        # 评估种群
        evaluate_population(population, aps, hosts)
        # 选择和生成新一代
        offspring = select_and_generate_offspring(population)
        # 变异
        mutate_offspring(offspring)
        # 非支配排序和拥挤度排序
        population = sort_by_dominance_and_crowding(offspring)

    return population

# 模拟退火算法
def simulated_annealing(solution, aps, hosts):
    # 初始化
    current_solution = initial_solution
    best_solution = current_solution
    current_temperature = initial_temperature
    cooling_rate = 0.99
    minimum_temperature = 1e-3

    # 计算当前解的适应度
    current_fitness = calculate_fitness(current_solution)

    # 模拟退火过程
    while current_temperature > minimum_temperature:
        for i in range(iterations_per_temperature):
            # 生成邻域解
            neighbor_solution = generate_neighbor(current_solution)
            neighbor_fitness = calculate_fitness(neighbor_solution)

            # 计算接受概率
            if neighbor_fitness > current_fitness:
                current_solution = neighbor_solution
                current_fitness = neighbor_fitness
                # 更新最佳解
                if neighbor_fitness > calculate_fitness(best_solution):
                    best_solution = neighbor_solution
            else:
                # 接受劣质解的概率
                delta = neighbor_fitness - current_fitness
                probability = exp(delta / current_temperature)
                if random() < probability:
                    current_solution = neighbor_solution
                    current_fitness = neighbor_fitness

        # 降低温度
        current_temperature *= cooling_rate
        # 输出最佳解
        return best_solution

# 初始化种群
def initialize_population(size, aps, hosts):
    population = []
    for _ in range(size):
        individual = {'aps': random_activation(aps), 'fitness': None}
        population.append(individual)
    return population
def random_activation(aps):
    activated_aps = []
    for ap in aps:
        if random.random() < 0.5:  # 假设有50%的概率激活每个AP
            activated_aps.append(ap)
    return activated_aps

# 适应度评估
def evaluate_population(population, aps, hosts):
    for individual in population:
        throughput, fairness = calculate_network_performance(individual['aps'], hosts)
        individual['fitness'] = (throughput, -len(individual['aps']))  # 目标是最大化吞吐量和最小化AP数量

# 选择
def tournament_selection(population, k=3):
    new_population = []
    for _ in range(len(population)):
        contenders = random.sample(population, k)
        winner = max(contenders, key=lambda ind: ind['fitness'])
        new_population.append(copy.deepcopy(winner))
    return new_population

# 交叉 
def crossover(parent1, parent2):
    if random.random() < CROSSOVER_RATE:
        point = random.randint(1, len(parent1['aps']) - 1)
        new_aps1 = parent1['aps'][:point] + parent2['aps'][point:]
        new_aps2 = parent2['aps'][:point] + parent1['aps'][point:]
        return {'aps': new_aps1, 'fitness': None}, {'aps': new_aps2, 'fitness': None}
    return parent1, parent2

# 变异
def mutate(individual):
    if random.random() < MUTATION_RATE:
        mutation_point = random.randint(0, len(individual['aps']) - 1)
        individual['aps'][mutation_point] = not individual['aps'][mutation_point]  # 翻转激活状态

Location_csv_path = 'model\Location\Exp1\Eng_Location.csv'
# 主程序
def main():
    aps, hosts = read_network_info(Location_csv_path)
    pareto_front = NSGA_II(aps, hosts)
    best_solution = select_best_solution(pareto_front)
    optimized_solution = simulated_annealing(best_solution, aps, hosts)
    print_active_aps(optimized_solution)

def print_active_aps(solution):
    print("Active APs:")
    for ap in solution['aps']:
        if ap.active:
            print(f"Active AP: {ap.apid} at position ({ap.xpos}, {ap.ypos})")

# 执行主程序
main()
