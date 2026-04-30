# gui/help_window.py
import tkinter as tk
import webbrowser
import os

class HelpWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Справочная информация")
        self.geometry("500x450")
        self.resizable(False, False)
        self.configure(bg="#f0f0f0")
        
        # Текст по референсу
        text_content = """
Самарский университет, институт информатики и кибернетики

Курсовой проект по дисциплине "Программная инженерия"
по теме "Автоматизированная система генерирования
структуры лабиринта и нахождения выхода из него"

Разработчики (обучающиеся группы 6304-020302D):

    Зотов Н.П.
    Шильченков М.А.

2026 г.
        """
        
        label_text = tk.Label(self, text=text_content, font=("Arial", 11), 
                              bg="#f0f0f0", justify="center")
        label_text.pack(pady=30, padx=20, fill=tk.BOTH, expand=True)
        
        # Кнопки
        btn_frame = tk.Frame(self, bg="#f0f0f0")
        btn_frame.pack(pady=20)
        
        btn_back = tk.Button(btn_frame, text="Назад", command=self.destroy,
                             bg="#cccccc", fg="#000000", font=("Arial", 10, "bold"), 
                             width=12, relief=tk.RAISED, bd=2)
        btn_back.pack(side=tk.LEFT, padx=15)
        
        btn_about = tk.Button(btn_frame, text="О системе", command=self.open_browser,
                              bg="#cccccc", fg="#000000", font=("Arial", 10, "bold"),
                              width=12, relief=tk.RAISED, bd=2)
        btn_about.pack(side=tk.LEFT, padx=15)
        
        self.center_window()
    
    def center_window(self):
        self.update_idletasks()
        w = self.winfo_width()
        h = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (w // 2)
        y = (self.winfo_screenheight() // 2) - (h // 2)
        self.geometry(f"{w}x{h}+{x}+{y}")
    
    def open_browser(self):
        html_content = """<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"><title>О системе</title></head>
<body style="font-family: Arial; max-width: 800px; margin: 40px auto; padding: 20px;">
<h1>Автоматизированная система лабиринтов</h1>
<p><b>Разработчики:</b> Зотов Н.П., Шильченков М.А.</p>
<p><b>Руководитель:</b> Зеленко Л.С.</p>
<p><b>Год:</b> 2026</p>
<h2>Функции:</h2>
<ul>
<li>Генерация лабиринтов (рекурсивный бэктрекинг, Краскал)</li>
<li>Поиск пути (волновой, правой руки)</li>
<li>Сохранение в PostgreSQL</li>
<li>4 темы оформления</li>
<li>Роли: администратор, игрок</li>
</ul>
</body>
</html>"""
        info_path = os.path.join(os.path.dirname(__file__), "..", "system_info.html")
        with open(info_path, "w", encoding="utf-8") as f:
            f.write(html_content)
        webbrowser.open(f"file://{info_path}")