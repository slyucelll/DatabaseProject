import tkinter as tk
from tkinter import messagebox, ttk
from PIL import Image, ImageTk
import os

from database.db import get_connection

try:
    from tkcalendar import DateEntry
except ImportError:
    DateEntry = None


class ModernButton(tk.Button):
    def __init__(self, master=None, **kwargs):
        super().__init__(
            master,
            font=("Arial", 12, "bold"),
            bg="#ffffff",
            relief="flat",
            bd=2,
            padx=12,
            pady=6,
            **kwargs
        )
        self.bind("<Enter>", lambda e: self.config(bg="#f0f0f0"))
        self.bind("<Leave>", lambda e: self.config(bg="#ffffff"))


class CreateTravelPlanScreen(tk.Frame):

    def __init__(self, master, on_back, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.master = master
        self.on_back = on_back


        img_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "images",
            "create_plan_screenn.jpg"
        )
        img = Image.open(img_path).resize((1200, 700))
        self.bg_image = ImageTk.PhotoImage(img)
        tk.Label(self, image=self.bg_image).place(x=0, y=0, relwidth=1, relheight=1)

        #  BUDGET MAP
        self.budget_value_map = {
            "< 500": 500,
            "500 - 1,000": 1000,
            "1,000 - 2,000": 2000,
            "2,000 - 5,000": 5000,
            "> 5,000": 10000
        }

        #  INPUTS
        self.plan_name_entry = tk.Entry(self, width=30, font=("Arial", 13))
        self.plan_name_entry.place(relx=0.35, rely=0.30, anchor="w")

        self.country_combo = ttk.Combobox(self, state="readonly", width=27, font=("Arial", 12))
        self.country_combo.place(relx=0.35, rely=0.38, anchor="w")
        self.country_combo.bind("<<ComboboxSelected>>", self.on_country_selected)

        self.city_combo = ttk.Combobox(self, state="readonly", width=27, font=("Arial", 12))
        self.city_combo.place(relx=0.35, rely=0.46, anchor="w")

        self.people_spin = tk.Spinbox(self, from_=1, to=20, width=5, font=("Arial", 13))
        self.people_spin.place(relx=0.35, rely=0.52, anchor="w")

        self.budget_combo = ttk.Combobox(
            self,
            values=list(self.budget_value_map.keys()),
            state="readonly",
            width=20,
            font=("Arial", 12)
        )
        self.budget_combo.place(relx=0.35, rely=0.60, anchor="w")
        self.budget_combo.set("Select budget range")

        self.start_date = DateEntry(self, width=18, date_pattern="yyyy-MM-dd")
        self.start_date.place(relx=0.35, rely=0.69, anchor="w")

        self.end_date = DateEntry(self, width=18, date_pattern="yyyy-MM-dd")
        self.end_date.place(relx=0.35, rely=0.78, anchor="w")

        # ================= BUTTONS =================
        ModernButton(self, text="← Back", width=10, command=self.on_back)\
            .place(relx=0.23, rely=0.83, anchor="center")


        ModernButton(
            self,
            text="SEARCH HOTEL",
            width=27,
            command=self.go_search_hotels
        ).place(relx=0.70, rely=0.83, anchor="center")

        self.country_map = {}
        self.city_map = {}
        self.load_countries()

    def load_countries(self):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT CountryId, CountryName FROM Countries ORDER BY CountryName")

        names = []
        for c in cur.fetchall():
            self.country_map[c.CountryName] = c.CountryId
            names.append(c.CountryName)

        conn.close()
        self.country_combo["values"] = names

    def on_country_selected(self, event=None):
        country_name = self.country_combo.get()
        country_id = self.country_map.get(country_name)

        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT CityId, CityName
            FROM Cities
            WHERE CountryId = ?
            ORDER BY CityName
        """, (country_id,))

        self.city_map.clear()
        names = []
        for c in cur.fetchall():
            self.city_map[c.CityName] = c.CityId
            names.append(c.CityName)

        conn.close()
        self.city_combo.set("")
        self.city_combo["values"] = names

    #  SEARCH HOTEL
    def go_search_hotels(self):
        plan_name = self.plan_name_entry.get().strip()
        country = self.country_combo.get()
        city = self.city_combo.get()
        people = int(self.people_spin.get())
        budget_text = self.budget_combo.get()

        if not plan_name or not country or not city:
            messagebox.showerror("Error", "All fields are required.")
            return

        if budget_text not in self.budget_value_map:
            messagebox.showerror("Error", "Select a budget range.")
            return

        start = self.start_date.get_date()
        end = self.end_date.get_date()

        if end < start:
            messagebox.showerror("Error", "End date cannot be before start date.")
            return

        plan_data = {
            "plan_name": plan_name,
            "country": country,
            "city": city,
            "people": people,
            "budget": self.budget_value_map[budget_text],
            "start_date": start,
            "end_date": end
        }

        self.master.show_search_hotel(plan_data)
