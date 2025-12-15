import tkinter as tk
from tkinter import messagebox, ttk
from PIL import Image, ImageTk
import os
import datetime

from database.db import get_connection


# ================= MODERN BUTTON =================
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
            padx=12,
            pady=6,
            **kwargs
        )
        self.bind("<Enter>", lambda e: self.config(bg="#f0f0f0"))
        self.bind("<Leave>", lambda e: self.config(bg="#ffffff"))



class MyTravelPlansScreen(tk.Frame):
    def __init__(self, master, on_back):
        super().__init__(master)
        self.master = master
        self.on_back = on_back

        self.current_plan_id = None
        self.selected_hotel_id = None

        img_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "images",
            "travel3.jpeg"
        )
        if os.path.exists(img_path):
            img = Image.open(img_path).resize((1200, 700))
            self.bg_image = ImageTk.PhotoImage(img)
            tk.Label(self, image=self.bg_image).place(
                x=0, y=0, relwidth=1, relheight=1
            )


        self.search_combo = ttk.Combobox(
            self, state="readonly", width=28, font=("Arial", 12)
        )
        self.search_combo.place(relx=0.42, rely=0.30, anchor="w")
        self.search_combo.bind("<<ComboboxSelected>>", self.on_plan_selected)

        ModernButton(self, text="SEARCH", command=self.on_plan_selected)\
            .place(relx=0.75, rely=0.30, anchor="center")


        self.plan_name_entry = tk.Entry(self, width=30, font=("Arial", 12))
        self.plan_name_entry.place(relx=0.42, rely=0.38, anchor="w")

        self.hotel_name_entry = tk.Entry(self, width=30, font=("Arial", 12))
        self.hotel_name_entry.place(relx=0.42, rely=0.43, anchor="w")

        self.destination_entry = tk.Entry(self, width=30, font=("Arial", 12))
        self.destination_entry.place(relx=0.42, rely=0.48, anchor="w")

        self.start_date_entry = tk.Entry(self, width=14, font=("Arial", 12))
        self.start_date_entry.place(relx=0.42, rely=0.55, anchor="w")

        self.end_date_entry = tk.Entry(self, width=14, font=("Arial", 12))
        self.end_date_entry.place(relx=0.58, rely=0.55, anchor="w")

        self.guests_entry = tk.Entry(self, width=10, font=("Arial", 12))
        self.guests_entry.place(relx=0.42, rely=0.63, anchor="w")

        self.budget_entry = tk.Entry(self, width=20, font=("Arial", 12))
        self.budget_entry.place(relx=0.42, rely=0.70, anchor="w")

        ModernButton(
            self,
            text="MAKE RESERVATION AND PAYMENT",
            width=32,
            command=self.make_reservation
        ).place(relx=0.42, rely=0.80, anchor="center")

        ModernButton(self, text="← Back", command=self.on_back)\
            .place(relx=0.21, rely=0.80, anchor="center")

        self.clear_entries()
        self.load_travel_plans_to_combo()


    def get_user_id(self):
        return getattr(self.master, "current_user_id", None)

    def format_date(self, d):
        if isinstance(d, str):
            return d[:10]
        if hasattr(d, "strftime"):
            return d.strftime("%Y-%m-%d")
        return str(d)

    def clear_entries(self):
        for e in (
            self.plan_name_entry,
            self.hotel_name_entry,
            self.destination_entry,
            self.start_date_entry,
            self.end_date_entry,
            self.guests_entry,
            self.budget_entry
        ):
            e.delete(0, tk.END)


    def load_travel_plans_to_combo(self):
        uid = self.get_user_id()
        if not uid:
            return

        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT PlanName
            FROM TravelPlans
            WHERE UserId=? AND IsActive=1
            ORDER BY PlanName
        """, (uid,))
        self.search_combo["values"] = [r.PlanName for r in cur.fetchall()]
        conn.close()


    def on_plan_selected(self, event=None):
        uid = self.get_user_id()
        plan_name = self.search_combo.get()
        if not plan_name:
            return

        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT
                TP.TravelPlanId,
                TP.StartDate,
                TP.EndDate,
                TP.NumberOfPeople,
                TP.Budget,
                C.CityId,
                C.CityName,
                CO.CountryName
            FROM TravelPlans TP
            JOIN Cities C ON TP.CityId = C.CityId
            JOIN Countries CO ON C.CountryId = CO.CountryId
            WHERE TP.UserId=? AND TP.PlanName=? AND TP.IsActive=1
        """, (uid, plan_name))
        r = cur.fetchone()

        if not r:
            conn.close()
            return

        cur.execute("""
            SELECT TOP 1 H.HotelId, H.HotelName
            FROM Hotels H
            JOIN HotelRooms R ON H.HotelId = R.HotelId
            WHERE H.CityId=? AND H.IsActive=1 AND R.IsActive=1
            ORDER BY R.PricePerNight
        """, (r.CityId,))
        hotel = cur.fetchone()
        conn.close()

        self.current_plan_id = r.TravelPlanId
        self.selected_hotel_id = hotel.HotelId if hotel else None

        self.clear_entries()
        self.plan_name_entry.insert(0, plan_name)
        self.hotel_name_entry.insert(0, hotel.HotelName if hotel else "No Hotel")
        self.destination_entry.insert(0, f"{r.CountryName} - {r.CityName}")
        self.start_date_entry.insert(0, self.format_date(r.StartDate))
        self.end_date_entry.insert(0, self.format_date(r.EndDate))
        self.guests_entry.insert(0, r.NumberOfPeople)
        self.budget_entry.insert(0, r.Budget)


    def make_reservation(self):
        print(">>> MAKE RESERVATION CLICKED")

        uid = self.get_user_id()
        if not uid or not self.current_plan_id:
            messagebox.showerror("Error", "Select a travel plan first.")
            return

        if not self.selected_hotel_id:
            messagebox.showerror("Error", "No active hotel found for this plan.")
            return

        try:
            start_dt = datetime.datetime.strptime(
                self.start_date_entry.get().strip(), "%Y-%m-%d"
            )
            end_dt = datetime.datetime.strptime(
                self.end_date_entry.get().strip(), "%Y-%m-%d"
            )
            guests = int(self.guests_entry.get())
        except Exception as e:
            messagebox.showerror("Error", f"Invalid date or guest info.\n{e}")
            return

        nights = (end_dt - start_dt).days
        if nights < 0:
            messagebox.showerror("Error", "Invalid date range.")
            return
        if nights == 0:
            nights = 1

        conn = get_connection()
        cur = conn.cursor()

        #  CHECK EXISTING RESERVATION FOR THIS TRAVEL PLAN
        cur.execute("""
            SELECT
                R.ReservationId,
                RS.StatusName,
                R.TotalPrice
            FROM Reservations R
            JOIN ReservationStatus RS ON R.StatusId = RS.StatusId
            WHERE R.TravelPlanId = ? AND R.IsActive = 1
        """, (int(self.current_plan_id),))

        existing = cur.fetchone()

        if existing:
            reservation_id = existing.ReservationId
            status_name = existing.StatusName
            total_price = float(existing.TotalPrice)

            # 🟡 NOT PAID → GO TO PAYMENT
            if status_name == "Not Paid":
                conn.close()

                self.master.pending_reservation = {
                    "reservation_id": reservation_id,
                    "total_price": total_price
                }

                messagebox.showinfo(
                    "Payment Required",
                    "You already have an unpaid reservation for this travel plan.\nRedirecting to payment."
                )

                self.master.show_payment()
                return

            #  PAID / COMPLETED → BLOCK
            else:
                conn.close()
                messagebox.showerror(
                    "Reservation Exists",
                    "This travel plan already has a completed reservation."
                )
                return

        # Cheapest room
        cur.execute("""
            SELECT TOP 1 RoomId, PricePerNight
            FROM HotelRooms
            WHERE HotelId=? AND IsActive=1
            ORDER BY PricePerNight
        """, (self.selected_hotel_id,))
        room = cur.fetchone()

        if not room:
            conn.close()
            messagebox.showerror("Error", "No available room.")
            return

        cur.execute("""
            SELECT StatusId
            FROM ReservationStatus
            WHERE StatusName='Not Paid'
        """)
        status_id = cur.fetchone().StatusId

        total_price = float(room.PricePerNight) * int(nights)

        cur.execute("""
            INSERT INTO Reservations (
                UserId,
                TravelPlanId,
                RoomId,
                CheckInDate,
                CheckOutDate,
                Guests,
                TotalPrice,
                StatusId,
                CreatedDate,
                IsActive
            )
            OUTPUT INSERTED.ReservationId
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, GETDATE(), 1)
        """, (
            int(uid),
            int(self.current_plan_id),
            int(room.RoomId),
            start_dt,
            end_dt,
            int(guests),
            total_price,
            int(status_id)
        ))

        row = cur.fetchone()
        conn.commit()
        conn.close()

        if not row:
            messagebox.showerror("Error", "Reservation could not be created.")
            return

        reservation_id = row[0]

        self.master.pending_reservation = {
            "reservation_id": reservation_id,
            "total_price": total_price
        }

        self.master.show_payment()
