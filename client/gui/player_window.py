import requests
import tkinter as tk
from tkinter import messagebox
from gui.play_maze_window import PlayMazeWindow
from gui.help_window import HelpWindow
from gui.maze_canvas import MazeCanvas


class PlayerWindow(tk.Frame):
    def __init__(self, parent, user_id, login):
        super().__init__(parent, bg="#e0e0e0")
        self.parent = parent
        self.login = login
        self.create_widgets()
        self.load_mazes()

    def create_widgets(self):
        tk.Label(self, text=f"Игрок: {self.login}").pack()

        tk.Button(self, text="Выйти",
                  command=self.logout).pack()

        self.container = tk.Frame(self)
        self.container.pack(fill=tk.BOTH, expand=True)

    def load_mazes(self):
        for w in self.container.winfo_children():
            w.destroy()

        try:
            response = requests.get("http://127.0.0.1:5000/mazes")
            mazes = response.json()
        except Exception as e:
            messagebox.showerror("Ошибка соединения", str(e))
            return

        if not mazes:
            tk.Label(self.container, text="Нет доступных лабиринтов",
                     font=("Arial", 12)).pack(pady=20)
            return

        cols = 2
        row = col = 0

        for m in mazes:
            card = tk.Frame(
                self.container,
                relief=tk.RAISED,
                bd=2,
                bg="white",
                padx=10,
                pady=10
            )
            card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")

            cell = 4  # уменьшенный размер

            preview = MazeCanvas(
                card,
                m["map"],
                theme="default",
                cell_size=cell,
                width=m["width"] * cell,
                height=m["height"] * cell,
                bg="white"
            )

            preview.unbind("<Configure>")  # отключаем авто‑resize
            preview.pack()

            tk.Label(
                card,
                text=f"{m['name']}\n{m['height']}x{m['width']}",
                bg="white",
                font=("Arial", 9)
            ).pack(pady=5)

            card.bind("<Button-1>",
                  lambda e, maze=m: self.play_maze(maze))
            preview.bind("<Button-1>",
                     lambda e, maze=m: self.play_maze(maze))

            col += 1
            if col >= cols:
                col = 0
                row += 1

        for i in range(cols):
            self.container.grid_columnconfigure(i, weight=1)

    def play_maze(self, maze):
        self.parent.show_frame(PlayMazeWindow, maze_data=maze)

    def logout(self):
        from gui.auth_window import AuthWindow
        self.parent.show_frame(AuthWindow)