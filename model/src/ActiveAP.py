#================================================================
# Rewrite the code from Roy: active AP algorithm
# Last modify date: 2024 05/1
# Author: WU BIN
#================================================================
import random
import csv
import sys
import pandas as pd
import math
from throughput_estimation import calculate_throughput_estimate
from throughput_estimation import Distance

#----------------------------------------------------------------
# 数据结构
class APInfo:
    def __init__(self, APID=0, PositionX=0.0, PositionY=0.0, GroupID=0, NoConHost=0, ConHost=None,
                 ifActive=0, HostMargin=0, ifSatisfied=0, type=0, participateInSelection=0,
                 nodeID=0, ChannelID=0):
        self.APID = APID
        self.PositionX = PositionX
        self.PositionY = PositionY
        self.GroupID = GroupID
        self.NoConHost = NoConHost
        self.ConHost = ConHost if ConHost is not None else []
        self.ifActive = ifActive
        self.HostMargin = HostMargin
        self.ifSatisfied = ifSatisfied
        self.type = type
        self.participateInSelection = participateInSelection
        self.nodeID = nodeID
        self.ChannelID = ChannelID

class HostInfo:
    def __init__(self, HostID=0, PositionX=0.0, PositionY=0.0, GroupID=0, HostActiveRate=0.0,
                 NoConAP=0, ConAP=None, AP_HostLinkSpeed=None, AssocAP=0, AssocAP_HostLinkSpeed=0.0,
                 NoSat=0, SatAP=None, nodeID=0, ChannelID=0, movable=0):
        self.HostID = HostID
        self.PositionX = PositionX
        self.PositionY = PositionY
        self.GroupID = GroupID
        self.HostActiveRate = HostActiveRate
        self.NoConAP = NoConAP
        self.ConAP = ConAP if ConAP is not None else []
        self.AP_HostLinkSpeed = AP_HostLinkSpeed if AP_HostLinkSpeed is not None else []
        self.AssocAP = AssocAP
        self.AssocAP_HostLinkSpeed = AssocAP_HostLinkSpeed
        self.NoSat = NoSat
        self.SatAP = SatAP if SatAP is not None else []
        self.nodeID = nodeID
        self.ChannelID = ChannelID
        self.movable = movable

# Constants
DEFAULT_MAX_AP = 100
DEFAULT_MAX_HOST = 100
DEFAULT_MAX_GROUP = 6
MAX_NO_OF_WALLS = 20
MAX_TYPE_WALLS = 7
LINK_SPEED_DROP_PER_WALL = 15
INITIAL_MAX_TX_TIME = 1000.0
LOOP_COUNT_LB_HOST_COUNT = 10000
LOOP_COUNT_LB_LINK_SPEED = 100
RAND_SEED = 50

# Create instances of APInfo and HostInfo to represent the arrays
AI = [APInfo() for _ in range(DEFAULT_MAX_AP)]
HI = [HostInfo() for _ in range(DEFAULT_MAX_HOST)]
AIActive = [APInfo() for _ in range(DEFAULT_MAX_AP)]
HIActive = [HostInfo() for _ in range(DEFAULT_MAX_HOST)]

# CSV文件地址
Location_csv_path = 'model\Location\Exp1\Eng_Location.csv'
# Location_csv_path = sys.argv[1]
# Walls_csv_path = sys.argv[3]
Walls_csv_path = 'model\Location\Exp1\Walls.csv'

adjustedRatio = 1.0
linkSpeedThreshold = float(1)
AverageHostThroughputThreshold = float(1.5)
LOOP_COUNT_LB_TX_TIME = int(365)
LOOP_COUNT_HILL_CLIMB_LB_TX_TIME = int(90)
LOOP_COUNT_AP_SELECTION_OPTIMIZATION = int(18)
HILL_CLIMB_MUTATION_FACTOR = int(0.9)
AP_SELECTION_HILL_CLIMBING_RATIO = int(.5)
THROUGHPUT_IMPROVE_MARGIN = float(.1)
totalBandwidth = float(1000)
#----------------------------------------------------------------

#----------------------------------------------------------------
random.seed(50)
# 读取坐标信息
gridSizeX = int(2)
gridSizeY = int(2)
gridScale = int(50)
APCoverageRm = float(110)
NoGroup = int(3)
NoAP = 0
NoHost = 0
# 从 CSV 文件中读取 Host 和 AP 的数量
with open(Location_csv_path, newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        if row["Type"] == "Host":
            NoHost += 1
        elif row["Type"] == "AP":
            NoAP += 1
# AI = [{'APID': 0, 'PositionX': 0.0, 'PositionY': 0.0, 'GroupID': 0, 'type': 0, 'ConHost': [], 'NoConHost': 0} for _ in range(NoAP)]
# HI = [{'HostID': 0, 'PositionX': 0.0, 'PositionY': 0.0, 'GroupID': 0, 'HostActiveRate': 0.0, 'movable': 0} for _ in range(NoHost)]
Aggr = [(1,1,1),(1,1,1),(1,1,1),(1,1,1)]
NoChanel = int(30)
MaxHost = int(50)

# 读取CSV文件
with open(Location_csv_path, newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    i = 0
    j = 0
    for row in reader:
        name = row["Name"]
        x = float(row["X"])
        y = float(row["Y"])
        entity_type = row["Type"]
        # 根据实体类型将坐标信息添加到相应的数组
        if entity_type == "AP":
            AI[i].APID = str(name)
            AI[i].PositionX = float(x)
            AI[i].PositionY = float(y)
            AI[i].GroupID = int(1)
            AI[i].type = int(0)
            i = i + 1
        elif entity_type == "Host":
            HI[j].HostID = str(name)
            HI[j].PositionX = float(x)
            HI[j].PositionY = float(y)
            HI[j].GroupID = int(1)
            HI[j].HostActiveRate = float(1)
            HI[j].movable = int(0)
            j = j + 1
#----------------------------------------------------------------
NoAPAll = 0
NoAPReal = 0
numMobAP = 0
numVAP = 0
numDefectAP = 0  

for i in range(NoAP):
    if AI[i].type == 0:
        NoAPAll += 1
        NoAPReal += 1
        AI[i].participateInSelection = 1
    elif AI[i].type == 1:
        numVAP += 1
        AI[i].participateInSelection = 0
    elif AI[i].type == 2:
        numMobAP += 1
        AI[i].participateInSelection = 0
    else:
        numDefectAP += 1
        AI[i].participateInSelection = 0
#----------------------------------------------------------------


#----------------------------------------------------------------
# 读取墙面信息
walls_data = pd.read_csv(Walls_csv_path)
# print(walls_data)

def determineAssociabilityOfAP_HostUsingOnlyCoverageRadius():
    for j in range(NoAP):
        AI[j].NoConHost = 0
    for i in range(NoHost):
        HI[i].NoConAP = 0

    i = 0
    j = 0
    for i in range(NoAP):
        for j in range(NoHost):
            # print(f"Checking APID: {AI[i].APID} against known AP Names in data")
            wall_info = walls_data[(walls_data['AP_Name'] == AI[i].APID) & (walls_data['Host_Name'] == HI[j].HostID)]
            # 检查 wall_info 是否为空
            # if not wall_info.empty:
                # print(f"No wall data available for AP {AI[i].APID} and Host {HI[j].HostID}")
            nk = wall_info.iloc[0, 2:].tolist()  # 从第三列开始是墙面信息
            if AI[i].APID.endswith(("_2")):
                # 2.4GHz Estimation
                with open("model\etc\parameters.txt", "r") as file:
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
                distanceBtwAP_Host = Distance(HI[j].PositionX, HI[j].PositionY, AI[i].PositionX, AI[i].PositionY)
                tempLinkSpeed2g = adjustedRatio * calculate_throughput_estimate(parameters, (HI[j].PositionX, HI[j].PositionY), (AI[i].PositionX, AI[i].PositionY), nk)
                if distanceBtwAP_Host <= APCoverageRm:
                    AI[i].ConHost.append(j + 1)
                    HI[j].ConAP.append(i + 1)
                    HI[j].AP_HostLinkSpeed.append(tempLinkSpeed2g)
                    AI[i].NoConHost += 1
                    HI[j].NoConAP += 1
            
            else:
                # 5GHz Estimation
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
                distanceBtwAP_Host = Distance(HI[j].PositionX, HI[j].PositionY, AI[i].PositionX, AI[i].PositionY)
                tempLinkSpeed5g = adjustedRatio * calculate_throughput_estimate(parameters, (HI[j].PositionX, HI[j].PositionY), (AI[i].PositionX, AI[i].PositionY), nk)
                if distanceBtwAP_Host <= APCoverageRm:
                    AI[i].ConHost.append(j + 1)
                    HI[j].ConAP.append(i + 1)
                    HI[j].AP_HostLinkSpeed.append(tempLinkSpeed5g)
                    AI[i].NoConHost += 1
                    HI[j].NoConAP += 1

determineAssociabilityOfAP_HostUsingOnlyCoverageRadius()
#----------------------------------------------------------------



#----------------------------------------------------------------
def calculateInitialAP_HostLinkSpeed():
    global AI, HI, AP_HostLinkSpeed, adjustedRatio
    
    # Initialize the AP_HostLinkSpeed list
    AP_HostLinkSpeed = [[0 for _ in range(len(HI))] for _ in range(len(AI))]

    # 2.4GHz Estimation
    for i in range(NoAP):  # Iterate over APs with step 2
        for j in range(NoHost):
            wall_info = walls_data[(walls_data['AP_Name'] == AI[i].APID) & (walls_data['Host_Name'] == HI[j].HostID)]
            nk = wall_info.iloc[0, 2:].tolist()  # 从第三列开始是墙面信息
            if AI[i].APID.endswith(("_2")):
                # 2.4GHz Estimation
                with open("model\etc\parameters.txt", "r") as file:
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
                tempLinkSpeed2g = adjustedRatio * calculate_throughput_estimate(parameters, (HI[j].PositionX, HI[j].PositionY), (AI[i].PositionX, AI[i].PositionY), nk)
                AP_HostLinkSpeed[i][j] = tempLinkSpeed2g
            else:
                # 5GHz Estimation
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
                tempLinkSpeed5g = adjustedRatio * calculate_throughput_estimate(parameters, (HI[j].PositionX, HI[j].PositionY), (AI[i].PositionX, AI[i].PositionY), nk)
                AP_HostLinkSpeed[i][j] = tempLinkSpeed5g
#----------------------------------------------------------------


#----------------------------------------------------------------
def phase_initialization():
    global AI, HI, AINew, HINew, AP_HostLinkSpeed, linkSpeedThreshold, Aggr
    
    # We need to define these arrays/lists before this function is called
    maxLinkSpeedForHost = [0.0] * len(HI)
    maxLinkSpeedAPforHost = [-1] * len(HI)
    
    calculateInitialAP_HostLinkSpeed()
    
    # Initializing new instances based on existing data
    HINew = [HostInfo(h.HostID, h.PositionX, h.PositionY, h.GroupID, h.HostActiveRate, h.movable) for h in HI]
    for h in HINew:
        h.NoConAP = 0
    
    AINew = [APInfo(a.APID, a.PositionX, a.PositionY, a.GroupID, participateInSelection=a.participateInSelection, type=a.type) for a in AI]
    for a in AINew:
        a.NoConHost = 0
    
    # Process each AP and Host to establish initial link conditions
    for i, ap in enumerate(AI):
        for j in range(ap.NoConHost):
            host_index = ap.ConHost[j] - 1
            if Aggr[ap.GroupID-1][HI[host_index].GroupID-1] == 1:
                tempLinkSpeed = AP_HostLinkSpeed[i][host_index]
                if tempLinkSpeed > maxLinkSpeedForHost[host_index]:
                    maxLinkSpeedForHost[host_index] = tempLinkSpeed
                    maxLinkSpeedAPforHost[host_index] = i
                
                if tempLinkSpeed >= linkSpeedThreshold:
                    curAP = i + 1
                    curHost = ap.ConHost[j]
                    AINew[i].ConHost.append(curHost)
                    AINew[i].NoConHost += 1
                    HINew[curHost - 1].ConAP.append(curAP)
                    HINew[curHost - 1].AP_HostLinkSpeed.append(tempLinkSpeed)
                    HINew[curHost - 1].NoConAP += 1
    
    # Handle hosts with no connections
    for i, h in enumerate(HINew):
        if h.NoConAP == 0:
            # print("BEST FIT!!")
            curAP = maxLinkSpeedAPforHost[i]
            if curAP != -1:  # Ensure there is a best AP
                AINew[curAP].ConHost.append(i + 1)
                AINew[curAP].NoConHost += 1
                HINew[i].ConAP.append(curAP + 1)
                HINew[i].AP_HostLinkSpeed.append(maxLinkSpeedForHost[i])
                HINew[i].NoConAP += 1
    
    # Set all APs to non-active initially
    for i in range(len(AINew)):
        AINew[i].ifActive = 0
        AIActive[i].ifActive = 0
        AIActive[i].type = AINew[i].type
        AIActive[i].participateInSelection = AINew[i].participateInSelection
        AIActive[i].APID = AINew[i].APID
        AIActive[i].PositionX = AINew[i].PositionX
        AIActive[i].PositionY = AINew[i].PositionY
        AIActive[i].GroupID = AINew[i].GroupID
        AIActive[i].NoConHost = 0

phase_initialization()
#----------------------------------------------------------------

print("phase_initialization Finished")

#----------------------------------------------------------------
sumLinkCandidate = 0
for i in range(NoAP):
    tempSumAP_HostLinkSpeed = 0.0
    if AINew[i].participateInSelection == 0:
        continue
    sumLinkCandidate += AINew[i].NoConHost
    for j in range(AINew[i].NoConHost):
        # Assuming AP_HostLinkSpeed is a 2D list and AINew[i].ConHost[j] gives the 1-based index of the host
        tempSumAP_HostLinkSpeed += AP_HostLinkSpeed[i][AINew[i].ConHost[j] - 1]
#----------------------------------------------------------------


#----------------------------------------------------------------
def phase_initial_solution_search():
    # Initialize association to -1 (no association)
    for host in HINew:
        host.AssocAP = -1

    while True:
        maxSumAP_HostLinkSpeed = 0.0
        maxAP = -1

        # Iterate over APs, step by 2 for some reason (perhaps every other AP is considered in a specific scenario)
        for i in range(0, NoAP, 2):
            if AINew[i].participateInSelection == 0 or AINew[i].ifActive != 0:
                continue

            tempSumAP_HostLinkSpeed = 0.0
            for j in AINew[i].ConHost:
                # Check if the host is unassociated
                if HINew[j - 1].AssocAP == -1:
                    tempSumAP_HostLinkSpeed += AP_HostLinkSpeed[i][j - 1]

            if tempSumAP_HostLinkSpeed > maxSumAP_HostLinkSpeed:
                maxSumAP_HostLinkSpeed = tempSumAP_HostLinkSpeed
                maxAP = i

        if maxAP != -1:
            AINew[maxAP].ifActive = 1
            AIActive[maxAP].ifActive = 1
            AIActive[maxAP].NoConHost = 0

            for j in AINew[maxAP].ConHost:
                if HINew[j - 1].AssocAP == -1:
                    HINew[j - 1].AssocAP = maxAP + 1
                    HINew[j - 1].AssocAP_HostLinkSpeed = AP_HostLinkSpeed[maxAP][j - 1]
                    AIActive[maxAP].ConHost.append(j)
                    AIActive[maxAP].NoConHost += 1

        # Check for any unallocated hosts
        flag = any(host.AssocAP == -1 for host in HINew)
        if not flag:
            break

# phase_initial_solution_search()
#----------------------------------------------------------------

print("phase_initial_solution_search Finished")

#----------------------------------------------------------------
# Initialize counter for active access points
noOfActiveAp = 0

# First loop: Update APs based on participation, connection, and active status
for i in range(NoAP):
    if AIActive[i].participateInSelection == 0 or AIActive[i].NoConHost == 0:
        continue
    if AIActive[i].ifActive == 1:
        AIActive[i].nodeID = noOfActiveAp
        noOfActiveAp += 1

# Second loop: Copy and update host details from new to active list
for i in range(NoHost):
    HIActive[i].HostID = HINew[i].HostID
    HIActive[i].PositionX = HINew[i].PositionX
    HIActive[i].PositionY = HINew[i].PositionY
    HIActive[i].GroupID = HINew[i].GroupID
    HIActive[i].HostActiveRate = HINew[i].HostActiveRate
    HIActive[i].AssocAP = HINew[i].AssocAP
    HIActive[i].movable = HINew[i].movable
    # Assuming AssocAP stores index starting from 1, adjust index for 0-based Python lists
    HIActive[i].AssocAP_HostLinkSpeed = AP_HostLinkSpeed[HIActive[i].AssocAP - 1][i]

    # Set nodeID based on current count of active APs
    HIActive[i].nodeID = noOfActiveAp + i

    # Reset connected APs count
    HIActive[i].NoConAP = 0

    # Third loop: Update associated APs considering only active APs
    for j in range(HINew[i].NoConAP):
        # Adjust index since ConAP is likely 1-based
        if AIActive[HINew[i].ConAP[j] - 1].ifActive == 1:
            HIActive[i].ConAP.append(HINew[i].ConAP[j])
            HIActive[i].AP_HostLinkSpeed.append(AP_HostLinkSpeed[HINew[i].ConAP[j] - 1][i])
            HIActive[i].NoConAP += 1
#----------------------------------------------------------------


#----------------------------------------------------------------
def test_nearest_ap_host_association():
    # Reset connections
    for ap in AIActive:
        if ap.ifActive:
            ap.NoConHost = 0

    for host in HIActive:
        host.AssocAP = -1

    # Find the nearest active AP for each host
    for i, host in enumerate(HIActive):
        ap_max_link_speed = -1
        max_link_speed = -0.1

        for j in range(host.NoConAP):
            # Assuming ConAP[j] contains 1-based indices
            ap_index = host.ConAP[j] - 1
            temp_link_speed = AP_HostLinkSpeed[ap_index][i]

            if temp_link_speed > max_link_speed:
                max_link_speed = temp_link_speed
                ap_max_link_speed = ap_index

        # Associate host with the AP having maximum link speed
        if ap_max_link_speed != -1:
            AIActive[ap_max_link_speed].ConHost.append(i + 1)  # Store 1-based index
            AIActive[ap_max_link_speed].NoConHost += 1

            # Update host info
            host.AssocAP = ap_max_link_speed + 1  # Store as 1-based index
            host.AssocAP_HostLinkSpeed = AP_HostLinkSpeed[ap_max_link_speed][i]

        # # Debug print similar to the commented out C printf statement
        # print(f"HIActive[{i}].AssocAP={host.AssocAP}")
#----------------------------------------------------------------


#----------------------------------------------------------------
def phase_random_move_to_reduce_tx_time_for_bottleneck_ap():
    INITIAL_MAX_TX_TIME = float('inf')  # Using a very large value
    globalMaxTxTime = INITIAL_MAX_TX_TIME
    movableHost = []
    bestLSpAPforHost = [-1] * NoHost
    bestLSpforHost = [0.0] * NoHost

    # Initialize host associations
    for i in range(NoHost):
        if HIActive[i].movable:
            continue
        for j in range(HIActive[i].NoConAP):
            ap_index = HIActive[i].ConAP[j] - 1
            if AP_HostLinkSpeed[ap_index][i] > bestLSpforHost[i]:
                bestLSpforHost[i] = AP_HostLinkSpeed[ap_index][i]
                bestLSpAPforHost[i] = ap_index

        if HIActive[i].NoConAP > 1:
            movableHost.append(i)

    # Optimization loop
    if movableHost:
        for _ in range(LOOP_COUNT_HILL_CLIMB_LB_TX_TIME):
            tempMaxTxTime = local_search_random_move_to_reduce_tx_time_for_bottleneck_ap()  # Assuming this is defined

            if tempMaxTxTime < globalMaxTxTime:
                globalMaxTxTime = tempMaxTxTime
            # Move hosts to their best link speed AP
            for host_index in movableHost:
                best_ap = bestLSpAPforHost[host_index]
                current_ap = HIActive[host_index].AssocAP - 1

                if best_ap != current_ap:
                    # Move host to new AP
                    AIActive[best_ap].ConHost.append(host_index + 1)
                    AIActive[best_ap].NoConHost += 1

                    # Remove from current AP
                    AIActive[current_ap].ConHost.remove(host_index + 1)
                    AIActive[current_ap].NoConHost -= 1

                    # Update host association
                    HIActive[host_index].AssocAP = best_ap + 1
                    HIActive[host_index].AssocAP_HostLinkSpeed = AP_HostLinkSpeed[best_ap][host_index]

            # Mutation step to randomly re-associate hosts
            for _ in range(int(len(movableHost) * HILL_CLIMB_MUTATION_FACTOR / 100)):
                host_index = random.choice(movableHost)
                current_ap = HIActive[host_index].AssocAP - 1
                possible_aps = [ap for ap in HIActive[host_index].ConAP if ap - 1 != current_ap]
                if possible_aps:
                    new_ap = random.choice(possible_aps) - 1
                    # Move host to new AP
                    AIActive[new_ap].ConHost.append(host_index + 1)
                    AIActive[new_ap].NoConHost += 1

                    # Remove from current AP
                    AIActive[current_ap].ConHost.remove(host_index + 1)
                    AIActive[current_ap].NoConHost -= 1

                    # Update host association
                    HIActive[host_index].AssocAP = new_ap + 1
                    HIActive[host_index].AssocAP_HostLinkSpeed = AP_HostLinkSpeed[new_ap][host_index]
#----------------------------------------------------------------



#----------------------------------------------------------------
def local_search_random_move_to_reduce_tx_time_for_bottleneck_ap():
    global AIActive, HIActive, AP_HostLinkSpeed, NoHost, NoAP
    # Initialize the transmission time list and other variables
    AP_TxTime = [0.0] * NoAP
    maxTxTime = -0.1
    AP_withMaxTxTime = -1
    
    # Initial calculations for each AP's transmission time
    for i in range(NoHost):
        if HIActive[i].AssocAP > 0:  # Ensure the association index is within bounds
            AP_index = HIActive[i].AssocAP - 1
            HIActive[i].AssocAP_HostLinkSpeed = AP_HostLinkSpeed[AP_index][i]
    
    # Determine the max transmission time and the corresponding AP
    for i in range(NoAP):
        if AIActive[i].participateInSelection and AIActive[i].ifActive:
            AP_TxTime[i] = calculate_tx_time_for_ap(i)
            if AP_TxTime[i] > maxTxTime:
                maxTxTime = AP_TxTime[i]
                AP_withMaxTxTime = i

    # Generate the list of movable hosts for the AP with max Tx time
    listOfMovableHostsForMaxTxTimeAP = []
    if AP_withMaxTxTime != -1:
        for host_index in AIActive[AP_withMaxTxTime].ConHost:
            host_index -= 1  # Adjust to zero-based index
            if HIActive[host_index].NoConAP > 1:
                listOfMovableHostsForMaxTxTimeAP.append(host_index)
    # Optimization loop
    for LoopCount in range(LOOP_COUNT_LB_TX_TIME):
        if not listOfMovableHostsForMaxTxTimeAP:
            break

        curHost = random.choice(listOfMovableHostsForMaxTxTimeAP)
        currentAPs = HIActive[curHost].ConAP
        curAP = random.choice([ap for ap in currentAPs if ap - 1 != HIActive[curHost].AssocAP - 1]) - 1
        
        # Calculate potential new Tx Times after moving the host
        adjust_tx_time(AP_TxTime, curHost, HIActive[curHost].AssocAP - 1, curAP, -1)
        adjust_tx_time(AP_TxTime, curHost, curAP, HIActive[curHost].AssocAP - 1, 1)

        newMaxTxTime = max(AP_TxTime)
        newAP_withMaxTxTime = AP_TxTime.index(newMaxTxTime)
        
        # Check if the new configuration is better
        if newMaxTxTime <= maxTxTime:
            # Commit changes if the new configuration is better
            commit_host_relocation(HIActive[curHost], AIActive, curAP, curHost)
            maxTxTime = newMaxTxTime
            AP_withMaxTxTime = newAP_withMaxTxTime
            listOfMovableHostsForMaxTxTimeAP = regenerate_movable_hosts_list(AIActive[AP_withMaxTxTime], HIActive)
        else:
            # Revert changes if not better
            adjust_tx_time(AP_TxTime, curHost, HIActive[curHost].AssocAP - 1, curAP, 1)
            adjust_tx_time(AP_TxTime, curHost, curAP, HIActive[curHost].AssocAP - 1, -1)

    return maxTxTime

def calculate_tx_time_for_ap(ap_index):
    sum_tx_time = 0.0
    tmp_map_speed = 30.00  # Fixed speed used for type 2 APs
    tmp_map_speed_accumulator = 0

    # Loop through all connected hosts of the AP
    for host_index in AIActive[ap_index].ConHost:
        host = HIActive[host_index - 1]  # Adjust index because ConHost likely stores 1-based indices
        host_rate_to_speed_ratio = host.HostActiveRate / host.AssocAP_HostLinkSpeed

        if AIActive[ap_index].type == 2:
            # Special handling for type 2 APs
            sum_tx_time += host_rate_to_speed_ratio
            tmp_map_speed_accumulator += host.HostActiveRate / tmp_map_speed
        else:
            # General handling for other types
            sum_tx_time += host_rate_to_speed_ratio

    # Additional check for type 2 APs
    if AIActive[ap_index].type == 2 and tmp_map_speed_accumulator >= sum_tx_time:
        sum_tx_time = tmp_map_speed_accumulator

    return sum_tx_time

def adjust_tx_time(AP_TxTime, host_index, from_ap, to_ap, direction):
    rate_adjustment = (1 / AP_HostLinkSpeed[to_ap][host_index]) * HIActive[host_index].HostActiveRate
    AP_TxTime[from_ap] += rate_adjustment * direction
    AP_TxTime[to_ap] -= rate_adjustment * direction

def commit_host_relocation(host, AIActive, new_ap, host_index):
    # Remove from old AP
    old_ap = host.AssocAP - 1
    AIActive[old_ap].ConHost.remove(host_index + 1)
    AIActive[old_ap].NoConHost -= 1
    
    # Add to new AP
    AIActive[new_ap].ConHost.append(host_index + 1)
    AIActive[new_ap].NoConHost += 1
    
    # Update host association
    host.AssocAP = new_ap + 1
    host.AssocAP_HostLinkSpeed = AP_HostLinkSpeed[new_ap][host_index]

def regenerate_movable_hosts_list(ap, HIActive):
    return [host_index for host_index in (h - 1 for h in ap.ConHost) if HIActive[host_index].NoConAP > 1]
#----------------------------------------------------------------


test_nearest_ap_host_association()

print("test_nearest_ap_host_association Finished")

phase_random_move_to_reduce_tx_time_for_bottleneck_ap()

print("phase_random_move_to_reduce_tx_time_for_bottleneck_ap")
#----------------------------------------------------------------
# phase_additional_AP_activation

def phase_additional_ap_activation():
    global AIActive, HIActive, NoAP, NoHost, AP_HostLinkSpeed, AverageHostThroughputThreshold

    # Active and Inactive AP tracking
    active_aps = [i for i, ap in enumerate(AIActive) if ap.ifActive]
    inactive_aps = [i for i, ap in enumerate(AIActive) if not ap.ifActive]
    no_of_active_aps = len(active_aps)

    # Optimization variables
    best_found_no_of_active_aps = no_of_active_aps
    best_found_max_tx_time = calculate_max_tx_time_among_aps()

    # Selection flags and host reassociation logic
    ap_selection_flag = [0] * NoAP

    # Optimization loop
    for loop_count in range(LOOP_COUNT_AP_SELECTION_OPTIMIZATION):
        for i in active_aps:
            ap_selection_flag[i] = 0

        for _ in range(LOOP_COUNT_AP_SELECTION_OPTIMIZATION):
            random.shuffle(inactive_aps)
            ap_to_activate = inactive_aps.pop()
            AIActive[ap_to_activate].ifActive = True

            # Attempt to reassociate hosts to the newly activated AP
            reassigned_hosts = reassociate_hosts(ap_to_activate)

            # Evaluate the new network state
            new_max_tx_time = calculate_max_tx_time_among_aps()

            # Determine if the new state is better
            if len(reassigned_hosts) > 0 and new_max_tx_time < best_found_max_tx_time:
                best_found_max_tx_time = new_max_tx_time
            else:
                # Revert changes if not better
                AIActive[ap_to_activate].ifActive = False
                for host in reassigned_hosts:
                    reassociate_host_to_original_ap(host)

            if len(inactive_aps) == 0:
                break

def reassociate_hosts(new_ap_index):
    reassigned_hosts = []
    for host_index, host in enumerate(HIActive):
        if host.AssocAP == new_ap_index + 1:  # Host is already associated with this AP
            continue
        # Logic to determine if reassigning this host is beneficial
        original_ap = host.AssocAP - 1
        original_tx_time = calculate_tx_time_for_ap(original_ap)
        new_tx_time = calculate_tx_time_for_ap(new_ap_index)

        if new_tx_time < original_tx_time:
            host.AssocAP = new_ap_index + 1
            reassigned_hosts.append(host_index)

    return reassigned_hosts

def calculate_max_tx_time_among_aps():
    max_tx_time = -0.1  # Initialize maxTxTime with a very low starting value
    global GlobalMaxTxTimeAP  # Define this as a global variable if it's used outside this function
    GlobalMaxTxTimeAP = -1  # Initialize the AP with the max Tx Time
    
    for i in range(NoAP):  # Loop through all APs
        if AIActive[i].ifActive:  # Only consider active APs
            ap_tx_time = calculate_tx_time_for_ap(i)  # Calculate the Tx time for this AP

            # Update the maximum Tx time and record which AP it belongs to
            if ap_tx_time > max_tx_time:
                max_tx_time = ap_tx_time
                GlobalMaxTxTimeAP = i  # Update the global variable with the index of the AP with the max Tx time

    return max_tx_time

def reassociate_host_to_original_ap(host_index):
    # This function would revert the host's association to its original state
    pass

#----------------------------------------------------------------
for i in range(0, NoAP, 2):  # Increment by 2 to only check even-indexed APs
    if AIActive[i].ifActive == 1:
        # Check if the next AP in the pair is inactive
        if i + 1 < NoAP and not AIActive[i + 1].ifActive:
            AIActive[i + 1].ifActive = 1  # Activate the next AP
            for j in range(NoHost):
                # Update all hosts to include this newly active AP in their list of connectable APs
                # i+2 because Python is 0-indexed but the AP list in the hosts might be 1-indexed
                HIActive[j].ConAP.append(i + 2)  # Assume ConAP is a list in Python
                HIActive[j].NoConAP += 1

phase_additional_ap_activation()
print("phase_additional_ap_activation Finished")
#----------------------------------------------------------------
phase_random_move_to_reduce_tx_time_for_bottleneck_ap()
print("phase_random_move_to_reduce_tx_time_for_bottleneck_ap")

def post_association_optimization():
    current_max_tx_time = calculate_max_tx_time_among_aps()
    if_swapped = True

    while if_swapped:
        if_swapped = False

        for i in range(NoHost):
            if HIActive[i].movable == 1:
                continue

            for j in range(NoHost):
                if HIActive[j].movable == 1 or i == j or HIActive[i].AssocAP == HIActive[j].AssocAP:
                    continue

                old_sum = (HIActive[i].HostActiveRate / HIActive[i].AssocAP_HostLinkSpeed) + \
                          (HIActive[j].HostActiveRate / HIActive[j].AssocAP_HostLinkSpeed)
                new_sum = (HIActive[i].HostActiveRate / AP_HostLinkSpeed[HIActive[j].AssocAP - 1][i]) + \
                          (HIActive[j].HostActiveRate / AP_HostLinkSpeed[HIActive[i].AssocAP - 1][j])

                if new_sum < old_sum:
                    temp_i = any(HIActive[i].ConAP[k] == HIActive[j].AssocAP for k in range(HIActive[i].NoConAP))
                    temp_j = any(HIActive[j].ConAP[k] == HIActive[i].AssocAP for k in range(HIActive[j].NoConAP))

                    if temp_i and temp_j:
                        # Swap the association of Host i with Host j if each other's AP is associable
                        AIActive[HIActive[i].AssocAP - 1].ConHost.remove(i + 1)
                        AIActive[HIActive[j].AssocAP - 1].ConHost.remove(j + 1)
                        AIActive[HIActive[i].AssocAP - 1].ConHost.append(j + 1)
                        AIActive[HIActive[j].AssocAP - 1].ConHost.append(i + 1)

                        swap_ap = HIActive[i].AssocAP
                        HIActive[i].AssocAP = HIActive[j].AssocAP
                        HIActive[j].AssocAP = swap_ap

                        HIActive[i].AssocAP_HostLinkSpeed = AP_HostLinkSpeed[HIActive[i].AssocAP - 1][i]
                        HIActive[j].AssocAP_HostLinkSpeed = AP_HostLinkSpeed[HIActive[j].AssocAP - 1][j]

                        new_max_tx_time = calculate_max_tx_time_among_aps()
                        if new_max_tx_time <= current_max_tx_time:
                            current_max_tx_time = new_max_tx_time
                            if_swapped = True
                        else:
                            # Revert the swap if no improvement
                            AIActive[HIActive[i].AssocAP - 1].ConHost.remove(i + 1)
                            AIActive[HIActive[j].AssocAP - 1].ConHost.remove(j + 1)
                            AIActive[HIActive[i].AssocAP - 1].ConHost.append(i + 1)
                            AIActive[HIActive[j].AssocAP - 1].ConHost.append(j + 1)

                            swap_ap = HIActive[i].AssocAP
                            HIActive[i].AssocAP = HIActive[j].AssocAP
                            HIActive[j].AssocAP = swap_ap

                            HIActive[i].AssocAP_HostLinkSpeed = AP_HostLinkSpeed[HIActive[i].AssocAP - 1][i]
                            HIActive[j].AssocAP_HostLinkSpeed = AP_HostLinkSpeed[HIActive[j].AssocAP - 1][j]


def print_active_aps():
    for i in range(NoAP):
        if AIActive[i].ifActive == 1:
            print(f"\nList of Active AP={i + 1}")

# Call the function to print active APs
print_active_aps()
