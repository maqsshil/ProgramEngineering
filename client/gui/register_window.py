import tkinter as tk
import requests
from tkinter import messagebox

class RegisterWindow(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="#f0f0f0")
        self.parent = parent
        self.create_widgets()

    def create_widgets(self):
        center_container = tk.Frame(self, bg="#f0f0f0")
        center_container.pack(expand=True)

        tk.Label(center_container, text="Регистрация", font=("Arial", 28, "bold"), bg="#f0f0f0", fg="#333").pack(pady=40)

        card = tk.Frame(center_container, bg="white", padx=50, pady=40, relief=tk.RAISED, bd=2)
        card.pack()

        tk.Label(card, text="Логин:", font=("Arial", 14), bg="white").grid(row=0, column=0, sticky="e", pady=15, padx=10)
        self.entry_login = tk.Entry(card, width=25, font=("Arial", 14))
        self.entry_login.grid(row=0, column=1, pady=15, padx=10)

        tk.Label(card, text="Пароль:", font=("Arial", 14), bg="white").grid(row=1, column=0, sticky="e", pady=15, padx=10)
        self.entry_password = tk.Entry(card, width=25, font=("Arial", 14), show="*")
        self.entry_password.grid(row=1, column=1, pady=15, padx=10)
        self.eye_pass = tk.Button(card, text="👁", command=self.toggle_password, font=("Arial", 12), width=3, 
            relief=tk.RAISED, bd=1, bg="#e0e0e0")
        self.eye_pass.grid(row=1, column=2, padx=5)

        tk.Label(card, text="Повторите пароль:", font=("Arial", 14), bg="white").grid(row=2, column=0, sticky="e", pady=15, padx=10)
        self.entry_confirm = tk.Entry(card, width=25, font=("Arial", 14), show="*")
        self.entry_confirm.grid(row=2, column=1, pady=15, padx=10)
        self.eye_confirm = tk.Button(card, text="👁", command=self.toggle_confirm, font=("Arial", 12), width=3, 
            relief=tk.RAISED, bd=1, bg="#e0e0e0")
        self.eye_confirm.grid(row=2, column=2, padx=5)

        btn_frame = tk.Frame(card, bg="white")
        btn_frame.grid(row=3, column=0, columnspan=3, pady=30)

        tk.Button(btn_frame, text="Зарегистрироваться", command=self.register, width=18, height=2, font=("Arial", 12), 
            relief=tk.RAISED, bd=1, bg="#e0e0e0").pack(side=tk.LEFT, padx=15)
        tk.Button(btn_frame, text="Назад", command=self.go_back, width=12, height=2, font=("Arial", 12), 
            relief=tk.RAISED, bd=1, bg="#e0e0e0").pack(side=tk.LEFT, padx=15)

    def toggle_password(self):
        if self.entry_password.cget("show") == "*":
            self.entry_password.config(show="")
        else:
            self.entry_password.config(show="*")

    def toggle_confirm(self):
        if self.entry_confirm.cget("show") == "*":
            self.entry_confirm.config(show="")
        else:
            self.entry_confirm.config(show="*")

    def register(self):
        login = self.entry_login.get().strip()
        password = self.entry_password.get().strip()
        confirm = self.entry_confirm.get().strip()

        if not (4 <= len(login) <= 10):
            messagebox.showerror("Ошибка",
                                 "Логин 4-10 символов")
            return

        if not (4 <= len(password) <= 10):
            messagebox.showerror("Ошибка",
                                 "Пароль 4-10 символов")
            return

        if password != confirm:
            messagebox.showerror("Ошибка",
                                 "Пароли не совпадают")
            return

        try:
            response = requests.post(
                "http://127.0.0.1:5000/register",
                json={
                    "login": login,
                    "password": password
                }
            )

            data = response.json()

            if data.get("status") == "success":
                messagebox.showinfo("Успех",
                                    "Регистрация успешна!")
                self.go_back()
            else:
                messagebox.showerror("Ошибка",
                                     data.get("message"))

        except Exception as e:
            messagebox.showerror("Ошибка соединения",
                                 str(e))

    def go_back(self):
        from gui.auth_window import AuthWindow
        self.parent.show_frame(AuthWindow)