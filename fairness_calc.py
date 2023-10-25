# 获取Host数量n
n = int(input("Enter the number of Hosts (n): "))

# 初始化S和C的列表
S_values = []
C_values = []

# 获取用户输入的S和C值
for i in range(1, n + 1):
    S = float(input(f"Enter the value of S_{i}: "))
    C = float(input(f"Enter the value of C_{i}: "))
    S_values.append(S)
    C_values.append(C)

# 计算分子和分母的总和
numerator = sum(C_values[i] / S_values[i] for i in range(n))
denominator = sum(1 / S_values[i] for i in range(n))

# 计算t
t = numerator / denominator

# 打印结果
print(f"t is: {t}")
