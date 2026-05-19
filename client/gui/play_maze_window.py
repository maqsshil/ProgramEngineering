# gui/play_maze_window.py
import tkinter as tk
from tkinter import messagebox
from gui.maze_canvas import MazeCanvas
from algorithms.pathfinding import wave_algorithm, right_hand_rule

class PlayMazeWindow(tk.Frame):
    def __init__(self, parent, maze_data, login):
        super().__init__(parent, bg="#f0f0f0")
        self.parent = parent
        self.login = login
        self.maze_data = maze_data
        self.maze = maze_data['map']
        self.entry = maze_data['entry']
        self.exit = maze_data['exit']
        self.running = False
        self.after_id = None
        self.current_pos = None
        self.step_index = 0
        self.create_widgets()
    
    def create_widgets(self):
        control = tk.Frame(self, bg="#f0f0f0", width=280)
        control.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)
        
        canvas_frame = tk.Frame(self, bg="#ffffff", relief=tk.SUNKEN, bd=2)
        canvas_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.canvas = MazeCanvas( canvas_frame, self.maze, theme=self.maze_data.get("theme", "default"), cell_size=25,
            entry=self.entry, exit=self.exit, bg="white")
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(control, text="Тема оформления:", font=("Arial", 10, "bold"), bg="#f0f0f0").pack(anchor="w", pady=(0,5))
        self.theme_var = tk.StringVar(value="default")
        themes = [("default","Стандартная"),("dark","Тёмная"),("forest","Лесная"),("sand","Песчаная")]
        for k,v in themes:
            tk.Radiobutton(control, text=v, variable=self.theme_var, value=k, bg="#f0f0f0", command=self.change_theme).pack(anchor="w")
        
        tk.Label(control, text="Алгоритм поиска:", font=("Arial", 10, "bold"), bg="#f0f0f0").pack(anchor="w", pady=(15,5))
        self.algo_var = tk.StringVar(value="wave")
        tk.Radiobutton(control, text="Волновой", variable=self.algo_var, value="wave", bg="#f0f0f0", command=self.toggle_options).pack(anchor="w")
        tk.Radiobutton(control, text="Правой руки", variable=self.algo_var, value="right_hand", bg="#f0f0f0", command=self.toggle_options).pack(anchor="w")
        
        self.mode_label = tk.Label(control, text="Режим прохождения:", font=("Arial", 10, "bold"), bg="#f0f0f0")
        self.mode_label.pack(anchor="w", pady=(10,5))
        self.mode_var = tk.StringVar(value="auto")
        self.auto_mode = tk.Radiobutton(control, text="Автоматический", variable=self.mode_var, value="auto", bg="#f0f0f0", command=self.toggle_speed)
        self.auto_mode.pack(anchor="w")
        self.step_mode = tk.Radiobutton(control, text="Пошаговый", variable=self.mode_var, value="step", bg="#f0f0f0", command=self.toggle_speed)
        self.step_mode.pack(anchor="w")
        
        self.speed_frame = tk.Frame(control, bg="#f0f0f0")
        self.speed_frame.pack(fill=tk.X, pady=5)
        tk.Label(self.speed_frame, text="Скорость прохождения:", font=("Arial", 10, "bold"), bg="#f0f0f0").pack(anchor="w")
        self.speed_var = tk.StringVar(value="medium")
        speeds = [("slow","Медленно"),("medium","Средне"),("fast","Быстро")]
        for k,v in speeds:
            tk.Radiobutton(self.speed_frame, text=v, variable=self.speed_var, value=k, bg="#f0f0f0").pack(anchor="w")
        
        self.start_btn = tk.Button(control, text="Применить", command=self.start_solution, bg="#cccccc", fg="#000000", font=("Arial", 10), relief=tk.RAISED, bd=2)
        self.start_btn.pack(pady=20)
        tk.Button(control, text="Назад", command=self.go_back, bg="#cccccc", fg="#000000", font=("Arial", 10), relief=tk.RAISED, bd=2).pack()
        
        self.toggle_speed()
        self.toggle_options()
        self.control_panel = control
    
    def change_theme(self):
        self.canvas.theme = self.theme_var.get()
        self.canvas.draw_maze()
        # Восстанавливаем вход (белый) и выход (красный)
        self.canvas.highlight_cell(self.entry[0], self.entry[1], "#ffffff", permanent=True)
        self.canvas.highlight_cell(self.exit[0], self.exit[1], "#e74c3c", permanent=True)
        # Если есть текущая позиция – перерисовать персонажа
        if self.current_pos:
            self.canvas.highlight_cell(self.current_pos[0], self.current_pos[1], "#3498db")
    
    def toggle_options(self):
        self._reset_execution()
        if self.algo_var.get() == "wave":
            # Отключаем заголовок режима
            self.mode_label.config(fg="gray")

            # Отключаем режим
            self.auto_mode.config(state=tk.DISABLED)
            self.step_mode.config(state=tk.DISABLED)

            # Отключаем скорость
            for child in self.speed_frame.winfo_children():
                if isinstance(child, (tk.Radiobutton, tk.Label)):
                    child.config(state=tk.DISABLED)

        else:
            # Включаем заголовок режима
            self.mode_label.config(fg="black")

            # Включаем режим
            self.auto_mode.config(state=tk.NORMAL)
            self.step_mode.config(state=tk.NORMAL)

            # Включаем скорость
            self.toggle_speed()
    
    def _reset_execution(self):
        # остановить after, если авто режим
        if self.after_id:
            try:
                self.after_cancel(self.after_id)
            except:
                pass
            self.after_id = None

        self.running = False
        self.start_btn.config(state=tk.NORMAL)

        # удалить панель пошагового режима
        self._clear_step_panel()

        # очистить холст
        self.canvas.delete("all")
        self.canvas.draw_maze()

        # вернуть вход/выход
        self.canvas.highlight_cell(self.entry[0], self.entry[1], "#ffffff", permanent=True)
        self.canvas.highlight_cell(self.exit[0], self.exit[1], "#e74c3c", permanent=True)

        self.current_pos = None
        self.history = []
        self.path_lines = []
    
    def toggle_speed(self):
        if self.mode_var.get() == "auto":
            self.set_speed_state(tk.NORMAL)
        else:
            self.set_speed_state(tk.DISABLED)
    
    def set_speed_state(self, state):
        for child in self.speed_frame.winfo_children():
            if isinstance(child, (tk.Radiobutton, tk.Label)):
                child.config(state=state)

    def _clear_step_panel(self):
        if hasattr(self, "step_panel") and self.step_panel:
            self.step_panel.destroy()
            self.step_panel = None
    
    def start_solution(self):
        self._reset_execution()
        self.canvas.update_idletasks()
        self.path_lines = []
        
        # Рисуем вход белым
        self.canvas.highlight_cell(self.entry[0], self.entry[1], "#ffffff", permanent=True)
        # Выход красным
        self.canvas.highlight_cell(self.exit[0], self.exit[1], "#e74c3c", permanent=True)
        
        if self.algo_var.get() == "wave":
            dist, path = wave_algorithm(
                self.maze,
                tuple(self.entry),
                tuple(self.exit)
            )

            if not path:
                messagebox.showerror("Ошибка", "Путь не найден!")
                self.running = False
                self.start_btn.config(state=tk.NORMAL)
                return

            self.canvas.draw_maze()
            self.canvas.highlight_cell(self.entry[0], self.entry[1], "#ffffff", permanent=True)
            self.canvas.highlight_cell(self.exit[0], self.exit[1], "#e74c3c", permanent=True)

            self.draw_shortest_path(path)
            return
        else:
            mode = self.mode_var.get()
            if mode == "step":
                self.step_by_step()
            else:
                self.auto_right_hand()
    
    def draw_shortest_path(self, path):
        """Рисует кратчайший путь сразу"""

        cell = self.canvas.cell_size
        h = len(self.maze)
        w = len(self.maze[0])

        total_width = w * cell
        total_height = h * cell

        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()

        offset_x = max(0, (canvas_width - total_width) // 2)
        offset_y = max(0, (canvas_height - total_height) // 2)

        points = []

        for x, y in path:
            cx = offset_x + x * cell + cell // 2
            cy = offset_y + y * cell + cell // 2
            points.append((cx, cy))

        for i in range(1, len(points)):
            x1, y1 = points[i - 1]
            x2, y2 = points[i]

            self.canvas.create_line(
                x1, y1, x2, y2,
                fill="#3498db",
                width=4,
                smooth=True
            )

        self.running = False
        self.start_btn.config(state=tk.NORMAL)

    def auto_right_hand(self):
        self.canvas.update_idletasks()
        gen = right_hand_rule(self.maze, self.entry, self.exit)

        self.current_pos = self.entry
        self.canvas.highlight_cell(self.entry[0], self.entry[1], "#3498db")

        self.path_positions = [self.entry]
        self.path_lines = []

        cell = self.canvas.cell_size
        h = len(self.maze)
        w = len(self.maze[0])

        total_width = w * cell
        total_height = h * cell

        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()

        offset_x = max(0, (canvas_width - total_width) // 2)
        offset_y = max(0, (canvas_height - total_height) // 2)

        def get_center(pos):
            x, y = pos
            cx = offset_x + x * cell + cell // 2
            cy = offset_y + y * cell + cell // 2
            return cx, cy

        def step():
            try:
                pos, _ = next(gen)

                # --- Достигли выхода ---
                if tuple(pos) == tuple(self.exit):
                    # Добавляем последнюю линию
                    last_center = get_center(self.path_positions[-1])
                    new_center = get_center(pos)

                    line_id = self.canvas.create_line(
                        last_center[0], last_center[1],
                        new_center[0], new_center[1],
                        fill="#5dade2",
                        width=4,
                        tags="path_line"
                    )

                    self.canvas.tag_raise("path_line")
                    self.path_lines.append(line_id)
                    self.path_positions.append(pos)

                    # Убираем старую позицию персонажа
                    if self.current_pos:
                        self.canvas.reset_cell_color(
                            self.current_pos[0],
                            self.current_pos[1]
                        )

                    self.canvas.tag_raise("path_line")

                    # Ставим персонажа в выход
                    self.current_pos = pos
                    self.canvas.highlight_cell(pos[0], pos[1], "#3498db")

                    self.running = False
                    self.start_btn.config(state=tk.NORMAL)
                    return

                # --- Возврат назад ---
                if pos in self.path_positions:
                    if self.path_lines:
                        self.canvas.delete(self.path_lines.pop())
                    self.path_positions.pop()
                else:
                    last_center = get_center(self.path_positions[-1])
                    new_center = get_center(pos)

                    line_id = self.canvas.create_line(
                        last_center[0], last_center[1],
                        new_center[0], new_center[1],
                        fill="#5dade2",
                        width=4,
                        tags="path_line"
                    )

                    self.canvas.tag_raise("path_line")

                    self.path_lines.append(line_id)
                    self.path_positions.append(pos)

                # --- Перемещение персонажа ---
                if self.current_pos:
                    self.canvas.reset_cell_color(
                        self.current_pos[0],
                        self.current_pos[1]
                    )
                    self.canvas.tag_raise("path_line")

                self.current_pos = pos
                self.canvas.highlight_cell(pos[0], pos[1], "#3498db")

                current_delay = {
                    "slow": 700,
                    "medium": 300,
                    "fast": 100
                }[self.speed_var.get()]

                self.after_id = self.after(current_delay, step)

            except StopIteration:
                self.running = False
                self.start_btn.config(state=tk.NORMAL)

        step()
    
    def step_by_step(self):
        self._clear_step_panel()
        self.canvas.update_idletasks()

        # генератор живой
        self.step_gen = right_hand_rule(self.maze, self.entry, self.exit)

        self.history = []
        self.step_index = 0
        self.segments = {} 
        
        # первый шаг (вход)
        pos, _ = next(self.step_gen)

        self.history.append(pos)
        self.step_index = 0

        self.current_pos = pos
        self.canvas.highlight_cell(pos[0], pos[1], "#3498db")

        # панель кнопок
        self.step_panel = tk.Frame(self.control_panel, bg="#f0f0f0")
        self.step_panel.pack(pady=10)

        self.prev_btn = tk.Button(
            self.step_panel,
            text="←",
            command=self.prev_step,
            width=3,
            font=("Arial", 14)
        )
        self.prev_btn.pack(side=tk.LEFT, padx=5)

        self.next_btn = tk.Button(
            self.step_panel,
            text="→",
            command=self.next_step,
            width=3,
            font=("Arial", 14)
        )
        self.next_btn.pack(side=tk.LEFT, padx=5)

        self._update_step_buttons()
        
    def next_step(self):
        if self.step_index < len(self.history) - 1:
            prev = self.history[self.step_index]
            self.step_index += 1
            curr = self.history[self.step_index]
        else:
            try:
                curr, _ = next(self.step_gen)
                prev = self.history[self.step_index]
                self.history.append(curr)
                self.step_index += 1
            except StopIteration:
                return

        self._toggle_segment(prev, curr)
        self._move_character(curr)
        self._update_step_buttons()
    
    def prev_step(self):
        if self.step_index <= 0:
            return

        curr = self.history[self.step_index]
        prev = self.history[self.step_index - 1]

        self._toggle_segment(prev, curr)

        self.canvas.reset_cell_color(curr[0], curr[1])
        self.canvas.tag_raise("path_line")

        self.step_index -= 1
        self.current_pos = prev
        self.canvas.highlight_cell(prev[0], prev[1], "#3498db")

        self._update_step_buttons()

    def _draw_line(self, from_pos, to_pos):
        cell = self.canvas.cell_size
        h = len(self.maze)
        w = len(self.maze[0])

        total_width = w * cell
        total_height = h * cell

        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()

        offset_x = max(0, (canvas_width - total_width) // 2)
        offset_y = max(0, (canvas_height - total_height) // 2)

        def get_center(p):
            x, y = p
            return (
                offset_x + x * cell + cell // 2,
                offset_y + y * cell + cell // 2
            )

        c1 = get_center(from_pos)
        c2 = get_center(to_pos)

        line_id = self.canvas.create_line(
            c1[0], c1[1],
            c2[0], c2[1],
            fill="#5dade2",
            width=4,
            tags="path_line"
        )

        self.canvas.tag_raise("path_line")
        return line_id

    def _move_character(self, pos):
        if self.current_pos:
            self.canvas.reset_cell_color(
                self.current_pos[0],
                self.current_pos[1]
            )

        self.canvas.tag_raise("path_line")

        self.current_pos = pos
        self.canvas.highlight_cell(pos[0], pos[1], "#3498db")
    
    def _update_step_buttons(self):
        if self.step_index > 0:
            self.prev_btn.config(state=tk.NORMAL)
        else:
            self.prev_btn.config(state=tk.DISABLED)

        if tuple(self.current_pos) == tuple(self.exit):
            self.next_btn.config(state=tk.DISABLED)
        else:
            self.next_btn.config(state=tk.NORMAL)
    
    def _toggle_segment(self, p1, p2):
        key = frozenset((p1, p2))

        if key in self.segments:
            # сегмент уже есть — удаляем
            self.canvas.delete(self.segments[key])
            del self.segments[key]
        else:
            # сегмента нет — рисуем
            line_id = self._draw_line(p1, p2)
            self.segments[key] = line_id
        
    def go_back(self):
        from gui.player_window import PlayerWindow
        self.parent.show_frame(PlayerWindow, user_id=None, login=self.login)