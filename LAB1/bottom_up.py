import time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Iterative Fibonacci with Memoization (Bottom-Up)
def nth_fibonacci(n):
    if n <= 1:
        return n
    memo = [0] * (n + 1)
    memo[1] = 1
    for i in range(2, n + 1):
        memo[i] = memo[i - 1] + memo[i - 2]
    return memo[n]

# Larger Fibonacci terms
n_values = [11000, 22015, 33420, 41325, 55130, 66135]

execution_times = []

# Measure execution time
for n in n_values:
    start_time = time.time()
    nth_fibonacci(n)
    end_time = time.time()
    execution_times.append(end_time - start_time)

table_data = np.zeros((4, len(n_values)))
table_data[1, :] = execution_times

df = pd.DataFrame(table_data, columns=n_values)
df.index = range(4)

pd.set_option('display.max_columns', None)
print(df)

plt.figure(figsize=(10, 5))
plt.plot(n_values, execution_times, marker='o', linestyle='-', color='b', label="`Bottom-up` Fibonacci Time")
plt.xlabel("Fibonacci Number (n)")
plt.ylabel("Execution Time (seconds)")
plt.title("Execution Time of Fibonacci Bottom-up Method")
plt.legend()
plt.grid(True)
plt.show()
