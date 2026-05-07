# gui/create_maze_window.py
import tkinter as tk
import requests
from tkinter import messagebox
from gui.maze_canvas import MazeCanvas
from algorithms.generation import recursive_backtracker, kruskal
from algorithms.maze_utils import auto_place_entrance_exit, has_isolated_areas, count_dead_ends

class CreateMazeWindow(tk.Frame):
    def __init__(self, parent, admin_id):
        super().__init__(parent, bg="#f0f0f0")
        self.parent = parent
        self.admin_id = admin_id
        self.maze = None
        self.entry = None
        self.exit = None
        self.theme = "default"
        self.height = 5
        self.width = 5
        self.current_step = 1
        self.pending = None
        
        self.create_layout()
        self.init_canvas()
    
    def create_layout(self):
        # Левая панель с настройками
        self.left = tk.Frame(self, bg="#f0f0f0", width=340)
        self.left.pack(side=tk.LEFT, fill=tk.BOTH, padx=10, pady=10, expand=False)
        
        # Правая панель с холстом
        self.right = tk.Frame(self, bg="#ffffff", relief=tk.SUNKEN, bd=2)
        self.right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Заголовок
        self.title_label = tk.Label(self.left, text="Создание лабиринта", font=("Arial", 14, "bold"), bg="#f0f0f0")
        self.title_label.pack(pady=10)
        
        # Canvas с прокруткой для настроек
        self.settings_canvas = tk.Canvas(self.left, bg="#f0f0f0", highlightthickness=0)
        self.settings_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = tk.Scrollbar(self.left, orient=tk.VERTICAL, command=self.settings_canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.settings_canvas.configure(yscrollcommand=scrollbar.set)
        
        # Фрейм внутри Canvas для содержимого
        self.settings_frame = tk.Frame(self.settings_canvas, bg="#f0f0f0")
        self.settings_canvas.create_window((0, 0), window=self.settings_frame, anchor="nw", width=self.left.winfo_width())
        
        self.settings_frame.bind("<Configure>", self._on_frame_configure)
        self.left.bind("<Configure>", self._on_left_resize)
        
        # Блок 1: Параметры
        self.block1_frame = tk.Frame(self.settings_frame, bg="#f0f0f0", relief=tk.RIDGE, bd=1)
        self.block1_frame.pack(fill=tk.X, pady=5, padx=5)
        tk.Label(self.block1_frame, text="Шаг 1: Параметры лабиринта", font=("Arial", 10, "bold"), bg="#f0f0f0").pack(anchor="w", padx=5, pady=2)
        
        tk.Label(self.block1_frame, text="Тема оформления:", bg="#f0f0f0").pack(anchor="w", padx=10)
        self.theme_var = tk.StringVar(value="default")
        theme_frame = tk.Frame(self.block1_frame, bg="#f0f0f0")
        theme_frame.pack(anchor="w", padx=20)
        for k,v in [("default","Стандартная"),("dark","Тёмная"),("forest","Лесная"),("sand","Песчаная")]:
            tk.Radiobutton(theme_frame, text=v, variable=self.theme_var, value=k, bg="#f0f0f0").pack(anchor="w")
        
        size_frame = tk.Frame(self.block1_frame, bg="#f0f0f0")
        size_frame.pack(pady=5, anchor="w", padx=10)
        tk.Label(size_frame, text="Высота (5-25, нечёт):").grid(row=0, column=0, sticky="w")
        self.h_entry = tk.Entry(size_frame, width=5)
        self.h_entry.insert(0, "5")
        self.h_entry.grid(row=0, column=1, padx=5)
        
        tk.Label(size_frame, text="Ширина (5-25, нечёт):").grid(row=1, column=0, sticky="w")
        self.w_entry = tk.Entry(size_frame, width=5)
        self.w_entry.insert(0, "5")
        self.w_entry.grid(row=1, column=1, padx=5)
        
        self.apply_btn = tk.Button(self.block1_frame, text="Применить", command=self.apply_step1, bg="#cccccc", fg="#000000", font=("Arial", 10), relief=tk.RAISED, bd=2)
        self.apply_btn.pack(pady=10)
        
        # Блок 2: Вход/выход
        self.block2_frame = tk.Frame(self.settings_frame, bg="#f0f0f0", relief=tk.RIDGE, bd=1)
        self.block2_frame.pack(fill=tk.X, pady=5, padx=5)
        tk.Label(self.block2_frame, text="Шаг 2: Вход и выход", font=("Arial", 10, "bold"), bg="#f0f0f0").pack(anchor="w", padx=5, pady=2)
        
        self.place_method = tk.StringVar(value="auto")
        tk.Radiobutton(self.block2_frame, text="Автоматическая расстановка", variable=self.place_method, value="auto", bg="#f0f0f0").pack(anchor="w", padx=20)
        self.manual_radio = tk.Radiobutton(self.block2_frame, text="Ручная расстановка (клик по периметру)", variable=self.place_method, value="manual", bg="#f0f0f0")
        self.manual_radio.pack(anchor="w", padx=20)
        
        self.entry_label = tk.Label(self.block2_frame, text="Вход: не выбран", bg="#f0f0f0")
        self.entry_label.pack(anchor="w", padx=20, pady=(5,0))
        self.exit_label = tk.Label(self.block2_frame, text="Выход: не выбран", bg="#f0f0f0")
        self.exit_label.pack(anchor="w", padx=20)
        
        self.apply_btn2 = tk.Button(self.block2_frame, text="Применить", command=self.apply_step2, bg="#cccccc", fg="#000000", font=("Arial", 10), relief=tk.RAISED, bd=2)
        self.apply_btn2.pack(pady=10)
        
        # Блок 3: Алгоритм
        self.block3_frame = tk.Frame(self.settings_frame, bg="#f0f0f0", relief=tk.RIDGE, bd=1)
        self.block3_frame.pack(fill=tk.X, pady=5, padx=5)
        tk.Label(self.block3_frame, text="Шаг 3: Алгоритм генерации", font=("Arial", 10, "bold"), bg="#f0f0f0").pack(anchor="w", padx=5, pady=2)
        
        self.algo_var = tk.StringVar(value="backtracker")
        tk.Radiobutton(self.block3_frame, text="Рекурсивный бэктрекинг", variable=self.algo_var, value="backtracker", bg="#f0f0f0").pack(anchor="w", padx=20)
        tk.Radiobutton(self.block3_frame, text="Алгоритм Краскала", variable=self.algo_var, value="kruskal", bg="#f0f0f0").pack(anchor="w", padx=20)
        
        self.generate_btn = tk.Button(self.block3_frame, text="Сгенерировать", command=self.generate, bg="#cccccc", fg="#000000", font=("Arial", 10), relief=tk.RAISED, bd=2)
        self.generate_btn.pack(pady=10)
        
        # Блок 4: Сохранение
        self.block4_frame = tk.Frame(self.settings_frame, bg="#f0f0f0", relief=tk.RIDGE, bd=1)
        self.block4_frame.pack(fill=tk.X, pady=5, padx=5)
        tk.Label(self.block4_frame, text="Шаг 4: Сохранение", font=("Arial", 10, "bold"), bg="#f0f0f0").pack(anchor="w", padx=5, pady=2)
        
        tk.Label(self.block4_frame, text="Название лабиринта:", bg="#f0f0f0").pack(anchor="w", padx=10, pady=(5,0))
        self.name_entry = tk.Entry(self.block4_frame, width=25)
        self.name_entry.pack(pady=5, padx=10)
        
        btn_frame = tk.Frame(self.block4_frame, bg="#f0f0f0")
        btn_frame.pack(pady=10)
        tk.Button(btn_frame, text="Сохранить", command=self.save, bg="#cccccc", fg="#000000", font=("Arial", 10), relief=tk.RAISED, bd=2).pack(side=tk.LEFT, padx=10)
        tk.Button(btn_frame, text="Отмена", command=self.cancel, bg="#cccccc", fg="#000000", font=("Arial", 10), relief=tk.RAISED, bd=2).pack(side=tk.LEFT, padx=10)
        
        # Изначально блоки 2,3,4 отключены
        self.enable_block2(False)
        self.enable_block3(False)
        self.enable_block4(False)
    
    def _on_frame_configure(self, event):
        self.settings_canvas.configure(scrollregion=self.settings_canvas.bbox("all"))
    
    def _on_left_resize(self, event):
        self.settings_canvas.itemconfig(1, width=event.width - 20)
    
    def init_canvas(self):
        temp_maze = [[1]]
        self.canvas = MazeCanvas(self.right, temp_maze, theme=self.theme, cell_size=25, bg="white")
        self.canvas.pack(fill=tk.BOTH, expand=True)
    
    def enable_block2(self, enabled):
        state = tk.NORMAL if enabled else tk.DISABLED
        self.manual_radio.config(state=state)
        self.apply_btn2.config(state=state)
    
    def enable_block3(self, enabled):
        state = tk.NORMAL if enabled else tk.DISABLED
        self.generate_btn.config(state=state)
        for child in self.block3_frame.winfo_children():
            if isinstance(child, tk.Radiobutton):
                child.config(state=state)
    
    def enable_block4(self, enabled):
        state = tk.NORMAL if enabled else tk.DISABLED
        self.name_entry.config(state=state)
        for child in self.block4_frame.winfo_children():
            if isinstance(child, tk.Button):
                child.config(state=state)
    
    def apply_step1(self):
        try:
            h = int(self.h_entry.get())
            w = int(self.w_entry.get())
        except:
            messagebox.showerror("Ошибка", "Введите целые числа")
            return
        if h < 5 or h > 25 or w < 5 or w > 25 or h % 2 == 0 or w % 2 == 0:
            messagebox.showerror("Ошибка", "Размеры должны быть нечётными от 5 до 25")
            return
        
        self.height = h
        self.width = w
        self.theme = self.theme_var.get()
        
        self.maze = [[1] * self.width for _ in range(self.height)]
        
        self.canvas.destroy()
        self.canvas = MazeCanvas(self.right, self.maze, theme=self.theme, cell_size=25, bg="white")
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        self.enable_block2(True)
        
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.pending = None
        self.entry = self.exit = None
        self.entry_label.config(text="Вход: не выбран")
        self.exit_label.config(text="Выход: не выбран")
    
    def on_canvas_click(self, event):
        if self.place_method.get() != "manual":
            return
        if not self.canvas or self.maze is None:
            return
        
        x = event.x // self.canvas.cell_size
        y = event.y // self.canvas.cell_size
        
        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            return
        
        on_perimeter = (x == 0 or x == self.width-1 or y == 0 or y == self.height-1)
        is_corner = (x == 0 and y == 0) or (x == 0 and y == self.height-1) or (x == self.width-1 and y == 0) or (x == self.width-1 and y == self.height-1)
        
        if not on_perimeter or is_corner:
            messagebox.showerror("Ошибка", "Вход/выход только на периметре (не в углах)")
            return
        
        if self.pending is None:
            self.entry = (x, y)
            self.entry_label.config(text=f"Вход: ({x}, {y})")
            self.pending = "exit"
            messagebox.showinfo("Ручная расстановка", "Теперь выберите клетку для выхода")
        elif self.pending == "exit":
            if (x, y) == self.entry:
                messagebox.showerror("Ошибка", "Вход и выход не могут совпадать")
                return
            self.exit = (x, y)
            self.exit_label.config(text=f"Выход: ({x}, {y})")
            self.pending = None
            messagebox.showinfo("Ручная расстановка", "Выход выбран. Нажмите 'Применить'")
    
    def apply_step2(self):
        if self.place_method.get() == "auto":
            self.entry, self.exit = auto_place_entrance_exit(self.maze)
        else:
            if self.entry is None or self.exit is None:
                messagebox.showerror("Ошибка", "Сначала выберите вход и выход вручную")
                return
            if abs(self.entry[0] - self.exit[0]) + abs(self.entry[1] - self.exit[1]) <= 1:
                messagebox.showerror("Ошибка", "Вход и выход не должны быть соседними")
                return
        
        self.maze[self.entry[1]][self.entry[0]] = 0
        self.maze[self.exit[1]][self.exit[0]] = 0
        
        self.canvas.maze = self.maze
        self.canvas.entry = self.entry
        self.canvas.exit = self.exit
        self.canvas.draw_maze()
        
        self.enable_block3(True)
    
    def generate(self):
        if self.algo_var.get() == "backtracker":
            self.maze = recursive_backtracker(self.height, self.width)
        else:
            self.maze = kruskal(self.height, self.width)
        
        # Восстанавливаем вход и выход
        self.maze[self.entry[1]][self.entry[0]] = 0
        self.maze[self.exit[1]][self.exit[0]] = 0
        
        # Проверка на изолированные зоны
        if has_isolated_areas(self.maze):
            messagebox.showerror("Ошибка", "Изолированные зоны! Перегенерируйте")
            return
        
        dead = count_dead_ends(self.maze)
        self.canvas.maze = self.maze
        self.canvas.draw_maze()
        messagebox.showinfo("Успех", f"Лабиринт сгенерирован. Тупиков: {dead}")
        
        self.enable_block4(True)
    
    def save(self):
        name = self.name_entry.get().strip()
        if not name:
            messagebox.showerror("Ошибка", "Введите название")
            return

        try:
            response = requests.post(
                "http://127.0.0.1:5000/mazes",
                json={
                "name": name,
                "height": self.height,
                "width": self.width,
                "maze_map": self.maze,
                "entry": self.entry,
                "exit": self.exit
            }
        )

            data = response.json()

            if data.get("status") == "success":
                messagebox.showinfo("Успех", "Лабиринт сохранён")
                self.cancel()
            else:
                messagebox.showerror("Ошибка", "Ошибка сохранения")

        except Exception as e:
            messagebox.showerror("Ошибка соединения", str(e))
    
    def cancel(self):
        from gui.admin_window import AdminWindow
        self.parent.show_frame(AdminWindow, user_id=self.admin_id, login="admin")