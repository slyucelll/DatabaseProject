import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import os


class ModernButton(tk.Button):
    def __init__(self, master=None, **kwargs):
        super().__init__(
            master,
            font=("Arial", 14, "bold"),
            fg="#1f1f1f",
            bg="#ffffff",
            activebackground="#e6e6e6",
            activeforeground="#000000",
            relief="flat",
            bd=2,
            highlightthickness=0,
            padx=20,
            pady=12,
            **kwargs
        )
        self.configure(
            borderwidth=1,
            highlightbackground="#bbbbbb",
            highlightcolor="#bbbbbb"
        )
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)

    def on_enter(self, event):
        self["bg"] = "#f0f0f0"

    def on_leave(self, event):
        self["bg"] = "#ffffff"


class TravelMenuScreen(tk.Frame):
    def __init__(self, master, on_back, *args, **kwargs):
        super().__init__(master, *args, **kwargs)

        self.master = master
        self.on_back = on_back

        # ==== BACKGROUND ====
        img_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "images",
            "travel_menu_screen.jpg"
        )

        img = Image.open(img_path)
        img = img.resize((1200, 700))
        self.bg_image = ImageTk.PhotoImage(img)

        bg = tk.Label(self, image=self.bg_image)
        bg.place(x=0, y=0, relwidth=1, relheight=1)



        # ==== 2x2 BUTTON GRID ====

        # SOL ÜST - Create Travel Plan
        btn1 = ModernButton(
            self,
            text="Create Travel Plan",
            width=18,
            command=self.master.show_create_travel_plan
        )
        btn1.place(relx=0.38, rely=0.40, anchor="center")

        # SAĞ ÜST - My Travel Plans
        btn2 = ModernButton(
            self,
            text="My Travel Plans",
            width=18,
            command=self.master.show_my_travel_plans
        )
        btn2.place(relx=0.62, rely=0.40, anchor="center")

        # SOL ALT - Search Hotels
        btn3 = ModernButton(
            self,
            text="Search Hotels",
            width=18,
            command=self.master.show_search_hotel
        )
        btn3.place(relx=0.38, rely=0.55, anchor="center")


        # SAĞ ALT - My Reservations
        btn4 = ModernButton(
            self,
            text="My Reservations",
            width=18,
            command=self.master.show_my_reservations
        )
        btn4.place(relx=0.62, rely=0.55, anchor="center")

        # ==== BACK BUTTON ====
        back_btn = ModernButton(
            self,
            text="← Back",
            width=10,
            command=self.on_back
        )
        back_btn.place(relx=0.22, rely=0.70)


    # ===== HANDLERS =====
    def on_create_travel_plan(self):
        messagebox.showinfo("Create Travel Plan", "Create Travel Plan screen will be implemented.")

    def on_my_travel_plans(self):
        messagebox.showinfo("My Travel Plans", "My Travel Plans screen will be implemented.")

    def on_search_hotels(self):
        messagebox.showinfo("Search Hotels", "Hotel search screen will be implemented.")

    def on_my_reservations(self):
        messagebox.showinfo("My Reservations", "Reservation list will be implemented.")
