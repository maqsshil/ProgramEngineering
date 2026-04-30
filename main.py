# main.py
import tkinter as tk
from db.database import DatabaseManager
from gui.auth_window import AuthWindow

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Автоматизированная система генерации лабиринтов")
        self.geometry("1100x750")
        self.minsize(900, 650)
        self.db = DatabaseManager()
        self.current_frame = None
        self.show_auth()
        self.protocol("WM_DELETE_WINDOW", self.quit_app)
    
    def show_auth(self):
        self.show_frame(AuthWindow)
    
    def show_frame(self, frame_class, **kwargs):
        if self.current_frame:
            self.current_frame.destroy()
        self.current_frame = frame_class(self, self.db, **kwargs)
        self.current_frame.pack(fill=tk.BOTH, expand=True)
    
    def quit_app(self):
        self.db.close()
        self.quit()

if __name__ == "__main__":
    app = App()
    app.mainloop()