import time
import matplotlib.pyplot as plt
import time
import numpy as np
import pandas as pd

def nth_fibonacci(n):
    if n <= 1:
        return n

    curr = 0
    prev1 = 1
    prev2 = 0

    for _ in range(2, n + 1):
        curr = prev1 + prev2
        prev2 = prev1
        prev1 = curr

    return curr

fib_values = []
times = []
n_values = [11000, 22015, 33420, 41325, 55130, 66135]

execution_times = []

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

for n in n_values:
    start_time = time.time()
    result = nth_fibonacci(n)
    end_time = time.time()

    fib_values.append(result)
    times.append(end_time - start_time)

plt.figure(figsize=(8, 5))
plt.plot(n_values, times, marker='o', linestyle='-')
plt.xlabel("n-th Fibonacci Term")
plt.ylabel("Time (seconds)")
plt.title("Iterative Space-Optimized Fibonacci Function")
plt.grid()
plt.show()
