import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
from tkcalendar import DateEntry
import os

from database.db import get_connection


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


class SearchHotelsScreen(tk.Frame):
    def __init__(self, master, plan_data=None, on_back=None):
        super().__init__(master)

        self.master = master
        self.plan_data = plan_data or {}
        self.on_back = on_back

        # Nereden gelindi?
        self.from_menu = not bool(plan_data)
        self.user_triggered_search = False

        self.city = self.plan_data.get("city")


        img_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "images",
            "hotel_s.jpeg"
        )
        if os.path.exists(img_path):
            img = Image.open(img_path).resize((1200, 700))
            self.bg_image = ImageTk.PhotoImage(img)
            tk.Label(self, image=self.bg_image).place(x=0, y=0, relwidth=1, relheight=1)


        self.search_entry = tk.Entry(self, width=30, font=("Arial", 12))
        self.search_entry.place(relx=0.30, rely=0.32, anchor="w")

        # Create Plan’dan gelindiyse city otomatik dolu ve kilitli
        if not self.from_menu and self.city:
            self.search_entry.insert(0, self.city)
            self.search_entry.config(state="readonly")

        self.checkin_entry = DateEntry(self, width=15, date_pattern="yyyy-MM-dd")
        self.checkin_entry.place(relx=0.33, rely=0.39, anchor="w")

        self.checkout_entry = DateEntry(self, width=15, date_pattern="yyyy-MM-dd")
        self.checkout_entry.place(relx=0.33, rely=0.47, anchor="w")

        ModernButton(
            self,
            text="SEARCH",
            width=7,
            command=self.on_search_click
        ).place(relx=0.60, rely=0.32, anchor="center")

        self.results_list = tk.Listbox(self, width=70, height=10, font=("Arial", 11))
        self.results_list.place(relx=0.20, rely=0.50)

        ModernButton(self, text="← Back", width=7, command=self.on_back)\
            .place(relx=0.20, rely=0.80, anchor="center")

        ModernButton(self, text="Save Plan", width=7, command=self.save_plan)\
            .place(relx=0.72, rely=0.80, anchor="center")




    def on_search_click(self):
        self.user_triggered_search = True
        self.search_hotels()


    # CITY → CITY ID

    def _resolve_city_id(self, city_name):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT CityId
            FROM Cities
            WHERE CityName = ?
        """, (city_name,))
        row = cur.fetchone()
        conn.close()
        return row[0] if row else None


    def search_hotels(self):
        self.results_list.delete(0, tk.END)

        city = self.search_entry.get().strip()
        if not city:
            if self.user_triggered_search:
                messagebox.showinfo("Search", "Please enter a city name.")
            return

        city_id = self._resolve_city_id(city)
        if not city_id:
            if self.user_triggered_search:
                messagebox.showinfo("Search", "City not found.")
            return

        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT H.HotelName
            FROM Hotels H
            WHERE H.IsActive = 1 AND H.CityId = ?
            ORDER BY H.HotelName
        """, (city_id,))
        rows = cur.fetchall()
        conn.close()

        if not rows:
            if self.user_triggered_search:
                messagebox.showinfo("Search", "No hotels found in this city.")
            return

        for r in rows:
            self.results_list.insert(tk.END, r.HotelName)


    def save_plan(self):
        if self.from_menu:
            messagebox.showinfo("Info", "This action is only for travel plans.")
            return

        city_id = self._resolve_city_id(self.city)
        plan = self.plan_data

        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO TravelPlans
                (UserId, CityId, PlanName, StartDate, EndDate, NumberOfPeople, Budget)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                int(self.master.current_user_id),
                city_id,
                plan["plan_name"],
                plan["start_date"].strftime("%Y-%m-%d"),
                plan["end_date"].strftime("%Y-%m-%d"),
                plan["people"],
                float(plan["budget"])
            ))
            conn.commit()
            conn.close()
        except Exception as e:
            messagebox.showerror("DB Error", str(e))
            return

        messagebox.showinfo("Success", "Travel plan saved successfully.")
