import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import os
import datetime
import re

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
        self.configure(borderwidth=1)
        self.bind("<Enter>", lambda e: self.config(bg="#f0f0f0"))
        self.bind("<Leave>", lambda e: self.config(bg="#ffffff"))



class RegisterScreen(tk.Frame):
    def __init__(self, master, on_back_to_login, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.on_back_to_login = on_back_to_login

        img_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "images",
            "register2.jpg"
        )

        img = Image.open(img_path).resize((1200, 700))
        self.bg_image = ImageTk.PhotoImage(img)
        tk.Label(self, image=self.bg_image).place(x=0, y=0, relwidth=1, relheight=1)


        self.first_name = tk.Entry(self, width=30, font=("Arial", 13))
        self.first_name.place(relx=0.5, rely=0.32, anchor="center")

        self.last_name = tk.Entry(self, width=30, font=("Arial", 13))
        self.last_name.place(relx=0.5, rely=0.40, anchor="center")

        self.email = tk.Entry(self, width=30, font=("Arial", 13))
        self.email.place(relx=0.5, rely=0.47, anchor="center")

        self.phone = tk.Entry(self, width=30, font=("Arial", 13))
        self.phone.place(relx=0.5, rely=0.55, anchor="center")

        self.password = tk.Entry(self, width=30, font=("Arial", 13), show="*")
        self.password.place(relx=0.5, rely=0.64, anchor="center")

        self.birthdate = tk.Entry(self, width=30, font=("Arial", 13))
        self.birthdate.place(relx=0.5, rely=0.71, anchor="center")


        self.accept_terms = tk.BooleanVar()
        tk.Checkbutton(
            self,
            text="I accept the User Agreement",
            variable=self.accept_terms,
            fg="white",
            bg="black",
            selectcolor="black",
            font=("Arial", 10, "bold")
        ).place(relx=0.7, rely=0.8, anchor="center")


        ModernButton(
            self,
            text="REGISTER",
            width=18,
            command=self.register_user
        ).place(relx=0.7, rely=0.87, anchor="center")

        ModernButton(
            self,
            text="← Back",
            width=10,
            command=self.on_back_to_login
        ).place(relx=0.20, rely=0.84)


    def register_user(self):
        fname = self.first_name.get().strip()
        lname = self.last_name.get().strip()
        email = self.email.get().strip()
        phone = self.phone.get().strip()
        password = self.password.get().strip()
        dob = self.birthdate.get().strip()

        if any(not field.strip() for field in [fname, lname, email, phone, password, dob]):
            messagebox.showerror("Error", "All fields must be filled.")
            return

        if not re.match(r"^[^@]+@[^@]+\.[^@]+$", email):
            messagebox.showerror("Error", "Invalid e-mail format.")
            return

        if not re.match(r"^05\d{9}$", phone):
            messagebox.showerror("Error", "Phone number must be 05XXXXXXXXX.")
            return

        if not self.accept_terms.get():
            messagebox.showerror("Error", "You must accept the User Agreement.")
            return

        try:
            year, month, day = map(int, dob.split("-"))
            birth = f"{year:04d}-{month:02d}-{day:02d}"
        except:
            messagebox.showerror("Error", "Birthdate must be YYYY-MM-DD.")
            return

        age = datetime.date.today().year - year
        if age < 18:
            messagebox.showerror("Error", "You must be at least 18.")
            return

        conn = get_connection()
        cursor = conn.cursor()

        # Email unique check
        cursor.execute("SELECT 1 FROM Users WHERE Email = ?", (email,))
        if cursor.fetchone():
            conn.close()
            messagebox.showerror("Error", "This e-mail is already registered.")
            return

        # User role
        cursor.execute("SELECT RoleId FROM Roles WHERE RoleName = 'User'")
        role_id = cursor.fetchone()[0]

        # INSERT USER
        cursor.execute("""
            INSERT INTO Users
            (FirstName, LastName, Email, PasswordHash, BirthDate, RoleId, IsActive)
            VALUES (?, ?, ?, ?, ?, ?, 1)
        """, (fname, lname, email, password, birth, role_id))

        # GET USER ID VIA EMAIL (GARANTİLİ)
        cursor.execute(
            "SELECT UserId FROM Users WHERE Email = ?",
            (email,)
        )
        user_id = cursor.fetchone()[0]

        # INSERT PHONE
        cursor.execute("""
            INSERT INTO UserPhones (UserId, PhoneNumber, IsPrimary)
            VALUES (?, ?, 1)
        """, (user_id, phone))

        conn.commit()
        conn.close()

        messagebox.showinfo("Success", "Registration successful!")
        self.on_back_to_login()
