from throughput_estimation import calculate_throughput_estimate
import random
import copy
from math import exp
import csv
import pandas as pd
import random

# Initialization parameters
POPULATION_SIZE = 100
GENERATIONS = 50
CROSSOVER_RATE = 0.9
MUTATION_RATE = 0.05
LOOP_COUNT = 1000  # Number of iterations for simulated annealing
TEMPERATURE = 100  # Initial temperature
COOLING_RATE = 0.95  # Cooling rate

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
        self.throughput = 0  # Initialize throughput attribute

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

def calculate_throughput(aps, hosts, walls_data):
    # print("calculate_throughput...")
    total_throughput = 0
    for ap in aps:
        if ap.active:
            for host in hosts:
                wall_info = walls_data[(walls_data['AP_Name'] == ap.apid[:-2] + "_1") & (walls_data['Host_Name'] == host.hostid)]
                if not wall_info.empty:
                    nk = wall_info.iloc[0, 2:].tolist()
                    parameters = read_parameters("model/etc/parameters2.txt")
                    throughput = calculate_throughput_estimate(parameters, (host.xpos, host.ypos), (ap.xpos, ap.ypos), nk)
                    host.throughput += throughput
    return sum(host.throughput for host in hosts)

def read_parameters(file_path):
    parameters = {}
    try:
        with open(file_path, "r") as file:
            for line in file:
                line = line.strip()
                if line.startswith('#') or not line:
                    continue
                key, value = line.split('=')
                parameters[key.strip()] = float(value.strip()) if key.strip() != 'Wk' else list(map(float, value.strip().split()))
    except Exception as e:
        print(f"Error processing parameters: {e}")
    return parameters

def initialize_population(size, aps, hosts):
    population = []
    print("Initializing population...")
    for _ in range(size):
        individual = {'aps': [copy.deepcopy(ap) for ap in aps if '_2' in ap.apid], 'fitness': None}
        for ap in individual['aps']:
            ap.active = random.choice([True, False])
            # print(f"AP {ap.apid} initialized as {'active' if ap.active else 'inactive'}.")  # Debugging AP states
        population.append(individual)
    return population

def evaluate_population(population, aps, hosts, walls_data):
    print("evaluate_population...")
    print("----------------------")
    for individual in population:
        throughput = calculate_throughput(individual['aps'], hosts, walls_data)
        num_active_aps = len([ap for ap in individual['aps'] if ap.active])
        individual['fitness'] = (throughput, -80000 * num_active_aps)

def calculate_network_performance(activated_aps, hosts, walls_data):
    print("calculate_network_performance...")
    host_throughputs = {host.hostid: 0 for host in hosts}
    active_aps_count = 0  # Track the number of active APs

    for ap in activated_aps:
        if ap.active:
            active_aps_count += 1  # Increment for each active AP
            for host in hosts:
                wall_info = walls_data[(walls_data['AP_Name'] == ap.apid) & (walls_data['Host_Name'] == host.hostid)]
                if not wall_info.empty:
                    nk = wall_info.iloc[0, 2:].tolist()
                    parameters = read_parameters("model/etc/parameters2.txt" if ap.apid.endswith("_2") else "model/etc/parameters.txt")
                    throughput = calculate_throughput_estimate(parameters, (host.xpos, host.ypos), (ap.xpos, ap.ypos), nk)
                    host_throughputs[host.hostid] += throughput

    total_throughput = sum(host_throughputs.values())
    fairness = calculate_fairness(list(host_throughputs.values()), active_aps_count)
    return total_throughput, fairness

def calculate_fairness(throughputs, active_aps):
    """
    Calculate fairness based on the throughput values and the number of active APs.
    
    :param throughputs: List of throughput values for each host.
    :param active_aps: Number of active APs.
    :return: Fairness index.
    """
    if active_aps == 0 or not throughputs:
        return 1  # Avoid division by zero and handle no active APs

    n = len(throughputs)
    sum_throughputs = sum(throughputs)
    sum_throughputs_squared = sum(x ** 2 for x in throughputs)
    if sum_throughputs_squared == 0:
        return 1  # Avoid division by zero in fairness calculation

    return (sum_throughputs ** 2) / (n * sum_throughputs_squared)


def NSGA_II(aps, hosts, walls_data):
    print("NSGA_II...")
    population = initialize_population(POPULATION_SIZE, aps, hosts)
    for generation in range(GENERATIONS):
        evaluate_population(population, aps, hosts, walls_data)
        population = select_and_generate_offspring(population)
    return population

def simulated_annealing(solution, aps, hosts, walls_data):
    print("simulated_annealing...")
    current_solution = solution
    best_solution = solution
    current_temperature = TEMPERATURE

    while current_temperature > 1e-3:
        neighbor_solution = copy.deepcopy(current_solution)
        # Mutate the neighbor solution directly, no need to wrap in a list
        mutate_offspring([neighbor_solution], MUTATION_RATE)
        neighbor_fitness = evaluate_solution(neighbor_solution, aps, hosts, walls_data)
        current_fitness = evaluate_solution(current_solution, aps, hosts, walls_data)

        if neighbor_fitness > current_fitness:
            current_solution = neighbor_solution
            if neighbor_fitness > evaluate_solution(best_solution, aps, hosts, walls_data):
                best_solution = neighbor_solution
        else:
            # Calculate the probability of accepting a worse solution
            delta = neighbor_fitness - current_fitness
            probability = exp(delta / current_temperature)
            if random.random() < probability:
                current_solution = neighbor_solution

        current_temperature *= COOLING_RATE

    return best_solution

def mutate_offspring(offspring, mutation_rate=MUTATION_RATE):
    print("Mutating offspring...")
    for individual in offspring:
        for ap in individual['aps']:
            if random.random() < mutation_rate:
                ap.active = not ap.active
                # print(f"AP {ap.apid} toggled to {'active' if ap.active else 'inactive'}.")

def evaluate_solution(solution, aps, hosts, walls_data):
    throughput, _ = calculate_network_performance(solution['aps'], hosts, walls_data)
    return throughput  # or include other metrics depending on your optimization criteria

def tournament_selection(population, tournament_size=3):
    new_population = []
    while len(new_population) < len(population):
        tournament = random.sample(population, tournament_size)
        best_individual = max(tournament, key=lambda ind: ind['fitness'])
        new_population.append(copy.deepcopy(best_individual))
    return new_population

def crossover(parent1, parent2, crossover_rate=0.9):
    if random.random() < crossover_rate:
        point = random.randint(1, len(parent1['aps']) - 1)
        for i in range(point, len(parent1['aps'])):
            # Swap the active state of APs from the crossover point
            parent1['aps'][i].active, parent2['aps'][i].active = parent2['aps'][i].active, parent1['aps'][i].active
    return [parent1, parent2]

def mutate(individual, mutation_rate=0.1):
    for ap in individual['aps']:
        if random.random() < mutation_rate:
            ap.active = not ap.active

def select_and_generate_offspring(population):
    # Selection
    selected = tournament_selection(population)
    # Generate offspring
    offspring = []
    for i in range(0, len(selected), 2):
        if i + 1 < len(selected):
            off1, off2 = crossover(copy.deepcopy(selected[i]), copy.deepcopy(selected[i+1]))
            mutate(off1)
            mutate(off2)
            offspring.extend([off1, off2])
        else:
            mutate(selected[i])
            offspring.append(selected[i])
    return offspring

def main():
    aps, hosts = read_network_info('model/Location/Exp1/Eng_Location.csv')
    walls_data = pd.read_csv('model/Location/Exp1/Walls.csv')
    pareto_front = NSGA_II(aps, hosts, walls_data)
    best_solution = min(pareto_front, key=lambda x: x['fitness'][1])
    optimized_solution = simulated_annealing(best_solution, aps, hosts, walls_data)
    print_active_aps(optimized_solution)

def print_active_aps(solution):
    print("Final active APs:")
    for ap in solution['aps']:
        if ap.active:
            print(f"Active AP: {ap.apid} at position ({ap.xpos}, {ap.ypos}).")

if __name__ == "__main__":
    main()
