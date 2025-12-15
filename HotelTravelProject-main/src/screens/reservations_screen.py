import tkinter as tk
from tkinter import messagebox, ttk
from PIL import Image, ImageTk
from tkcalendar import DateEntry
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
            activeforeground="#000000",
            relief="flat",
            bd=2,
            padx=12,
            pady=6,
            **kwargs
        )
        self.bind("<Enter>", lambda e: self.config(bg="#f0f0f0"))
        self.bind("<Leave>", lambda e: self.config(bg="#ffffff"))


class MyReservationsScreen(tk.Frame):
    def __init__(self, master, on_back):
        super().__init__(master)

        self.master = master
        self.on_back = on_back

        self.current_reservation_id = None
        self.current_status_id = None

        #  STATUS MAP (DB’den)
        self.status_id_to_name = {}
        self.status_name_to_id = {}


        img_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "images",
            "r_screen.jpeg"
        )
        if os.path.exists(img_path):
            img = Image.open(img_path).resize((1200, 700))
            self.bg_image = ImageTk.PhotoImage(img)
            tk.Label(self, image=self.bg_image).place(x=0, y=0, relwidth=1, relheight=1)


        self.plan_combo = ttk.Combobox(
            self,
            state="readonly",
            width=28,
            font=("Arial", 12)
        )
        self.plan_combo.place(relx=0.41, rely=0.26, anchor="w")
        self.plan_combo.bind("<<ComboboxSelected>>", self.load_by_plan_name)


        self.hotel_name_entry = tk.Entry(self, width=30, font=("Arial", 12))
        self.hotel_name_entry.place(relx=0.56, rely=0.34, anchor="center")

        self.location_entry = tk.Entry(self, width=25, font=("Arial", 12))
        self.location_entry.place(relx=0.31, rely=0.44, anchor="w")

        self.total_price_entry = tk.Entry(self, width=15, font=("Arial", 12))
        self.total_price_entry.place(relx=0.31, rely=0.54, anchor="w")

        self.checkin_entry = DateEntry(self, width=15, font=("Arial", 12), date_pattern="yyyy-mm-dd")
        self.checkin_entry.place(relx=0.31, rely=0.64, anchor="w")

        self.checkout_entry = DateEntry(self, width=15, font=("Arial", 12), date_pattern="yyyy-mm-dd")
        self.checkout_entry.place(relx=0.66, rely=0.64, anchor="w")

        self.address_entry = tk.Entry(self, width=25, font=("Arial", 12))
        self.address_entry.place(relx=0.64, rely=0.44, anchor="w")

        self.guests_combo = ttk.Combobox(
            self,
            values=["1", "2", "3", "4", "5", "6"],
            width=10,
            font=("Arial", 12)
        )
        self.guests_combo.place(relx=0.63, rely=0.54, anchor="w")

        self.payment_status_combo = ttk.Combobox(
            self,
            state="readonly",
            width=12,
            font=("Arial", 12)
        )
        self.payment_status_combo.place(relx=0.35, rely=0.73, anchor="w")


        ModernButton(self, text="← Back", width=10, command=self.on_back)\
            .place(relx=0.20, rely=0.86, anchor="center")

        ModernButton(self, text="Cancel Reservation", width=18, command=self.cancel_reservation)\
            .place(relx=0.80, rely=0.86, anchor="center")

        #  LOAD DATA
        self.load_statuses()
        self.load_plan_names()


    # LOAD STATUS FROM DB (ReservationStatus)

    def load_statuses(self):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT StatusId, StatusName FROM ReservationStatus ORDER BY StatusId")
        rows = cur.fetchall()
        conn.close()

        names = []
        for r in rows:
            self.status_id_to_name[r.StatusId] = r.StatusName
            self.status_name_to_id[r.StatusName] = r.StatusId
            names.append(r.StatusName)

        self.payment_status_combo["values"] = names


    # LOAD PLAN NAMES

    def load_plan_names(self):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT DISTINCT TP.PlanName
            FROM TravelPlans TP
            JOIN Reservations R ON TP.TravelPlanId = R.TravelPlanId
            WHERE R.IsActive = 1
            ORDER BY TP.PlanName
        """)
        self.plan_combo["values"] = [r.PlanName for r in cur.fetchall()]
        conn.close()


    # LOAD RESERVATION

    def load_by_plan_name(self, event=None):
        plan_name = self.plan_combo.get()
        if not plan_name:
            return

        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT TOP 1
                R.ReservationId,
                R.StatusId,
                R.CheckInDate,
                R.CheckOutDate,
                R.Guests,
                R.TotalPrice,
                H.HotelName,
                H.Address,
                C.CityName,
                CO.CountryName
            FROM TravelPlans TP
            JOIN Reservations R ON TP.TravelPlanId = R.TravelPlanId
            JOIN HotelRooms HR ON R.RoomId = HR.RoomId
            JOIN Hotels H ON HR.HotelId = H.HotelId
            JOIN Cities C ON H.CityId = C.CityId
            JOIN Countries CO ON C.CountryId = CO.CountryId
            WHERE TP.PlanName = ?
            ORDER BY R.CreatedDate DESC
        """, (plan_name,))
        r = cur.fetchone()
        conn.close()

        if not r:
            messagebox.showwarning("Load", "No reservation found.")
            return

        self.current_reservation_id = r.ReservationId
        self.current_status_id = r.StatusId

        self.hotel_name_entry.delete(0, tk.END)
        self.hotel_name_entry.insert(0, r.HotelName)

        self.address_entry.delete(0, tk.END)
        self.address_entry.insert(0, r.Address)

        self.location_entry.delete(0, tk.END)
        self.location_entry.insert(0, f"{r.CityName}, {r.CountryName}")

        self.guests_combo.set(str(r.Guests))
        self.total_price_entry.delete(0, tk.END)
        self.total_price_entry.insert(0, str(r.TotalPrice))

        self.checkin_entry.set_date(r.CheckInDate)
        self.checkout_entry.set_date(r.CheckOutDate)

        self.payment_status_combo.set(
            self.status_id_to_name.get(r.StatusId, "")
        )

    def cancel_reservation(self):
        if not self.current_reservation_id:
            messagebox.showwarning("Cancel", "No reservation selected.")
            return

        #  ZATEN CANCELLED İSE
        if self.current_status_id == self.status_name_to_id.get("Cancelled"):
            messagebox.showwarning(
                "Cancel",
                "This reservation is already cancelled."
            )
            return

        #  PAID İSE
        if self.current_status_id == self.status_name_to_id.get("Paid"):
            messagebox.showerror(
                "Cancel",
                "Completed (paid) reservations cannot be cancelled."
            )
            return

        if not messagebox.askyesno("Cancel Reservation", "Are you sure?"):
            return

        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            UPDATE Reservations
            SET StatusId = ?, IsActive = 0
            WHERE ReservationId = ?
        """, (
            self.status_name_to_id.get("Cancelled"),
            self.current_reservation_id
        ))
        conn.commit()
        conn.close()

        self.payment_status_combo.set("Cancelled")
        self.current_status_id = self.status_name_to_id.get("Cancelled")

        messagebox.showinfo("Cancelled", "Reservation cancelled successfully.")
