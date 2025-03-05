import random
import time
import pandas as pd
import matplotlib.pyplot as plt

# Tim Sort Implementation
def insertion_sort(array, left, right):
    for i in range(left + 1, right + 1):
        key = array[i]
        j = i - 1
        while j >= left and array[j] > key:
            array[j + 1] = array[j]
            j -= 1
        array[j + 1] = key

def merge(array, left, mid, right):
    left_part = array[left:mid + 1]
    right_part = array[mid + 1:right + 1]
    i = j = 0
    k = left
    while i < len(left_part) and j < len(right_part):
        if left_part[i] <= right_part[j]:
            array[k] = left_part[i]
            i += 1
        else:
            array[k] = right_part[j]
            j += 1
        k += 1
    while i < len(left_part):
        array[k] = left_part[i]
        i += 1
        k += 1
    while j < len(right_part):
        array[k] = right_part[j]
        j += 1
        k += 1

def tim_sort(array):
    n = len(array)
    min_run = 32
    for i in range(0, n, min_run):
        insertion_sort(array, i, min(i + min_run - 1, n - 1))
    size = min_run
    while size < n:
        for left in range(0, n, 2 * size):
            mid = min(n - 1, left + size - 1)
            right = min(n - 1, left + 2 * size - 1)
            merge(array, left, mid, right)
        size *= 2
    return array

# Experimental Analysis
sizes = [1000, 2000, 5000, 10000, 20000, 50000, 100000, 200000, 500000, 1000000, 2000000]
types = {
    "Negative Numbers": lambda size: [random.randint(-10**9, -10**6) for _ in range(size)],
    "Positive Numbers": lambda size: [random.randint(10**6, 10**9) for _ in range(size)],
    "Decreasing Numbers": lambda size: sorted([random.randint(10**6, 10**9) for _ in range(size)], reverse=True)
}

plt.figure(figsize=(10, 5))

for label, generator in types.items():
    execution_times = []
    for size in sizes:
        array = generator(size)
        start_time = time.time()
        tim_sort(array)
        end_time = time.time()
        execution_times.append(end_time - start_time)
        print(f"{label}, Array size: {size}, Execution time: {end_time - start_time:.6f} seconds")

    plt.plot(sizes, execution_times, marker='o', linestyle='-', label=label)

    df = pd.DataFrame({"Array size (n)": sizes, "Time Taken (seconds)": execution_times})
    print(f"\nFinal Execution Time Table for {label}:\n", df)

plt.xlabel('Array Size')
plt.ylabel('Execution Time (seconds)')
plt.title('Tim Sort Execution Time for Different Types of Numbers')
plt.xscale('log')
plt.yscale('log')
plt.grid(True)
plt.legend()
plt.show()
