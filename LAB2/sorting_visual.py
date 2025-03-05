import tkinter as tk
from tkinter import ttk, messagebox
import random
import time

# ----------------------------
# Instrumented Sorting Algorithms
# ----------------------------

def quick_sort_gen(array):
    def _quick_sort(arr, low, high):
        if low < high:
            pivot = arr[high]
            i = low - 1
            for j in range(low, high):
                # Highlight indices being compared: j and high (pivot)
                yield (arr.copy(), [j, high])
                if arr[j] <= pivot:
                    i += 1
                    arr[i], arr[j] = arr[j], arr[i]
                    yield (arr.copy(), [i, j])
            arr[i + 1], arr[high] = arr[high], arr[i + 1]
            yield (arr.copy(), [i+1, high])
            yield from _quick_sort(arr, low, i)
            yield from _quick_sort(arr, i+2, high)
    yield from _quick_sort(array, 0, len(array) - 1)

def quick_sort_opt_gen(array):
    def _quick_sort(arr, low, high):
        if low < high:
            pivot = arr[high]
            i = low - 1
            for j in range(low, high):
                if arr[j] <= pivot:
                    i += 1
                    arr[i], arr[j] = arr[j], arr[i]
                    yield arr.copy()
            arr[i + 1], arr[high] = arr[high], arr[i + 1]
            yield arr.copy()
            yield from _quick_sort(arr, low, i)
            yield from _quick_sort(arr, i+2, high)
    yield from _quick_sort(array, 0, len(array)-1)

def merge_sort_gen(array):
    def _merge_sort(arr, l, r):
        if l < r:
            m = (l + r) // 2
            yield from _merge_sort(arr, l, m)
            yield from _merge_sort(arr, m+1, r)
            yield from merge(arr, l, m, r)
    def merge(arr, l, m, r):
        temp = arr[l:r+1]
        i, j, k = 0, m-l+1, l
        while i < m-l+1 and j < r-l+1:
            yield (arr.copy(), [l+i, l+j])
            if temp[i] <= temp[j]:
                arr[k] = temp[i]
                i += 1
            else:
                arr[k] = temp[j]
                j += 1
            k += 1
            yield (arr.copy(), [k-1])
        while i < m-l+1:
            arr[k] = temp[i]
            i += 1
            k += 1
            yield (arr.copy(), [k-1])
        while j < r-l+1:
            arr[k] = temp[j]
            j += 1
            k += 1
            yield (arr.copy(), [k-1])
    yield from _merge_sort(array, 0, len(array)-1)

def merge_sort_opt_gen(array):
    def _merge_sort(arr, l, r):
        if l < r:
            if arr[l:r+1] == sorted(arr[l:r+1]):
                yield arr.copy()
                return
            m = (l + r) // 2
            yield from _merge_sort(arr, l, m)
            yield from _merge_sort(arr, m+1, r)
            yield from merge(arr, l, m, r)
    def merge(arr, l, m, r):
        temp = arr[l:r+1]
        i, j, k = 0, m-l+1, l
        while i < m-l+1 and j < r-l+1:
            yield (arr.copy(), [l+i, l+j])
            if temp[i] <= temp[j]:
                arr[k] = temp[i]
                i += 1
            else:
                arr[k] = temp[j]
                j += 1
            k += 1
            yield (arr.copy(), [k-1])
        while i < m-l+1:
            arr[k] = temp[i]
            i += 1
            k += 1
            yield (arr.copy(), [k-1])
        while j < r-l+1:
            arr[k] = temp[j]
            j += 1
            k += 1
            yield (arr.copy(), [k-1])
    yield from _merge_sort(array, 0, len(array)-1)

def heap_sort_gen(array):
    def heapify(arr, n, i):
        largest = i
        l = 2*i+1
        r = 2*i+2
        if l < n and arr[l] > arr[largest]:
            largest = l
        if r < n and arr[r] > arr[largest]:
            largest = r
        if largest != i:
            arr[i], arr[largest] = arr[largest], arr[i]
            yield (arr.copy(), [i, largest])
            yield from heapify(arr, n, largest)
    n = len(array)
    for i in range(n//2-1, -1, -1):
        yield from heapify(array, n, i)
    for i in range(n-1, 0, -1):
        array[0], array[i] = array[i], array[0]
        yield (array.copy(), [0, i])
        yield from heapify(array, i, 0)

def heap_sort_opt_gen(array):
    def heapify(arr, n, i):
        while True:
            largest = i
            l = 2*i+1
            r = 2*i+2
            if l < n and arr[l] > arr[largest]:
                largest = l
            if r < n and arr[r] > arr[largest]:
                largest = r
            if largest != i:
                arr[i], arr[largest] = arr[largest], arr[i]
                yield (arr.copy(), [i, largest])
                i = largest
            else:
                break
    n = len(array)
    for i in range(n//2-1, -1, -1):
        yield from heapify(array, n, i)
    for i in range(n-1, 0, -1):
        array[0], array[i] = array[i], array[0]
        yield (array.copy(), [0, i])
        yield from heapify(array, i, 0)

def insertion_sort_gen(arr, left, right):
    for i in range(left+1, right+1):
        key = arr[i]
        j = i-1
        while j >= left and arr[j] > key:
            yield (arr.copy(), [j, i])
            arr[j+1] = arr[j]
            j -= 1
            yield (arr.copy(), [j+1, i])
        arr[j+1] = key
        yield (arr.copy(), [j+1, i])

def tim_sort_gen(array):
    n = len(array)
    min_run = 32
    # Sort small runs with insertion sort
    for start in range(0, n, min_run):
        end = min(start+min_run-1, n-1)
        yield from insertion_sort_gen(array, start, end)
    size = min_run
    while size < n:
        for left in range(0, n, 2*size):
            mid = min(n-1, left+size-1)
            right = min(n-1, left+2*size-1)
            if mid < right:
                yield from merge(array, left, mid, right)
        size *= 2

def tim_sort_opt_gen(array):
    n = len(array)
    min_run = 32
    for start in range(0, n, min_run):
        end = min(start+min_run-1, n-1)
        yield from insertion_sort_gen(array, start, end)
    def merge(arr, l, m, r):
        if arr[m] <= arr[m+1]:
            yield arr.copy()
            return
        temp = arr[l:r+1]
        i, j, k = 0, m-l+1, l
        while i < m-l+1 and j < r-l+1:
            yield (arr.copy(), [l+i, l+j])
            if temp[i] <= temp[j]:
                arr[k] = temp[i]
                i += 1
            else:
                arr[k] = temp[j]
                j += 1
            k += 1
            yield (arr.copy(), [k-1])
        while i < m-l+1:
            arr[k] = temp[i]
            i += 1
            k += 1
            yield (arr.copy(), [k-1])
        while j < r-l+1:
            arr[k] = temp[j]
            j += 1
            k += 1
            yield (arr.copy(), [k-1])
    size = min_run
    while size < n:
        for left in range(0, n, 2*size):
            mid = min(n-1, left+size-1)
            right = min(n-1, left+2*size-1)
            if mid < right:
                yield from merge(array, left, mid, right)
        size *= 2

# ----------------------------
# Enhanced UI: Full-Screen Gray Theme with Improved Layout
# ----------------------------

class SortingVisualizer:
    def __init__(self, root):
        self.root = root
        self.root.title("Sorting Visualizer")
        self.root.attributes("-fullscreen", True)
        self.root.configure(bg="#E0E0E0")

        # Menu Bar
        menubar = tk.Menu(self.root)
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Exit", command=self.root.quit)
        menubar.add_cascade(label="File", menu=file_menu)
        self.root.config(menu=menubar)

        # Style configuration
        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.style.configure("TFrame", background="#E0E0E0")
        self.style.configure("TLabel", background="#E0E0E0", foreground="#333333", font=("Segoe UI", 11))
        self.style.configure("Title.TLabel", font=("Segoe UI", 24, "bold"), foreground="#444444", underline=True)
        self.style.configure("TButton", font=("Segoe UI", 10), padding=6, background="#B0B0B0", foreground="#333333")
        self.style.configure("TCombobox", font=("Segoe UI", 10), fieldbackground="#B0B0B0", background="#B0B0B0", foreground="#333333")
        self.style.map("TButton", background=[("active", "#909090")])

        # Colors for canvas and bars
        self.canvas_bg = "#E0E0E0"
        self.bar_color = "#00bfff"
        self.highlight_color = "#ff4500"

        self.array = []
        self.working_array = []
        self.generator = None
        self.start_time = 0
        self.after_id = None
        self.animation_speed = 50
        self.comparison_count = 0
        self.swap_count = 0
        self.highlight_indices = []

        # Main container frame (full width)
        main_frame = ttk.Frame(root, padding="10")
        main_frame.grid(row=0, column=0, sticky="nsew")
        root.grid_rowconfigure(0, weight=1)
        root.grid_columnconfigure(0, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)

        # Header
        header_frame = ttk.Frame(main_frame)
        header_frame.grid(row=0, column=0, sticky="ew", pady=(0,15))
        header_frame.grid_columnconfigure(0, weight=1)
        title_label = ttk.Label(header_frame, text="Sorting Visualizer", style="Title.TLabel")
        title_label.grid(row=0, column=0, sticky="w")
        info_btn = ttk.Button(header_frame, text="ⓘ", width=3, command=self.show_info)
        info_btn.grid(row=0, column=1, sticky="e")

        # Controls Panel
        control_frame = ttk.Frame(main_frame)
        control_frame.grid(row=1, column=0, sticky="ew", pady=(0,15))
        for i in range(3):
            control_frame.grid_columnconfigure(i, weight=1, uniform="col")
        ttk.Label(control_frame, text="Array Size:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.size_entry = ttk.Entry(control_frame, width=8)
        self.size_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.size_entry.insert(0, "50")
        gen_btn = ttk.Button(control_frame, text="Generate Array", command=self.generate_array)
        gen_btn.grid(row=0, column=2, padx=5, pady=5, sticky="ew")
        ttk.Label(control_frame, text="Algorithm:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.sort_var = tk.StringVar()
        algo_combo = ttk.Combobox(control_frame, textvariable=self.sort_var,
                                  values=["Quick Sort", "Quick Sort Optimised",
                                          "Merge Sort", "Merge Sort Optimised",
                                          "Heap Sort", "Heap Sort Optimised",
                                          "Tim Sort", "Tim Sort Optimised"])
        algo_combo.grid(row=1, column=1, columnspan=2, padx=5, pady=5, sticky="ew")
        algo_combo.current(0)
        ttk.Label(control_frame, text="Speed:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.speed_var = tk.IntVar(value=50)
        speed_scale = ttk.Scale(control_frame, from_=1, to=100, variable=self.speed_var,
                                orient="horizontal", command=self.update_speed)
        speed_scale.grid(row=2, column=1, columnspan=2, padx=5, pady=5, sticky="ew")

        # Buttons Panel for Start and Reset (full width)
        btn_frame = ttk.Frame(control_frame)
        btn_frame.grid(row=3, column=0, columnspan=3, pady=(10,0), sticky="ew")
        btn_frame.grid_columnconfigure(0, weight=1)
        btn_frame.grid_columnconfigure(1, weight=1)
        start_btn = ttk.Button(btn_frame, text="Start Sorting", command=self.start_sorting)
        start_btn.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        reset_btn = ttk.Button(btn_frame, text="Reset", command=self.reset)
        reset_btn.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        # Canvas for Visualization
        self.canvas_frame = ttk.Frame(main_frame)
        self.canvas_frame.grid(row=2, column=0, sticky="nsew", pady=(0,15))
        main_frame.rowconfigure(2, weight=3)
        canvas_border = tk.Frame(self.canvas_frame, bg="#B0B0B0", bd=2, relief="ridge")
        canvas_border.pack(fill="both", expand=True)
        self.canvas = tk.Canvas(canvas_border, bg=self.canvas_bg, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True, padx=5, pady=5)

        # Stats Panel (in one row)
        stats_frame = ttk.Frame(main_frame)
        stats_frame.grid(row=3, column=0, sticky="ew", pady=(0,15))
        for i in range(4):
            stats_frame.grid_columnconfigure(i, weight=1)
        self.time_label = ttk.Label(stats_frame, text="Time: 0.000 sec", anchor="center")
        self.time_label.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        self.comp_label = ttk.Label(stats_frame, text="Comparisons: 0", anchor="center")
        self.comp_label.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.swap_label = ttk.Label(stats_frame, text="Swaps: 0", anchor="center")
        self.swap_label.grid(row=0, column=2, padx=5, pady=5, sticky="ew")
        self.array_size_label = ttk.Label(stats_frame, text="Array Size: 0", anchor="center")
        self.array_size_label.grid(row=0, column=3, padx=5, pady=5, sticky="ew")

        # Array Elements Display (bigger height)
        self.elements_text = tk.Text(main_frame, height=8, font=("Consolas", 10), bg="#E0E0E0", fg="#333333")
        self.elements_text.grid(row=4, column=0, sticky="nsew")
        main_frame.rowconfigure(4, weight=1)
        self.elements_text.configure(state="disabled")

    def show_info(self):
        info_text = (
            "Enhanced Sorting Visualizer\n\n"
            "Visualize various sorting algorithms with highlighted comparisons.\n"
            "Elements under comparison are highlighted in orange.\n\n"
            "Controls:\n"
            " - Enter array size and click 'Generate Array'\n"
            " - Choose an algorithm and adjust the speed slider\n"
            " - Click 'Start Sorting' to visualize the sort\n"
            " - Click 'Reset' to clear the visualization\n"
            " - Use the File menu or press ESC to exit full screen"
        )
        messagebox.showinfo("About Sorting Visualizer", info_text)

    def update_speed(self, val):
        self.animation_speed = 101 - self.speed_var.get()

    def generate_array(self):
        try:
            size = int(self.size_entry.get())
            if size < 1 or size > 500:
                messagebox.showerror("Error", "Array size must be between 1 and 500")
                return
            self.array = [random.randint(-100, 100) for _ in range(size)]
            self.array_size_label.config(text=f"Array Size: {size}")
            self.draw_array()
            self.reset_stats()
        except ValueError:
            messagebox.showerror("Error", "Invalid array size")

    def reset_stats(self):
        self.comparison_count = 0
        self.swap_count = 0
        self.time_label.config(text="Time: 0.000 sec")
        self.comp_label.config(text="Comparisons: 0")
        self.swap_label.config(text="Swaps: 0")

    def draw_array(self):
        self.canvas.delete("all")
        if not self.array:
            return
        n = len(self.array)
        width = self.canvas.winfo_width() or 800
        height = self.canvas.winfo_height() or 400
        bar_width = width / n
        max_val = max(abs(x) for x in self.array) or 1
        baseline = height // 2
        # Draw baseline
        self.canvas.create_line(0, baseline, width, baseline, fill="#777777", dash=(4,2))
        for i, num in enumerate(self.array):
            x0 = i * bar_width + 1
            x1 = (i+1) * bar_width - 1
            bar_height = (abs(num) / max_val) * (baseline - 20)
            if num >= 0:
                y0 = baseline - bar_height
                y1 = baseline
            else:
                y0 = baseline
                y1 = baseline + bar_height
            fill = self.highlight_color if i in self.highlight_indices else (self.bar_color if num >= 0 else "#c0392b")
            self.canvas.create_rectangle(x0, y0, x1, y1, fill=fill, outline="#888888")
            if bar_width > 15:
                self.canvas.create_text((x0+x1)/2, y0-10 if num>=0 else y1+10,
                                        text=str(num), font=("Segoe UI", 8), fill="#333333")
        self.elements_text.configure(state="normal")
        self.elements_text.delete("1.0", tk.END)
        self.elements_text.insert(tk.END, ", ".join(map(str, self.array)))
        self.elements_text.configure(state="disabled")

    def start_sorting(self):
        if not self.array:
            messagebox.showinfo("Info", "Please generate an array first.")
            return
        if self.generator:
            messagebox.showinfo("Info", "Sorting is in progress...")
            return
        self.working_array = self.array.copy()
        self.start_time = time.time()
        self.reset_stats()
        self.size_entry.config(state="disabled")
        sort_type = self.sort_var.get()
        if sort_type == "Quick Sort":
            self.generator = quick_sort_gen(self.working_array)
        elif sort_type == "Quick Sort Optimised":
            self.generator = quick_sort_opt_gen(self.working_array)
        elif sort_type == "Merge Sort":
            self.generator = merge_sort_gen(self.working_array)
        elif sort_type == "Merge Sort Optimised":
            self.generator = merge_sort_opt_gen(self.working_array)
        elif sort_type == "Heap Sort":
            self.generator = heap_sort_gen(self.working_array)
        elif sort_type == "Heap Sort Optimised":
            self.generator = heap_sort_opt_gen(self.working_array)
        elif sort_type == "Tim Sort":
            self.generator = tim_sort_gen(self.working_array)
        elif sort_type == "Tim Sort Optimised":
            self.generator = tim_sort_opt_gen(self.working_array)
        self.animate()

    def animate(self):
        try:
            result = next(self.generator)
            if isinstance(result, tuple):
                self.array = result[0].copy()
                self.highlight_indices = result[1]
            else:
                self.array = result.copy()
                self.highlight_indices = []
            self.comparison_count += 1
            self.swap_count += 1
            elapsed = time.time() - self.start_time
            self.time_label.config(text=f"Time: {elapsed:.3f} sec")
            self.comp_label.config(text=f"Comparisons: {self.comparison_count}")
            self.swap_label.config(text=f"Swaps: {self.swap_count}")
            self.draw_array()
            self.after_id = self.root.after(self.animation_speed, self.animate)
        except StopIteration:
            self.size_entry.config(state="normal")
            self.generator = None
            self.after_id = None
            elapsed = time.time() - self.start_time
            messagebox.showinfo("Sort Complete",
                                f"Algorithm: {self.sort_var.get()}\nTime: {elapsed:.3f} sec\nComparisons: {self.comparison_count}\nSwaps: {self.swap_count}")

    def reset(self):
        if self.after_id is not None:
            self.root.after_cancel(self.after_id)
            self.after_id = None
        self.array = []
        self.working_array = []
        self.generator = None
        self.highlight_indices = []
        self.size_entry.config(state="normal")
        self.canvas.delete("all")
        self.elements_text.configure(state="normal")
        self.elements_text.delete("1.0", tk.END)
        self.elements_text.configure(state="disabled")
        self.reset_stats()
        self.array_size_label.config(text="Array Size: 0")

if __name__ == "__main__":
    root = tk.Tk()
    app = SortingVisualizer(root)
    # Allow exit full-screen with ESC key
    root.bind("<Escape>", lambda e: root.attributes("-fullscreen", False))
    root.mainloop()
