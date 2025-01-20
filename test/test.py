import concurrent.futures
import math

# 一个示例函数，计算某个数的阶乘
def compute_factorial(number):
    return math.factorial(number)

# 要计算阶乘的数字列表
numbers = [5, 7, 11, 15, 20, 22, 25]

# 使用 ProcessPoolExecutor
with concurrent.futures.ProcessPoolExecutor() as executor:
    # 将任务映射到多个进程
    results = list(executor.map(compute_factorial, numbers))

print(results)
