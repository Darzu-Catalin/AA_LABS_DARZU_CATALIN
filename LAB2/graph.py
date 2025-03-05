import tkinter as tk
from tkinter import ttk, messagebox, font
import random
import time
import threading
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
import matplotlib.pyplot as plt


# Sorting algorithms implementations (non-generator versions)
def quick_sort(arr):
    def _quick_sort(array, low, high):
        if low < high:
            pi = partition(array, low, high)
            _quick_sort(array, low, pi - 1)
            _quick_sort(array, pi + 1, high)

    def partition(array, low, high):
        pivot = array[high]
        i = low - 1
        for j in range(low, high):
            if array[j] <= pivot:
                i += 1
                array[i], array[j] = array[j], array[i]
        array[i + 1], array[high] = array[high], array[i + 1]
        return i + 1

    _quick_sort(arr, 0, len(arr) - 1)


def heap_sort(arr):
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

    n = len(arr)
    for i in range(n // 2 - 1, -1, -1):
        heapify(arr, n, i)
    for i in range(n - 1, 0, -1):
        arr[i], arr[0] = arr[0], arr[i]
        heapify(arr, i, 0)


def merge_sort(arr):
    if len(arr) > 1:
        mid = len(arr) // 2
        L = arr[:mid]
        R = arr[mid:]
        merge_sort(L)
        merge_sort(R)
        i = j = k = 0
        while i < len(L) and j < len(R):
            if L[i] <= R[j]:
                arr[k] = L[i]
                i += 1
            else:
                arr[k] = R[j]
                j += 1
            k += 1
        while i < len(L):
            arr[k] = L[i]
            i += 1
            k += 1
        while j < len(R):
            arr[k] = R[j]
            j += 1
            k += 1


def tim_sort(arr):
    RUN = 32
    n = len(arr)

    def insertion_sort(array, left, right):
        for i in range(left + 1, right + 1):
            temp = array[i]
            j = i - 1
            while j >= left and array[j] > temp:
                array[j + 1] = array[j]
                j -= 1
            array[j + 1] = temp

    def merge(array, left, mid, right):
        len1, len2 = mid - left + 1, right - mid
        left_part, right_part = array[left:left + len1], array[mid + 1:mid + 1 + len2]
        i, j, k = 0, 0, left
        while i < len1 and j < len2:
            if left_part[i] <= right_part[j]:
                array[k] = left_part[i]
                i += 1
            else:
                array[k] = right_part[j]
                j += 1
            k += 1
        while i < len1:
            array[k] = left_part[i]
            i += 1
            k += 1
        while j < len2:
            array[k] = right_part[j]
            j += 1
            k += 1

    for i in range(0, n, RUN):
        insertion_sort(arr, i, min((i + RUN - 1), n - 1))

    size = RUN
    while size < n:
        for left in range(0, n, 2 * size):
            mid = left + size - 1
            right = min((left + 2 * size - 1), (n - 1))
            if mid < right:
                merge(arr, left, mid, right)
        size *= 2


class SortingVisualizer:
    def __init__(self, root):
        self.root = root
        self.root.title("Sorting Algorithm Performance Analyzer")
        self.root.geometry("1200x800")
        self.root.configure(bg="#f5f5f5")

        # Configure styles
        self.setup_styles()

        # Variables
        self.test_thread = None
        self.running = False
        self.progress_var = tk.DoubleVar(value=0)
        self.status_var = tk.StringVar(value="Ready")
        self.algorithm_colors = {
            "Quick Sort": "#1f77b4",  # Blue
            "Merge Sort": "#ff7f0e",  # Orange
            "Heap Sort": "#2ca02c",  # Green
            "Tim Sort": "#d62728"  # Red
        }

        # Create main frames
        self.create_header()
        self.create_main_frame()

        # Set default values
        self.set_defaults()

    def setup_styles(self):
        # Configure ttk styles
        self.style = ttk.Style()
        self.style.theme_use("clam")

        # Configure fonts
        default_font = font.nametofont("TkDefaultFont")
        default_font.configure(family="Segoe UI", size=10)

        # Configure styles
        self.style.configure("TFrame", background="#f5f5f5")
        self.style.configure("TLabel", background="#f5f5f5", font=("Segoe UI", 10))
        self.style.configure("TButton", font=("Segoe UI", 10, "bold"), padding=6)
        self.style.configure("TEntry", font=("Segoe UI", 10))
        self.style.configure("Header.TLabel", font=("Segoe UI", 16, "bold"), foreground="#2c3e50")
        self.style.configure("Status.TLabel", font=("Segoe UI", 9), foreground="#555555")
        self.style.configure("Card.TFrame", background="#ffffff", relief="ridge", borderwidth=1)
        self.style.configure("Progress.Horizontal.TProgressbar", background="#4CAF50")

    def create_header(self):
        # Header frame
        header_frame = ttk.Frame(self.root)
        header_frame.pack(fill=tk.X, padx=20, pady=(20, 0))

        # Title
        title_label = ttk.Label(
            header_frame,
            text="Sorting Algorithm Performance Analyzer",
            style="Header.TLabel"
        )
        title_label.pack(side=tk.LEFT)

        # Version info
        version_label = ttk.Label(
            header_frame,
            text="v1.0",
            style="Status.TLabel"
        )
        version_label.pack(side=tk.RIGHT, padx=10)

    def create_main_frame(self):
        # Main content area
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Left panel for controls
        self.create_control_panel(main_frame)

        # Right panel for visualization
        self.create_visualization_panel(main_frame)

        # Bottom status bar
        self.create_status_bar()

    def create_control_panel(self, parent):
        # Control panel (left side)
        control_frame = ttk.Frame(parent, style="Card.TFrame")
        control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))

        # Parameters section
        params_frame = ttk.Frame(control_frame)
        params_frame.pack(fill=tk.X, padx=15, pady=15)

        ttk.Label(params_frame, text="Test Parameters", font=("Segoe UI", 12, "bold")).pack(anchor=tk.W, pady=(0, 10))

        # Size range frame
        size_frame = ttk.Frame(params_frame)
        size_frame.pack(fill=tk.X, pady=5)

        # Min size
        ttk.Label(size_frame, text="Minimum Array Size:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.min_entry = ttk.Entry(size_frame, width=10)
        self.min_entry.grid(row=0, column=1, padx=5, pady=5, sticky=tk.E)

        # Max size
        ttk.Label(size_frame, text="Maximum Array Size:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.max_entry = ttk.Entry(size_frame, width=10)
        self.max_entry.grid(row=1, column=1, padx=5, pady=5, sticky=tk.E)

        # Number of test points
        ttk.Label(size_frame, text="Number of Test Points:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.num_arrays_entry = ttk.Entry(size_frame, width=10)
        self.num_arrays_entry.grid(row=2, column=1, padx=5, pady=5, sticky=tk.E)

        # Separator
        ttk.Separator(params_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)

        # Algorithm selection
        algo_frame = ttk.Frame(params_frame)
        algo_frame.pack(fill=tk.X, pady=5)

        ttk.Label(algo_frame, text="Select Algorithms", font=("Segoe UI", 11, "bold")).pack(anchor=tk.W, pady=(0, 5))

        # Create algorithm selection with checkbuttons
        self.algo_vars = {}
        algorithms = ["Quick Sort", "Merge Sort", "Heap Sort", "Tim Sort"]

        for i, algo in enumerate(algorithms):
            var = tk.BooleanVar(value=False)
            self.algo_vars[algo] = var

            algo_cb = ttk.Checkbutton(
                algo_frame,
                text=algo,
                variable=var,
                style="TCheckbutton"
            )
            algo_cb.pack(anchor=tk.W, pady=2)

        # Separator
        ttk.Separator(params_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)

        # Action buttons frame
        action_frame = ttk.Frame(params_frame)
        action_frame.pack(fill=tk.X, pady=10)

        # Run button
        self.run_button = ttk.Button(
            action_frame,
            text="Run Analysis",
            command=self.start_tests,
            width=15
        )
        self.run_button.pack(side=tk.LEFT, padx=(0, 5))

        # Reset button
        self.reset_button = ttk.Button(
            action_frame,
            text="Reset",
            command=self.reset,
            width=10
        )
        self.reset_button.pack(side=tk.LEFT)

        # Algorithm info section
        info_frame = ttk.Frame(control_frame)
        info_frame.pack(fill=tk.X, padx=15, pady=(0, 15))

        ttk.Label(info_frame, text="Algorithm Information", font=("Segoe UI", 12, "bold")).pack(anchor=tk.W,
                                                                                                pady=(0, 10))

        # Info text widget with scrollbar
        info_scroll = ttk.Scrollbar(info_frame)
        info_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.info_text = tk.Text(
            info_frame,
            height=10,
            width=30,
            wrap=tk.WORD,
            font=("Segoe UI", 9),
            yscrollcommand=info_scroll.set,
            background="#f8f8f8",
            relief=tk.FLAT
        )
        self.info_text.pack(fill=tk.BOTH, expand=True)
        info_scroll.config(command=self.info_text.yview)

        # Add algorithm descriptions
        self.info_text.insert(tk.END,
                              "Quick Sort: A divide-and-conquer algorithm that works by selecting a 'pivot' element and partitioning the array around it. Average time complexity: O(n log n).\n\n")
        self.info_text.insert(tk.END,
                              "Merge Sort: A divide-and-conquer algorithm that divides the array in half, sorts each half, then merges them. Time complexity: O(n log n).\n\n")
        self.info_text.insert(tk.END,
                              "Heap Sort: Uses a binary heap data structure to sort elements. Time complexity: O(n log n).\n\n")
        self.info_text.insert(tk.END,
                              "Tim Sort: A hybrid sorting algorithm that divides the list into small runs, sorts them using Insertion Sort, and merges them using Merge Sort for efficiency. Time complexity: O(n log n).")
        self.info_text.configure(state=tk.DISABLED)

    def create_visualization_panel(self, parent):
        # Visualization panel (right side)
        viz_frame = ttk.Frame(parent, style="Card.TFrame")
        viz_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Plot title
        plot_title_frame = ttk.Frame(viz_frame)
        plot_title_frame.pack(fill=tk.X, padx=15, pady=15)

        ttk.Label(
            plot_title_frame,
            text="Performance Comparison",
            font=("Segoe UI", 12, "bold")
        ).pack(side=tk.LEFT)

        # Results label
        self.results_label = ttk.Label(
            plot_title_frame,
            text="",
            style="Status.TLabel"
        )
        self.results_label.pack(side=tk.RIGHT)

        # Create matplotlib figure and canvas
        self.figure = Figure(figsize=(8, 6), dpi=100, facecolor="#ffffff")
        self.ax = self.figure.add_subplot(111)

        # Configure plot appearance
        self.ax.set_xlabel("Array Size", fontsize=10)
        self.ax.set_ylabel("Time (seconds)", fontsize=10)
        self.ax.set_title("Sorting Algorithm Performance Comparison", fontsize=12)
        self.ax.grid(True, linestyle='--', alpha=0.7)
        self.figure.tight_layout(pad=3.0)

        # Create canvas
        self.canvas = FigureCanvasTkAgg(self.figure, master=viz_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))

        # Add toolbar
        toolbar_frame = ttk.Frame(viz_frame)
        toolbar_frame.pack(fill=tk.X, padx=15, pady=(0, 15))

        self.toolbar = NavigationToolbar2Tk(self.canvas, toolbar_frame)
        self.toolbar.update()

    def create_status_bar(self):
        # Status bar at bottom
        status_frame = ttk.Frame(self.root)
        status_frame.pack(fill=tk.X, padx=20, pady=(0, 10))

        # Progress bar
        self.progress_bar = ttk.Progressbar(
            status_frame,
            orient=tk.HORIZONTAL,
            mode='determinate',
            variable=self.progress_var,
            style="Progress.Horizontal.TProgressbar"
        )
        self.progress_bar.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))

        # Status label
        self.status_label = ttk.Label(
            status_frame,
            textvariable=self.status_var,
            style="Status.TLabel"
        )
        self.status_label.pack(side=tk.RIGHT)

    def set_defaults(self):
        # Set default values
        self.min_entry.insert(0, "100")
        self.max_entry.insert(0, "10000")
        self.num_arrays_entry.insert(0, "10")

        # Select Quick Sort and Merge Sort by default
        self.algo_vars["Quick Sort"].set(True)
        self.algo_vars["Merge Sort"].set(True)

    def start_tests(self):
        if self.running:
            return

        # Get parameters
        try:
            min_size = int(self.min_entry.get())
            max_size = int(self.max_entry.get())
            num_points = int(self.num_arrays_entry.get())

            # Get selected algorithms
            algorithms = [algo for algo, var in self.algo_vars.items() if var.get()]

        except ValueError:
            messagebox.showerror("Input Error", "Please enter valid numeric values for array sizes and test points.")
            return

        # Validate input
        if not algorithms:
            messagebox.showerror("Selection Error", "Please select at least one sorting algorithm.")
            return

        if min_size <= 0 or max_size <= min_size or num_points <= 0:
            messagebox.showerror("Range Error",
                                 "Please ensure minimum size is positive, maximum size is greater than minimum, and number of test points is positive.")
            return

        if num_points > 50:
            if not messagebox.askyesno("Performance Warning",
                                       "Running many test points may take a long time. Continue?"):
                return

        # Generate test sizes
        if num_points == 1:
            sizes = [min_size]
        else:
            step = (max_size - min_size) / (num_points - 1)
            sizes = [int(min_size + i * step) for i in range(num_points)]

        # Reset plot
        self.ax.clear()
        self.ax.set_xlabel("Array Size", fontsize=10)
        self.ax.set_ylabel("Time (seconds)", fontsize=10)
        self.ax.set_title("Sorting Algorithm Performance Comparison", fontsize=12)
        self.ax.grid(True, linestyle='--', alpha=0.7)
        self.canvas.draw()

        # Reset progress
        self.progress_var.set(0)
        self.status_var.set("Initializing tests...")
        self.results_label.config(text="Running analysis...")

        # Disable controls during test
        self.running = True
        self.run_button.config(state=tk.DISABLED)

        # Start test thread
        self.test_thread = threading.Thread(
            target=self.run_tests,
            args=(sizes, algorithms),
            daemon=True
        )
        self.test_thread.start()

        # Start monitoring thread
        self.root.after(100, self.monitor_thread)

    def monitor_thread(self):
        if self.test_thread and self.test_thread.is_alive():
            self.root.after(100, self.monitor_thread)
        else:
            self.running = False
            self.run_button.config(state=tk.NORMAL)
            self.status_var.set("Analysis complete")
            self.progress_var.set(100)

    def run_tests(self, sizes, algorithms):
        total_tests = len(sizes) * len(algorithms)
        completed = 0
        data = {algo: {'sizes': [], 'times': []} for algo in algorithms}

        try:
            for size in sizes:
                # Generate random array once for each size
                arr = [random.randint(-1000, 1000) for _ in range(size)]

                for algo in algorithms:
                    # Update status
                    status_msg = f"Testing {algo} with array size {size}..."
                    self.root.after(0, lambda m=status_msg: self.status_var.set(m))

                    # Make a copy to avoid modifying the original
                    arr_copy = arr.copy()
                    start_time = time.perf_counter()

                    # Run the appropriate sorting algorithm
                    if algo == "Quick Sort":
                        quick_sort(arr_copy)
                    elif algo == "Merge Sort":
                        merge_sort(arr_copy)
                    elif algo == "Heap Sort":
                        heap_sort(arr_copy)
                    elif algo == "Tim Sort":
                        tim_sort(arr_copy)

                    # Record time
                    elapsed = time.perf_counter() - start_time
                    data[algo]['sizes'].append(size)
                    data[algo]['times'].append(elapsed)

                    # Update progress
                    completed += 1
                    progress = (completed / total_tests) * 100
                    self.root.after(0, lambda p=progress: self.progress_var.set(p))

                    # Verify that array is sorted
                    is_sorted = all(arr_copy[i] <= arr_copy[i + 1] for i in range(len(arr_copy) - 1))
                    if not is_sorted:
                        print(f"Warning: {algo} failed to sort array of size {size}")

            # Update plot with results
            self.root.after(0, lambda: self.update_plot(data))

        except Exception as e:
            # Handle any exceptions
            error_msg = f"Error during test: {str(e)}"
            self.root.after(0, lambda: messagebox.showerror("Error", error_msg))
            self.root.after(0, lambda: self.status_var.set("Test failed"))

    def update_plot(self, data):
        try:
            self.ax.clear()

            # Plot each algorithm with a different color
            for algo in data:
                if not data[algo]['sizes'] or not data[algo]['times']:
                    continue

                self.ax.plot(
                    data[algo]['sizes'],
                    data[algo]['times'],
                    marker='o',
                    markersize=5,
                    linestyle='-',
                    linewidth=2,
                    label=algo,
                    color=self.algorithm_colors.get(algo)
                )

            # Find the fastest algorithm for the largest size
            summary_text = ""
            if data:
                max_size = 0
                for algo in data:
                    if data[algo]['sizes']:
                        current_max = max(data[algo]['sizes'])
                        if current_max > max_size:
                            max_size = current_max

                if max_size > 0:
                    fastest_algo = None
                    fastest_time = float('inf')

                    for algo in data:
                        if not data[algo]['sizes']:
                            continue

                        # Find the index of the largest size
                        try:
                            idx = [i for i, size in enumerate(data[algo]['sizes']) if size == max_size]
                            if idx:
                                time_taken = data[algo]['times'][idx[0]]

                                if time_taken < fastest_time:
                                    fastest_time = time_taken
                                    fastest_algo = algo
                        except (ValueError, IndexError):
                            continue

                    if fastest_algo:
                        summary_text = f"Fastest for size {max_size}: {fastest_algo} ({fastest_time:.6f}s)"
                        self.results_label.config(text=summary_text)

            # Set labels and title
            self.ax.set_xlabel("Array Size", fontsize=10)
            self.ax.set_ylabel("Time (seconds)", fontsize=10)
            self.ax.set_title("Sorting Algorithm Performance Comparison", fontsize=12)

            # Add grid
            self.ax.grid(True, linestyle='--', alpha=0.7)

            # Add legend
            if data:
                self.ax.legend(loc='upper left')

            # Format axes
            self.ax.tick_params(axis='both', which='major', labelsize=9)

            # Option to use logarithmic scale if large differences
            if any('Tim Sort' in algo for algo in data.keys()):
                # Check if we need log scale due to large differences
                max_time = max(max(times['times']) for times in data.values() if times['times'])
                min_time = min(min(times['times']) for times in data.values() if times['times'])

                if max_time / min_time > 100:  # If difference is more than 100x
                    self.ax.set_yscale('log')
                    self.ax.set_ylabel("Time (seconds) - Log Scale", fontsize=10)

            # Adjust layout
            self.figure.tight_layout(pad=3.0)

            # Redraw canvas
            self.canvas.draw()

        except Exception as e:
            messagebox.showerror("Plot Error", f"Error updating plot: {str(e)}")

    def reset(self):
        # Reset plot
        self.ax.clear()
        self.ax.set_xlabel("Array Size", fontsize=10)
        self.ax.set_ylabel("Time (seconds)", fontsize=10)
        self.ax.set_title("Sorting Algorithm Performance Comparison", fontsize=12)
        self.ax.grid(True, linestyle='--', alpha=0.7)
        self.canvas.draw()

        # Reset input fields
        self.min_entry.delete(0, tk.END)
        self.max_entry.delete(0, tk.END)
        self.num_arrays_entry.delete(0, tk.END)

        # Reset algorithm selection
        for var in self.algo_vars.values():
            var.set(False)

        # Reset status
        self.progress_var.set(0)
        self.status_var.set("Ready")
        self.results_label.config(text="")

        # Set defaults again
        self.set_defaults()


if __name__ == "__main__":
    root = tk.Tk()
    app = SortingVisualizer(root)
    root.mainloop()