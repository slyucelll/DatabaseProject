import tkinter as tk
from tkinter import ttk, messagebox
from database.db import get_connection
from tkcalendar import DateEntry
import datetime
import os
from PIL import Image, ImageTk


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


class ReservationsManagementScreen(tk.Frame):

    def __init__(self, master, on_back):
        super().__init__(master)
        self.master = master
        self.on_back = on_back


        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        bg_path = os.path.join(base_dir, "images", "reservation4.jpg")

        bg_image = Image.open(bg_path)
        bg_image = bg_image.resize((1200, 700))
        self.bg_photo = ImageTk.PhotoImage(bg_image)

        bg_label = tk.Label(self, image=self.bg_photo)
        bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        bg_label.lower()  # en arkaya at

        #  STATE
        self.current_reservation_id = None
        self.current_status = None
        self.roomtype_map = {}

        #  LIST
        self.listbox = tk.Listbox(self, width=120, height=16, font=("Arial", 11))
        self.listbox.place(x=40, y=40)
        self.listbox.bind("<<ListboxSelect>>", self.on_select)

        # FORM
        self.res_id_entry = tk.Entry(self, width=10, state="readonly")
        self.res_id_entry.place(x=230, y=455)

        self.hotel_entry = tk.Entry(self, width=30, state="readonly")
        self.hotel_entry.place(x=160, y=510)

        self.room_type_combo = ttk.Combobox(self, state="readonly", width=20)
        self.room_type_combo.place(x=650, y=505)

        self.guests_entry = tk.Entry(self, width=10)
        self.guests_entry.place(x=160, y=572)

        self.checkin = DateEntry(self, width=12, date_pattern="yyyy-MM-dd")
        self.checkin.place(x=465, y=570)

        self.checkout = DateEntry(self, width=12, date_pattern="yyyy-MM-dd")
        self.checkout.place(x=755, y=570)

        self.price_entry = tk.Entry(self, width=12)
        self.price_entry.place(x=1033, y=570)

        #  BUTTONS
        ModernButton(self, text="Update Selected", command=self.update_reservation)\
            .place(x=760, y=600)

        ModernButton(self, text="Cancel Reservation", command=self.cancel_reservation)\
            .place(x=940, y=600)

        ModernButton(self, text="← Back", command=self.on_back)\
            .place(x=40, y=600)

        self.load_roomtypes()
        self.load_reservations()


    def load_roomtypes(self):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT RoomTypeId, TypeName, MaxCapacity FROM RoomTypes")
        self.roomtype_map.clear()
        names = []
        for r in cur.fetchall():
            self.roomtype_map[r.TypeName] = (r.RoomTypeId, r.MaxCapacity)
            names.append(r.TypeName)
        conn.close()
        self.room_type_combo["values"] = names


    def load_reservations(self):
        self.listbox.delete(0, tk.END)

        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT
                R.ReservationId,
                H.HotelName,
                RT.TypeName,
                R.Guests,
                R.CheckInDate,
                R.CheckOutDate,
                R.TotalPrice,
                RS.StatusName
            FROM Reservations R
            JOIN HotelRooms HR ON R.RoomId = HR.RoomId
            JOIN Hotels H ON HR.HotelId = H.HotelId
            JOIN RoomTypes RT ON HR.RoomTypeId = RT.RoomTypeId
            JOIN ReservationStatus RS ON R.StatusId = RS.StatusId
            ORDER BY R.ReservationId DESC
        """)
        self.rows = cur.fetchall()
        conn.close()

        for r in self.rows:
            self.listbox.insert(
                tk.END,
                f"{r.ReservationId} • {r.HotelName} • {r.TypeName} • "
                f"{r.Guests}p • {r.CheckInDate} → {r.CheckOutDate} • "
                f"{r.TotalPrice} € • {r.StatusName}"
            )


    def on_select(self, event):
        sel = self.listbox.curselection()
        if not sel:
            return

        r = self.rows[sel[0]]
        self.current_reservation_id = r.ReservationId
        self.current_status = r.StatusName

        self.res_id_entry.config(state="normal")
        self.res_id_entry.delete(0, tk.END)
        self.res_id_entry.insert(0, r.ReservationId)
        self.res_id_entry.config(state="readonly")

        self.hotel_entry.config(state="normal")
        self.hotel_entry.delete(0, tk.END)
        self.hotel_entry.insert(0, r.HotelName)
        self.hotel_entry.config(state="readonly")

        self.room_type_combo.set(r.TypeName)
        self.guests_entry.delete(0, tk.END)
        self.guests_entry.insert(0, r.Guests)
        self.checkin.set_date(r.CheckInDate)
        self.checkout.set_date(r.CheckOutDate)
        self.price_entry.delete(0, tk.END)
        self.price_entry.insert(0, r.TotalPrice)


    def update_reservation(self):
        if not self.current_reservation_id:
            messagebox.showwarning("Update", "Select a reservation first.")
            return

        if self.current_status == "Cancelled":
            messagebox.showerror("Update", "Cancelled reservations cannot be updated.")
            return

        try:
            guests = int(self.guests_entry.get())
        except:
            messagebox.showerror("Error", "Guests must be numeric.")
            return

        room_type = self.room_type_combo.get()
        _, max_capacity = self.roomtype_map[room_type]

        if guests > max_capacity:
            messagebox.showerror("Capacity Error", f"Max {max_capacity} guests allowed.")
            return

        checkin = self.checkin.get_date()
        checkout = self.checkout.get_date()

        if checkout < checkin:
            messagebox.showerror("Date Error", "Check-out cannot be before check-in.")
            return

        for r in self.rows:
            if r.ReservationId == self.current_reservation_id:
                def to_date(v):
                    if isinstance(v, datetime.datetime):
                        return v.date()
                    if isinstance(v, datetime.date):
                        return v
                    return datetime.datetime.strptime(str(v), "%Y-%m-%d").date()

                if (
                    guests == r.Guests and
                    room_type == r.TypeName and
                    checkin == to_date(r.CheckInDate) and
                    checkout == to_date(r.CheckOutDate)
                ):
                    messagebox.showwarning(
                        "Update",
                        "No changes detected. You did not modify any field."
                    )
                    return
                break

        nights = max(1, (checkout - checkin).days)

        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "SELECT PricePerNight FROM RoomTypes WHERE TypeName = ?",
            (room_type,)
        )
        price_per_night = float(cur.fetchone().PricePerNight)

        total_price = price_per_night * nights

        cur.execute("""
            UPDATE Reservations
            SET Guests = ?, CheckInDate = ?, CheckOutDate = ?, TotalPrice = ?
            WHERE ReservationId = ?
        """, (
            guests,
            checkin.strftime("%Y-%m-%d"),
            checkout.strftime("%Y-%m-%d"),
            total_price,
            self.current_reservation_id
        ))

        conn.commit()
        conn.close()

        self.price_entry.delete(0, tk.END)
        self.price_entry.insert(0, f"{total_price:.2f}")

        messagebox.showinfo("Updated", "Reservation updated successfully.")
        self.load_reservations()


    def cancel_reservation(self):
        if not self.current_reservation_id:
            messagebox.showwarning("Cancel", "Select a reservation first.")
            return

        if self.current_status == "Cancelled":
            messagebox.showerror("Cancel", "Already cancelled.")
            return

        if self.current_status == "Completed":
            messagebox.showerror("Cancel", "Completed reservations cannot be cancelled.")
            return

        if self.current_status != "Not Paid":
            messagebox.showerror("Cancel", "Only 'Not Paid' reservations can be cancelled.")
            return

        if not messagebox.askyesno("Confirm", "Cancel this reservation?"):
            return

        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT StatusId FROM ReservationStatus WHERE StatusName='Cancelled'")
        status_id = cur.fetchone().StatusId

        cur.execute("""
            UPDATE Reservations
            SET StatusId = ?, IsActive = 0
            WHERE ReservationId = ?
        """, (status_id, self.current_reservation_id))

        conn.commit()
        conn.close()

        messagebox.showinfo("Cancelled", "Reservation cancelled.")
        self.load_reservations()
