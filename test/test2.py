import csv
from throughput_estimation import calculate_throughput_estimate


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

# 打印AP和Host的坐标数组
print("AP Coordinates:")
for ap in ap_coordinates:
    print(ap)

print("Host Coordinates:")
for host in host_coordinates:
    print(host)

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


# 遍历每个主机和每个接入点，计算吞吐量

# Calculate throughput for each host and AP combination
for host_name, host_x, host_y in host_coordinates:
    for ap_name, ap_x, ap_y in ap_coordinates:
        nk = [0, 0, 0, 0, 0, 0]  # Update this with the appropriate nk values
        try:
            result = calculate_throughput_estimate(parameters, (host_x, host_y), (ap_x, ap_y), nk)
            print(f"{host_name} for {ap_name}: {result}")
        except ValueError as e:
            print(e)




