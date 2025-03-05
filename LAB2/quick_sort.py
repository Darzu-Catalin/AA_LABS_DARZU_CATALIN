import random
import time
import matplotlib.pyplot as plt
import pandas as pd

def quicksort(array):
    if len(array) <= 1:
        return array
    pivot_index = random.randint(0, len(array) - 1)
    pivot = array[pivot_index]
    left = [x for x in array if x < pivot]
    middle = [x for x in array if x == pivot]
    right = [x for x in array if x > pivot]
    return quicksort(left) + middle + quicksort(right)

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
        quicksort(array)
        end_time = time.time()
        execution_times.append(end_time - start_time)
        print(f"{label}, Array size: {size}, Execution time: {end_time - start_time:.6f} seconds")

    plt.plot(sizes, execution_times, marker='o', linestyle='-', label=label)

    df = pd.DataFrame({"Array size (n)": sizes, "Time Taken (seconds)": execution_times})
    print(f"\nFinal Execution Time Table for {label}:\n", df)

plt.xlabel('Array Size')
plt.ylabel('Execution Time (seconds)')
plt.title('Quick Sort Execution Time for Different Types of Numbers')
plt.xscale('log')
plt.yscale('log')
plt.grid(True)
plt.legend()
plt.show()