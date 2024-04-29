#======================================================
# Fairness Index calculation
# Last modify date: 2023 11/04
#======================================================
def calculate_fairness_index(X):
    try:
        values = [value for row in X for value in row if value != 0]
        numerator = sum(values) ** 2
        denominator = len(values) * sum(value ** 2 for value in values)
        fairness_index = numerator / denominator
        return fairness_index
    except ZeroDivisionError:
        return "Zero division error. Please provide a matrix with non-zero values."
