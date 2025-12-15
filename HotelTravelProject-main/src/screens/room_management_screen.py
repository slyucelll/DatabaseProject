import tkinter as tk
from tkinter import messagebox, ttk
from PIL import Image, ImageTk
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


class RoomManagementScreen(tk.Frame):

    def __init__(self, master, on_back):
        super().__init__(master)
        self.master = master
        self.on_back = on_back

        self.current_room_id = None
        self.hotel_map = {}
        self.roomtype_map = {}
        self.rows = []

        # ================= BACKGROUND =================
        img_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "images",
            "room_mm_.jpeg"
        )
        if os.path.exists(img_path):
            img = Image.open(img_path).resize((1200, 700))
            self.bg_image = ImageTk.PhotoImage(img)
            tk.Label(self, image=self.bg_image).place(
                x=0, y=0, relwidth=1, relheight=1
            )

        # ================= LISTBOX =================
        self.room_listbox = tk.Listbox(self, width=50, height=18, font=("Arial", 12))
        self.room_listbox.place(x=80, y=170)
        self.room_listbox.bind("<<ListboxSelect>>", self.on_select)

        # ================= INPUTS =================
        self.hotel_combo = ttk.Combobox(self, state="readonly", width=30)
        self.hotel_combo.place(x=830, y=185)

        self.room_number_entry = tk.Entry(self, width=32)
        self.room_number_entry.place(x=830, y=230)

        self.room_type_combo = ttk.Combobox(self, state="readonly", width=30)
        self.room_type_combo.place(x=830, y=280)
        self.room_type_combo.bind("<<ComboboxSelected>>", self.on_roomtype_change)

        self.price_entry = tk.Entry(self, width=32)
        self.price_entry.place(x=830, y=330)

        self.capacity_combo = ttk.Combobox(
            self,
            values=["1", "2", "3", "4", "5", "6"],
            state="readonly",
            width=30
        )
        self.capacity_combo.place(x=830, y=380)

        # ================= BUTTONS =================
        ModernButton(self, text="Add Room", command=self.add_room).place(x=640, y=470)
        ModernButton(self, text="Update Selected", command=self.update_room).place(x=840, y=470)
        ModernButton(self, text="Delete Selected", command=self.delete_room).place(x=1030, y=470)
        ModernButton(self, text="← Back", command=self.on_back).place(x=80, y=550)

        self.load_hotels()
        self.load_room_types()
        self.load_rooms()

    # ================= LOADS =================
    def load_hotels(self):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT HotelId, HotelName FROM Hotels WHERE IsActive = 1")
        self.hotel_map = {r.HotelName: r.HotelId for r in cur.fetchall()}
        self.hotel_combo["values"] = list(self.hotel_map.keys())
        conn.close()

    def load_room_types(self):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT RoomTypeId, TypeName, MaxCapacity, PricePerNight
            FROM RoomTypes
        """)
        self.roomtype_map = {
            r.TypeName: (r.RoomTypeId, r.MaxCapacity, r.PricePerNight)
            for r in cur.fetchall()
        }
        self.room_type_combo["values"] = list(self.roomtype_map.keys())
        conn.close()

    def load_rooms(self):
        self.room_listbox.delete(0, tk.END)
        self.current_room_id = None

        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT 
                R.RoomId,
                R.RoomNumber,
                H.HotelName,
                RT.TypeName,
                R.Capacity,
                R.PricePerNight,
                R.HotelId
            FROM HotelRooms R
            JOIN Hotels H ON R.HotelId = H.HotelId
            JOIN RoomTypes RT ON R.RoomTypeId = RT.RoomTypeId
            WHERE R.IsActive = 1 AND H.IsActive = 1
            ORDER BY H.HotelName, R.RoomNumber
        """)
        self.rows = cur.fetchall()
        conn.close()

        for r in self.rows:
            self.room_listbox.insert(
                tk.END,
                f"{r.RoomNumber} • {r.HotelName} • {r.TypeName} • "
                f"{r.Capacity}p • €{r.PricePerNight}"
            )

    # ================= ROOMTYPE CHANGE → PRICE FROM DB =================
    def on_roomtype_change(self, event):
        room_type = self.room_type_combo.get()
        if not room_type:
            return

        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT PricePerNight
            FROM RoomTypes
            WHERE TypeName = ?
        """, (room_type,))
        row = cur.fetchone()
        conn.close()

        if row:
            self.price_entry.delete(0, tk.END)
            self.price_entry.insert(0, f"{row.PricePerNight:.2f}")

    # ================= SELECT =================
    def on_select(self, event):
        sel = self.room_listbox.curselection()
        if not sel:
            return

        r = self.rows[sel[0]]
        self.current_room_id = r.RoomId

        self.room_number_entry.delete(0, tk.END)
        self.room_number_entry.insert(0, r.RoomNumber)

        self.room_type_combo.set(r.TypeName)
        self.capacity_combo.set(str(r.Capacity))

        self.price_entry.delete(0, tk.END)
        self.price_entry.insert(0, r.PricePerNight)

        for name, hid in self.hotel_map.items():
            if hid == r.HotelId:
                self.hotel_combo.set(name)
                break

    # ================= ADD ROOM =================
    def add_room(self):
        hotel_name = self.hotel_combo.get()
        room_type = self.room_type_combo.get()

        if hotel_name not in self.hotel_map or room_type not in self.roomtype_map:
            messagebox.showerror("Error", "Select hotel and room type.")
            return

        try:
            room_number = int(self.room_number_entry.get())
            capacity = int(self.capacity_combo.get())
        except:
            messagebox.showerror("Error", "Invalid numeric values.")
            return

        hotel_id = self.hotel_map[hotel_name]
        roomtype_id, max_capacity, price = self.roomtype_map[room_type]

        if capacity > max_capacity:
            messagebox.showerror("Capacity Error", f"Max {max_capacity} guests allowed.")
            return

        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT 1 FROM HotelRooms
            WHERE HotelId = ? AND RoomNumber = ? AND IsActive = 1
        """, (hotel_id, room_number))

        if cur.fetchone():
            conn.close()
            messagebox.showerror(
                "Duplicate Room",
                "This room number already exists in this hotel."
            )
            return

        cur.execute("""
            INSERT INTO HotelRooms
            (HotelId, RoomNumber, RoomTypeId, Capacity, PricePerNight, IsActive)
            VALUES (?, ?, ?, ?, ?, 1)
        """, (hotel_id, room_number, roomtype_id, capacity, price))

        conn.commit()
        conn.close()

        self.load_rooms()
        messagebox.showinfo("Added", "Room added successfully.")

    # ================= UPDATE ROOM =================
    def update_room(self):
        if not self.current_room_id:
            messagebox.showwarning("Update", "Select a room first.")
            return

        room_type = self.room_type_combo.get()
        if room_type not in self.roomtype_map:
            messagebox.showerror("Error", "Select room type.")
            return

        try:
            new_room_number = int(self.room_number_entry.get())
            new_capacity = int(self.capacity_combo.get())
        except:
            messagebox.showerror("Error", "Invalid numeric values.")
            return

        roomtype_id, max_capacity, price = self.roomtype_map[room_type]

        if new_capacity > max_capacity:
            messagebox.showerror(
                "Capacity Error",
                f"This room type allows max {max_capacity} guests."
            )
            return

        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            UPDATE HotelRooms
            SET RoomNumber = ?, RoomTypeId = ?, Capacity = ?, PricePerNight = ?
            WHERE RoomId = ?
        """, (new_room_number, roomtype_id, new_capacity, price, self.current_room_id))

        conn.commit()
        conn.close()

        self.price_entry.delete(0, tk.END)
        self.price_entry.insert(0, f"{price:.2f}")

        self.load_rooms()
        messagebox.showinfo("Updated", "Room updated successfully.")

    # ================= DELETE ROOM =================
    def delete_room(self):
        if not self.current_room_id:
            return

        if not messagebox.askyesno(
            "Confirm",
            "Deleting this room will deactivate all related reservations and users.\nContinue?"
        ):
            return

        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            UPDATE Users
            SET IsActive = 0
            WHERE UserId IN (
                SELECT UserId FROM Reservations WHERE RoomId = ?
            )
        """, (self.current_room_id,))

        cur.execute("""
            UPDATE Reservations
            SET IsActive = 0
            WHERE RoomId = ?
        """, (self.current_room_id,))

        cur.execute("""
            UPDATE HotelRooms
            SET IsActive = 0
            WHERE RoomId = ?
        """, (self.current_room_id,))

        conn.commit()
        conn.close()

        self.load_rooms()
        messagebox.showinfo("Deleted", "Room and related users deactivated.")
