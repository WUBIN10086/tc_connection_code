from fairness_calc import Fairness_calc

n = 3
#S = [130,124]
S = [53.5, 49.9, 52.0]
#C = [66.4,54.2]
C = [13.4,16.4, 10.5]

target =[]
target = Fairness_calc(n , S , C)
print(target)