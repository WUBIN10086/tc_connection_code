#================================================================
# Rewrite the code from Roy: active AP algorithm
# Last modify date: 2024 05/1
# Author: WU BIN
# read file from CSV and input network info
#================================================================
import csv
def input_network_info(file_path):
    gridSizeX = int(2)
    gridSizeY = int(2)
    gridScale = int(50)
    APCoverageRm = float(110)
    NoGroup = int(3)
    # 从 CSV 文件中读取 Host 和 AP 的数量
    with open(file_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        NoHost = 0
        NoAP = 0
        for row in reader:
            if row["Type"] == "Host":
                NoHost += 1
            elif row["Type"] == "AP":
                NoAP += 1
    AI = [{'APID': 0, 'PositionX': 0.0, 'PositionY': 0.0, 'GroupID': 0, 'type': 0} for _ in range(NoAP)]
    HI = [{'HostID': 0, 'PositionX': 0.0, 'PositionY': 0.0, 'GroupID': 0, 'HostActiveRate': 0.0, 'movable': 0} for _ in range(NoHost)]
    Aggr = [(1,1,1),(1,1,1),(1,1,1),(1,1,1)]
    NoChanel = int(30)
    MaxHost = int(50)

    # 读取CSV文件
    with open(file_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            name = row["Name"]
            x = float(row["X"])
            y = float(row["Y"])
            entity_type = row["Type"]
            # 根据实体类型将坐标信息添加到相应的数组
            i = 1
            if entity_type == "AP":
                AI[i]['APID'] = name
                AI[i]['PositionX'] = float(x)
                AI[i]['PositionY'] = float(y)
                AI[i]['GroupID'] = int(1)
                AI[i]['type'] = int(0)
                i = i + 1
            elif entity_type == "Host":
                HI[i]['HostID'] = name
                HI[i]['PositionX'] = float(x)
                HI[i]['PositionY'] = float(y)
                HI[i]['GroupID'] = int(1)
                HI[i]['HostActiveRate'] = float(1)
                HI[i]['movable'] = int(0)
                i = i + 1

