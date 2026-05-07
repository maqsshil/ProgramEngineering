import requests
import tkinter as tk
from tkinter import messagebox
from gui.create_maze_window import CreateMazeWindow
from gui.help_window import HelpWindow
from gui.maze_canvas import MazeCanvas


class AdminWindow(tk.Frame):
    def __init__(self, parent, user_id, login):
        super().__init__(parent, bg="#e0e0e0")
        self.parent = parent
        self.login = login
        self.create_widgets()
        self.load_mazes()

    def create_widgets(self):
        top = tk.Frame(self, bg="#e0e0e0")
        top.pack(fill=tk.X, padx=20, pady=10)

        tk.Button(top, text="Создать лабиринт",
                  command=self.create_maze).pack(side=tk.RIGHT)

        tk.Button(top, text="Выйти",
                  command=self.logout).pack(side=tk.RIGHT)

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
            tk.Label(self.container, text="Нет сохранённых лабиринтов",
                 font=("Arial", 12)).pack(pady=20)
            return

        cols = 2
        row = col = 0

        for m in mazes:
            card = tk.Frame(self.container,
                relief=tk.RAISED,
                bd=2,
                bg="white",
                padx=10,
                pady=10)

            card.grid(row=row, column=col, padx=10, pady=10)

            cell = 4

            preview = MazeCanvas(
                card,
                m["map"],
                theme="default",
                cell_size=cell,
                width=m["width"] * cell,
                height=m["height"] * cell,
                bg="white"
            )

            preview.unbind("<Configure>")
            preview.pack()

            tk.Label(card,
                 text=f"{m['name']}\n{m['height']}x{m['width']}",
                 bg="white",
                 font=("Arial", 9)).pack(pady=5)

            # Удаление по клику
            card.bind("<Button-1>",
                  lambda e, mid=m["id"]: self.confirm_delete(mid))
            preview.bind("<Button-1>",
                     lambda e, mid=m["id"]: self.confirm_delete(mid))

            col += 1
            if col >= cols:
                col = 0
                row += 1

    def open_maze(self, maze):
        messagebox.showinfo("Информация", f"Лабиринт: {maze['name']}")

    def delete_maze(self, maze_id):
        requests.delete(f"http://127.0.0.1:5000/mazes/{maze_id}")
        self.load_mazes()

    def create_maze(self):
        self.parent.show_frame(CreateMazeWindow, admin_id=None)

    def logout(self):
        from gui.auth_window import AuthWindow
        self.parent.show_frame(AuthWindow)