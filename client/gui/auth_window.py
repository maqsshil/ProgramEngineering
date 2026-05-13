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
        # Контейнер для полного центрирования
        center_container = tk.Frame(self, bg="#f0f0f0")
        center_container.pack(expand=True)

        # Заголовок
        tk.Label(center_container, text="Авторизация", font=("Arial", 28, "bold"), bg="#f0f0f0", fg="#333").pack(pady=40)

        # Центральная карточка
        card = tk.Frame(center_container, bg="white", padx=50, pady=40, relief=tk.RAISED, bd=2)
        card.pack()

        # Логин
        tk.Label(card, text="Логин:", font=("Arial", 14), bg="white").grid(row=0, column=0, sticky="e", pady=15, padx=10)

        self.entry_login = tk.Entry(card, width=25, font=("Arial", 14))
        self.entry_login.grid(row=0, column=1, pady=15, padx=10)

        # Пароль
        tk.Label(card, text="Пароль:", font=("Arial", 14), bg="white").grid(row=1, column=0, sticky="e", pady=15, padx=10)
        self.entry_password = tk.Entry(card, width=25, font=("Arial", 14), show="*")
        self.entry_password.grid(row=1, column=1, pady=15, padx=10)
        self.eye_btn = tk.Button(card, text="👁", command=self.toggle_password, font=("Arial", 12), width=3, relief=tk.RAISED, bd=1, bg="#e0e0e0")
        self.eye_btn.grid(row=1, column=2, padx=5)

        # Кнопки
        btn_frame = tk.Frame(card, bg="white")
        btn_frame.grid(row=2, column=0, columnspan=3, pady=30)
        tk.Button(btn_frame, text="Вход", command=self.login, width=14, height=2, font=("Arial", 12),
            relief=tk.RAISED, bd=1, bg="#e0e0e0").pack(side=tk.LEFT, padx=15)
        tk.Button(btn_frame, text="Регистрация", command=self.open_register, width=14, height=2, font=("Arial", 12),
            relief=tk.RAISED, bd=1, bg="#e0e0e0").pack(side=tk.LEFT, padx=15)
    
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
        from gui.register_window import RegisterWindow
        self.parent.show_frame(RegisterWindow)