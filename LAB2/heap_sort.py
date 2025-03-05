import random
import time
import matplotlib.pyplot as plt
import pandas as pd

def heapify(array, n, i):
    largest = i
    left = 2 * i + 1
    right = 2 * i + 2

    if left < n and array[left] > array[largest]:
        largest = left

    if right < n and array[right] > array[largest]:
        largest = right

    if largest != i:
        array[i], array[largest] = array[largest], array[i]
        heapify(array, n, largest)

def heap_sort(array):
    n = len(array)

    start_index = (n - 1) // 2
    for i in range(start_index, -1, -1):
        heapify(array, n, i)

    for i in range(n - 1, 0, -1):
        array[i], array[0] = array[0], array[i]
        heapify(array, i, 0)

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
        heap_sort(array)
        end_time = time.time()
        execution_times.append(end_time - start_time)
        print(f"{label}, Array size: {size}, Execution time: {end_time - start_time:.6f} seconds")

    plt.plot(sizes, execution_times, marker='o', linestyle='-', label=label)

    df = pd.DataFrame({"Array size (n)": sizes, "Time Taken (seconds)": execution_times})
    print(f"\nFinal Execution Time Table for {label}:\n", df)

plt.xlabel('Array Size')
plt.ylabel('Execution Time (seconds)')
plt.title('Heap Sort Execution Time for Different Types of Numbers')
plt.xscale('log')
plt.yscale('log')
plt.grid(True)
plt.legend()
plt.show()