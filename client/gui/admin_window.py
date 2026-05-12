import requests
import tkinter as tk
from tkinter import messagebox
from gui.create_maze_window import CreateMazeWindow


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
            if response.status_code != 200:
                messagebox.showerror("Ошибка сервера", response.text)
                return
            mazes = response.json()
        except Exception as e:
            messagebox.showerror("Ошибка соединения", str(e))
            return

        if not mazes:
            tk.Label(self.container, text="Нет сохранённых лабиринтов",
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
                  lambda e, mid=m["id"]: self.confirm_delete(mid))
            title.bind("<Button-1>",
                   lambda e, mid=m["id"]: self.confirm_delete(mid))
            size.bind("<Button-1>",
                  lambda e, mid=m["id"]: self.confirm_delete(mid))

    def open_maze(self, maze):
        messagebox.showinfo("Информация", f"Лабиринт: {maze['name']}")

    def confirm_delete(self, maze_id):
        if messagebox.askyesno("Подтверждение", "Удалить этот лабиринт?"):
            requests.delete(
                f"http://127.0.0.1:5000/mazes/{maze_id}"
            )
            self.load_mazes()

    def create_maze(self):
        self.parent.show_frame(CreateMazeWindow, admin_id=None)

    def logout(self):
        from gui.auth_window import AuthWindow
        self.parent.show_frame(AuthWindow)