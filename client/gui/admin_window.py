import requests
import tkinter as tk
from tkinter import messagebox
from gui.create_maze_window import CreateMazeWindow
from gui.help_window import HelpWindow
from gui.maze_canvas import MazeCanvas


class AdminWindow(tk.Frame):
    CARD_WIDTH = 240
    CARD_HEIGHT = 320
    PREVIEW_SIZE = 200
    MAX_COLS = 5

    def __init__(self, parent, user_id, login):
        super().__init__(parent, bg="#f0f0f0")
        self.parent = parent
        self.login = login
        self.create_widgets()
        self.load_mazes()
        self.bind("<Configure>", self.on_resize)

    def create_widgets(self):
        self.top_bar = tk.Frame(self, bg="#e8e8e8", height=70)
        self.top_bar.pack(fill=tk.X)

        self.top_bar.grid_columnconfigure(0, weight=1)
        self.top_bar.grid_columnconfigure(1, weight=1)
        self.top_bar.grid_columnconfigure(2, weight=1)

        tk.Label(self.top_bar, text=f"Администратор: {self.login}", font=("Arial", 14, "bold"), bg="#e8e8e8").grid(row=0, column=0, sticky="w", padx=20)

        tk.Button(self.top_bar, text="Создать лабиринт", font=("Arial", 12, "bold"), width=18, height=2,
                  relief=tk.RAISED, bd=1, bg="#e0e0e0",
                  command=self.create_maze).grid(row=0, column=1)

        btn_frame = tk.Frame(self.top_bar, bg="#e8e8e8")
        btn_frame.grid(row=0, column=2, sticky="e", padx=20)

        tk.Button(btn_frame, text="?", font=("Arial", 12, "bold"), width=4, height=2,
                  relief=tk.RAISED, bd=1, bg="#e0e0e0",
                  command=self.show_help).pack(side=tk.LEFT, padx=8)

        tk.Button(btn_frame, text="Выйти", font=("Arial", 12, "bold"), width=10, height=2,
                  relief=tk.RAISED, bd=1, bg="#e0e0e0",
                  command=self.logout).pack(side=tk.LEFT, padx=8)

        self.list_container = tk.Frame(self, bg="#f0f0f0")
        self.list_container.pack(fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(self.list_container, bg="#f0f0f0", highlightthickness=0)
        self.scrollbar = tk.Scrollbar(self.list_container, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.cards_frame = tk.Frame(self.canvas, bg="#f0f0f0")
        self.canvas_window = self.canvas.create_window((0, 0), window=self.cards_frame, anchor="n")

        self.cards_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind_all("<MouseWheel>", lambda e: self.canvas.yview_scroll(int(-1*(e.delta/120)), "units"))
        self.canvas.bind("<Configure>", self.on_canvas_configure)

    def on_canvas_configure(self, event):
        self.canvas.itemconfig(self.canvas_window, width=event.width)

    def load_mazes(self):
        for w in self.cards_frame.winfo_children():
            w.destroy()

        try:
            response = requests.get("http://127.0.0.1:5000/mazes")
            mazes = response.json()
        except Exception as e:
            messagebox.showerror("Ошибка соединения", str(e))
            return

        self.mazes = mazes
        self.render_cards()

    def render_cards(self):
        for w in self.cards_frame.winfo_children():
            w.destroy()

        if not self.mazes:
            tk.Label(self.cards_frame, text="Нет сохранённых лабиринтов", font=("Arial", 14),
                     bg="#f0f0f0").pack(pady=40)
            return

        width = self.winfo_width()
        cols = min(self.MAX_COLS, max(1, width // (self.CARD_WIDTH + 30)))

        row = 0
        col = 0

        for maze in self.mazes:
            card = self.create_card(self.cards_frame, maze)
            card.grid(row=row, column=col, padx=20, pady=20)

            col += 1
            if col >= cols:
                col = 0
                row += 1

        for i in range(cols):
            self.cards_frame.grid_columnconfigure(i, weight=1)

    def create_card(self, parent, maze):
        card = tk.Frame(parent, width=self.CARD_WIDTH, height=self.CARD_HEIGHT,
                        bg="white", relief=tk.RAISED, bd=2)
        card.grid_propagate(False)

        tk.Label(card, text=maze["name"], font=("Arial", 12, "bold"),
                 bg="white").pack(pady=(10, 5))

        tk.Label(card, text=f"{maze['height']} x {maze['width']}",
                 font=("Arial", 11), bg="white").pack()

        INNER_PADDING = 15

        preview_frame = tk.Frame(card,
                                 width=self.PREVIEW_SIZE + INNER_PADDING*2,
                                 height=self.PREVIEW_SIZE + INNER_PADDING*2,
                                 bg="white")
        preview_frame.pack(pady=20)
        preview_frame.pack_propagate(False)

        cell = min(self.PREVIEW_SIZE // maze["width"],
                   self.PREVIEW_SIZE // maze["height"])

        canvas_width = maze["width"] * cell
        canvas_height = maze["height"] * cell

        preview = MazeCanvas(
            preview_frame, 
            maze["map"],
            cell_size=cell,
            width=canvas_width,
            height=canvas_height,
            theme="preview",
            bg="white",
            highlightthickness=0,
            bd=0
        )

        preview.unbind("<Configure>")

        preview.place(x=INNER_PADDING + (self.PREVIEW_SIZE - canvas_width)//2,
                      y=INNER_PADDING + (self.PREVIEW_SIZE - canvas_height)//2)

        card.bind("<Button-1>",
                  lambda e, mid=maze["id"]: self.confirm_delete(mid))
        preview.bind("<Button-1>",
                     lambda e, mid=maze["id"]: self.confirm_delete(mid))

        return card

    def confirm_delete(self, maze_id):
        if messagebox.askyesno("Подтверждение", "Удалить этот лабиринт?"):
            requests.delete(f"http://127.0.0.1:5000/mazes/{maze_id}")
            self.load_mazes()

    def create_maze(self):
        self.parent.show_frame(CreateMazeWindow, admin_id=None)

    def show_help(self):
        HelpWindow(self)

    def logout(self):
        from gui.auth_window import AuthWindow
        self.parent.show_frame(AuthWindow)

    def on_resize(self, event):
        self.render_cards()