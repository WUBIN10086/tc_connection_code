import math
x1 = 0
x2 = 5
y1 = 0
y2 = 5
alpha = 2.02

P_1 = -28


def Distance(x1, y1, x2, y2):
    distance = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
    return distance

def Rss_calculate(alpha, P_1, d):
    try:
        """ if len(nk) != len(Wk):
            raise ValueError("nk and Wk must have the same length") """
        
        #sum_nk_Wk = sum(nk_i * Wk_i for nk_i, Wk_i in zip(nk, Wk))
        #RSS = P_1 - 10 * alpha * math.log10(d) - sum_nk_Wk
        RSS = P_1 - 10 * alpha * math.log10(d)
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



a = 59.5
b = 62
c = 6.78
d = Distance(x1, y1, x2, y2)
Rss = Rss_calculate(alpha, P_1, d)
Thr = Calculate_throughput(a, b, c, Rss)
print(Thr)