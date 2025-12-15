import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import os
import hashlib

from database.db import get_connection


# ---------------- MODERN BUTTON ----------------
class ModernButton(tk.Button):
    def __init__(self, master=None, **kwargs):
        super().__init__(
            master,
            font=("Arial", 12, "bold"),
            fg="#1f1f1f",
            bg="#ffffff",
            activebackground="#e6e6e6",
            activeforeground="#000000",
            relief="flat",
            bd=2,
            highlightthickness=0,
            padx=12,
            pady=6,
            **kwargs
        )
        self.bind("<Enter>", lambda e: self.config(bg="#f0f0f0"))
        self.bind("<Leave>", lambda e: self.config(bg="#ffffff"))


def hash_password(pw: str) -> str:
    return hashlib.sha256(pw.encode()).hexdigest()


# ---------------- USERS MANAGEMENT ----------------
class UsersManagementScreen(tk.Frame):

    def __init__(self, master, on_back, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.master = master
        self.on_back = on_back
        self.current_user_id = None

        # BACKGROUND
        self.configure(bg="white")
        img_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "images",
            "users_mg_screenn.jpg"
        )
        if os.path.exists(img_path):
            try:
                img = Image.open(img_path).resize((1200, 700))
                self.bg_image = ImageTk.PhotoImage(img)
                tk.Label(self, image=self.bg_image).place(x=0, y=0, relwidth=1, relheight=1)
            except:
                pass

        # ------------ LISTBOX ------------
        self.user_listbox = tk.Listbox(self, width=53, height=18, font=("Arial", 12))
        self.user_listbox.place(x=150, y=180)
        self.user_listbox.bind("<<ListboxSelect>>", self.on_select)

        # ------------ FIND USER ------------
        self.search_entry = tk.Entry(self, width=25, font=("Arial", 12))
        self.search_entry.place(x=150, y=530)

        ModernButton(self, text="Find User", width=5, command=self.find_user)\
            .place(x=370, y=530)

        # ------------ INPUTS (RIGHT) ------------
        self.fn_entry = tk.Entry(self, width=30, font=("Arial", 13))
        self.fn_entry.place(x=760, y=190)

        self.ln_entry = tk.Entry(self, width=30, font=("Arial", 13))
        self.ln_entry.place(x=760, y=248)

        self.email_entry = tk.Entry(self, width=30, font=("Arial", 13))
        self.email_entry.place(x=760, y=320)

        self.dob_entry = tk.Entry(self, width=30, font=("Arial", 13))
        self.dob_entry.place(x=760, y=380)

        self.role_combo = ttk.Combobox(
            self, state="readonly", width=27, font=("Arial", 12)
        )
        self.role_combo.place(x=750, y=445)

        # ------------ BUTTONS ------------
        ModernButton(self, text="Add User", width=12, command=self.add_user)\
            .place(x=600, y=550)

        ModernButton(self, text="Update Selected", width=12, command=self.update_user)\
            .place(x=800, y=550)

        ModernButton(self, text="Delete Selected", width=12, command=self.delete_user)\
            .place(x=1000, y=550)

        ModernButton(self, text="Review All", width=12, command=self.review_all)\
            .place(x=250, y=580)

        ModernButton(self, text="← Back", width=12, command=self.on_back)\
            .place(x=60, y=580)

        self.load_roles()
        self.load_users()

    # ---------------- LOAD ROLES ----------------
    def load_roles(self):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT RoleName FROM Roles ORDER BY RoleName")
        self.role_combo["values"] = [r.RoleName for r in cur.fetchall()]
        conn.close()

    # ---------------- LOAD USERS ----------------
    def load_users(self):
        self.user_listbox.delete(0, tk.END)
        self.current_user_id = None

        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT 
                U.UserId,
                U.FirstName,
                U.LastName,
                U.Email,
                U.BirthDate,
                R.RoleName
            FROM Users U
            JOIN Roles R ON U.RoleId = R.RoleId
            WHERE U.IsActive = 1
            ORDER BY U.UserId
        """)

        for u in cur.fetchall():
            birth = str(u.BirthDate) if u.BirthDate else "-"
            self.user_listbox.insert(
                tk.END,
                f"{u.UserId} • {u.FirstName} {u.LastName} • {u.Email} • {birth} • {u.RoleName}"
            )

        conn.close()
        self.clear_inputs()

    # ---------------- CLEAR INPUTS ----------------
    def clear_inputs(self):
        self.fn_entry.delete(0, tk.END)
        self.ln_entry.delete(0, tk.END)
        self.email_entry.delete(0, tk.END)
        self.dob_entry.delete(0, tk.END)
        self.role_combo.set("")

    # ---------------- SELECT USER ----------------
    def on_select(self, event):
        sel = self.user_listbox.curselection()
        if not sel:
            return

        user_id = int(self.user_listbox.get(sel[0]).split("•")[0].strip())
        self.current_user_id = user_id

        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT 
                U.FirstName,
                U.LastName,
                U.Email,
                U.BirthDate,
                R.RoleName
            FROM Users U
            JOIN Roles R ON U.RoleId =  R.RoleId
            WHERE U.UserId = ?
        """, (user_id,))
        u = cur.fetchone()
        conn.close()

        self.fn_entry.delete(0, tk.END)
        self.fn_entry.insert(0, u.FirstName)

        self.ln_entry.delete(0, tk.END)
        self.ln_entry.insert(0, u.LastName)

        self.email_entry.delete(0, tk.END)
        self.email_entry.insert(0, u.Email)

        # ✅ FIXED BIRTHDATE
        self.dob_entry.delete(0, tk.END)
        if u.BirthDate:
            bd = u.BirthDate
            if hasattr(bd, "strftime"):
                bd = bd.strftime("%Y-%m-%d")
            self.dob_entry.insert(0, bd)

        self.role_combo.set(u.RoleName)

    # ---------------- ADD USER ----------------
    def add_user(self):
        fname = self.fn_entry.get().strip()
        lname = self.ln_entry.get().strip()
        email = self.email_entry.get().strip()
        birth = self.dob_entry.get().strip() or None
        role_name = self.role_combo.get()

        if not fname or not lname or not email or not role_name:
            messagebox.showerror("Error", "Please fill required fields.")
            return

        conn = get_connection()
        cur = conn.cursor()

        cur.execute("SELECT RoleId FROM Roles WHERE RoleName = ?", (role_name,))
        role = cur.fetchone()
        if not role:
            conn.close()
            return

        try:
            cur.execute("""
                INSERT INTO Users 
                    (FirstName, LastName, Email, BirthDate, PasswordHash, RoleId)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                fname,
                lname,
                email,
                birth,
                hash_password("1234"),
                role.RoleId
            ))
            conn.commit()
        except Exception as e:
            messagebox.showerror("DB Error", str(e))
        finally:
            conn.close()

        self.load_users()
        messagebox.showinfo("Added", "User added. Default password: 1234")

    # ---------------- UPDATE USER ----------------
    # ---------------- UPDATE USER ----------------
    def update_user(self):
        if not self.current_user_id:
            return

        fname = self.fn_entry.get().strip()
        lname = self.ln_entry.get().strip()
        email = self.email_entry.get().strip()
        birth = self.dob_entry.get().strip() or None
        role_name = self.role_combo.get()

        conn = get_connection()
        cur = conn.cursor()

        # 🔹 Mevcut kullanıcıyı DB'den al
        cur.execute("""
            SELECT 
                U.FirstName,
                U.LastName,
                U.Email,
                U.BirthDate,
                R.RoleName
            FROM Users U
            JOIN Roles R ON U.RoleId = R.RoleId
            WHERE U.UserId = ?
        """, (self.current_user_id,))
        current = cur.fetchone()

        # 🔹 Hiçbir şey değişmediyse
        if (
                current.FirstName == fname and
                current.LastName == lname and
                current.Email == email and
                (str(current.BirthDate) if current.BirthDate else None) == birth and
                current.RoleName == role_name
        ):
            conn.close()
            messagebox.showinfo("Info", "No changes detected. Update cancelled.")
            return

        # 🔹 RoleId al
        cur.execute("SELECT RoleId FROM Roles WHERE RoleName = ?", (role_name,))
        role = cur.fetchone()

        # 🔹 Gerçek update
        cur.execute("""
            UPDATE Users
            SET FirstName=?, LastName=?, Email=?, BirthDate=?, RoleId=?
            WHERE UserId=?
        """, (
            fname,
            lname,
            email,
            birth,
            role.RoleId,
            self.current_user_id
        ))

        conn.commit()
        conn.close()

        self.load_users()
        messagebox.showinfo("Updated", "User updated successfully.")

    # ---------------- DELETE USER (SOFT) ----------------
    def delete_user(self):
        if not self.current_user_id:
            return

        if not messagebox.askyesno("Confirm", "Deactivate selected user?"):
            return

        conn = get_connection()
        cur = conn.cursor()
        cur.execute("UPDATE Users SET IsActive=0 WHERE UserId=?", (self.current_user_id,))
        conn.commit()
        conn.close()

        self.load_users()
        messagebox.showinfo("Deleted", "User deactivated.")

    # ---------------- FIND USER ----------------
    def find_user(self):
        key = self.search_entry.get().strip().lower()
        if not key:
            return

        for i in range(self.user_listbox.size()):
            if key in self.user_listbox.get(i).lower():
                self.user_listbox.selection_clear(0, tk.END)
                self.user_listbox.selection_set(i)
                self.user_listbox.see(i)
                self.on_select(None)
                return

        messagebox.showinfo("Not found", "No matching user.")

    # ---------------- REVIEW ALL ----------------
    def review_all(self):
        win = tk.Toplevel(self)
        win.title("All Users")
        win.geometry("600x400")

        txt = tk.Text(win, font=("Arial", 11))
        txt.pack(fill="both", expand=True)

        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT 
                U.UserId,
                U.FirstName,
                U.LastName,
                U.Email,
                U.BirthDate,
                R.RoleName
            FROM Users U
            JOIN Roles R ON U.RoleId = R.RoleId
            WHERE U.IsActive = 1
        """)

        for u in cur.fetchall():
            txt.insert(
                tk.END,
                f"ID: {u.UserId}\n"
                f"Name: {u.FirstName} {u.LastName}\n"
                f"Email: {u.Email}\n"
                f"Birth Date: {u.BirthDate}\n"
                f"Role: {u.RoleName}\n"
                "----------------------\n"
            )

        conn.close()
        txt.config(state="disabled")
