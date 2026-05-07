# gui/register_window.py
import tkinter as tk
import requests
from tkinter import messagebox

class RegisterWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Регистрация")
        self.geometry("420x420")
        self.resizable(False, False)
        self.configure(bg="#f0f0f0")
        self.create_widgets()
        self.center_window()
    
    def center_window(self):
        self.update_idletasks()
        w = self.winfo_width()
        h = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (w // 2)
        y = (self.winfo_screenheight() // 2) - (h // 2)
        self.geometry(f"{w}x{h}+{x}+{y}")
    
    def create_widgets(self):
        tk.Label(self, text="Регистрация", font=("Arial", 14, "bold"), bg="#f0f0f0").pack(pady=20)
        
        center_frame = tk.Frame(self, bg="#f0f0f0")
        center_frame.pack(expand=True)
        
        # Логин
        tk.Label(center_frame, text="Логин (4-10):", font=("Arial", 10), bg="#f0f0f0", width=12, anchor="e").grid(row=0, column=0, padx=5, pady=8, sticky="e")
        self.entry_login = tk.Entry(center_frame, width=20, font=("Arial", 10))
        self.entry_login.grid(row=0, column=1, padx=5, pady=8)
        
        # Пароль
        tk.Label(center_frame, text="Пароль (4-10):", font=("Arial", 10), bg="#f0f0f0", width=12, anchor="e").grid(row=1, column=0, padx=5, pady=8, sticky="e")
        self.entry_password = tk.Entry(center_frame, width=20, font=("Arial", 10), show="*")
        self.entry_password.grid(row=1, column=1, padx=5, pady=8)
        self.eye1 = tk.Button(center_frame, text="👁", command=self.toggle_pass, width=3, bg="#cccccc", relief=tk.RAISED, bd=1)
        self.eye1.grid(row=1, column=2, padx=2, pady=8)
        
        # Подтверждение
        tk.Label(center_frame, text="Подтверждение:", font=("Arial", 10), bg="#f0f0f0", width=12, anchor="e").grid(row=2, column=0, padx=5, pady=8, sticky="e")
        self.entry_confirm = tk.Entry(center_frame, width=20, font=("Arial", 10), show="*")
        self.entry_confirm.grid(row=2, column=1, padx=5, pady=8)
        self.eye2 = tk.Button(center_frame, text="👁", command=self.toggle_confirm, width=3, bg="#cccccc", relief=tk.RAISED, bd=1)
        self.eye2.grid(row=2, column=2, padx=2, pady=8)
        
        # Кнопки
        btn_frame = tk.Frame(center_frame, bg="#f0f0f0")
        btn_frame.grid(row=3, column=0, columnspan=3, pady=30)
        tk.Button(btn_frame, text="Зарегистрироваться", command=self.register, bg="#cccccc", fg="#000000", font=("Arial", 10), relief=tk.RAISED, bd=2).pack(side=tk.LEFT, padx=10)
        tk.Button(btn_frame, text="Назад", command=self.destroy, bg="#cccccc", fg="#000000", font=("Arial", 10), relief=tk.RAISED, bd=2).pack(side=tk.LEFT, padx=10)
    
    def toggle_pass(self):
        if self.entry_password.cget("show") == "*":
            self.entry_password.config(show="")
            self.eye1.config(text="👁‍🗨")
        else:
            self.entry_password.config(show="*")
            self.eye1.config(text="👁")
    
    def toggle_confirm(self):
        if self.entry_confirm.cget("show") == "*":
            self.entry_confirm.config(show="")
            self.eye2.config(text="👁‍🗨")
        else:
            self.entry_confirm.config(show="*")
            self.eye2.config(text="👁")
    
    def register(self):
        login = self.entry_login.get().strip()
        password = self.entry_password.get().strip()
        confirm = self.entry_confirm.get().strip()

        if not (4 <= len(login) <= 10):
            messagebox.showerror("Ошибка", "Логин 4-10 символов")
            return
        if not (4 <= len(password) <= 10):
            messagebox.showerror("Ошибка", "Пароль 4-10 символов")
            return
        if password != confirm:
            messagebox.showerror("Ошибка", "Пароли не совпадают")
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
                messagebox.showinfo("Успех", "Регистрация успешна!")
                self.destroy()
            else:
                messagebox.showerror("Ошибка", data.get("message"))

        except Exception as e:
            messagebox.showerror("Ошибка соединения", str(e))