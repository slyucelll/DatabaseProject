import pyodbc


def get_connection():
    try:
        conn = pyodbc.connect(
            "DRIVER={SQL Server};"
            "SERVER=DESKTOP-3H6HK4P\\SQLEXPRESS01;"
            "DATABASE=HotelP;"
            "Trusted_Connection=yes;"

        )
        return conn
    except Exception as e:
        print("Database connection error:", e)
        raise
