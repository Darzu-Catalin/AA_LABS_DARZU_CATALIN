import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import collections
import heapq
import time
import random
import math  # For spring layout k calculation
import matplotlib.pyplot as plt
import networkx as nx
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import traceback  # For debugging


# --- Disjoint Set Union (DSU) for Kruskal's Algorithm ---
class DSU:
    def __init__(self, n):
        self.parent = list(range(n))
        self.rank = [0] * n

    def find(self, i):
        if self.parent[i] == i: return i
        self.parent[i] = self.find(self.parent[i])
        return self.parent[i]

    def union(self, i, j):
        root_i = self.find(i)
        root_j = self.find(j)
        if root_i != root_j:
            if self.rank[root_i] < self.rank[root_j]:
                self.parent[root_i] = root_j
            elif self.rank[root_i] > self.rank[root_j]:
                self.parent[root_j] = root_i
            else:
                self.parent[root_j] = root_i
                self.rank[root_i] += 1
            return True
        return False


# --- Graph Representation ---
class Graph:
    def __init__(self, num_nodes, directed=False):
        self.num_nodes = num_nodes
        self.directed = directed
        self.adj = collections.defaultdict(list)
        self.edges = []  # List of (u, v, weight)
        self.nodes = set(range(num_nodes))

    def add_edge(self, u, v, weight=1):
        if u >= self.num_nodes or v >= self.num_nodes or u < 0 or v < 0: return
        self.adj[u].append((v, weight))
        # Ensure self.edges stores unique representations for undirected graphs if used by Kruskal directly
        # However, Kruskal implementation below processes self.edges to make them unique.
        self.edges.append((u, v, weight))
        if not self.directed:
            self.adj[v].append((u, weight))

    def get_adjacency_matrix(self):
        matrix = [[float('inf')] * self.num_nodes for _ in range(self.num_nodes)]
        for i in range(self.num_nodes): matrix[i][i] = 0
        for u in self.adj:
            for v, weight in self.adj[u]: matrix[u][v] = weight
        return matrix


# --- Graph Algorithms ---
class Algorithms:
    # DFS and BFS stepwise (from previous version, minor adjustments if needed)
    @staticmethod
    def dfs_stepwise(graph, start_node):
        if start_node < 0 or start_node >= graph.num_nodes:
            yield {"type": "error", "message": f"Start node {start_node} is invalid for {graph.num_nodes} nodes."}
            return
        if not graph.nodes:
            yield {"type": "error", "message": "Graph has no nodes."}
            return

        visited_nodes = set()
        traversal_tree_edges = []
        dfs_stack = [(start_node, None)]

        yield {"type": "initial", "current_node": None, "frontier_nodes": {start_node},
               "visited_nodes": set(), "tree_edges": [], "message": f"DFS init. Stack: [{start_node}]"}

        while dfs_stack:
            current_node, parent_node = dfs_stack.pop()
            if current_node in visited_nodes:
                yield {"type": "node_already_visited", "current_node": current_node,
                       "frontier_nodes": {n for n, p in dfs_stack}, "visited_nodes": visited_nodes.copy(),
                       "tree_edges": list(traversal_tree_edges), "message": f"Node {current_node} already visited."}
                continue
            visited_nodes.add(current_node)
            if parent_node is not None: traversal_tree_edges.append(tuple(sorted((parent_node, current_node))))

            yield {"type": "node_visit", "current_node": current_node, "frontier_nodes": {n for n, p in dfs_stack},
                   "visited_nodes": visited_nodes.copy(), "tree_edges": list(traversal_tree_edges),
                   "message": f"Visiting {current_node}."}

            neighbors_to_add = []
            # Sort for consistent behavior, reverse for typical stack processing (e.g. smaller index first if not reversed)
            sorted_neighbors = sorted([data[0] for data in graph.adj[current_node]], reverse=True)
            for neighbor_node in sorted_neighbors:
                if neighbor_node not in visited_nodes: neighbors_to_add.append((neighbor_node, current_node))

            if neighbors_to_add:
                yield {"type": "explore_neighbors", "current_node": current_node,
                       "frontier_nodes": {n for n, p in dfs_stack} | {n for n, p in neighbors_to_add},
                       "visited_nodes": visited_nodes.copy(), "tree_edges": list(traversal_tree_edges),
                       "message": f"Adding {[n for n, p in neighbors_to_add]} to stack."}
            for neighbor_node, _ in neighbors_to_add: dfs_stack.append((neighbor_node, current_node))

        yield {"type": "completed", "current_node": None, "frontier_nodes": set(),
               "visited_nodes": visited_nodes.copy(), "tree_edges": list(traversal_tree_edges),
               "message": "DFS complete."}

    @staticmethod
    def bfs_stepwise(graph, start_node):
        if start_node < 0 or start_node >= graph.num_nodes:
            yield {"type": "error", "message": f"Start node {start_node} is invalid."}
            return
        if not graph.nodes:
            yield {"type": "error", "message": "Graph has no nodes."}
            return

        visited_nodes = {start_node}
        bfs_queue = collections.deque([(start_node, None)])
        traversal_tree_edges = []

        yield {"type": "initial", "current_node": None, "frontier_nodes": {start_node},
               "visited_nodes": {start_node}, "tree_edges": [], "message": f"BFS init. Queue: [{start_node}]"}

        while bfs_queue:
            current_node, parent_node = bfs_queue.popleft()
            yield {"type": "node_visit", "current_node": current_node, "frontier_nodes": {n for n, p in bfs_queue},
                   "visited_nodes": visited_nodes.copy(), "tree_edges": list(traversal_tree_edges),
                   "message": f"Processing {current_node}."}
            if parent_node is not None:
                edge_to_add = tuple(sorted((parent_node, current_node)))
                if edge_to_add not in traversal_tree_edges: traversal_tree_edges.append(edge_to_add)

            neighbors_added_to_queue = []
            sorted_neighbors = sorted([data[0] for data in graph.adj[current_node]])
            for neighbor_node in sorted_neighbors:
                if neighbor_node not in visited_nodes:
                    visited_nodes.add(neighbor_node)
                    bfs_queue.append((neighbor_node, current_node))
                    neighbors_added_to_queue.append(neighbor_node)

            if neighbors_added_to_queue:
                yield {"type": "explore_neighbors", "current_node": current_node,
                       "frontier_nodes": {n for n, p in bfs_queue}, "visited_nodes": visited_nodes.copy(),
                       "tree_edges": list(traversal_tree_edges),
                       "message": f"Adding {neighbors_added_to_queue} to queue."}

        yield {"type": "completed", "current_node": None, "frontier_nodes": set(),
               "visited_nodes": visited_nodes.copy(), "tree_edges": list(traversal_tree_edges),
               "message": "BFS complete."}

    @staticmethod
    def dijkstra_stepwise(graph, start_node):
        if start_node < 0 or start_node >= graph.num_nodes:
            yield {"type": "error", "message": f"Start node {start_node} is invalid."};
            return
        if not graph.nodes: yield {"type": "error", "message": "Graph has no nodes."}; return

        distances = {node: float('inf') for node in graph.nodes}
        predecessors = {node: None for node in graph.nodes}
        distances[start_node] = 0
        pq = [(0, start_node)]  # (distance, node)
        spt_edges = []
        processed_nodes = set()  # Nodes whose final shortest path is found

        yield {"type": "initial", "current_node": None, "frontier_nodes": {start_node}, "processed_nodes": set(),
               "distances": distances.copy(), "spt_edges": [],
               "message": f"Dijkstra init. Start: {start_node}. PQ: {pq}"}

        while pq:
            dist_u, u = heapq.heappop(pq)

            if u in processed_nodes:  # Already processed this node with its shortest path
                yield {"type": "skip_processed_in_pq", "current_node": u, "frontier_nodes": {n for _, n in pq},
                       "processed_nodes": processed_nodes.copy(), "distances": distances.copy(),
                       "spt_edges": list(spt_edges),
                       "message": f"Node {u} already processed. Dist: {dist_u} vs known {distances[u]}"}
                continue

            if dist_u > distances[u]:  # Stale entry in PQ
                yield {"type": "stale_pq_entry", "current_node": u, "frontier_nodes": {n for _, n in pq},
                       "processed_nodes": processed_nodes.copy(), "distances": distances.copy(),
                       "spt_edges": list(spt_edges),
                       "message": f"Stale PQ entry for {u}. Current dist {distances[u]} < {dist_u}."}
                continue

            processed_nodes.add(u)  # Mark u as processed

            if predecessors[u] is not None:
                actual_weight = next((w for v_neighbor, w in graph.adj[predecessors[u]] if v_neighbor == u), 0)
                spt_edges.append(tuple(sorted((predecessors[u], u)) + (actual_weight,)))

            yield {"type": "node_process", "current_node": u, "frontier_nodes": {n for _, n in pq},
                   "processed_nodes": processed_nodes.copy(), "distances": distances.copy(),
                   "spt_edges": list(spt_edges), "message": f"Processing node {u}. Final dist: {distances[u]}."}

            for v, weight in graph.adj[u]:
                if v not in processed_nodes:
                    if distances[u] + weight < distances[v]:
                        old_dist_v = distances[v]
                        distances[v] = distances[u] + weight
                        predecessors[v] = u
                        heapq.heappush(pq, (distances[v], v))
                        yield {"type": "edge_relax", "current_node": u, "neighbor_node": v,
                               "frontier_nodes": {n for _, n in pq}, "processed_nodes": processed_nodes.copy(),
                               "distances": distances.copy(), "spt_edges": list(spt_edges),
                               "message": f"Relaxed edge ({u}-{v}). Dist to {v}: {old_dist_v} -> {distances[v]}. PQ updated."}

        yield {"type": "completed", "current_node": None, "frontier_nodes": set(),
               "processed_nodes": processed_nodes.copy(), "distances": distances.copy(),
               "spt_edges": list(spt_edges), "message": "Dijkstra complete."}

    @staticmethod
    def prim_stepwise(graph, start_node):
        if start_node < 0 or start_node >= graph.num_nodes:
            yield {"type": "error", "message": f"Start node {start_node} is invalid."};
            return
        if not graph.nodes: yield {"type": "error", "message": "Graph has no nodes."}; return

        pq = []
        nodes_in_mst = {start_node}
        mst_edges = []
        total_weight = 0

        for v_neighbor, weight in graph.adj[start_node]:
            heapq.heappush(pq, (weight, start_node, v_neighbor))

        yield {"type": "initial", "current_edge": None, "nodes_in_mst": nodes_in_mst.copy(),
               "mst_edges": [], "total_weight": 0, "pq_edges": [(u, v, w) for w, u, v in pq],
               "message": f"Prim init. Start: {start_node}. PQ populated from start node."}

        while pq and len(nodes_in_mst) < graph.num_nodes:
            weight, u, v = heapq.heappop(pq)

            yield {"type": "edge_consider", "current_edge": (u, v, weight), "nodes_in_mst": nodes_in_mst.copy(),
                   "mst_edges": list(mst_edges), "total_weight": total_weight,
                   "pq_edges": [(n1, n2, w) for w, n1, n2 in pq],
                   "message": f"Considering edge ({u}-{v}) with weight {weight} from PQ."}

            if v not in nodes_in_mst:
                nodes_in_mst.add(v)
                mst_edges.append((u, v, weight))
                total_weight += weight

                yield {"type": "node_added_to_mst", "current_edge": (u, v, weight), "nodes_in_mst": nodes_in_mst.copy(),
                       "mst_edges": list(mst_edges), "total_weight": total_weight,
                       "pq_edges": [(n1, n2, w) for w, n1, n2 in pq],
                       "message": f"Added node {v} and edge ({u}-{v}) to MST. Total weight: {total_weight}."}

                new_edges_to_pq_msg = []
                for neighbor_node, neighbor_weight in graph.adj[v]:
                    if neighbor_node not in nodes_in_mst:
                        heapq.heappush(pq, (neighbor_weight, v, neighbor_node))
                        new_edges_to_pq_msg.append(f"({v}-{neighbor_node}, {neighbor_weight})")

                if new_edges_to_pq_msg:
                    yield {"type": "pq_updated", "current_edge": (u, v, weight), "nodes_in_mst": nodes_in_mst.copy(),
                           "mst_edges": list(mst_edges), "total_weight": total_weight,
                           "pq_edges": [(n1, n2, w) for w, n1, n2 in pq],
                           "message": f"Added to PQ from {v}: {', '.join(new_edges_to_pq_msg)}."}
            else:
                yield {"type": "node_already_in_mst", "current_edge": (u, v, weight),
                       "nodes_in_mst": nodes_in_mst.copy(),
                       "mst_edges": list(mst_edges), "total_weight": total_weight,
                       "pq_edges": [(n1, n2, w) for w, n1, n2 in pq],
                       "message": f"Node {v} of edge ({u}-{v}) already in MST. Skipping."}

        if len(nodes_in_mst) != graph.num_nodes and graph.num_nodes > 0 and any(graph.adj.values()):
            yield {"type": "completed_disconnected", "current_edge": None, "nodes_in_mst": nodes_in_mst.copy(),
                   "mst_edges": list(mst_edges), "total_weight": total_weight, "pq_edges": [],
                   "message": f"Prim complete (graph might be disconnected). MST for connected component of start node."}
        else:
            yield {"type": "completed", "current_edge": None, "nodes_in_mst": nodes_in_mst.copy(),
                   "mst_edges": list(mst_edges), "total_weight": total_weight, "pq_edges": [],
                   "message": "Prim complete."}

    @staticmethod
    def kruskal_stepwise(graph):
        if not graph.nodes: yield {"type": "error", "message": "Graph has no nodes."}; return

        mst_edges_final = []
        total_weight = 0

        unique_edges_for_kruskal = []
        seen_edges_tuples = set()
        for u_orig, v_orig, w_orig in graph.edges:
            edge_key = frozenset({u_orig, v_orig}) # Use frozenset for undirected graph uniqueness
            if edge_key not in seen_edges_tuples:
                unique_edges_for_kruskal.append((w_orig, u_orig, v_orig))
                seen_edges_tuples.add(edge_key)
            elif graph.directed: # For directed graphs, (u,v) is different from (v,u)
                 unique_edges_for_kruskal.append((w_orig, u_orig, v_orig))


        sorted_graph_edges = sorted(unique_edges_for_kruskal)

        yield {"type": "initial", "sorted_edges": [(u, v, w) for w, u, v in sorted_graph_edges],
               "mst_edges": [], "total_weight": 0, "dsu_sets": {i: [i] for i in range(graph.num_nodes)},
               "message": f"Kruskal init. {len(sorted_graph_edges)} unique edges sorted by weight."}

        dsu = DSU(graph.num_nodes)
        num_edges_in_mst = 0

        for i, (weight, u, v) in enumerate(sorted_graph_edges):
            current_processing_edge = (u, v, weight)
            yield {"type": "edge_consider", "current_edge": current_processing_edge,
                   "sorted_edges_remaining": [(n1, n2, w) for w, n1, n2 in sorted_graph_edges[i + 1:]],
                   "mst_edges": list(mst_edges_final), "total_weight": total_weight,
                   "dsu_sets": {node_idx: [n for n in range(graph.num_nodes) if dsu.find(n) == dsu.find(node_idx)] for node_idx in range(graph.num_nodes) if dsu.parent[node_idx] == node_idx }, # More accurate DSU sets
                   "message": f"Considering edge ({u}-{v}), weight {weight}."}

            root_u = dsu.find(u)
            root_v = dsu.find(v)

            if root_u != root_v:
                dsu.union(u, v)
                mst_edges_final.append((u, v, weight))
                total_weight += weight
                num_edges_in_mst += 1

                current_dsu_sets = collections.defaultdict(list)
                for node_idx in range(graph.num_nodes): current_dsu_sets[dsu.find(node_idx)].append(node_idx)

                yield {"type": "edge_added_to_mst", "current_edge": current_processing_edge,
                       "mst_edges": list(mst_edges_final), "total_weight": total_weight,
                       "dsu_sets": dict(current_dsu_sets),
                       "message": f"Added ({u}-{v}) to MST. Roots: {root_u} != {root_v}. Union made."}

                if num_edges_in_mst == graph.num_nodes - 1 and graph.num_nodes > 0:
                    break # Optimization: MST is complete
            else:
                current_dsu_sets = collections.defaultdict(list)
                for node_idx in range(graph.num_nodes): current_dsu_sets[dsu.find(node_idx)].append(node_idx)
                yield {"type": "edge_forms_cycle", "current_edge": current_processing_edge,
                       "mst_edges": list(mst_edges_final), "total_weight": total_weight,
                        "dsu_sets": dict(current_dsu_sets),
                       "message": f"Edge ({u}-{v}) forms a cycle (roots {root_u} == {root_v}). Skipped."}

        final_dsu_sets = collections.defaultdict(list)
        for node_idx in range(graph.num_nodes): final_dsu_sets[dsu.find(node_idx)].append(node_idx)

        msg_suffix = ""
        # A valid MST for a connected graph with N nodes must have N-1 edges.
        # If the graph might be disconnected, Kruskal finds an MST for each connected component (a forest).
        if graph.num_nodes > 0 and num_edges_in_mst < graph.num_nodes - 1 and any(graph.adj.values()):
             msg_suffix = " (Graph may be disconnected or not all nodes spanned by edges considered)"


        yield {"type": "completed", "mst_edges": list(mst_edges_final), "total_weight": total_weight,
               "dsu_sets": dict(final_dsu_sets), "message": f"Kruskal complete.{msg_suffix}"}

    @staticmethod
    def dfs(graph, start_node):
        final_state = {}
        for state in Algorithms.dfs_stepwise(graph, start_node):
            if state["type"] == "completed":
                final_state = state; break
            elif state["type"] == "error":
                return [], [] # Return empty for error
        return list(final_state.get("visited_nodes", [])), final_state.get("tree_edges", [])

    @staticmethod
    def bfs(graph, start_node):
        final_state = {}
        for state in Algorithms.bfs_stepwise(graph, start_node):
            if state["type"] == "completed":
                final_state = state; break
            elif state["type"] == "error":
                return [], [] # Return empty for error
        return list(final_state.get("visited_nodes", [])), final_state.get("tree_edges", [])

    @staticmethod
    def dijkstra(graph, start_node):
        final_state = {}
        for state in Algorithms.dijkstra_stepwise(graph, start_node):
            if state["type"] == "completed":
                final_state = state; break
            elif state["type"] == "error":
                return {}, [] # Return empty for error
        return final_state.get("distances", {}), final_state.get("spt_edges", [])

    @staticmethod
    def prim(graph, start_node=0):
        # Ensure start_node is valid, if not, try to pick a valid one or default to 0 if graph is not empty
        if not graph.nodes: return [], 0
        valid_start_node = start_node
        if start_node < 0 or start_node >= graph.num_nodes:
            valid_start_node = 0 # Default to 0 or first available node if graph.nodes is not empty

        final_state = {}
        for state in Algorithms.prim_stepwise(graph, valid_start_node):
            if state["type"] in ["completed", "completed_disconnected"]:
                final_state = state; break
            elif state["type"] == "error":
                return [], 0 # Return empty for error
        return final_state.get("mst_edges", []), final_state.get("total_weight", 0)

    @staticmethod
    def kruskal(graph):
        final_state = {}
        for state in Algorithms.kruskal_stepwise(graph):
            if state["type"] == "completed":
                final_state = state; break
            elif state["type"] == "error":
                return [], 0 # Return empty for error
        return final_state.get("mst_edges", []), final_state.get("total_weight", 0)

    @staticmethod
    def floyd_warshall(graph):
        n = graph.num_nodes
        if n == 0: return []
        dist = graph.get_adjacency_matrix()
        # Initialize predecessors matrix (optional, but good for path reconstruction)
        # pred = [[None] * n for _ in range(n)]
        # for i in range(n):
        #     for j in range(n):
        #         if i == j or dist[i][j] != float('inf'):
        #             pred[i][j] = i


        for k_fw in range(n): # Intermediate vertex
            for i in range(n): # Source vertex
                for j in range(n): # Destination vertex
                    if dist[i][k_fw] != float('inf') and \
                       dist[k_fw][j] != float('inf') and \
                       dist[i][k_fw] + dist[k_fw][j] < dist[i][j]:
                        dist[i][j] = dist[i][k_fw] + dist[k_fw][j]
                        # pred[i][j] = pred[k_fw][j] # Update predecessor if path is shortened
        return dist # Can also return pred if path reconstruction is needed


# --- Graph Generation ---
def generate_random_graph(num_nodes, num_edges, weighted=True, directed=False, max_weight=20):
    if num_nodes <= 0: return Graph(0, directed)
    graph = Graph(num_nodes, directed)
    if num_nodes == 1 and num_edges > 0: num_edges = 0 # No edges possible for a single node

    # Calculate maximum possible edges for the given graph type
    if directed:
        max_possible_edges = num_nodes * (num_nodes - 1)
    else:
        max_possible_edges = num_nodes * (num_nodes - 1) // 2

    num_edges = min(num_edges, max_possible_edges)
    if num_edges < 0: num_edges = 0


    edges_added_set = set()
    attempts = 0
    max_attempts = num_edges * 10 + num_nodes * 5 + 50 # Increased max attempts

    while len(graph.edges) < num_edges: # Check graph.edges directly as add_edge handles undirected duplicates for adj list
        if attempts > max_attempts :
            print(f"Warning: Could not generate all {num_edges} requested edges after {max_attempts} attempts. Generated {len(graph.edges)}.")
            break
        if num_nodes < 2: break # Cannot create edges with less than 2 nodes

        u, v = random.sample(range(num_nodes), 2) # Ensure u != v

        # For undirected graphs, store a canonical representation (smaller, larger) in edges_added_set
        # This set is to avoid adding the *exact same directional edge* multiple times if using graph.edges for control
        # and to avoid u-v and v-u if the graph is undirected and control is based on edges_added_set
        edge_key_for_set = tuple(sorted((u,v))) if not directed else (u,v)

        # Check if this specific edge (u,v) or its reverse (v,u for undirected) has been considered for adding
        # This logic is tricky. The goal is to reach num_edges unique edges.
        # graph.add_edge handles the adjacency list correctly for directed/undirected.
        # The primary loop control should be len(graph.edges) < num_edges for undirected due to duplicate u-v, v-u in graph.edges if not handled
        # For Kruskal, graph.edges is later filtered for unique (weight, u, v) tuples where (u,v) is canonical for undirected.

        # Simplified: Rely on Graph.add_edge to build adj list and graph.edges.
        # Control loop by number of unique edges desired.
        # For undirected graphs, an edge (u,v) is the same as (v,u).
        # We use edges_added_set to track unique conceptual edges.
        if edge_key_for_set not in edges_added_set:
            weight_val = random.randint(1, max_weight) if weighted else 1
            graph.add_edge(u, v, weight_val) # This adds to adj and appends (u,v,w) to graph.edges
                                             # If undirected, it also adds (v,u,w) to adj list of v
            edges_added_set.add(edge_key_for_set)
        attempts += 1

    # If graph is undirected, graph.edges might have duplicates like (u,v,w) and (v,u,w) if add_edge was called for both.
    # The current add_edge adds (u,v,w) to graph.edges once.
    # For Kruskal, we make edges unique later.
    return graph


# --- Tkinter GUI Application ---
class GraphApp:
    def __init__(self, master):
        self.master = master
        master.title("Graph Algorithms Analyzer")
        master.geometry("1350x950")

        self.graph = None
        self.nx_graph = None # networkx graph for visualization
        self.performance_data = collections.defaultdict(list) # Store perf data
        self.algorithm_generator = None # For stepwise execution
        self.current_algo_state = None
        self._graph_pos = None # Store graph layout positions
        self._animation_job = None # For run_animated

        # --- Main Frames ---
        self.control_frame = ttk.LabelFrame(master, text="Controls", padding=10)
        self.control_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ns")

        self.graph_frame = ttk.LabelFrame(master, text="Graph Visualization", padding=10)
        self.graph_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        self.results_frame = ttk.LabelFrame(master, text="Results & Performance", padding=10)
        self.results_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky="ew")

        master.grid_columnconfigure(1, weight=1) # Graph frame should expand
        master.grid_rowconfigure(0, weight=1) # Row with graph and controls should expand

        # --- Control Frame Widgets ---
        ttk.Label(self.control_frame, text="Algorithm:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.algo_var = tk.StringVar()
        self.algo_combo = ttk.Combobox(self.control_frame, textvariable=self.algo_var,
                                       values=["DFS", "BFS", "Dijkstra", "Prim", "Kruskal", "Floyd-Warshall", "Compare All (Performance)"])
        self.algo_combo.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.algo_combo.current(0) # Default to DFS
        self.algo_combo.bind("<<ComboboxSelected>>", self.on_algo_select)

        ttk.Label(self.control_frame, text="Nodes:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.nodes_var = tk.IntVar(value=8)
        self.nodes_entry = ttk.Entry(self.control_frame, textvariable=self.nodes_var, width=7)
        self.nodes_entry.grid(row=1, column=1, padx=5, pady=5, sticky="w")

        ttk.Label(self.control_frame, text="Edges:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.edges_var = tk.IntVar(value=10)
        self.edges_entry = ttk.Entry(self.control_frame, textvariable=self.edges_var, width=7)
        self.edges_entry.grid(row=2, column=1, padx=5, pady=5, sticky="w")

        self.start_node_label = ttk.Label(self.control_frame, text="Start Node:")
        self.start_node_label.grid(row=3, column=0, padx=5, pady=5, sticky="w")
        self.start_node_var = tk.IntVar(value=0)
        self.start_node_entry = ttk.Entry(self.control_frame, textvariable=self.start_node_var, width=7)
        self.start_node_entry.grid(row=3, column=1, padx=5, pady=5, sticky="w")

        self.generate_button = ttk.Button(self.control_frame, text="Generate & Setup Algorithm", command=self.setup_algorithm_run)
        self.generate_button.grid(row=4, column=0, columnspan=2, padx=5, pady=10)

        self.step_button = ttk.Button(self.control_frame, text="Next Step", command=self.execute_next_step, state=tk.DISABLED)
        self.step_button.grid(row=5, column=0, padx=5, pady=5, sticky="ew")

        self.run_animated_button = ttk.Button(self.control_frame, text="Run Animated", command=self.run_animated_click, state=tk.DISABLED)
        self.run_animated_button.grid(row=5, column=1, padx=5, pady=5, sticky="ew")


        self.animation_delay_label = ttk.Label(self.control_frame, text="Anim. Delay (ms):")
        self.animation_delay_label.grid(row=6, column=0, padx=5, pady=2, sticky="w")
        self.animation_delay_var = tk.IntVar(value=500)
        self.animation_delay_entry = ttk.Entry(self.control_frame, textvariable=self.animation_delay_var, width=7)
        self.animation_delay_entry.grid(row=6, column=1, padx=5, pady=2, sticky="w")


        ttk.Separator(self.control_frame, orient="horizontal").grid(row=7, column=0, columnspan=2, sticky="ew", pady=10)

        ttk.Label(self.control_frame, text="Performance Analysis:").grid(row=8, column=0, columnspan=2, padx=5, pady=5, sticky="w")
        ttk.Label(self.control_frame, text="Node Sizes (e.g., 10,20,50):").grid(row=9, column=0, padx=5, pady=2, sticky="w")
        self.node_sizes_var = tk.StringVar(value="10, 20, 30, 40, 50") # Example values
        self.node_sizes_entry = ttk.Entry(self.control_frame, textvariable=self.node_sizes_var)
        self.node_sizes_entry.grid(row=9, column=1, padx=5, pady=2, sticky="ew")

        ttk.Label(self.control_frame, text="Edge Factor (nodes*factor):").grid(row=10, column=0, padx=5, pady=2, sticky="w")
        self.edge_factor_var = tk.DoubleVar(value=1.5) # Example: for N nodes, N*1.5 edges
        self.edge_factor_entry = ttk.Entry(self.control_frame, textvariable=self.edge_factor_var, width=7)
        self.edge_factor_entry.grid(row=10, column=1, padx=5, pady=2, sticky="w")


        self.performance_button = ttk.Button(self.control_frame, text="Run Performance Analysis", command=self.run_performance_analysis_gui)
        self.performance_button.grid(row=11, column=0, columnspan=2, padx=5, pady=10)

        self.control_frame.grid_columnconfigure(1, weight=1) # Allow combobox/entries to expand a bit
        self.on_algo_select() # Initial setup of control visibility

        # --- Graph Visualization Canvas (Matplotlib) ---
        self.fig_graph, self.ax_graph = plt.subplots(figsize=(8,7)) # Adjusted size
        self.canvas_graph = FigureCanvasTkAgg(self.fig_graph, master=self.graph_frame)
        self.canvas_graph.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.ax_graph.set_title("Graph Structure")
        self.ax_graph.axis('off')
        self.fig_graph.tight_layout()
        self.canvas_graph.draw()

        # --- Results and Performance Plot Area (Paned Window) ---
        self.results_paned_window = ttk.PanedWindow(self.results_frame, orient=tk.HORIZONTAL)
        self.results_paned_window.pack(fill=tk.BOTH, expand=True)

        # Text Results Area
        self.text_results_frame = ttk.Frame(self.results_paned_window, width=450) # Initial width hint
        self.results_paned_window.add(self.text_results_frame, weight=1) # Adjust weight as needed

        self.text_results = tk.Text(self.text_results_frame, wrap=tk.WORD, height=12, width=55) # Default height/width
        self.text_results_scrollbar = ttk.Scrollbar(self.text_results_frame, orient="vertical", command=self.text_results.yview)
        self.text_results.configure(yscrollcommand=self.text_results_scrollbar.set)
        self.text_results_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.text_results.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self._update_text_results("Algorithm results and step messages will appear here.\nPerformance plots will show after analysis.")

        # Performance Plot Area
        self.plot_results_frame = ttk.Frame(self.results_paned_window, width=650) # Initial width hint
        self.results_paned_window.add(self.plot_results_frame, weight=2) # Adjust weight

        self.fig_perf, self.ax_perf = plt.subplots(figsize=(8,4)) # Adjusted
        self.canvas_perf = FigureCanvasTkAgg(self.fig_perf, master=self.plot_results_frame)
        self.canvas_perf.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.ax_perf.set_title("Performance Analysis")
        self.ax_perf.set_xlabel("Number of Nodes (Size)")
        self.ax_perf.set_ylabel("Time (seconds)")
        self.ax_perf.grid(True, which="both", linestyle='--', linewidth=0.5)
        self.fig_perf.tight_layout()
        self.canvas_perf.draw()

    def on_algo_select(self, event=None):
        selected_algo = self.algo_var.get()
        is_stepwise_algo = selected_algo in ["DFS", "BFS", "Dijkstra", "Prim", "Kruskal"]

        # Enable/disable step and animated run buttons
        can_step_or_animate = is_stepwise_algo and self.algorithm_generator is not None
        self.step_button.config(state=tk.NORMAL if can_step_or_animate else tk.DISABLED)
        self.run_animated_button.config(state=tk.NORMAL if can_step_or_animate else tk.DISABLED)

        # Show/hide animation delay controls
        if is_stepwise_algo:
            self.animation_delay_label.grid()
            self.animation_delay_entry.grid()
        else:
            self.animation_delay_label.grid_remove()
            self.animation_delay_entry.grid_remove()

        # Show/hide start node entry
        if selected_algo in ["DFS", "BFS", "Dijkstra", "Prim"]:
            self.start_node_label.grid()
            self.start_node_entry.grid()
        else:
            self.start_node_label.grid_remove()
            self.start_node_entry.grid_remove()

        # Disable generate button for performance comparison mode
        if selected_algo == "Compare All (Performance)":
            self.generate_button.config(state=tk.DISABLED)
            # Also disable step/animate if they were somehow enabled
            self.step_button.config(state=tk.DISABLED)
            self.run_animated_button.config(state=tk.DISABLED)
        else:
            self.generate_button.config(state=tk.NORMAL)

    def _update_text_results(self, content, append=False):
        self.text_results.config(state=tk.NORMAL)
        if not append:
            self.text_results.delete(1.0, tk.END)
        self.text_results.insert(tk.END, str(content) + "\n")
        self.text_results.see(tk.END) # Scroll to the end
        self.text_results.config(state=tk.DISABLED)

    def _generate_current_graph_structure(self, num_nodes, num_edges, is_weighted=True, is_directed=False, max_weight=20):
        """Generates self.graph (custom) and self.nx_graph (NetworkX)"""
        algo = self.algo_var.get()
        # Determine if the graph should be directed based on the algorithm
        # Floyd-Warshall and Dijkstra typically assume directed or handle weights appropriately.
        # MST algos (Prim, Kruskal) typically use undirected graphs. DFS/BFS can be on either.
        if algo in ["Dijkstra", "Floyd-Warshall"]:
            is_directed_for_algo = True # Often makes sense for these
        elif algo in ["Prim", "Kruskal"]:
            is_directed_for_algo = False # Must be undirected for typical MST
        else: # DFS, BFS
            is_directed_for_algo = is_directed # Use provided or default

        self.graph = generate_random_graph(num_nodes, num_edges,
                                           weighted=is_weighted,
                                           directed=is_directed_for_algo,
                                           max_weight=max_weight)
        # Create NetworkX graph for visualization
        if is_directed_for_algo:
            self.nx_graph = nx.DiGraph()
        else:
            self.nx_graph = nx.Graph()

        if self.graph and self.graph.nodes:
            self.nx_graph.add_nodes_from(range(self.graph.num_nodes))
            # For NetworkX, add edges based on self.graph.edges to ensure weights are captured
            # and avoid duplicate edges in the visualization if self.graph.adj was used directly for undirected
            temp_edges_for_nx = set()
            for u, v, weight in self.graph.edges:
                # For undirected nx_graph, add canonical edge to avoid duplicates if graph.edges has u,v and v,u
                if not is_directed_for_algo:
                    edge_key = tuple(sorted((u,v)))
                    if edge_key not in temp_edges_for_nx:
                        self.nx_graph.add_edge(u,v, weight=weight if is_weighted else 1.0)
                        temp_edges_for_nx.add(edge_key)
                else: # Directed graph
                     self.nx_graph.add_edge(u,v, weight=weight if is_weighted else 1.0)


        self._graph_pos = None # Reset positions for new graph
        return self.graph


    def _draw_graph(self, algo_state=None):
        self.ax_graph.clear()
        if not self.nx_graph or not self.nx_graph.nodes():
            self.ax_graph.text(0.5, 0.5, "No graph generated or graph is empty.", ha='center', va='center')
            self.ax_graph.axis('off'); self.canvas_graph.draw(); return

        num_nodes_for_layout = self.nx_graph.number_of_nodes()
        if self._graph_pos is None or set(self._graph_pos.keys()) != set(self.nx_graph.nodes()):
            try:
                if num_nodes_for_layout > 0 and num_nodes_for_layout < 50:
                     # Kamada-Kawai often gives good layouts for smaller graphs
                    self._graph_pos = nx.kamada_kawai_layout(self.nx_graph)
                elif num_nodes_for_layout > 0 : # Check added for num_nodes_for_layout > 0
                    k_val = (1.5 / math.sqrt(num_nodes_for_layout))
                    self._graph_pos = nx.spring_layout(self.nx_graph, k=k_val, iterations=75 if num_nodes_for_layout < 100 else 50, seed=42)
                else: # No nodes, empty pos
                    self._graph_pos = {}
            except Exception as e: # Catch layout errors
                print(f"Layout generation error: {e}. Falling back to spring_layout.")
                if num_nodes_for_layout > 0:
                    k_val = (1.0 / math.sqrt(num_nodes_for_layout))
                    self._graph_pos = nx.spring_layout(self.nx_graph, k=k_val, iterations=50, seed=42)
                else:
                    self._graph_pos = {}


        pos = self._graph_pos
        if not pos and self.nx_graph.nodes(): # If pos is empty but nodes exist, try a default spring layout
            print("Warning: Graph positions were empty despite nodes existing. Attempting default spring layout.")
            self._graph_pos = nx.spring_layout(self.nx_graph, seed=42)
            pos = self._graph_pos
        if not pos: # If still no positions (e.g., no nodes), then cannot draw
             self.ax_graph.text(0.5, 0.5, "Cannot determine graph layout.", ha='center', va='center')
             self.ax_graph.axis('off'); self.canvas_graph.draw(); return


        # Default colors and styles
        node_colors_map = {node: 'skyblue' for node in self.nx_graph.nodes()}
        edge_colors_map = {edge: 'gray' for edge in self.nx_graph.edges()}
        edge_styles_map = {edge: 'solid' for edge in self.nx_graph.edges()}
        edge_widths_map = {edge: 1.0 for edge in self.nx_graph.edges()}
        node_labels = {node: str(node) for node in self.nx_graph.nodes()}
        edge_labels = {(u,v): data.get('weight',1) for u,v,data in self.nx_graph.edges(data=True)}


        algo_type = self.algo_var.get()

        if algo_state:
            # DFS/BFS specific coloring
            if algo_type in ["DFS", "BFS"]:
                if "visited_nodes" in algo_state:
                    for node in algo_state["visited_nodes"]: node_colors_map[node] = 'lightgreen'
                if "frontier_nodes" in algo_state:
                    for node in algo_state["frontier_nodes"]: node_colors_map[node] = 'coral'
                if "current_node" in algo_state and algo_state["current_node"] is not None:
                    node_colors_map[algo_state["current_node"]] = 'red'
                if "tree_edges" in algo_state:
                    for u, v in algo_state["tree_edges"]:
                        # Ensure edge exists in nx_graph (could be (u,v) or (v,u) for undirected)
                        if self.nx_graph.has_edge(u,v):
                            edge_colors_map[(u,v)] = 'black'; edge_widths_map[(u,v)] = 2.0
                        elif self.nx_graph.has_edge(v,u): # For undirected graph representation in NetworkX
                            edge_colors_map[(v,u)] = 'black'; edge_widths_map[(v,u)] = 2.0


            # Dijkstra specific coloring
            elif algo_type == "Dijkstra":
                if "processed_nodes" in algo_state:
                    for node in algo_state["processed_nodes"]: node_colors_map[node] = 'lightgreen' # Finalized
                if "frontier_nodes" in algo_state: # Nodes in PQ
                    for node in algo_state["frontier_nodes"]: node_colors_map[node] = 'coral'
                if "current_node" in algo_state and algo_state["current_node"] is not None:
                    node_colors_map[algo_state["current_node"]] = 'red' # Being processed
                if "spt_edges" in algo_state: # Shortest Path Tree edges
                    for u,v,w in algo_state["spt_edges"]:
                        if self.nx_graph.has_edge(u,v):
                            edge_colors_map[(u,v)] = 'blue'; edge_widths_map[(u,v)] = 2.5
                        elif self.nx_graph.has_edge(v,u) and not self.nx_graph.is_directed():
                             edge_colors_map[(v,u)] = 'blue'; edge_widths_map[(v,u)] = 2.5

            # Prim specific coloring
            elif algo_type == "Prim":
                if "nodes_in_mst" in algo_state:
                    for node in algo_state["nodes_in_mst"]: node_colors_map[node] = 'palegreen'
                if "mst_edges" in algo_state:
                    for u,v,w in algo_state["mst_edges"]:
                        if self.nx_graph.has_edge(u,v):
                            edge_colors_map[(u,v)] = 'green'; edge_widths_map[(u,v)] = 2.5
                        elif self.nx_graph.has_edge(v,u) and not self.nx_graph.is_directed():
                             edge_colors_map[(v,u)] = 'green'; edge_widths_map[(v,u)] = 2.5
                if "current_edge" in algo_state and algo_state["current_edge"]:
                    u,v,w = algo_state["current_edge"]
                    if self.nx_graph.has_edge(u,v): edge_colors_map[(u,v)] = 'orange'
                    elif self.nx_graph.has_edge(v,u) and not self.nx_graph.is_directed(): edge_colors_map[(v,u)] = 'orange'
                    if u is not None: node_colors_map[u] = 'lightcoral' # Node from which current edge originates
                    if v is not None: node_colors_map[v] = 'lightcoral' # Node to which current edge points

            # Kruskal specific coloring
            elif algo_type == "Kruskal":
                if "mst_edges" in algo_state:
                    for u,v,w in algo_state["mst_edges"]:
                        if self.nx_graph.has_edge(u,v):
                            edge_colors_map[(u,v)] = 'darkgreen'; edge_widths_map[(u,v)] = 2.5
                        elif self.nx_graph.has_edge(v,u) and not self.nx_graph.is_directed():
                            edge_colors_map[(v,u)] = 'darkgreen'; edge_widths_map[(v,u)] = 2.5

                if "current_edge" in algo_state and algo_state["current_edge"]:
                    u,v,w = algo_state["current_edge"]
                    if self.nx_graph.has_edge(u,v): edge_colors_map[(u,v)] = 'red' ; edge_styles_map[(u,v)] = 'dashed'
                    elif self.nx_graph.has_edge(v,u) and not self.nx_graph.is_directed(): edge_colors_map[(v,u)] = 'red'; edge_styles_map[(v,u)] = 'dashed'

                # Color nodes based on DSU sets
                if "dsu_sets" in algo_state:
                    # Generate a color for each set root
                    set_roots = sorted(list(algo_state["dsu_sets"].keys()))
                    num_sets = len(set_roots)
                    set_colors_available = plt.cm.get_cmap('viridis', num_sets if num_sets > 0 else 1)
                    root_to_color = {root: set_colors_available(i) for i, root in enumerate(set_roots)}

                    for root, nodes_in_set in algo_state["dsu_sets"].items():
                        for node in nodes_in_set:
                            if node in node_colors_map: # Ensure node is in the graph
                                node_colors_map[node] = root_to_color.get(root, 'skyblue')


        # Prepare lists for nx.draw
        final_node_colors = [node_colors_map.get(node, 'skyblue') for node in self.nx_graph.nodes()]
        final_edge_colors = [edge_colors_map.get(edge, 'gray') for edge in self.nx_graph.edges()]
        final_edge_styles = [edge_styles_map.get(edge, 'solid') for edge in self.nx_graph.edges()]
        final_edge_widths = [edge_widths_map.get(edge, 1.0) for edge in self.nx_graph.edges()]


        nx.draw(self.nx_graph, pos, ax=self.ax_graph, with_labels=True, labels=node_labels,
                node_color=final_node_colors, node_size=700, font_size=10,
                edge_color=final_edge_colors, style=final_edge_styles, width=final_edge_widths,
                arrows=self.nx_graph.is_directed(), arrowstyle='->', arrowsize=15)

        if self.nx_graph.is_directed() or algo_type in ["Dijkstra", "Prim", "Kruskal"]: # Show edge weights for these
            # Filter edge_labels to only include edges present in nx_graph
            valid_edge_labels = {k:v for k,v in edge_labels.items() if self.nx_graph.has_edge(k[0], k[1])}
            nx.draw_networkx_edge_labels(self.nx_graph, pos, ax=self.ax_graph, edge_labels=valid_edge_labels, font_size=8)


        self.ax_graph.set_title(f"Graph: {algo_type}" + (f" - Step: {algo_state.get('type', 'N/A')}" if algo_state else ""))
        self.ax_graph.axis('off')
        self.canvas_graph.draw()


    def setup_algorithm_run(self):
        if self._animation_job: # Cancel any ongoing animation
            self.master.after_cancel(self._animation_job)
            self._animation_job = None

        try:
            num_nodes = self.nodes_var.get()
            num_edges = self.edges_var.get()
            start_node = self.start_node_var.get()
            selected_algo = self.algo_var.get()

            if num_nodes <= 0:
                messagebox.showerror("Error", "Number of nodes must be positive.")
                return

            # Determine if graph should be weighted/directed based on algorithm
            is_weighted = selected_algo in ["Dijkstra", "Prim", "Kruskal", "Floyd-Warshall"]
            # For simplicity, let's assume most algos here work better with/expect undirected,
            # except those explicitly for directed or weighted paths like Dijkstra/Floyd.
            is_directed = selected_algo in ["Dijkstra", "Floyd-Warshall"] # Or if user explicitly sets a directed graph option later


            self._generate_current_graph_structure(num_nodes, num_edges, is_weighted=is_weighted, is_directed=is_directed)

            if not self.graph or not self.graph.nodes:
                 self._update_text_results("Graph generation failed or resulted in an empty graph.")
                 self._draw_graph() # Draw empty state
                 self.step_button.config(state=tk.DISABLED)
                 self.run_animated_button.config(state=tk.DISABLED)
                 return


            self.algorithm_generator = None # Reset generator

            if selected_algo == "DFS":
                if start_node < 0 or start_node >= num_nodes:
                    messagebox.showerror("Error", f"Start node {start_node} is invalid for {num_nodes} nodes.")
                    self._draw_graph(); return
                self.algorithm_generator = Algorithms.dfs_stepwise(self.graph, start_node)
            elif selected_algo == "BFS":
                if start_node < 0 or start_node >= num_nodes:
                    messagebox.showerror("Error", f"Start node {start_node} is invalid for {num_nodes} nodes.")
                    self._draw_graph(); return
                self.algorithm_generator = Algorithms.bfs_stepwise(self.graph, start_node)
            elif selected_algo == "Dijkstra":
                if start_node < 0 or start_node >= num_nodes:
                    messagebox.showerror("Error", f"Start node {start_node} is invalid for {num_nodes} nodes.")
                    self._draw_graph(); return
                self.algorithm_generator = Algorithms.dijkstra_stepwise(self.graph, start_node)
            elif selected_algo == "Prim":
                if start_node < 0 or start_node >= num_nodes:
                    messagebox.showerror("Error", f"Start node {start_node} is invalid for {num_nodes} nodes.")
                    self._draw_graph(); return
                self.algorithm_generator = Algorithms.prim_stepwise(self.graph, start_node)
            elif selected_algo == "Kruskal":
                self.algorithm_generator = Algorithms.kruskal_stepwise(self.graph)
            elif selected_algo == "Floyd-Warshall":
                # Floyd-Warshall is not stepwise visually in this setup, run directly
                dist_matrix = Algorithms.floyd_warshall(self.graph)
                result_text = "Floyd-Warshall All-Pairs Shortest Paths:\n"
                if not dist_matrix:
                    result_text += "No graph or nodes to process."
                else:
                    for i in range(len(dist_matrix)):
                        row_str = []
                        for j in range(len(dist_matrix[i])):
                            val = dist_matrix[i][j]
                            row_str.append("inf" if val == float('inf') else str(val))
                        result_text += f"Row {i}: [{', '.join(row_str)}]\n"
                self._update_text_results(result_text)
                self._draw_graph() # Draw initial graph, no specific algo state
                self.step_button.config(state=tk.DISABLED)
                self.run_animated_button.config(state=tk.DISABLED)
                return # Handled, no generator

            if self.algorithm_generator:
                self.current_algo_state = next(self.algorithm_generator, None)
                if self.current_algo_state:
                    self._update_text_results(f"Algorithm: {selected_algo}\n" + self.current_algo_state.get("message", "Setup complete."))
                    self._draw_graph(self.current_algo_state)
                    self.step_button.config(state=tk.NORMAL)
                    self.run_animated_button.config(state=tk.NORMAL)
                else: # Generator immediately exhausted (e.g., error state from generator)
                    self._update_text_results(f"Could not initialize {selected_algo}.")
                    self._draw_graph()
                    self.step_button.config(state=tk.DISABLED)
                    self.run_animated_button.config(state=tk.DISABLED)
            else: # No generator for selected algo (should be handled by Floyd-Warshall path or if more non-stepwise added)
                 self._draw_graph() # Draw the generated graph
                 self.step_button.config(state=tk.DISABLED)
                 self.run_animated_button.config(state=tk.DISABLED)


        except ValueError:
            messagebox.showerror("Input Error", "Please enter valid numbers for nodes, edges, and start node.")
            self._draw_graph() # Clear or show empty
            self.step_button.config(state=tk.DISABLED)
            self.run_animated_button.config(state=tk.DISABLED)
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred: {e}\n{traceback.format_exc()}")
            self._draw_graph()
            self.step_button.config(state=tk.DISABLED)
            self.run_animated_button.config(state=tk.DISABLED)


    def execute_next_step(self):
        if self._animation_job: # Cancel animation if stepping manually
            self.master.after_cancel(self._animation_job)
            self._animation_job = None
            self.run_animated_button.config(text="Run Animated") # Reset button text

        if self.algorithm_generator:
            try:
                self.current_algo_state = next(self.algorithm_generator, None)
                if self.current_algo_state:
                    self._update_text_results(self.current_algo_state.get("message", "Next step."), append=True)
                    self._draw_graph(self.current_algo_state)
                    if self.current_algo_state.get("type") in ["completed", "completed_disconnected", "error"]:
                        self.step_button.config(state=tk.DISABLED)
                        self.run_animated_button.config(state=tk.DISABLED)
                        self.algorithm_generator = None # Mark as finished
                else: # Generator is exhausted
                    self._update_text_results("Algorithm complete (no more steps).", append=True)
                    self.step_button.config(state=tk.DISABLED)
                    self.run_animated_button.config(state=tk.DISABLED)
                    self.algorithm_generator = None
            except StopIteration:
                self._update_text_results("Algorithm finished.", append=True)
                self.step_button.config(state=tk.DISABLED)
                self.run_animated_button.config(state=tk.DISABLED)
                self.algorithm_generator = None
            except Exception as e:
                messagebox.showerror("Step Execution Error", f"Error during step: {e}\n{traceback.format_exc()}")
                self.step_button.config(state=tk.DISABLED)
                self.run_animated_button.config(state=tk.DISABLED)
                self.algorithm_generator = None
        else:
            self._update_text_results("No algorithm setup or already completed.", append=True)
            self.step_button.config(state=tk.DISABLED)
            self.run_animated_button.config(state=tk.DISABLED)

    def run_animated_click(self):
        if self._animation_job: # If animation is running, stop it
            self.master.after_cancel(self._animation_job)
            self._animation_job = None
            self.run_animated_button.config(text="Run Animated")
            # Keep step button enabled if generator still exists
            if self.algorithm_generator: self.step_button.config(state=tk.NORMAL)
        else: # If animation is not running, start it
            if self.algorithm_generator:
                self.run_animated_button.config(text="Stop Animation")
                self.step_button.config(state=tk.DISABLED) # Disable manual stepping during animation
                self._animation_job = self.master.after(self.animation_delay_var.get(), self._animate_step)
            else:
                self._update_text_results("No algorithm setup or already completed for animation.", append=True)


    def _animate_step(self):
        if not self.algorithm_generator:
            self.run_animated_button.config(text="Run Animated")
            self.step_button.config(state=tk.DISABLED) # No generator
            self._animation_job = None
            return

        try:
            self.current_algo_state = next(self.algorithm_generator, None)
            if self.current_algo_state:
                self._update_text_results(self.current_algo_state.get("message", "Animating..."), append=True)
                self._draw_graph(self.current_algo_state)

                if self.current_algo_state.get("type") in ["completed", "completed_disconnected", "error"]:
                    self.run_animated_button.config(text="Run Animated")
                    self.run_animated_button.config(state=tk.DISABLED) # Algo finished
                    self.step_button.config(state=tk.DISABLED)
                    self.algorithm_generator = None
                    self._animation_job = None
                else:
                    # Schedule next step
                    self._animation_job = self.master.after(self.animation_delay_var.get(), self._animate_step)
            else: # Generator exhausted
                self._update_text_results("Animation complete (no more steps).", append=True)
                self.run_animated_button.config(text="Run Animated")
                self.run_animated_button.config(state=tk.DISABLED)
                self.step_button.config(state=tk.DISABLED)
                self.algorithm_generator = None
                self._animation_job = None
        except StopIteration:
            self._update_text_results("Animation finished.", append=True)
            self.run_animated_button.config(text="Run Animated")
            self.run_animated_button.config(state=tk.DISABLED)
            self.step_button.config(state=tk.DISABLED)
            self.algorithm_generator = None
            self._animation_job = None
        except Exception as e:
            messagebox.showerror("Animation Error", f"Error during animation: {e}\n{traceback.format_exc()}")
            self.run_animated_button.config(text="Run Animated")
            # Consider re-enabling step button if generator might still be valid, or disable all
            self.step_button.config(state=tk.DISABLED)
            self.run_animated_button.config(state=tk.DISABLED)
            self.algorithm_generator = None
            self._animation_job = None


    def measure_algorithm_performance(self, algo_func, graph_instance, start_node_perf=0):
        """Measures execution time of a non-stepwise algorithm function."""
        try:
            if algo_func == Algorithms.kruskal or algo_func == Algorithms.floyd_warshall :
                start_time = time.perf_counter()
                algo_func(graph_instance)
                end_time = time.perf_counter()
            elif algo_func == Algorithms.prim: # Prim needs a start node
                 if graph_instance.num_nodes == 0: return None # Cannot run on empty graph
                 valid_start_node = start_node_perf if 0 <= start_node_perf < graph_instance.num_nodes else 0
                 start_time = time.perf_counter()
                 algo_func(graph_instance, valid_start_node)
                 end_time = time.perf_counter()
            else: # DFS, BFS, Dijkstra need a start node
                if graph_instance.num_nodes == 0: return None # Cannot run on empty graph
                valid_start_node = start_node_perf if 0 <= start_node_perf < graph_instance.num_nodes else 0
                start_time = time.perf_counter()
                algo_func(graph_instance, valid_start_node)
                end_time = time.perf_counter()

            return end_time - start_time
        except Exception as e:
            print(f"Error measuring performance for {algo_func.__name__}: {e}")
            return None # Indicate failure


    def run_performance_analysis_gui(self):
        self._update_text_results("Starting performance analysis...", append=False)
        self.master.update_idletasks() # Update GUI to show message

        try:
            node_sizes_str = self.node_sizes_var.get()
            edge_factor = self.edge_factor_var.get()
            node_sizes = [int(s.strip()) for s in node_sizes_str.split(',') if s.strip().isdigit()]

            if not node_sizes:
                messagebox.showerror("Input Error", "Please enter valid comma-separated node sizes.")
                return
            if edge_factor <= 0:
                messagebox.showerror("Input Error", "Edge factor must be positive.")
                return

            self.performance_data.clear() # Reset data for new analysis

            algorithms_to_test = {
                "DFS": Algorithms.dfs,
                "BFS": Algorithms.bfs,
                "Dijkstra": Algorithms.dijkstra,
                "Prim": Algorithms.prim,
                "Kruskal": Algorithms.kruskal,
                "Floyd-Warshall": Algorithms.floyd_warshall
            }
            selected_algo_name = self.algo_var.get()

            if selected_algo_name != "Compare All (Performance)":
                if selected_algo_name in algorithms_to_test:
                    algo_func = algorithms_to_test[selected_algo_name]
                    self.performance_data[selected_algo_name] = []
                    for size in node_sizes:
                        num_edges_perf = int(size * edge_factor)
                        # Determine if weighted/directed based on the specific algo for performance test
                        is_weighted_perf = selected_algo_name in ["Dijkstra", "Prim", "Kruskal", "Floyd-Warshall"]
                        is_directed_perf = selected_algo_name in ["Dijkstra", "Floyd-Warshall"]

                        graph_perf = generate_random_graph(size, num_edges_perf, weighted=is_weighted_perf, directed=is_directed_perf)
                        if not graph_perf or graph_perf.num_nodes == 0:
                            print(f"Skipping size {size} for {selected_algo_name}, graph not generated.")
                            self.performance_data[selected_algo_name].append((size, float('nan'))) # Mark as NaN if graph gen fails
                            continue

                        # Pick a random start node for algos that need it, ensure it's valid
                        start_node_for_perf = random.randint(0, size - 1) if size > 0 else 0

                        time_taken = self.measure_algorithm_performance(algo_func, graph_perf, start_node_for_perf)
                        if time_taken is not None:
                            self.performance_data[selected_algo_name].append((size, time_taken))
                            self._update_text_results(f"{selected_algo_name} with {size} nodes, {num_edges_perf} edges: {time_taken:.6f}s", append=True)
                        else:
                            self.performance_data[selected_algo_name].append((size, float('nan'))) # Use NaN for failed measurement
                            self._update_text_results(f"{selected_algo_name} with {size} nodes: Measurement failed.", append=True)
                        self.master.update_idletasks()
                else:
                    messagebox.showinfo("Info", f"{selected_algo_name} is not set up for performance analysis via this button. Choose 'Compare All' or select a specific algorithm.")
                    return
            else: # "Compare All (Performance)"
                for algo_name_loop, algo_func_loop in algorithms_to_test.items():
                    self.performance_data[algo_name_loop] = []
                    self._update_text_results(f"\nTesting {algo_name_loop}...", append=True)
                    for size in node_sizes:
                        num_edges_perf = int(size * edge_factor)
                        is_weighted_perf = algo_name_loop in ["Dijkstra", "Prim", "Kruskal", "Floyd-Warshall"]
                        is_directed_perf = algo_name_loop in ["Dijkstra", "Floyd-Warshall"]

                        graph_perf = generate_random_graph(size, num_edges_perf, weighted=is_weighted_perf, directed=is_directed_perf)
                        if not graph_perf or graph_perf.num_nodes == 0 :
                            print(f"Skipping size {size} for {algo_name_loop}, graph not generated.")
                            self.performance_data[algo_name_loop].append((size, float('nan')))
                            continue

                        start_node_for_perf = random.randint(0, size - 1) if size > 0 else 0
                        time_taken = self.measure_algorithm_performance(algo_func_loop, graph_perf, start_node_for_perf)

                        if time_taken is not None:
                            self.performance_data[algo_name_loop].append((size, time_taken))
                            self._update_text_results(f"  {size} nodes, {num_edges_perf} edges: {time_taken:.6f}s", append=True)
                        else:
                            self.performance_data[algo_name_loop].append((size, float('nan')))
                            self._update_text_results(f"  {size} nodes: Measurement failed.", append=True)
                        self.master.update_idletasks()


            self._plot_performance(selected_algo_name if selected_algo_name != "Compare All (Performance)" else None)
            self._update_text_results("\nPerformance analysis complete.", append=True)

        except ValueError:
            messagebox.showerror("Input Error", "Invalid input for node sizes or edge factor.")
        except Exception as e:
            messagebox.showerror("Performance Analysis Error", f"An error occurred: {e}\n{traceback.format_exc()}")
            self._update_text_results(f"Performance analysis failed: {e}", append=True)

    def _plot_performance(self, algo_name_filter=None):
        self.ax_perf.clear()
        self.ax_perf.set_title("Performance Analysis")
        self.ax_perf.set_xlabel("Number of Nodes (Size)")
        self.ax_perf.set_ylabel("Time (seconds)")
        self.ax_perf.grid(True, which="both", linestyle='--', linewidth=0.5)
        legend_handles = []
        plotted_anything = False

        data_to_plot_on_graph = {}
        if algo_name_filter and algo_name_filter in self.performance_data:
            data_to_plot_on_graph[algo_name_filter] = self.performance_data[algo_name_filter]
        elif not algo_name_filter: # Plot all if no filter (e.g. for "Compare All")
            data_to_plot_on_graph = self.performance_data


        for name, data_points in data_to_plot_on_graph.items():
            if not data_points:
                print(f"Plot: No data points for {name}.")
                continue

            # Filter out NaN times (where t != t is true for NaN) and prepare for zipping
            valid_data_points = [(s, t) for s, t in data_points if not (isinstance(t, float) and t != t)]

            if not valid_data_points:
                print(f"Plot: No valid (non-NaN) data points for {name} after filtering.")
                self._update_text_results(f"No valid data points to plot for {name}.", append=True)
                continue # Skip this algorithm if no valid points

            try:
                # This is the critical part: ensure valid_data_points is not empty before zip
                sizes, times = zip(*valid_data_points)
            except ValueError: # Should be caught by "if not valid_data_points" but as safety
                print(f"Plot: ValueError during zip for {name}. valid_data_points might be unexpectedly empty.")
                self._update_text_results(f"Error plotting {name}: Could not unpack data points.", append=True)
                continue # Skip this algorithm

            if sizes and times: # Check if zip produced non-empty tuples
                line, = self.ax_perf.plot(sizes, times, marker='o', linestyle='-', label=name)
                legend_handles.append(line)
                plotted_anything = True
            else:
                print(f"Plot: Sizes or times were empty for {name} after zip (data was: {valid_data_points}).")


        if plotted_anything and legend_handles:
            self.ax_perf.legend(handles=legend_handles)
        elif not any(data_to_plot_on_graph.values()): # If no data was even considered for plotting
             self.ax_perf.text(0.5, 0.5, "No performance data generated.",
                              ha='center', va='center', transform=self.ax_perf.transAxes)
        elif not plotted_anything: # Data existed but nothing could be plotted (e.g. all NaN)
            self.ax_perf.text(0.5, 0.5, "No valid performance data to display.",
                              ha='center', va='center', transform=self.ax_perf.transAxes)


        self.fig_perf.tight_layout()
        self.canvas_perf.draw()


if __name__ == '__main__':
    root = tk.Tk()
    app = GraphApp(root)
    root.mainloop()