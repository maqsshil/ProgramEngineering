# gui/player_window.py
import tkinter as tk
from tkinter import messagebox
from gui.play_maze_window import PlayMazeWindow
from gui.help_window import HelpWindow
from gui.maze_canvas import MazeCanvas

class PlayerWindow(tk.Frame):
    def __init__(self, parent, db, user_id, login):
        super().__init__(parent, bg="#e0e0e0")
        self.parent = parent
        self.db = db
        self.user_id = user_id
        self.login = login
        self.create_widgets()
        self.load_mazes()
    
    def create_widgets(self):
        top = tk.Frame(self, bg="#e0e0e0")
        top.pack(fill=tk.X, padx=20, pady=10)
        tk.Label(top, text=f"Игрок: {self.login}", font=("Arial",14,"bold"), bg="#e0e0e0").pack(side=tk.LEFT)
        tk.Button(top, text="?", command=self.show_help, width=3, bg="#cccccc", fg="#000000", font=("Arial", 10), relief=tk.RAISED, bd=2).pack(side=tk.RIGHT, padx=5)
        tk.Button(top, text="Выйти", command=self.logout, bg="#cccccc", fg="#000000", font=("Arial", 10), relief=tk.RAISED, bd=2).pack(side=tk.RIGHT, padx=5)
        self.canvas_container = tk.Frame(self, bg="#e0e0e0")
        self.canvas_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        self.canvas = tk.Canvas(self.canvas_container, bg="#e0e0e0")
        scroll = tk.Scrollbar(self.canvas_container, orient=tk.VERTICAL, command=self.canvas.yview)
        self.scrollable = tk.Frame(self.canvas, bg="#e0e0e0")
        self.scrollable.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.create_window((0,0), window=self.scrollable, anchor="nw")
        self.canvas.configure(yscrollcommand=scroll.set)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas_container.bind("<Configure>", self._on_resize)
    
    def _on_resize(self, event):
        self.canvas.itemconfig(1, width=event.width)
    
    def load_mazes(self):
        for w in self.scrollable.winfo_children():
            w.destroy()
        mazes = self.db.load_all_mazes()
        if not mazes:
            tk.Label(self.scrollable, text="Нет доступных лабиринтов", font=("Arial",12), bg="#e0e0e0").pack(pady=20)
            return
        cols = 2
        row = col = 0
        for m in mazes:
            frame = tk.Frame(self.scrollable, relief=tk.RAISED, bd=2, bg="white", padx=10, pady=10)
            frame.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
            prev = MazeCanvas(frame, m['map'], theme='default', cell_size=6, width=m['width']*6, height=m['height']*6, bg="white")
    
            tk.Label(frame, text=f"{m['name']}\n{m['height']}x{m['width']}", bg="white", font=("Arial",9)).pack(pady=5)
            frame.bind("<Button-1>", lambda e, mdata=m: self.play_maze(mdata))
            prev.bind("<Button-1>", lambda e, mdata=m: self.play_maze(mdata))
            col += 1
            if col >= cols:
                col = 0; row += 1
        for i in range(cols):
            self.scrollable.grid_columnconfigure(i, weight=1)
    
    def play_maze(self, maze):
        self.parent.show_frame(PlayMazeWindow, maze_data=maze)
    
    def show_help(self):
        HelpWindow(self)
    
    def logout(self):
        from gui.auth_window import AuthWindow
        self.parent.show_frame(AuthWindow)