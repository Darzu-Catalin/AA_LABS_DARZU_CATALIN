import time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


# Function to calculate the nth Fibonacci number using memoization
def nth_fibonacci_util(n, memo):
    if n <= 1:
        return n

    # heck if the result is already in the memo table
    if memo[n] != -1:
        return memo[n]

    # Compute Fibonacci using memoization
    memo[n] = nth_fibonacci_util(n - 1, memo) + nth_fibonacci_util(n - 2, memo)
    return memo[n]

def nth_fibonacci(n):
    memo = [-1] * (n + 1)
    return nth_fibonacci_util(n, memo)

# Large Fibonacci values to compute
n_values = [100, 315, 420, 525, 630, 835]
execution_times = []

for n in n_values:
    start_time = time.time()
    nth_fibonacci(n)
    end_time = time.time()
    execution_times.append(end_time - start_time)

table_data = np.zeros((4, len(n_values)))
table_data[2, :] = execution_times

df = pd.DataFrame(table_data, columns=n_values)
df.index = range(4)  # Row indices

pd.set_option('display.max_columns', None)
print(df)

plt.figure(figsize=(10, 5))
plt.plot(n_values, execution_times, marker='o', linestyle='-', color='b', label="Memoization Fibonacci Time")
plt.xlabel("Fibonacci Number (n)")
plt.ylabel("Execution Time (seconds)")
plt.title("Execution Time of Memoization-Based Fibonacci Method")
plt.legend()
plt.grid(True)
plt.show()
