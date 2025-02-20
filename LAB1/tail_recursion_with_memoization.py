import timeit
import matplotlib.pyplot as plt
import concurrent.futures
from functools import lru_cache


# 1. Tail Recursion with Memoization
@lru_cache(None)
def fibonacci_tail(n, a=0, b=1):
    return a if n == 0 else fibonacci_tail(n - 1, b, a + b)


# 2. Iterative Bitwise Doubling Method
def fib_doubling(n):
    a, b = 0, 1
    for i in range(n.bit_length() - 1, -1, -1):
        c = a * ((b << 1) - a)
        d = a * a + b * b
        a, b = c, d
        if (n >> i) & 1:
            a, b = b, a + b
    return a


# 3. Parallelized Fibonacci Calculation (Optimized with Memoization)
@lru_cache(None)
def fibonacci_parallel(n):
    if n <= 1:
        return n
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future1 = executor.submit(fibonacci_parallel, n - 1)
        future2 = executor.submit(fibonacci_parallel, n - 2)
        return future1.result() + future2.result()


# Benchmarking and Performance Testing
def test_performance():
    sizes = [5, 10, 15, 20, 25, 30, 35, 40]
    times = {
        "Tail Recursion": [],
        "Bitwise Doubling": [],
        "Parallel Fibonacci": []
    }

    for n in sizes:
        times["Tail Recursion"].append(timeit.timeit(lambda: fibonacci_tail(n), number=5))
        times["Bitwise Doubling"].append(timeit.timeit(lambda: fib_doubling(n), number=5))
        times["Parallel Fibonacci"].append(timeit.timeit(lambda: fibonacci_parallel(n), number=5))

    for method, t in times.items():
        plt.plot(sizes, t, label=method)

    plt.xlabel("n-th Fibonacci Term")
    plt.ylabel("Execution Time (s)")
    plt.title("Fibonacci Algorithm Performance Comparison")
    plt.legend()
    plt.show()


# Run performance test
test_performance()
