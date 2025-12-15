import tkinter as tk
from PIL import Image, ImageTk
import os


class WelcomeScreen(tk.Frame):
    def __init__(self, master, on_admin_login, on_user_login, *args, **kwargs):
        super().__init__(master, *args, **kwargs)

        self.on_admin_login = on_admin_login
        self.on_user_login = on_user_login

        # ==== BACKGROUND FOTOĞRAF ====
        image_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "images",
            "welcomescreen.jpg"
        )

        original_image = Image.open(image_path)
        resized_image = original_image.resize((1200, 700))
        self.bg_image = ImageTk.PhotoImage(resized_image)

        bg_label = tk.Label(self, image=self.bg_image)
        bg_label.place(x=0, y=0, relwidth=1, relheight=1)

        # ==== BUTTONS DIRECTLY (NO FRAME) ====

        # EKRAN GENİŞLİĞİNİ AL
        screen_width = 1200  # sabit ekran genişliği
        button_width_px = 220  # 20 karakter genişlik = yaklaşık 220px
        spacing = 60  # iki buton arasındaki boşluk

        # BUTONLARIN X KONUMU

        shift_left = 50  # butonları sola kaydırma miktarı

        left_button_x = (screen_width // 2) - button_width_px - (spacing // 2) - shift_left
        right_button_x = (screen_width // 2) + (spacing // 2) - shift_left

        # BUTONLARIN Y KONUMU (sayfanın ortasından biraz aşağı)
        y_position = 400   # bunu artırırsan butonlar daha aşağı iner

        # ---- ADMIN BUTTON ----
        self.admin_button = tk.Button(
            self,
            text="ADMIN LOGIN",
            font=("Arial", 12, "bold"),
            width=20,
            bg="white",
            relief="solid",
            bd=1,
            command=self.on_admin_login
        )
        self.admin_button.place(x=left_button_x, y=y_position)

        # ---- USER BUTTON ----
        self.user_button = tk.Button(
            self,
            text="USER LOGIN",
            font=("Arial", 12, "bold"),
            width=20,
            bg="white",
            relief="solid",
            bd=1,
            command=self.on_user_login
        )
        self.user_button.place(x=right_button_x, y=y_position)
