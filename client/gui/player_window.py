import requests
import tkinter as tk
from tkinter import messagebox
from gui.play_maze_window import PlayMazeWindow


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
            if response.status_code != 200:
                messagebox.showerror("Ошибка сервера", response.text)
                return
            mazes = response.json()
        except Exception as e:
            messagebox.showerror("Ошибка соединения", str(e))
            return

        if not mazes:
            tk.Label(self.container, text="Нет доступных лабиринтов",
                 font=("Arial", 12)).pack(pady=20)
            return

        for m in mazes:
            card = tk.Frame(
                self.container,
                bg="white",
                bd=2,
                relief=tk.RAISED,
                padx=20,
                pady=15
            )
            card.pack(fill=tk.X, padx=20, pady=10)

            title = tk.Label(
                card,
                text=m["name"],
                font=("Arial", 12, "bold"),
                bg="white"
            )
            title.pack(anchor="w")

            size = tk.Label(
                card,
                text=f"{m['height']} x {m['width']}",
                bg="white"
            )
            size.pack(anchor="w")

            # Кликабельность
            card.bind("<Button-1>",
                  lambda e, maze=m: self.play_maze(maze))
            title.bind("<Button-1>",
                   lambda e, maze=m: self.play_maze(maze))
            size.bind("<Button-1>",
                  lambda e, maze=m: self.play_maze(maze))

    def play_maze(self, maze):
        self.parent.show_frame(PlayMazeWindow, maze_data=maze, login=self.login)

    def logout(self):
        from gui.auth_window import AuthWindow
        self.parent.show_frame(AuthWindow)