import itertools

n = int(input("请输入行数 n: "))
m = int(input("请输入列数 m: "))

all_matrices = []

for combination in itertools.product([0, 1], repeat=n * m):
    matrix = [list(combination[i:i+m]) for i in range(0, n * m, m)]

    # 筛选条件1：删除包含 1 多于一个的行
    if all(row.count(1) <= 1 for row in matrix):
        # 筛选条件2：检查每一列是否至少有一个 1
        if all(any(row[j] == 1 for row in matrix) for j in range(m)):
            # 筛选条件3：检查每一行是否至少有一个 1
            if all(1 in row for row in matrix):
                all_matrices.append(matrix)

for i, matrix in enumerate(all_matrices):
    print(f"Matrix {i + 1}:")
    for row in matrix:
        print(row)
    print()


