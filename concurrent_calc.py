#======================================================
# Concurrent Throughput estimation model calculation
# Last modify date: 2023 10/20
#======================================================
# Change: make function code
#         example for 80211n protocol TP-Link T4UH ver.2
#         function list: concurrent throughput calc.
#======================================================


def calculate_srf(m):
    try:
        srf = (1 / (m + 0.1 * (m - 1) / 4)) * (1 - (0.1 * (m - 1)))
        return srf
    except ZeroDivisionError:
        return "Division by zero is not allowed. Please provide a valid value of 'm'."
