import pyodbc
from tkinter import messagebox # Vẫn cần messagebox để hiện lỗi

# Đây là chuỗi kết nối CSDL, tập trung ở một nơi
# Nếu bạn đổi server, chỉ cần sửa ở đây
DB_CONN_STRING = (
    r'DRIVER={SQL Server};'
    r'SERVER=LAPTOP-MKC70SQE\SQLEXPRESS;' 
    r'DATABASE=QL_VanTai;'
    r'Trusted_Connection=yes;' # Dùng Windows Authentication
)

def connect_db():
    """
    Hàm kết nối đến CSDL SQL Server.
    Giờ đây được dùng chung cho tất cả các form.
    """
    try:
        conn = pyodbc.connect(DB_CONN_STRING)
        return conn
    except pyodbc.Error as e:
        # Hiện lỗi và trả về None
        messagebox.showerror("Lỗi kết nối CSDL", f"Không thể kết nối đến SQL Server:\n{e}")
        return None
    except Exception as e:
        messagebox.showerror("Lỗi không xác định", f"Lỗi: {str(e)}")
        return None