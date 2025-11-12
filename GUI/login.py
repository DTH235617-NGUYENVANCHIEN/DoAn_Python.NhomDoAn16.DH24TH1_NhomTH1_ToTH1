import tkinter as tk
from tkinter import ttk, messagebox
import pyodbc
import subprocess
import sys
import os
import hashlib # <-- ĐÃ THÊM THƯ VIỆN BĂM

# ================================================================
# KẾT NỐI CSDL (Giống các form khác)
# ================================================================
def connect_db():
    """Hàm kết nối đến CSDL SQL Server."""
    try:
        conn_string = (
            r'DRIVER={SQL Server};'
            r'SERVER=LAPTOP-MKC70SQE\SQLEXPRESS;' # Giữ nguyên server của bạn
            r'DATABASE=QL_VanTai;'
            r'Trusted_Connection=yes;' 
        )
        conn = pyodbc.connect(conn_string)
        return conn
    except pyodbc.Error as e:
        messagebox.showerror("Lỗi kết nối CSDL", f"Không thể kết nối đến SQL Server:\n{e}")
        return None
    except Exception as e:
        messagebox.showerror("Lỗi không xác định", f"Lỗi: {str(e)}")
        return None

# ================================================================
# HÀM XỬ LÝ ĐĂNG NHẬP (ĐÃ CẬP NHẬT HASH)
# ================================================================

def hash_password(password):
    """Hàm băm mật khẩu bằng SHA-256."""
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def check_login():
    username = entry_username.get()
    password = entry_password.get()

    if not username or not password:
        messagebox.showwarning("Thiếu thông tin", "Vui lòng nhập Tên đăng nhập và Mật khẩu.")
        return

    conn = connect_db()
    if conn is None:
        return

    try:
        cur = conn.cursor()
        # Lấy MatKhau (đã băm) và VaiTro từ CSDL
        sql = "SELECT MatKhau, VaiTro FROM TaiKhoan WHERE TenDangNhap = ?"
        cur.execute(sql, (username,))
        record = cur.fetchone()

        if record:
            # === LOGIC KIỂM TRA MẬT KHẨU ĐÃ BĂM ===
            
            # 1. Lấy mật khẩu đã băm từ CSDL
            db_hashed_password = record[0] 
            db_role = record[1]

            # 2. Băm mật khẩu mà người dùng vừa nhập
            input_hashed_password = hash_password(password)
            
            # 3. So sánh hai chuỗi băm
            if input_hashed_password == db_hashed_password:
                messagebox.showinfo("Thành công", f"Đăng nhập thành công với vai trò: {db_role}")
                
                # Đóng cửa sổ đăng nhập
                login_window.destroy()
                
                # Mở Main Menu và truyền vai trò qua
                open_main_menu(db_role)
                
            else:
                messagebox.showerror("Sai thông tin", "Sai Mật khẩu. Vui lòng thử lại.")
            # === KẾT THÚC LOGIC KIỂM TRA ===
            
        else:
            messagebox.showerror("Sai thông tin", "Không tìm thấy Tên đăng nhập.")

    except pyodbc.Error as e:
        messagebox.showerror("Lỗi SQL", f"Lỗi truy vấn:\n{str(e)}")
    except Exception as e:
        messagebox.showerror("Lỗi không xác định", f"Lỗi: {str(e)}")
    finally:
        if conn:
            conn.close()

def open_main_menu(role):
    """
    Hàm này chạy file main.py và truyền vai trò (role) vào.
    """
    print(f"Mở Main Menu với vai trò: {role}")
    
    python_executable = sys.executable
    current_dir = os.path.dirname(os.path.abspath(__file__))
    main_menu_path = os.path.join(current_dir, "main.py") # Phải đặt tên file là main.py

    if not os.path.exists(main_menu_path):
        messagebox.showerror("Lỗi", "Không tìm thấy file: main.py")
        return

    try:
        # Chạy main.py và truyền 'role' làm đối số dòng lệnh
        subprocess.Popen([python_executable, main_menu_path, role])
    except Exception as e:
        messagebox.showerror("Lỗi khi mở Main Menu", f"Không thể khởi chạy main.py:\n{e}")

# ================================================================
# THIẾT KẾ GIAO DIỆN ĐĂNG NHẬP (Giữ nguyên)
# ================================================================

login_window = tk.Tk()
login_window.title("Đăng nhập - Hệ thống Quản lý Vận tải")

# Căn giữa cửa sổ
w = 400
h = 250
ws = login_window.winfo_screenwidth()
hs = login_window.winfo_screenheight()
x = (ws/2) - (w/2)
y = (hs/2) - (h/2)
login_window.geometry('%dx%d+%d+%d' % (w, h, x, y))
login_window.resizable(False, False)

# --- Style ---
style = ttk.Style()
style.configure("Title.TLabel", font=("Arial", 16, "bold"), foreground="#003366")
style.configure("Login.TButton", font=("Arial", 12, "bold"), padding=10)

# --- Frame chính ---
main_frame = ttk.Frame(login_window, padding=20)
main_frame.pack(fill=tk.BOTH, expand=True)

lbl_title = ttk.Label(main_frame, text="ĐĂNG NHẬP HỆ THỐNG", 
                      style="Title.TLabel", anchor="center")
lbl_title.pack(pady=10)

# --- Frame thông tin đăng nhập ---
form_frame = ttk.Frame(main_frame)
form_frame.pack(pady=10)

tk.Label(form_frame, text="Tên đăng nhập:", font=("Arial", 12)).grid(row=0, column=0, padx=5, pady=10, sticky="w")
entry_username = ttk.Entry(form_frame, width=25, font=("Arial", 12))
entry_username.grid(row=0, column=1, padx=5, pady=10)

tk.Label(form_frame, text="Mật khẩu:", font=("Arial", 12)).grid(row=1, column=0, padx=5, pady=10, sticky="w")
entry_password = ttk.Entry(form_frame, width=25, font=("Arial", 12), show="*")
entry_password.grid(row=1, column=1, padx=5, pady=10)

# --- Nút đăng nhập ---
btn_login = ttk.Button(main_frame, text="Đăng nhập", 
                       style="Login.TButton", 
                       command=check_login)
btn_login.pack(pady=10)

# Bắt sự kiện nhấn Enter
login_window.bind('<Return>', lambda event: check_login())

login_window.mainloop()