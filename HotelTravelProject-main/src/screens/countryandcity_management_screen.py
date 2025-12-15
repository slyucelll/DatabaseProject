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
            fg="#1f1f1f",
            bg="#ffffff",
            activebackground="#e6e6e6",
            activeforeground="#000000",
            relief="flat",
            bd=1,
            highlightthickness=0,
            padx=10,
            pady=6,
            **kwargs
        )
        self.bind("<Enter>", lambda e: self.config(bg="#f0f0f0"))
        self.bind("<Leave>", lambda e: self.config(bg="#ffffff"))


class CountryAndCityManagementScreen(tk.Frame):
    def __init__(self, master, on_back, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.master = master
        self.on_back = on_back

        # ================= BACKGROUND =================
        img_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "images",
            "cac_mng_screen.jpg"
        )
        try:
            if os.path.exists(img_path):
                img = Image.open(img_path).resize((1200, 700))
                self.bg_image = ImageTk.PhotoImage(img)
                bg = tk.Label(self, image=self.bg_image)
                bg.place(x=0, y=0, relwidth=1, relheight=1)
                bg.lower()
        except:
            self.configure(bg="white")

        # ================= UI =================
        self.country_listbox = tk.Listbox(self, width=30, height=15, font=("Arial", 11))
        self.country_listbox.place(relx=0.25, rely=0.32, anchor="n")
        self.country_listbox.bind("<<ListboxSelect>>", self.on_country_selected)

        self.country_entry = tk.Entry(self, width=25, font=("Arial", 11))
        self.country_entry.place(relx=0.25, rely=0.75, anchor="n")

        ModernButton(self, text="Add Country", width=14, command=self.add_country)\
            .place(relx=0.12, rely=0.80, anchor="n")
        ModernButton(self, text="Update Selected", width=14, command=self.update_country)\
            .place(relx=0.26, rely=0.80, anchor="n")
        ModernButton(self, text="Delete Selected", width=14, command=self.delete_country)\
            .place(relx=0.40, rely=0.80, anchor="n")

        self.city_listbox = tk.Listbox(self, width=40, height=15, font=("Arial", 11))
        self.city_listbox.place(relx=0.70, rely=0.32, anchor="n")

        tk.Label(self, text="Country for new city:", font=("Arial", 10))\
            .place(relx=0.62, rely=0.66, anchor="w")

        self.country_combo_for_city = ttk.Combobox(self, state="readonly", width=22)
        self.country_combo_for_city.place(relx=0.62, rely=0.70, anchor="w")

        self.city_entry = tk.Entry(self, width=28, font=("Arial", 11))
        self.city_entry.place(relx=0.62, rely=0.74, anchor="w")

        ModernButton(self, text="Add City", width=14, command=self.add_city)\
            .place(relx=0.58, rely=0.82, anchor="w")
        ModernButton(self, text="Update Selected", width=14, command=self.update_city)\
            .place(relx=0.72, rely=0.82, anchor="w")
        ModernButton(self, text="Delete Selected", width=14, command=self.delete_city)\
            .place(relx=0.86, rely=0.82, anchor="w")

        ModernButton(self, text="← Back", width=10, command=self.on_back)\
            .place(relx=0.08, rely=0.92, anchor="w")

        self.load_countries()

    # ================= LOAD =================
    def load_countries(self):
        self.country_listbox.delete(0, tk.END)

        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT CountryId, CountryName FROM Countries ORDER BY CountryName")

        self.countries = {}
        for r in cur.fetchall():
            self.countries[r.CountryName] = r.CountryId
            self.country_listbox.insert(tk.END, r.CountryName)

        self.country_combo_for_city["values"] = list(self.countries.keys())
        conn.close()

    def load_cities(self, country_name):
        self.city_listbox.delete(0, tk.END)

        if not country_name:
            return

        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT CityName
            FROM Cities
            WHERE CountryId = ?
            ORDER BY CityName
        """, (self.countries[country_name],))

        for c in cur.fetchall():
            self.city_listbox.insert(tk.END, c.CityName)

        conn.close()

    # ================= COUNTRY CRUD =================
    def add_country(self):
        name = self.country_entry.get().strip()
        if not name:
            return

        conn = get_connection()
        cur = conn.cursor()
        try:
            cur.execute("INSERT INTO Countries (CountryName) VALUES (?)", (name,))
            conn.commit()
        except:
            messagebox.showwarning("Warning", "Country already exists.")
        conn.close()

        self.country_entry.delete(0, tk.END)
        self.load_countries()

    def update_country(self):
        sel = self.country_listbox.curselection()
        if not sel:
            return

        old_name = self.country_listbox.get(sel[0])
        new_name = self.country_entry.get().strip()
        if not new_name:
            return

        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "UPDATE Countries SET CountryName=? WHERE CountryId=?",
            (new_name, self.countries[old_name])
        )
        conn.commit()
        conn.close()

        self.country_entry.delete(0, tk.END)
        self.load_countries()

    def delete_country(self):
        sel = self.country_listbox.curselection()
        if not sel:
            return

        name = self.country_listbox.get(sel[0])

        conn = get_connection()
        cur = conn.cursor()
        try:
            cur.execute("DELETE FROM Countries WHERE CountryId=?", (self.countries[name],))
            conn.commit()
        except:
            messagebox.showerror("Error", "Country has cities. Delete cities first.")
        conn.close()

        self.load_countries()
        self.city_listbox.delete(0, tk.END)

    # ================= CITY CRUD =================
    def add_city(self):
        country = self.country_combo_for_city.get()
        city = self.city_entry.get().strip()
        if not country or not city:
            return

        conn = get_connection()
        cur = conn.cursor()
        try:
            cur.execute(
                "INSERT INTO Cities (CountryId, CityName) VALUES (?, ?)",
                (self.countries[country], city)
            )
            conn.commit()
        except:
            messagebox.showwarning("Warning", "City already exists in this country.")
        conn.close()

        self.city_entry.delete(0, tk.END)
        self.load_cities(country)

    def update_city(self):
        sel_city = self.city_listbox.curselection()
        if not sel_city:
            messagebox.showinfo("Update", "Select a city to update.")
            return

        new_city = self.city_entry.get().strip()
        if not new_city:
            messagebox.showerror("Error", "New city name cannot be empty.")
            return

        old_city = self.city_listbox.get(sel_city[0])
        country = self.country_combo_for_city.get()

        if not country:
            messagebox.showerror("Error", "Select a country.")
            return

        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            UPDATE Cities
            SET CityName = ?
            WHERE CityName = ? AND CountryId = ?
        """, (new_city, old_city, self.countries[country]))

        conn.commit()
        conn.close()

        self.city_entry.delete(0, tk.END)
        self.load_cities(country)
        messagebox.showinfo("Success", "City updated.")

    def delete_city(self):
        sel_city = self.city_listbox.curselection()
        if not sel_city:
            messagebox.showinfo("Delete", "Select a city to delete.")
            return

        city = self.city_listbox.get(sel_city[0])
        country = self.country_combo_for_city.get()

        if not country:
            messagebox.showerror("Error", "Select a country.")
            return

        ok = messagebox.askyesno(
            "Confirm delete",
            f"Delete city '{city}' from '{country}'?"
        )
        if not ok:
            return

        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            DELETE FROM Cities
            WHERE CityName = ? AND CountryId = ?
        """, (city, self.countries[country]))

        conn.commit()
        conn.close()

        self.load_cities(country)
        messagebox.showinfo("Deleted", "City deleted.")



    # ================= EVENTS =================
    def on_country_selected(self, event=None):
        sel = self.country_listbox.curselection()
        if not sel:
            return

        country = self.country_listbox.get(sel[0])
        self.country_combo_for_city.set(country)
        self.load_cities(country)
