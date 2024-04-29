# this file is to fast calc. all results to fairness target

from main.src.fairness_calc import Fairness_calc
import csv

S = []
C = []

# 读取CSV文件
with open("Measurement.csv", newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        name = row["Name"]
        value = float(row["Value"])
        entity_type = row["Type"]

        # 根据实体类型将坐标信息添加到相应的数组
        if entity_type == "S":
            S.append((name, value))
        elif entity_type == "C":
            C.append((name, value))

S_send = []
C_send = []

# 从用户键盘输入获取选择的名称，可以输入多个名称，用逗号分隔
selected_names = input("请输入您想选择的名称（用逗号分隔）: ").split(',')

# 对每个选择的名称进行处理
for selected_name in selected_names:
    selected_name = selected_name.strip()  # 去除可能的空白字符
    for s in S:
        if s[0] == selected_name:
            S_send.append(s[1])
    for c in C:
        if c[0] == selected_name:
            C_send.append(c[1])

n = len(S_send)
# 输出结果
print("S_send 中的元素数量: ", n)
print("S_send: ", S_send)
print("C_send: ", C_send)

# 使用Fairness_calc类进行计算
target = Fairness_calc(n, S_send , C_send)
print(target)
