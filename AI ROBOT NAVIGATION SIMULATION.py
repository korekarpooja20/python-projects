import tkinter as tk
from tkinter import messagebox
from collections import deque
import time

ROWS, COLS = 12, 16
CELL = 36
START = (0, 0)
GOAL = (ROWS - 1, COLS - 1)

# 1 = wall, 0 = free cell
DEFAULT_WALLS = {
    (0, 4), (1, 4), (2, 4), (3, 4), (4, 4),
    (5, 2), (5, 3), (5, 4), (5, 5), (5, 6),
    (2, 8), (3, 8), (4, 8), (5, 8), (6, 8),
    (7, 8), (8, 8), (8, 9), (8, 10), (8, 11),
    (3, 12), (4, 12), (5, 12), (6, 12),
    (9, 3), (10, 3), (10, 4), (10, 5), (10, 6),
}

class RobotNavigationApp:
    def __init__(self, root):
        self.root = root
        self.root.title("AI Robot Navigation Simulator — BFS & DFS")
        self.root.resizable(False, False)
        self.walls = set(DEFAULT_WALLS)
        self.path = []
        self.visited = []
        self.algorithm = "BFS"
        self.cell_items = {}
        self.draw_ui()
        self.draw_grid()

    def draw_ui(self):
        header = tk.Label(self.root, text="AI Robot Navigation Simulator",
                          font=("Arial", 17, "bold"), pady=8)
        header.pack()
        subtitle = tk.Label(self.root, text="Search algorithms: Breadth-First Search (BFS) and Depth-First Search (DFS)",
                            font=("Arial", 10))
        subtitle.pack()

        controls = tk.Frame(self.root, pady=8)
        controls.pack()
        tk.Button(controls, text="Find Path with BFS", command=lambda: self.solve("BFS"),
                  width=18, bg="#d8ecff").grid(row=0, column=0, padx=5)
        tk.Button(controls, text="Find Path with DFS", command=lambda: self.solve("DFS"),
                  width=18, bg="#ffe7c2").grid(row=0, column=1, padx=5)
        tk.Button(controls, text="Reset", command=self.reset, width=12).grid(row=0, column=2, padx=5)
        tk.Button(controls, text="Clear Walls", command=self.clear_walls, width=12).grid(row=0, column=3, padx=5)

        self.canvas = tk.Canvas(self.root, width=COLS*CELL, height=ROWS*CELL,
                                bg="white", highlightthickness=1, highlightbackground="#555")
        self.canvas.pack(padx=12, pady=5)
        self.canvas.bind("<Button-1>", self.toggle_wall)

        legend = tk.Label(self.root, text="Green = Start   Red = Goal   Dark = Obstacle   Blue = Visited   Yellow = Path",
                          font=("Arial", 10), pady=5)
        legend.pack()
        self.status = tk.Label(self.root, text="Click empty cells to add/remove obstacles, then run BFS or DFS.",
                               font=("Arial", 10), pady=6)
        self.status.pack()

    def neighbors(self, node):
        r, c = node
        # Fixed ordering makes runs reproducible
        for nr, nc in ((r-1,c), (r,c+1), (r+1,c), (r,c-1)):
            nxt = (nr, nc)
            if 0 <= nr < ROWS and 0 <= nc < COLS and nxt not in self.walls:
                yield nxt

    def search(self, algorithm):
        frontier = deque([START]) if algorithm == "BFS" else [START]
        parent = {START: None}
        visited_order = []
        while frontier:
            current = frontier.popleft() if algorithm == "BFS" else frontier.pop()
            if current in visited_order:
                continue
            visited_order.append(current)
            if current == GOAL:
                break
            for nxt in self.neighbors(current):
                if nxt not in parent:
                    parent[nxt] = current
                    frontier.append(nxt)
        if GOAL not in parent:
            return None, visited_order
        path = []
        node = GOAL
        while node is not None:
            path.append(node)
            node = parent[node]
        path.reverse()
        return path, visited_order

    def solve(self, algorithm):
        self.algorithm = algorithm
        self.path, self.visited = [], []
        started = time.perf_counter()
        path, visited = self.search(algorithm)
        elapsed_ms = (time.perf_counter() - started) * 1000
        self.path, self.visited = path or [], visited
        self.draw_grid()
        if path:
            self.status.config(
                text=f"{algorithm}: Path found! Path length: {len(path)-1} moves | "
                     f"Visited cells: {len(visited)} | Search time: {elapsed_ms:.3f} ms")
        else:
            self.status.config(text=f"{algorithm}: No path found. Visited cells: {len(visited)}")
            messagebox.showinfo("No path", "No route exists. Try clearing or removing some obstacles.")

    def draw_grid(self):
        self.canvas.delete("all")
        for r in range(ROWS):
            for c in range(COLS):
                pos = (r, c)
                color = "white"
                if pos in self.walls:
                    color = "#333333"
                if pos in self.visited and pos not in (START, GOAL) and pos not in self.walls:
                    color = "#9ed0ff"
                if pos in self.path and pos not in (START, GOAL):
                    color = "#ffe66d"
                if pos == START:
                    color = "#54c878"
                elif pos == GOAL:
                    color = "#f06b6b"
                x1, y1 = c*CELL, r*CELL
                self.canvas.create_rectangle(x1, y1, x1+CELL, y1+CELL,
                                             fill=color, outline="#b8b8b8")
                if pos == START:
                    self.canvas.create_text(x1+CELL/2, y1+CELL/2, text="S", font=("Arial", 12, "bold"))
                elif pos == GOAL:
                    self.canvas.create_text(x1+CELL/2, y1+CELL/2, text="G", font=("Arial", 12, "bold"))

    def toggle_wall(self, event):
        c, r = event.x // CELL, event.y // CELL
        pos = (r, c)
        if not (0 <= r < ROWS and 0 <= c < COLS) or pos in (START, GOAL):
            return
        if pos in self.walls:
            self.walls.remove(pos)
        else:
            self.walls.add(pos)
        self.path, self.visited = [], []
        self.draw_grid()
        self.status.config(text="Obstacle map updated. Choose BFS or DFS to search again.")

    def reset(self):
        self.walls = set(DEFAULT_WALLS)
        self.path, self.visited = [], []
        self.draw_grid()
        self.status.config(text="Grid reset to the default map.")

    def clear_walls(self):
        self.walls.clear()
        self.path, self.visited = [], []
        self.draw_grid()
        self.status.config(text="All obstacles cleared. Choose BFS or DFS.")

if __name__ == "__main__":
    root = tk.Tk()
    app = RobotNavigationApp(root)
    root.mainloop()
