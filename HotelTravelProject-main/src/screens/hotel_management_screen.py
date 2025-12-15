import tkinter as tk
from tkinter import messagebox, ttk
from PIL import Image, ImageTk
import os

from database.db import get_connection


class ModernButton(tk.Button):
    def __init__(self, master=None, **kwargs):
        super().__init__(
            master,
            font=("Arial", 11, "bold"),
            bg="#ffffff",
            relief="flat",
            bd=1,
            padx=10,
            pady=6,
            **kwargs
        )
        self.bind("<Enter>", lambda e: self.config(bg="#f0f0f0"))
        self.bind("<Leave>", lambda e: self.config(bg="#ffffff"))


class HotelManagementScreen(tk.Frame):

    def __init__(self, master, on_back, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.master = master
        self.on_back = on_back
        self.current_hotel_id = None

        # ================= BACKGROUND =================
        img_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "images",
            "hotee_l.jpeg"
        )
        if os.path.exists(img_path):
            img = Image.open(img_path).resize((1200, 700))
            self.bg_image = ImageTk.PhotoImage(img)
            tk.Label(self, image=self.bg_image).place(x=0, y=0, relwidth=1, relheight=1)

        # ================= LEFT LIST =================
        self.hotels_listbox = tk.Listbox(self, width=48, height=20, font=("Arial", 11))
        self.hotels_listbox.place(relx=0.10, rely=0.23)
        self.hotels_listbox.bind("<<ListboxSelect>>", self.on_hotel_selected)

        self.search_var = tk.StringVar()
        tk.Entry(self, textvariable=self.search_var, width=26).place(relx=0.10, rely=0.78)

        ModernButton(self, text="Search", command=self.search_hotels).place(relx=0.10, rely=0.82)
        ModernButton(self, text="Reload", command=self.load_hotels).place(relx=0.10, rely=0.82)

        # ================= RIGHT FORM =================
        base_x = 0.61

        self.name_entry = tk.Entry(self, width=38)
        self.name_entry.place(relx=0.61, rely=0.24)

        self.country_combo = ttk.Combobox(self, state="readonly", width=35)
        self.country_combo.place(relx=0.61, rely=0.31)
        self.country_combo.bind("<<ComboboxSelected>>", self.load_cities)

        self.city_combo = ttk.Combobox(self, state="readonly", width=35)
        self.city_combo.place(relx=base_x, rely=0.40)

        self.address_entry = tk.Entry(self, width=45)
        self.address_entry.place(relx=base_x, rely=0.48)

        self.stars_spin = tk.Spinbox(self, from_=1, to=5, width=5)
        self.stars_spin.place(relx=base_x, rely=0.58)

        self.desc_entry = tk.Text(self, width=30, height=3)
        self.desc_entry.place(relx=base_x, rely=0.65)

        self.status_combo = ttk.Combobox(
            self,
            values=["Active", "Inactive"],
            width=14,
            state="readonly"
        )
        self.status_combo.place(relx=base_x, rely=0.75)
        self.status_combo.set("Active")

        # ================= BUTTONS =================
        ModernButton(self, text="Add Hotel", command=self.add_hotel).place(relx=0.55, rely=0.90)
        ModernButton(self, text="Update Selected", command=self.update_hotel).place(relx=0.68, rely=0.90)
        ModernButton(self, text="Delete Selected", command=self.delete_hotel).place(relx=0.83, rely=0.90)
        ModernButton(self, text="← Back", command=self.on_back).place(relx=0.06, rely=0.90)

        self.load_countries()
        self.load_hotels()

    # ================= LOADERS =================
    def load_countries(self):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT CountryId, CountryName FROM Countries ORDER BY CountryName")
        self.countries = {row.CountryName: row.CountryId for row in cur.fetchall()}
        self.country_combo["values"] = list(self.countries.keys())
        conn.close()

    def load_cities(self, event=None):
        country_name = self.country_combo.get()
        if not country_name:
            return

        country_id = self.countries[country_name]
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "SELECT CityId, CityName FROM Cities WHERE CountryId=? ORDER BY CityName",
            (country_id,)
        )
        self.cities = {row.CityName: row.CityId for row in cur.fetchall()}
        self.city_combo["values"] = list(self.cities.keys())
        conn.close()

    def load_hotels(self):
        self.hotels_listbox.delete(0, tk.END)
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT h.HotelId, h.HotelName, c.CityName
            FROM Hotels h
            JOIN Cities c ON h.CityId = c.CityId
            WHERE h.IsActive = 1
            ORDER BY h.HotelName
        """)
        for h in cur.fetchall():
            self.hotels_listbox.insert(
                tk.END,
                f"{h.HotelId:04d} — {h.HotelName} ({h.CityName})"
            )
        conn.close()
        self.clear_inputs()

    # ================= CRUD =================
    def add_hotel(self):
        if not self.city_combo.get():
            messagebox.showerror("Error", "Select country and city.")
            return

        city_id = self.cities[self.city_combo.get()]

        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO Hotels (CityId, HotelName, Address, Stars, Description, IsActive)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            city_id,
            self.name_entry.get(),
            self.address_entry.get(),
            int(self.stars_spin.get()),
            self.desc_entry.get("1.0", tk.END).strip(),
            1 if self.status_combo.get() == "Active" else 0
        ))
        conn.commit()
        conn.close()

        self.load_hotels()
        messagebox.showinfo("Success", "Hotel added.")

    def update_hotel(self):
        if not self.current_hotel_id:
            return

        conn = get_connection()
        cur = conn.cursor()

        # mevcut veriyi al
        cur.execute("""
            SELECT CityId, HotelName, Address, Stars, Description, IsActive
            FROM Hotels
            WHERE HotelId = ?
        """, (self.current_hotel_id,))
        current = cur.fetchone()

        city_id = self.cities[self.city_combo.get()]
        new_data = (
            city_id,
            self.name_entry.get(),
            self.address_entry.get(),
            int(self.stars_spin.get()),
            self.desc_entry.get("1.0", tk.END).strip(),
            1 if self.status_combo.get() == "Active" else 0
        )

        # HİÇBİR ŞEY DEĞİŞMEDİYSE
        if (
                current.CityId == new_data[0] and
                current.HotelName == new_data[1] and
                (current.Address or "") == (new_data[2] or "") and
                current.Stars == new_data[3] and
                (current.Description or "") == (new_data[4] or "") and
                current.IsActive == new_data[5]
        ):
            conn.close()
            messagebox.showinfo("Info", "No changes detected.")
            return

        # gerçekten değişiklik varsa update
        cur.execute("""
            UPDATE Hotels
            SET CityId=?, HotelName=?, Address=?, Stars=?, Description=?, IsActive=?
            WHERE HotelId=?
        """, (*new_data, self.current_hotel_id))

        conn.commit()
        conn.close()

        self.load_hotels()
        messagebox.showinfo("Updated", "Hotel updated.")

    def delete_hotel(self):
        if not self.current_hotel_id:
            return

        if not messagebox.askyesno("Confirm", "Deactivate selected hotel?"):
            return

        conn = get_connection()
        cur = conn.cursor()

        # 1️⃣ HOTEL SOFT DELETE
        cur.execute("""
            UPDATE Hotels
            SET IsActive = 0
            WHERE HotelId = ?
        """, (self.current_hotel_id,))

        # 2️⃣ CASCADE SOFT DELETE (ROOMS)
        cur.execute("""
            UPDATE HotelRooms
            SET IsActive = 0
            WHERE HotelId = ?
        """, (self.current_hotel_id,))

        conn.commit()
        conn.close()

        self.load_hotels()
        messagebox.showinfo("Deactivated", "Hotel and its rooms deactivated.")

    # ================= SELECT =================
    def on_hotel_selected(self, event=None):
        sel = self.hotels_listbox.curselection()
        if not sel:
            return

        hotel_id = int(self.hotels_listbox.get(sel[0]).split("—")[0].strip())
        self.current_hotel_id = hotel_id

        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT h.*, c.CityName, co.CountryName
            FROM Hotels h
            JOIN Cities c ON h.CityId = c.CityId
            JOIN Countries co ON c.CountryId = co.CountryId
            WHERE h.HotelId=?
        """, (hotel_id,))
        h = cur.fetchone()
        conn.close()

        self.name_entry.delete(0, tk.END)
        self.name_entry.insert(0, h.HotelName)

        self.address_entry.delete(0, tk.END)
        self.address_entry.insert(0, h.Address)

        self.stars_spin.delete(0, tk.END)
        self.stars_spin.insert(0, h.Stars)

        self.desc_entry.delete("1.0", tk.END)
        self.desc_entry.insert("1.0", h.Description or "")

        self.status_combo.set("Active" if h.IsActive else "Inactive")

        self.country_combo.set(h.CountryName)
        self.load_cities()
        self.city_combo.set(h.CityName)

    def search_hotels(self):
        q = self.search_var.get().lower()
        self.hotels_listbox.delete(0, tk.END)

        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT h.HotelId, h.HotelName, c.CityName
            FROM Hotels h
            JOIN Cities c ON h.CityId = c.CityId
            WHERE h.IsActive = 1
              AND LOWER(h.HotelName) LIKE ?
        """, (f"%{q}%",))
        for h in cur.fetchall():
            self.hotels_listbox.insert(
                tk.END,
                f"{h.HotelId:04d} — {h.HotelName} ({h.CityName})"
            )
        conn.close()

    def clear_inputs(self):
        self.current_hotel_id = None
        self.name_entry.delete(0, tk.END)
        self.address_entry.delete(0, tk.END)
        self.stars_spin.delete(0, tk.END)
        self.stars_spin.insert(0, "1")
        self.desc_entry.delete("1.0", tk.END)
        self.status_combo.set("Active")
