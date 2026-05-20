# gui/maze_canvas.py
import tkinter as tk
from gui.themes import get_theme
from PIL import Image, ImageTk
import os

class MazeCanvas(tk.Canvas):
    def __init__(self, parent, maze, theme='default', cell_size=None, entry=None, exit=None, **kwargs):
        super().__init__(parent, **kwargs)
        self.maze = maze
        self.theme = theme
        self.base_cell_size = cell_size if cell_size else 25
        self.entry = entry
        self.exit = exit
        self.images = {}
        self.load_textures()
        self.bind("<Configure>", self.on_resize)
        self.draw_maze()
    
    def on_resize(self, event):
        """При изменении размера холста пересчитываем оптимальный размер клетки"""
        if not self.maze or len(self.maze) == 0 or len(self.maze[0]) == 0:
            return
        
        h = len(self.maze)
        w = len(self.maze[0])
        
        # Доступное пространство
        available_width = event.width - 20
        available_height = event.height - 20
        
        # Оптимальный размер клетки
        cell_by_width = available_width // w
        cell_by_height = available_height // h
        
        # Берём минимальный, чтобы лабиринт точно поместился
        optimal_cell = min(cell_by_width, cell_by_height)
        
        # Ограничиваем: минимум 15px, максимум 45px
        optimal_cell = max(15, min(45, optimal_cell))
        
        self.cell_size = optimal_cell
        self.draw_maze()
    
    def draw_maze(self):
        self.delete("all")
        if not self.maze or len(self.maze) == 0:
            return
        
        h = len(self.maze)
        w = len(self.maze[0])
        colors = get_theme(self.theme)
        
        # Если cell_size ещё не установлен (например, первый вызов до resize)
        if not hasattr(self, 'cell_size') or self.cell_size is None:
            self.cell_size = self.base_cell_size
        
        self.resize_textures()

        # Вычисляем отступы для центрирования
        total_width = w * self.cell_size
        total_height = h * self.cell_size
        canvas_width = self.winfo_width() if self.winfo_width() > 0 else total_width
        canvas_height = self.winfo_height() if self.winfo_height() > 0 else total_height
        
        offset_x = max(0, (canvas_width - total_width) // 2)
        offset_y = max(0, (canvas_height - total_height) // 2)
        
        for y in range(h):
            for x in range(w):
                x1 = offset_x + x * self.cell_size
                y1 = offset_y + y * self.cell_size

                if self.maze[y][x] == 1:
                    if "wall" in self.images:
                        self.create_image(
                            x1, y1,
                            image=self.images["wall"],
                            anchor="nw"
                        )
                    else:
                        self.create_rectangle(
                            x1, y1,
                            x1 + self.cell_size,
                            y1 + self.cell_size,
                            fill="#444444"
                        )
                else:
                    if "path" in self.images:
                        self.create_image(
                            x1, y1,
                            image=self.images["path"],
                            anchor="nw"
                        )
                    else:
                        self.create_rectangle(
                            x1, y1,
                            x1 + self.cell_size,
                            y1 + self.cell_size,
                            fill="#eeeeee"
                        )
        
        # Вход
        if self.entry:
            self.draw_marker_frame(self.entry, "#2ecc71")  # зелёный

        # Выход
        if self.exit:
            self.draw_marker_frame(self.exit, "#e74c3c")  # красный

        # --- Рисуем сетку ---
        for y in range(h):
            for x in range(w):
                x1 = offset_x + x * self.cell_size
                y1 = offset_y + y * self.cell_size
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size

                self.create_rectangle(
                    x1, y1, x2, y2,
                    outline="#888888",
                    width=1,
                    tags="grid"
                )

        self.tag_raise("grid")

        # Поднимаем рамку выше клеток
        self.tag_raise("marker")
        
    def draw_marker_frame(self, pos, color):
        x, y = pos

        h = len(self.maze)
        w = len(self.maze[0])

        total_width = w * self.cell_size
        total_height = h * self.cell_size

        canvas_width = self.winfo_width() if self.winfo_width() > 0 else total_width
        canvas_height = self.winfo_height() if self.winfo_height() > 0 else total_height

        offset_x = max(0, (canvas_width - total_width) // 2)
        offset_y = max(0, (canvas_height - total_height) // 2)

        x1 = offset_x + x * self.cell_size
        y1 = offset_y + y * self.cell_size
        x2 = x1 + self.cell_size
        y2 = y1 + self.cell_size

        # внутренний отступ
        padding = 1

        self.create_rectangle(
            x1 + padding,
            y1 + padding,
            x2 - padding,
            y2 - padding,
            outline=color,
            width=3,
            tags="marker"
        )
    
    def highlight_cell(self, x, y, color, permanent=False):
        if not self.maze:
            return
        
        h = len(self.maze)
        w = len(self.maze[0])
        total_width = w * self.cell_size
        total_height = h * self.cell_size
        canvas_width = self.winfo_width() if self.winfo_width() > 0 else total_width
        canvas_height = self.winfo_height() if self.winfo_height() > 0 else total_height
        
        offset_x = max(0, (canvas_width - total_width) // 2)
        offset_y = max(0, (canvas_height - total_height) // 2)
        
        x1 = offset_x + x * self.cell_size
        y1 = offset_y + y * self.cell_size
        x2 = x1 + self.cell_size
        y2 = y1 + self.cell_size
        
        tag = "permanent" if permanent else "highlight"
        if not permanent:
            self.delete(f"cell_{x}_{y}_highlight")
        rect = self.create_rectangle(x1, y1, x2, y2, fill=color, outline="", tag=tag)
        if permanent:
            self.tag_lower(tag)
        self.update_idletasks()
    
    def reset_cell_color(self, x, y):
        if not self.maze:
            return

        h = len(self.maze)
        w = len(self.maze[0])

        total_width = w * self.cell_size
        total_height = h * self.cell_size

        canvas_width = self.winfo_width() if self.winfo_width() > 0 else total_width
        canvas_height = self.winfo_height() if self.winfo_height() > 0 else total_height

        offset_x = max(0, (canvas_width - total_width) // 2)
        offset_y = max(0, (canvas_height - total_height) // 2)

        x1 = offset_x + x * self.cell_size
        y1 = offset_y + y * self.cell_size

        self.delete("character")

        if self.maze[y][x] == 1:
            if "wall" in self.images:
                self.create_image(x1, y1, image=self.images["wall"], anchor="nw")
        else:
            if "path" in self.images:
                self.create_image(x1, y1, image=self.images["path"], anchor="nw")
    
    def load_textures(self):
        theme = self.theme

        base_path = os.path.join(
            os.path.dirname(__file__),
            "..",
            "assets",
            theme
        )

        if not os.path.exists(base_path):
            return

        try:
            wall = Image.open(os.path.join(base_path, "wall.png"))
            path = Image.open(os.path.join(base_path, "path.png"))

            self.images["wall_raw"] = wall
            self.images["path_raw"] = path

            # если есть персонаж
            char_path = os.path.join(base_path, "character.png")
            if os.path.exists(char_path):
                char = Image.open(char_path)
                self.images["character_raw"] = char

        except Exception as e:
            print("Ошибка загрузки текстур:", e)
    
    def resize_textures(self):
        size = (self.cell_size, self.cell_size)

        if "wall_raw" in self.images:
            self.images["wall"] = ImageTk.PhotoImage(
                self.images["wall_raw"].resize(size, Image.LANCZOS)
            )

        if "path_raw" in self.images:
            self.images["path"] = ImageTk.PhotoImage(
                self.images["path_raw"].resize(size, Image.LANCZOS)
            )

        if "character_raw" in self.images:
            self.images["character"] = ImageTk.PhotoImage(
                self.images["character_raw"].resize(size, Image.LANCZOS)
            )
    
    def clear_highlights(self):
        self.delete("highlight")