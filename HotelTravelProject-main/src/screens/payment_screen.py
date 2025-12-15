import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import os
import datetime

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


class PaymentScreen(tk.Frame):
    def __init__(self, master, on_back):
        super().__init__(master)
        self.master = master
        self.on_back = on_back

        self.pending = getattr(master, "pending_reservation", None)
        if not self.pending:
            messagebox.showerror("Error", "No reservation data found.")
            self.on_back()
            return


        img_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "images",
            "payment_screen.jpg"
        )
        if os.path.exists(img_path):
            img = Image.open(img_path).resize((1200, 700))
            self.bg_image = ImageTk.PhotoImage(img)
            tk.Label(self, image=self.bg_image).place(
                x=0, y=0, relwidth=1, relheight=1
            )

        #  CARD NUMBER (MAX 16 DIGITS)
        vcmd = (self.register(self.validate_card), "%P")
        self.card_number_entry = tk.Entry(
            self, width=25, font=("Arial", 13),
            validate="key", validatecommand=vcmd
        )
        self.card_number_entry.place(relx=0.40, rely=0.40, anchor="w")

        self.card_holder_entry = tk.Entry(self, width=25, font=("Arial", 13))
        self.card_holder_entry.place(relx=0.40, rely=0.47, anchor="w")

        self.month_entry = tk.Entry(self, width=5, font=("Arial", 13))
        self.month_entry.place(relx=0.40, rely=0.53, anchor="w")

        self.year_entry = tk.Entry(self, width=7, font=("Arial", 13))
        self.year_entry.place(relx=0.45, rely=0.53, anchor="w")

        self.cvv_entry = tk.Entry(self, width=6, font=("Arial", 13), show="*")
        self.cvv_entry.place(relx=0.40, rely=0.61, anchor="w")

        ModernButton(
            self,
            text="COMPLETE AND CONFIRM PAYMENT",
            width=28,
            command=self.pay_now
        ).place(relx=0.69, rely=0.78, anchor="center")

        ModernButton(
            self,
            text="← Back",
            width=10,
            command=self.on_back
        ).place(relx=0.23, rely=0.78, anchor="center")

    #  CARD VALIDATION
    def validate_card(self, value):
        if value == "":
            return True
        if not value.isdigit():
            return False
        return len(value) <= 16


    # PAYMENT ve DB UPDATE

    def pay_now(self):
        card_no = self.card_number_entry.get().strip()
        holder = self.card_holder_entry.get().strip()
        mm = self.month_entry.get().strip()
        yy = self.year_entry.get().strip()
        cvv = self.cvv_entry.get().strip()

        # ---- VALIDATIONS ----
        if len(card_no) != 16:
            messagebox.showerror("Payment", "Card number must be exactly 16 digits.")
            return

        if not holder:
            messagebox.showerror("Payment", "Card holder name is required.")
            return

        if not mm.isdigit() or not yy.isdigit():
            messagebox.showerror("Payment", "Expiry date must be numeric.")
            return

        mm, yy = int(mm), int(yy)
        if mm < 1 or mm > 12:
            messagebox.showerror("Payment", "Expiry month must be between 1 and 12.")
            return

        today = datetime.date.today()
        expiry = datetime.date(yy, mm, 1)
        if expiry < today.replace(day=1):
            messagebox.showerror("Payment", "Card has expired.")
            return

        if not cvv.isdigit() or len(cvv) != 3:
            messagebox.showerror("Payment", "CVV must be exactly 3 digits.")
            return

        reservation_id = int(self.pending["reservation_id"])
        total_price = float(self.pending["total_price"])

        try:
            conn = get_connection()
            cur = conn.cursor()

            # INSERT PAYMENT
            cur.execute("""
                INSERT INTO Payments (
                    ReservationId,
                    PaymentTypeId,
                    Amount,
                    CreatedDate
                )
                VALUES (?, ?, ?, GETDATE())
            """, (
                reservation_id,
                1,  # Card
                total_price
            ))

            #  UPDATE RESERVATION STATUS → COMPLETED
            cur.execute("""
                SELECT StatusId
                FROM ReservationStatus
                WHERE StatusName = 'Completed'
            """)
            completed_status_id = cur.fetchone().StatusId

            cur.execute("""
                UPDATE Reservations
                SET StatusId = ?
                WHERE ReservationId = ?
            """, (completed_status_id, reservation_id))

            conn.commit()

        except Exception as e:
            messagebox.showerror("DB Error", str(e))
            return
        finally:
            conn.close()

        delattr(self.master, "pending_reservation")
        messagebox.showinfo("Payment", "Payment completed successfully! 🎉")
        self.master.show_my_reservations()
