# gui/auth_window.py
import requests
import tkinter as tk
from tkinter import messagebox
from gui.register_window import RegisterWindow

class AuthWindow(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="#f0f0f0")
        self.parent = parent
        self.create_widgets()
    
    def create_widgets(self):
        # Заголовок
        tk.Label(self, text="Авторизация", font=("Arial", 16, "bold"), bg="#f0f0f0", fg="#333").pack(pady=40)
        
        # Центрирующий фрейм
        center_frame = tk.Frame(self, bg="#f0f0f0")
        center_frame.pack(expand=True)
        
        # Используем grid для точного выравнивания
        # Логин
        tk.Label(center_frame, text="Логин:", font=("Arial", 10), bg="#f0f0f0", width=10, anchor="e").grid(row=0, column=0, padx=5, pady=8, sticky="e")
        self.entry_login = tk.Entry(center_frame, width=20, font=("Arial", 10))
        self.entry_login.grid(row=0, column=1, padx=5, pady=8)
        
        # Пароль
        tk.Label(center_frame, text="Пароль:", font=("Arial", 10), bg="#f0f0f0", width=10, anchor="e").grid(row=1, column=0, padx=5, pady=8, sticky="e")
        self.entry_password = tk.Entry(center_frame, width=20, font=("Arial", 10), show="*")
        self.entry_password.grid(row=1, column=1, padx=5, pady=8)
        
        # Кнопка "глаз"
        self.eye_btn = tk.Button(center_frame, text="👁", command=self.toggle_password, width=3, bg="#cccccc", relief=tk.RAISED, bd=1)
        self.eye_btn.grid(row=1, column=2, padx=2, pady=8)
        
        # Кнопки
        btn_frame = tk.Frame(center_frame, bg="#f0f0f0")
        btn_frame.grid(row=2, column=0, columnspan=3, pady=30)
        tk.Button(btn_frame, text="Вход", command=self.login, width=12, bg="#cccccc", fg="#000000", font=("Arial", 10), relief=tk.RAISED, bd=2).pack(side=tk.LEFT, padx=10)
        tk.Button(btn_frame, text="Регистрация", command=self.open_register, width=12, bg="#cccccc", fg="#000000", font=("Arial", 10), relief=tk.RAISED, bd=2).pack(side=tk.LEFT, padx=10)
    
    def toggle_password(self):
        if self.entry_password.cget("show") == "*":
            self.entry_password.config(show="")
            self.eye_btn.config(text="👁‍🗨")
        else:
            self.entry_password.config(show="*")
            self.eye_btn.config(text="👁")
    
    def login(self):
        login = self.entry_login.get().strip()
        password = self.entry_password.get().strip()

        try:
            response = requests.post(
                "http://127.0.0.1:5000/login",
                json={"login": login, "password": password}
            )

            data = response.json()

            if data.get("status") == "success":
                role = data.get("role")

                if role == "admin":
                    from gui.admin_window import AdminWindow
                    self.parent.show_frame(AdminWindow, user_id=None, login=login)

                elif role == "player":
                    from gui.player_window import PlayerWindow
                    self.parent.show_frame(PlayerWindow, user_id=None, login=login)

            else:
                messagebox.showerror("Ошибка", data.get("message"))

        except Exception as e:
            messagebox.showerror("Ошибка соединения", str(e))
    
    def open_register(self):
        RegisterWindow(self)