# gui/maze_canvas.py
import tkinter as tk
from gui.themes import get_theme

class MazeCanvas(tk.Canvas):
    def __init__(self, parent, maze, theme='default', cell_size=None, entry=None, exit=None, **kwargs):
        super().__init__(parent, **kwargs)
        self.maze = maze
        self.theme = theme
        self.base_cell_size = cell_size if cell_size else 25
        self.entry = entry
        self.exit = exit
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
        
        # Вычисляем отступы для центрирования
        total_width = w * self.cell_size
        total_height = h * self.cell_size
        canvas_width = self.winfo_width() if self.winfo_width() > 0 else total_width
        canvas_height = self.winfo_height() if self.winfo_height() > 0 else total_height
        
        offset_x = max(0, (canvas_width - total_width) // 2)
        offset_y = max(0, (canvas_height - total_height) // 2)
        
        for y in range(h):
            for x in range(w):
                if self.maze[y][x] == 1:
                    fill = colors['wall']
                else:
                    fill = colors['path']
                
                x1 = offset_x + x * self.cell_size
                y1 = offset_y + y * self.cell_size
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size
                
                self.create_rectangle(x1, y1, x2, y2, fill=fill, outline=colors['outline'], tags=f"cell_{x}_{y}")
        
        if self.entry:
            self.highlight_cell(self.entry[0], self.entry[1], "#ffffff", permanent=True)
        if self.exit:
            self.highlight_cell(self.exit[0], self.exit[1], "#e74c3c", permanent=True)
    
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
        """Восстанавливает исходный цвет клетки"""
        if not self.maze:
            return
        colors = get_theme(self.theme)
        is_wall = self.maze[y][x] == 1
        fill = colors['wall'] if is_wall else colors['path']
        
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
        
        self.delete(f"cell_{x}_{y}_highlight")
        self.create_rectangle(x1, y1, x2, y2, fill=fill, outline=colors['outline'], tags=f"cell_{x}_{y}_reset")
        self.update_idletasks()
    
    def clear_highlights(self):
        self.delete("highlight")