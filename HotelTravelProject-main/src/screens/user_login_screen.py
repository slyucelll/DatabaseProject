import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import os

from database.db import get_connection


class ModernButton(tk.Button):
    def __init__(self, master=None, **kwargs):
        super().__init__(
            master,
            font=("Arial", 12, "bold"),
            fg="#1f1f1f",
            bg="#ffffff",
            activebackground="#e6e6e6",
            relief="flat",
            bd=2,
            highlightthickness=0,
            padx=12,
            pady=6,
            **kwargs
        )
        self.bind("<Enter>", lambda e: self.config(bg="#f0f0f0"))
        self.bind("<Leave>", lambda e: self.config(bg="#ffffff"))



class UserLoginScreen(tk.Frame):
    def __init__(self, master, on_back, *args, **kwargs):
        super().__init__(master, *args, **kwargs)

        self.master = master
        self.on_back = on_back

        img_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "images",
            "userloginscreen.jpg"
        )

        img = Image.open(img_path).resize((1200, 700))
        self.bg_image = ImageTk.PhotoImage(img)
        tk.Label(self, image=self.bg_image).place(x=0, y=0, relwidth=1, relheight=1)

        self.email_entry = tk.Entry(self, width=30, font=("Arial", 13))
        self.email_entry.place(relx=0.50, rely=0.45, anchor="center")

        self.password_entry = tk.Entry(self, width=30, font=("Arial", 13), show="*")
        self.password_entry.place(relx=0.50, rely=0.59, anchor="center")

        self.show_pw = tk.BooleanVar()
        tk.Checkbutton(
            self,
            text="Show Password",
            variable=self.show_pw,
            command=self.toggle_password,
            fg="white",
            bg="black",
            selectcolor="black",
            font=("Arial", 10, "bold")
        ).place(relx=0.70, rely=0.59, anchor="center")

        ModernButton(self, text="← Back", width=10, command=self.on_back)\
            .place(relx=0.27, rely=0.75, anchor="center")

        ModernButton(self, text="LOGIN", width=10, command=self.on_login_clicked)\
            .place(relx=0.50, rely=0.75, anchor="center")

        ModernButton(self, text="REGISTER", width=10, command=self.go_register_screen)\
            .place(relx=0.70, rely=0.75, anchor="center")

    def toggle_password(self):
        self.password_entry.config(show="" if self.show_pw.get() else "*")

    def on_login_clicked(self):
        email = self.email_entry.get().strip()
        password = self.password_entry.get().strip()

        if not email or not password:
            messagebox.showerror("Error", "E-mail and password cannot be empty.")
            return

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT U.UserId
            FROM Users U
            JOIN Roles R ON U.RoleId = R.RoleId
            WHERE U.Email = ?
              AND U.PasswordHash = ?
              AND R.RoleName = 'User'
              AND U.IsActive = 1
        """, (email, password))

        user = cursor.fetchone()
        conn.close()

        if user:
            self.master.current_user_id = user[0]
            messagebox.showinfo("Login", "Login successful")
            self.master.show_travel_menu()
        else:
            messagebox.showerror("Login", "Invalid e-mail or password.")

    def go_register_screen(self):
        self.master.show_register()
