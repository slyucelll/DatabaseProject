import tkinter as tk

from screens.welcome_screen import WelcomeScreen
from screens.admin_login_screen import AdminLoginScreen
from screens.user_login_screen import UserLoginScreen
from screens.register_screen import RegisterScreen
from screens.travel_menu_screen import TravelMenuScreen
from screens.create_travel_plan_screen import CreateTravelPlanScreen
from screens.travel_plans_screen import MyTravelPlansScreen
from screens.reservations_screen import MyReservationsScreen
from screens.search_hotels_screen import SearchHotelsScreen
from screens.payment_screen import PaymentScreen

from database.db import get_connection



class App(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Travel Planning & Hotel Reservation")
        self.geometry("1200x700")
        self.configure(bg="white")

        self.current_screen = None
        self.current_user_id = 1

        # Rezervasyon listesi
        self.reservations = []
        self.next_reservation_id = 1

        # ilk ekran
        print("DEBUG: App initialized")
        self.show_welcome()

    def clear_screen(self):
        if self.current_screen is not None:
            self.current_screen.destroy()
            self.current_screen = None


    def show_welcome(self):
        print("DEBUG: show_welcome called")
        self.clear_screen()
        self.current_screen = WelcomeScreen(
            master=self,
            on_admin_login=self.show_admin_login,
            on_user_login=self.show_user_login
        )
        self.current_screen.pack(fill="both", expand=True)


    def show_admin_login(self):
        print("DEBUG: show_admin_login called")
        self.clear_screen()
        self.current_screen = AdminLoginScreen(
            master=self,
            on_back=self.show_welcome
        )
        self.current_screen.pack(fill="both", expand=True)


    def show_admin_menu(self):
        print("DEBUG: show_admin_menu called")
        from screens.admin_menu_screen import AdminMenuScreen
        self.clear_screen()
        self.current_screen = AdminMenuScreen(
            master=self,
            on_back=self.show_welcome
        )
        self.current_screen.pack(fill="both", expand=True)


    def show_country_city_mgmt(self):
        print("DEBUG: show_country_city_mgmt called")
        from screens.countryandcity_management_screen import CountryAndCityManagementScreen
        self.clear_screen()
        self.current_screen = CountryAndCityManagementScreen(master=self, on_back=self.show_admin_menu)
        self.current_screen.pack(fill="both", expand=True)


    def show_user_login(self):
        print("DEBUG: show_user_login called")
        self.clear_screen()
        self.current_screen = UserLoginScreen(
            master=self,
            on_back=self.show_welcome
        )
        self.current_screen.pack(fill="both", expand=True)


    def show_register(self):
        print("DEBUG: show_register called")
        self.clear_screen()
        self.current_screen = RegisterScreen(
            master=self,
            on_back_to_login=self.show_user_login
        )
        self.current_screen.pack(fill="both", expand=True)

    def register_user(self, fname, lname, email, pw, dob):
        try:
            conn = get_connection()
            cursor = conn.cursor()

            # Şifreyi hashle
            password_hash = sha256(pw.encode("utf-8")).hexdigest()

            # Aynı email var mı?
            cursor.execute("SELECT 1 FROM Users WHERE Email = ?", (email,))
            if cursor.fetchone():
                raise Exception("Bu e-posta zaten kayıtlı.")

            # INSERT
            cursor.execute("""
                INSERT INTO Users (FirstName, LastName, Email, PasswordHash, RoleId, IsActive)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                fname,
                lname,
                email,
                password_hash,
                2,  # RoleId → User
                1  # IsActive
            ))

            conn.commit()
            conn.close()

            print(" DB'ye yazıldı:", fname, lname, email)

        except Exception as e:
            print("Register error:", e)
            raise


    def show_travel_menu(self):
        print("DEBUG: show_travel_menu called")
        self.clear_screen()
        self.current_screen = TravelMenuScreen(
            master=self,
            on_back=self.show_user_login
        )
        self.current_screen.pack(fill="both", expand=True)


    def show_create_travel_plan(self):
        print("DEBUG: show_create_travel_plan called")
        self.clear_screen()
        self.current_screen = CreateTravelPlanScreen(
            master=self,
            on_back=self.show_travel_menu
        )
        self.current_screen.pack(fill="both", expand=True)


    def show_my_travel_plans(self):
        print("DEBUG: show_my_travel_plans called")
        self.clear_screen()
        self.current_screen = MyTravelPlansScreen(
            master=self,
            on_back=self.show_travel_menu
        )
        self.current_screen.pack(fill="both", expand=True)


    def show_my_reservations(self):
        print("DEBUG: show_my_reservations called")
        self.clear_screen()
        self.current_screen = MyReservationsScreen(
            master=self,
            on_back=self.show_travel_menu
        )
        self.current_screen.pack(fill="both", expand=True)



    def show_search_hotel(self, plan_data=None):
        print("DEBUG: show_search_hotel called")
        self.clear_screen()
        self.current_screen = SearchHotelsScreen(
            master=self,
            plan_data=plan_data,  # None olabilir
            on_back=self.show_travel_menu
        )
        self.current_screen.pack(fill="both", expand=True)


    def add_reservation(self, reservation_data: dict) -> int:
        reservation = {
            "id": self.next_reservation_id,
            "user_id": self.current_user_id,
            **reservation_data
        }
        self.reservations.append(reservation)
        self.next_reservation_id += 1
        print("DEBUG: reservation added, id=", reservation["id"])
        return reservation["id"]

    def get_reservations_for_current_user(self):
        return [r for r in self.reservations if r["user_id"] == self.current_user_id]


    def show_payment(self):
        print("DEBUG: show_payment called")
        self.clear_screen()
        self.current_screen = PaymentScreen(
            master=self,
            on_back=self.show_my_reservations
        )
        self.current_screen.pack(fill="both", expand=True)


    def show_hotel_mgmt(self):
        print("DEBUG: show_hotel_mgmt called")
        from screens.hotel_management_screen import HotelManagementScreen
        self.clear_screen()
        self.current_screen = HotelManagementScreen(self, self.show_admin_menu)
        self.current_screen.pack(fill="both", expand=True)

    def show_reservations_mgmt(self):
        print("DEBUG: show_reservations_mgmt called")
        from screens.reservations_management_screen import ReservationsManagementScreen
        self.clear_screen()
        self.current_screen = ReservationsManagementScreen(self, self.show_admin_menu)
        self.current_screen.pack(fill="both", expand=True)

    def show_room_mgmt(self):
        print("DEBUG: show_room_mgmt called")
        from screens.room_management_screen import RoomManagementScreen
        self.clear_screen()
        self.current_screen = RoomManagementScreen(self, self.show_admin_menu)
        self.current_screen.pack(fill="both", expand=True)

    def show_users_mgmt(self):
        print("DEBUG: show_users_mgmt called")
        from screens.users_management_screen import UsersManagementScreen
        self.clear_screen()
        self.current_screen = UsersManagementScreen(self, self.show_admin_menu)
        self.current_screen.pack(fill="both", expand=True)


if __name__ == "__main__":
    app = App()
    app.mainloop()