# this is the test file to calc. the fairness index

def calculate_fairness_index(X):
    try:
        # 检查X是否是一维数组
        if all(isinstance(i, (int, float)) for i in X):
            values = [value for value in X if value != 0]
        else:
            values = [value for row in X for value in row if value != 0]
        
        numerator = sum(values) ** 2
        denominator = len(values) * sum(value ** 2 for value in values)
        fairness_index = numerator / denominator
        return fairness_index
    except ZeroDivisionError:
        return "Zero division error. Please provide a matrix with non-zero values."

R = [
59.4,
21.9,
28.4,
54.2]

index = calculate_fairness_index(R)
print(f"{index:.4f}")
