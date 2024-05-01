#================================================================
# Rewrite the code from Roy: active AP algorithm
# Last modify date: 2024 05/1
# Author: WU BIN
#================================================================
import random
import csv
import sys

# Default paramerter
Default_RandomSeed = 50
Location_csv_path = sys.argv[1]
Custom_RandomSeed = sys.argv[2]
# Generate random number
# Default seed = 50

random.seed(50)

# APcoverage(m)
APCoverageRm = 110
Max_Host = 50

# 从 CSV 文件中读取 Host 和 AP 的数量
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