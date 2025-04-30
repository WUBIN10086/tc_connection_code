import os
import csv

# 当前目？
folder_path = os.getcwd()

# ？出文件路径
output_csv = os.path.join(folder_path, "all_thrr.csv")

# 文件名列表
file_list = [f"through{i}.txt" for i in range(1, 25)]

all_data = []

for filename in file_list:
    with open(filename, 'r') as file:
        for line in file:
            line = line.strip()
            if line:  # 去除空行
                all_data.append([line])  # ？列形式

# 写入 CSV
with open("all_thrr.csv", "w", newline='') as f:
    writer = csv.writer(f)
    writer.writerows(all_data)

print("保存成功：all_rss.csv")
