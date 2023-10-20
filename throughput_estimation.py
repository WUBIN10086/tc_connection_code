#======================================================
# Throughput estimation model calculation
# Last modify date: 2023 10/20
#======================================================
# Change: make function code
#         example for 80211n protocol TP-Link T4UH ver.2
#         function list: 1. Distance calc.
#                         2. Rss calc.
#                         3. Thr. calc.
#======================================================
import math

def Distance(x1, y1, x2, y2):
    distance = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
    return distance

def Rss_calculate(alpha, P_1, d, nk, Wk):
    try:
        sum_nk_Wk = sum(nk_i * Wk_i for nk_i, Wk_i in zip(nk, Wk))
        RSS = P_1 - 10 * alpha * math.log10(d) - sum_nk_Wk
        return RSS
    except ValueError:
        return "Please check the code or parameter input."

def Calculate_throughput(a, b, c, Pd):
    try:
        exponent = -(120 + Pd - b) / c
        throughput = a / (1 + math.exp(exponent))
        return throughput
    except ValueError:
        return "Please calculate the Pd, and check the input parameters."

def calculate_throughput_estimate(parameters, coordinates, i, j, nk):
    alpha = parameters.get('alpha', 0.0)
    P_1 = parameters.get('P_1', 0.0)
    a = parameters.get('a', 0.0)
    b = parameters.get('b', 0.0)
    c = parameters.get('c', 0.0)
    Wk = parameters.get('Wk', [])

    if i >= 1 and i <= len(coordinates) and j >= 1 and j <= len(coordinates):
        i_row = coordinates[i - 1]
        j_row = coordinates[j - 1]
        x1, y1 = float(i_row['X']), float(i_row['Y'])
        x2, y2 = float(j_row['X']), float(j_row['Y'])
        d = Distance(x1, y1, x2, y2)
        Pd = Rss_calculate(alpha, P_1, d, nk, Wk)
        Thr_estimation = Calculate_throughput(a, b, c, Pd)
        return Thr_estimation
    else:
        raise ValueError("Invalid values for i and j. Please provide valid values.")






