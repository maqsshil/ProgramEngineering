# gui/play_maze_window.py
import tkinter as tk
from tkinter import messagebox
from gui.maze_canvas import MazeCanvas
from algorithms.pathfinding import wave_algorithm, right_hand_rule

class PlayMazeWindow(tk.Frame):
    def __init__(self, parent, db, maze_data):
        super().__init__(parent, bg="#f0f0f0")
        self.parent = parent
        self.db = db
        self.maze_data = maze_data
        self.maze = maze_data['map']
        self.entry = maze_data['entry']
        self.exit = maze_data['exit']
        self.running = False
        self.after_id = None
        self.current_pos = None
        self.create_widgets()
    
    def create_widgets(self):
        control = tk.Frame(self, bg="#f0f0f0", width=280)
        control.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)
        
        canvas_frame = tk.Frame(self, bg="#ffffff", relief=tk.SUNKEN, bd=2)
        canvas_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.canvas = MazeCanvas(canvas_frame, self.maze, theme="default", cell_size=25,
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
        
        tk.Label(control, text="Режим прохождения:", font=("Arial", 10, "bold"), bg="#f0f0f0").pack(anchor="w", pady=(10,5))
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
        
        self.start_btn = tk.Button(control, text="Старт", command=self.start_solution, bg="#cccccc", fg="#000000", font=("Arial", 10), relief=tk.RAISED, bd=2)
        self.start_btn.pack(pady=20)
        tk.Button(control, text="Назад", command=self.go_back, bg="#cccccc", fg="#000000", font=("Arial", 10), relief=tk.RAISED, bd=2).pack()
        
        self.toggle_options()
        self.toggle_speed()
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
        if self.algo_var.get() == "wave":
            self.auto_mode.config(state=tk.DISABLED)
            self.step_mode.config(state=tk.DISABLED)
            self.set_speed_state(tk.DISABLED)
        else:
            self.auto_mode.config(state=tk.NORMAL)
            self.step_mode.config(state=tk.NORMAL)
            self.toggle_speed()
    
    def toggle_speed(self):
        if self.mode_var.get() == "auto":
            self.set_speed_state(tk.NORMAL)
        else:
            self.set_speed_state(tk.DISABLED)
    
    def set_speed_state(self, state):
        for child in self.speed_frame.winfo_children():
            if isinstance(child, (tk.Radiobutton, tk.Label)):
                child.config(state=state)
    
    def start_solution(self):
        if self.running:
            return
        self.running = True
        self.start_btn.config(state=tk.DISABLED)
        self.canvas.clear_highlights()
        
        # Рисуем вход белым
        self.canvas.highlight_cell(self.entry[0], self.entry[1], "#ffffff", permanent=True)
        # Выход красным
        self.canvas.highlight_cell(self.exit[0], self.exit[1], "#e74c3c", permanent=True)
        
        if self.algo_var.get() == "wave":
            path = wave_algorithm(self.maze, self.entry, self.exit)
            if not path:
                messagebox.showerror("Ошибка","Путь не найден!")
                self.running = False
                self.start_btn.config(state=tk.NORMAL)
                return
            self.animate_path(path)
        else:
            mode = self.mode_var.get()
            delay = {"slow":700, "medium":300, "fast":100}[self.speed_var.get()]
            if mode == "step":
                self.step_by_step()
            else:
                self.auto_right_hand(delay)
    
    def animate_path(self, path):
        """Волновой алгоритм – бегающая клетка по заранее вычисленному пути"""
        self.current_pos = self.entry
        self.path = path
        self.path_index = 0
        
        def move():
            if self.path_index >= len(self.path):
                # Достигли выхода
                self.canvas.reset_cell_color(self.current_pos[0], self.current_pos[1])
                self.running = False
                self.start_btn.config(state=tk.NORMAL)
                # Выход становится цветом темы (игрок вышел)
                self.canvas.reset_cell_color(self.exit[0], self.exit[1])
                return
            
            # Убираем подсветку с предыдущей позиции
            if self.current_pos:
                self.canvas.reset_cell_color(self.current_pos[0], self.current_pos[1])
            
            # Перемещаемся на следующую позицию
            self.current_pos = self.path[self.path_index]
            self.canvas.highlight_cell(self.current_pos[0], self.current_pos[1], "#3498db")
            self.path_index += 1
            
            delay = 100
            self.after_id = self.after(delay, move)
        
        move()
    
    def auto_right_hand(self, delay):
        """Правой руки – бегающая клетка"""
        gen = right_hand_rule(self.maze, self.entry, self.exit)
        self.current_pos = self.entry
        self.canvas.highlight_cell(self.entry[0], self.entry[1], "#3498db")
        
        def step():
            try:
                pos, _ = next(gen)
                
                # Убираем подсветку с предыдущей позиции
                if self.current_pos:
                    self.canvas.reset_cell_color(self.current_pos[0], self.current_pos[1])
                
                # Перемещаемся
                self.current_pos = pos
                self.canvas.highlight_cell(pos[0], pos[1], "#3498db")
                
                self.after_id = self.after(delay, step)
            except StopIteration:
                # Достигли выхода
                self.canvas.reset_cell_color(self.current_pos[0], self.current_pos[1])
                self.running = False
                self.start_btn.config(state=tk.NORMAL)
                # Выход становится цветом темы (игрок вышел)
                self.canvas.reset_cell_color(self.exit[0], self.exit[1])
        step()
    
    def step_by_step(self):
        """Правой руки – пошаговый режим с бегающей клеткой"""
        gen = right_hand_rule(self.maze, self.entry, self.exit)
        self.step_gen = gen
        self.current_pos = self.entry
        self.canvas.highlight_cell(self.entry[0], self.entry[1], "#3498db")
        
        self.step_btn = tk.Button(self.control_panel, text="Следующий шаг", command=self.next_step, bg="#cccccc", fg="#000000", font=("Arial", 10), relief=tk.RAISED, bd=2)
        self.step_btn.pack(pady=5)
    
    def next_step(self):
        try:
            pos, _ = next(self.step_gen)
            
            # Убираем подсветку с предыдущей позиции
            if self.current_pos:
                self.canvas.reset_cell_color(self.current_pos[0], self.current_pos[1])
            
            # Перемещаемся
            self.current_pos = pos
            self.canvas.highlight_cell(pos[0], pos[1], "#3498db")
            
        except StopIteration:
            # Достигли выхода
            self.step_btn.config(state=tk.DISABLED)
            self.running = False
            self.start_btn.config(state=tk.NORMAL)
            # Убираем персонажа
            self.canvas.reset_cell_color(self.current_pos[0], self.current_pos[1])
            # Выход становится цветом темы (игрок вышел)
            self.canvas.reset_cell_color(self.exit[0], self.exit[1])
    
    def go_back(self):
        from gui.player_window import PlayerWindow
        self.parent.show_frame(PlayerWindow, user_id=None, login="player")