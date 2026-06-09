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
        info_path = os.path.join(os.path.dirname(__file__), "..", "system_info.html")
        webbrowser.open(f"file://{info_path}")