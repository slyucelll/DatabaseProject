import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import os

from database.db import get_connection


# ---- MODERN BUTON SINIFI ----
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
        self.configure(
            borderwidth=1,
            highlightbackground="#bbbbbb",
            highlightcolor="#bbbbbb"
        )
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)

    def on_enter(self, event):
        self["bg"] = "#f0f0f0"

    def on_leave(self, event):
        self["bg"] = "#ffffff"


class AdminLoginScreen(tk.Frame):
    def __init__(self, master, on_back, *args, **kwargs):
        super().__init__(master, *args, **kwargs)

        self.master = master
        self.on_back = on_back

        # ==== BACKGROUND FOTOĞRAF ====
        img_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "images",
            "Adminloginscreen.jpg"
        )

        if not os.path.exists(img_path):
            print(" Foto bulunamadı:", img_path)

        img = Image.open(img_path).resize((1200, 700))
        self.bg_image = ImageTk.PhotoImage(img)

        bg = tk.Label(self, image=self.bg_image)
        bg.place(x=0, y=0, relwidth=1, relheight=1)

        # ==== INPUTLAR ====
        self.email_entry = tk.Entry(self, width=30, font=("Arial", 14))
        self.email_entry.place(relx=0.50, rely=0.45, anchor="center")

        self.password_entry = tk.Entry(self, width=30, font=("Arial", 14), show="*")
        self.password_entry.place(relx=0.50, rely=0.59, anchor="center")

        # ==== SHOW / HIDE PASSWORD ====
        self.show_pw = tk.BooleanVar()
        show_pw_check = tk.Checkbutton(
            self,
            text="Show Password",
            variable=self.show_pw,
            command=self.toggle_password,
            fg="white",
            font=("Arial", 10, "bold")
        )
        show_pw_check.place(relx=0.70, rely=0.59, anchor="center")

        # ==== BUTONLAR ====
        login_btn = ModernButton(
            self,
            text="LOGIN",
            width=18,
            command=self.on_login_clicked
        )
        login_btn.place(relx=0.50, rely=0.75, anchor="center")

        back_btn = ModernButton(
            self,
            text="← Back",
            width=10,
            command=self.on_back
        )
        back_btn.place(relx=0.22, rely=0.82)

    def toggle_password(self):
        if self.show_pw.get():
            self.password_entry.config(show="")
        else:
            self.password_entry.config(show="*")

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
              AND R.RoleName = 'Admin'
              AND U.IsActive = 1
        """, (email, password))

        admin = cursor.fetchone()
        conn.close()

        if admin:
            self.master.current_user_id = admin[0]
            messagebox.showinfo("Admin Login", "Admin login successful")
            self.master.show_admin_menu()
        else:
            messagebox.showerror("Admin Login", "Invalid admin credentials")
