import random
import time
import pandas as pd
import matplotlib.pyplot as plt

def merge_sort(array):
    if len(array) <= 1:
        return array

    middle = len(array) // 2
    left_array = array[:middle]
    right_array = array[middle:]

    return merge(merge_sort(left_array), merge_sort(right_array))

def merge(left, right):
    sorted_array = []
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i] < right[j]:
            sorted_array.append(left[i])
            i += 1
        else:
            sorted_array.append(right[j])
            j += 1
    return sorted_array + left[i:] + right[j:]

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
        merge_sort(array)
        end_time = time.time()
        execution_times.append(end_time - start_time)
        print(f"{label}, Array size: {size}, Execution time: {end_time - start_time:.6f} seconds")

    plt.plot(sizes, execution_times, marker='o', linestyle='-', label=label)

    df = pd.DataFrame({"Array size (n)": sizes, "Time Taken (seconds)": execution_times})
    print(f"\nFinal Execution Time Table for {label}:\n", df)

plt.xlabel('Array Size')
plt.ylabel('Execution Time (seconds)')
plt.title('Merge Sort Execution Time for Different Types of Numbers')
plt.xscale('log')
plt.yscale('log')
plt.grid(True)
plt.legend()
plt.show()
