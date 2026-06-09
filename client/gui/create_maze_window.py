# gui/create_maze_window.py
import tkinter as tk
import requests
from tkinter import messagebox
from gui.maze_canvas import MazeCanvas
from algorithms.generation import recursive_backtracker, kruskal
from algorithms.maze_utils import auto_place_entrance_exit, has_isolated_areas

class CreateMazeWindow(tk.Frame):
    def __init__(self, parent, admin_id):
        super().__init__(parent, bg="#f0f0f0")
        self.parent = parent
        self.admin_id = admin_id
        self.maze = None
        self.entry = None
        self.exit = None
        self.theme = "summer"
        self.height = 11
        self.width = 11
        self.current_step = 1
        self.pending = None
        self.replace_mode = "entry"
        
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
        self.theme_var = tk.StringVar(value="summer")
        theme_frame = tk.Frame(self.block1_frame, bg="#f0f0f0")
        theme_frame.pack(anchor="w", padx=20)
        for k,v in [("winter","Зима"), ("spring","Весна"), ("summer","Лето"), ("autumn","Осень")]:
            tk.Radiobutton(theme_frame, text=v, variable=self.theme_var, value=k, bg="#f0f0f0").pack(anchor="w")
        
        size_frame = tk.Frame(self.block1_frame, bg="#f0f0f0")
        size_frame.pack(pady=5, anchor="w", padx=10)
        tk.Label(size_frame, text="Высота (11-25, нечёт):").grid(row=0, column=0, sticky="w")
        self.h_entry = tk.Entry(size_frame, width=5)
        self.h_entry.insert(0, "11")
        self.h_entry.grid(row=0, column=1, padx=5)
        
        tk.Label(size_frame, text="Ширина (11-25, нечёт):").grid(row=1, column=0, sticky="w")
        self.w_entry = tk.Entry(size_frame, width=5)
        self.w_entry.insert(0, "11")
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
        
        # Нижняя панель
        bottom_frame = tk.Frame(self.settings_frame, bg="#f0f0f0")
        bottom_frame.pack(fill=tk.X, pady=20, padx=5)
        tk.Button(bottom_frame, text="Назад", width=14, height=2, command=self.cancel).pack(side=tk.LEFT, padx=10)
        self.save_btn = tk.Button(bottom_frame, text="Сохранить", width=14, height=2, command=self.open_save_dialog, state=tk.DISABLED)
        self.save_btn.pack(side=tk.LEFT, padx=10)

        # Изначально блоки 2,3,4 отключены
        self.enable_block2(False)
        self.enable_block3(False)
    
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

    def enable_save(self, enabled):
        state = tk.NORMAL if enabled else tk.DISABLED
        self.save_btn.config(state=state)
    
    def apply_step1(self):
        try:
            h = int(self.h_entry.get())
            w = int(self.w_entry.get())
        except:
            messagebox.showerror("Ошибка", "Введите целые числа")
            return

        original_h = h
        original_w = w

        h = max(11, min(25, h))
        w = max(11, min(25, w))

        if h % 2 == 0:
            h += 1 if h < 25 else -1
        if w % 2 == 0:
            w += 1 if w < 25 else -1

        if h != original_h or w != original_w:
            messagebox.showwarning("Коррекция размера",
                f"Размеры скорректированы до {h} x {w}\nМинимум 11, максимум 25, только нечётные значения.")

        self.h_entry.delete(0, tk.END)
        self.h_entry.insert(0, str(h))
        self.w_entry.delete(0, tk.END)
        self.w_entry.insert(0, str(w))

        self.height = h
        self.width = w
        self.theme = self.theme_var.get()

        self.maze = [[1] * self.width for _ in range(self.height)]

        self.canvas.destroy()
        self.canvas = MazeCanvas(self.right, self.maze, theme=self.theme, cell_size=25, bg="white")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.entry = None
        self.exit = None
        self.pending = None

        self.enable_block2(True)
        self.enable_block3(False)
        self.enable_save(False)

        self.canvas.bind("<Button-1>", self.on_canvas_click)
    
    def on_canvas_click(self, event):
        if self.place_method.get() != "manual":
            return

        h = len(self.maze)
        w = len(self.maze[0])

        total_width = w * self.canvas.cell_size
        total_height = h * self.canvas.cell_size

        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()

        offset_x = max(0, (canvas_width - total_width) // 2)
        offset_y = max(0, (canvas_height - total_height) // 2)

        x = (event.x - offset_x) // self.canvas.cell_size
        y = (event.y - offset_y) // self.canvas.cell_size

        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            return

        # --- Проверка периметра ---
        if not (x == 0 or x == self.width-1 or y == 0 or y == self.height-1):
            messagebox.showerror("Ошибка", "Точка должна быть на границе")
            return

        # --- Проверка углов ---
        if (x == 0 and y == 0) or (x == 0 and y == self.height-1) or \
           (x == self.width-1 and y == 0) or (x == self.width-1 and y == self.height-1):
            messagebox.showerror("Ошибка", "Нельзя ставить в угол")
            return

        new_point = (x, y)

        # --- Проверка совпадения ---
        if self.entry and new_point == self.entry:
            messagebox.showerror("Ошибка", "Вход и выход не могут совпадать")
            return

        if self.exit and new_point == self.exit:
            messagebox.showerror("Ошибка", "Вход и выход не могут совпадать")
            return

        # --- Проверка соседства ---
        if self.entry:
            ex, ey = self.entry
            if abs(ex - x) + abs(ey - y) <= 1:
                messagebox.showerror("Ошибка", "Вход и выход не могут быть соседними")
                return

        if self.exit:
            ex, ey = self.exit
            if abs(ex - x) + abs(ey - y) <= 1:
                messagebox.showerror("Ошибка", "Вход и выход не могут быть соседними")
                return
            
        # --- Проверка зоны угла ---
        if self.entry:
            entry_corner = self.get_corner_zone(self.entry)
            new_corner = self.get_corner_zone(new_point)

            if entry_corner and new_corner and entry_corner == new_corner:
                messagebox.showerror("Ошибка", "Недопустимо размещать вход и выход возле одного угла")
                return
        
        if self.exit:
            exit_corner = self.get_corner_zone(self.exit)
            new_corner = self.get_corner_zone(new_point)

            if exit_corner and new_corner and exit_corner == new_corner:
                messagebox.showerror("Ошибка", "Недопустимо размещать вход и выход возле одного угла")
                return

        # --- Установка ---
        if not self.entry:
            self.entry = new_point
        elif not self.exit:
            self.exit = new_point
        else:
            if self.replace_mode == "entry":
                self.maze[self.entry[1]][self.entry[0]] = 1
                self.entry = new_point
                self.replace_mode = "exit"
            else:
                self.maze[self.exit[1]][self.exit[0]] = 1
                self.exit = new_point
                self.replace_mode = "entry"

        # --- Обновление сетки ---
        if self.entry:
            self.maze[self.entry[1]][self.entry[0]] = 0
        if self.exit:
            self.maze[self.exit[1]][self.exit[0]] = 0

        self.canvas.entry = self.entry
        self.canvas.exit = self.exit
        self.canvas.draw_maze()

        if self.entry and self.exit:
            self.enable_block3(True)

    def get_corner_zone(self, point):
        x, y = point

        # верхний левый угол
        if x <= 2 and y == 0:
            return "tl"
        if x == 0 and y <= 2:
            return "tl"

        # верхний правый
        if x >= self.width-3 and y == 0:
            return "tr"
        if x == self.width-1 and y <= 2:
            return "tr"

        # нижний левый
        if x <= 2 and y == self.height-1:
            return "bl"
        if x == 0 and y >= self.height-3:
            return "bl"

        # нижний правый
        if x >= self.width-3 and y == self.height-1:
            return "br"
        if x == self.width-1 and y >= self.height-3:
            return "br"

        return None

    def apply_step2(self):
        self.canvas.bind("<Button-1>", self.on_canvas_click)

        # Полный сброс к шаблону
        self.maze = [[1] * self.width for _ in range(self.height)]
        self.canvas.maze = self.maze

        self.entry = None
        self.exit = None
        self.canvas.entry = None
        self.canvas.exit = None

        self.enable_block3(False)
        self.enable_save(False)

        if self.place_method.get() == "auto":
            self.entry, self.exit = auto_place_entrance_exit(self.maze)

            self.maze[self.entry[1]][self.entry[0]] = 0
            self.maze[self.exit[1]][self.exit[0]] = 0

            self.canvas.entry = self.entry
            self.canvas.exit = self.exit
            self.canvas.draw_maze()

            self.enable_block3(True)

        else:
            self.canvas.draw_maze()
            messagebox.showinfo("Ручная расстановка", "Выберите вход и выход кликами по границе.")

    def generate(self):
        if not self.entry or not self.exit:
            return

        forbidden = self.get_forbidden_node()
        valid = False

        while not valid:

            if self.algo_var.get() == "backtracker":
                maze = recursive_backtracker(self.height, self.width, forbidden_node=forbidden)
            else:
                maze = kruskal(self.height, self.width, forbidden_node=forbidden)

            # подключаем вход и выход
            def connect_point(p):
                x, y = p
                if y == 0:
                    maze[y][x] = 0
                    maze[y+1][x] = 0
                elif y == self.height - 1:
                    maze[y][x] = 0
                    maze[y-1][x] = 0
                elif x == 0:
                    maze[y][x] = 0
                    maze[y][x+1] = 0
                elif x == self.width - 1:
                    maze[y][x] = 0
                    maze[y][x-1] = 0

            if forbidden:
                connect_point(self.entry)
                connect_point(self.exit)
            else:
                maze[self.entry[1]][self.entry[0]] = 0
                maze[self.exit[1]][self.exit[0]] = 0

            # проверяем связность
            if has_isolated_areas(maze):
                continue

            # проверяем наличие пути
            from algorithms.pathfinding import wave_algorithm
            dist, path = wave_algorithm(maze, tuple(self.entry), tuple(self.exit))
            if not path:
                continue

            # проверка длины
            min_length = (self.height * self.width) * 0.20
            if len(path) < min_length:
                continue

            valid = True

        self.maze = maze
        self.canvas.maze = self.maze
        self.canvas.draw_maze()
        self.canvas.unbind("<Button-1>")
        self.enable_save(True)

    def get_forbidden_node(self):
        def get_inner(p):
            x, y = p
            if y == 0:
                return (x, y + 1)
            if y == self.height - 1:
                return (x, y - 1)
            if x == 0:
                return (x + 1, y)
            if x == self.width - 1:
                return (x - 1, y)

        inner_entry = get_inner(self.entry)
        inner_exit = get_inner(self.exit)

        if not inner_entry or not inner_exit:
            return None

        dx = abs(inner_entry[0] - inner_exit[0])
        dy = abs(inner_entry[1] - inner_exit[1])

        # если узлы находятся через одну вершину (расстояние 2)
        if dx + dy == 2:
            mid_x = (inner_entry[0] + inner_exit[0]) // 2
            mid_y = (inner_entry[1] + inner_exit[1]) // 2
            return (mid_x, mid_y)

        return None

    def open_save_dialog(self):
        if not self.maze:
            messagebox.showerror("Ошибка", "Сначала сгенерируйте лабиринт")
            return

        dialog = tk.Toplevel(self)
        dialog.title("Сохранение лабиринта")
        dialog.geometry("350x180")
        dialog.resizable(False, False)
        dialog.grab_set()

        tk.Label(dialog, text="Название лабиринта:", font=("Arial", 12)).pack(pady=15)

        name_entry = tk.Entry(dialog, width=25, font=("Arial", 12))
        name_entry.pack(pady=5)
        name_entry.config(validate="key", validatecommand=(dialog.register(lambda s: len(s) <= 20), "%P"))

        btn_frame = tk.Frame(dialog)
        btn_frame.pack(pady=15)

        tk.Button(btn_frame, text="ОК", width=10,
                  command=lambda: self.save_maze(dialog, name_entry.get())).pack(side=tk.LEFT, padx=10)

        tk.Button(btn_frame, text="Отмена", width=10,
                  command=dialog.destroy).pack(side=tk.LEFT, padx=10)

    def save_maze(self, dialog, name):
        name = name.strip()

        if not name:
            messagebox.showerror("Ошибка", "Название не может быть пустым")
            return

        if len(name) > 20:
            messagebox.showerror("Ошибка", "Название не должно превышать 20 символов")
            return

        try:
            response = requests.post(
                "http://127.0.0.1:5000/mazes",
                json={
                    "name": name,
                    "height": self.height,
                    "width": self.width,
                    "maze_map": self.maze,
                    "theme": self.theme,
                    "entry": self.entry,
                    "exit": self.exit
                }
            )

            data = response.json()

            if data.get("status") == "success":
                dialog.destroy()
                from gui.admin_window import AdminWindow
                self.parent.show_frame(AdminWindow, user_id=self.admin_id, login="admin")
            else:
                messagebox.showerror(
                    "Ошибка",
                    data.get("message", "Ошибка сохранения")
                )

        except Exception as e:
            messagebox.showerror("Ошибка соединения", str(e))
    
    def cancel(self):
        from gui.admin_window import AdminWindow
        self.parent.show_frame(AdminWindow, user_id=self.admin_id, login="admin")