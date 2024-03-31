# distance estimation base on the throughput drop method
# refer in paper: https://doi.org/10.1587/transinf.2020NTP0008

import math

def calculate_d(RSS, alpha, P_1):
    try:
        if alpha == 0:
            raise ValueError("alpha must not be zero")
        sum_nk_Wk = 2 * 7.21
        d = 10 ** ((P_1 - RSS - sum_nk_Wk) / (10 * alpha))
        return d
    except ValueError as ve:
        return str(ve)


def Rss_calculate(alpha, P_1, d):
    sum_nk_Wk = 2 * 7.21
    RSS = P_1 - 10 * alpha * math.log10(d)- sum_nk_Wk
    return RSS


def calculate_srf(m):
    # * (1 - (0.1 * (m - 1))表示附带一点点的误差补偿
    # 实际上的测量值可能更低
    try:
        srf = (1 / (m + 0.1 * (m - 1) / 4)) * (1 - (0.1 * (m - 1)))
        return srf
    except ZeroDivisionError:
        return "Division by zero is not allowed. Please provide a valid value of 'm'."

RSS = -70
alpha = 2.2
P_1 = -28.9 
d = 10
m = 8
R_c = 50 * calculate_srf(m)
R = calculate_d(RSS, alpha, P_1)
R_rss = Rss_calculate(alpha, P_1, d)
print(R)
print(R_rss)
print(R_c)
