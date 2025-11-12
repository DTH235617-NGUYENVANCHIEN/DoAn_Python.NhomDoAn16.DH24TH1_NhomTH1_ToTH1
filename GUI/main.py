import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import subprocess
import sys
import os

# ================================================================
# LẤY VAI TRÒ (ROLE) TỪ LÚC ĐĂNG NHẬP
# ================================================================
try:
    # sys.argv[0] là tên file (main.py)
    # sys.argv[1] là đối số ta truyền vào (vai trò 'Admin' hoặc 'TaiXe')
    USER_ROLE = sys.argv[1]
except IndexError:
    # Nếu chạy file main.py trực tiếp (không qua đăng nhập) để test
    messagebox.showwarning("Lỗi", "Vui lòng chạy file 'form_login.py' để đăng nhập.")
    USER_ROLE = "TaiXe" # Mặc định là Tài xế nếu chạy trực tiếp
    # sys.exit() # Nên thoát nếu chạy trực tiếp

print(f"Đang chạy Main Menu với vai trò: {USER_ROLE}")

# ================================================================
# HÀM MỞ FORM (Giữ nguyên)
# ================================================================

def open_form(form_filename):
    """Hàm này tìm và chạy một file Python khác (một form)."""
    print(f"Đang mở {form_filename}...")
    
    python_executable = sys.executable
    current_dir = os.path.dirname(os.path.abspath(__file__))
    form_path = os.path.join(current_dir, form_filename)

    if not os.path.exists(form_path):
        messagebox.showerror("Lỗi", f"Không tìm thấy file: {form_filename}\n\nHãy đảm bảo bạn đã lưu file này trong cùng thư mục.")
        return

    try:
        subprocess.Popen([python_executable, form_path])
    except Exception as e:
        messagebox.showerror("Lỗi khi mở form", f"Không thể khởi chạy {form_filename}:\n{e}")

# ================================================================
# THIẾT KẾ GIAO DIỆN CHÍNH
# ================================================================

# --- Cửa sổ chính ---
root = tk.Tk()
# Sửa lỗi: Tên file của bạn là login.py, không phải form_login.py
root.title(f"Hệ Thống Quản Lý Vận Tải (Vai trò: {USER_ROLE})") 
root.geometry("800x600")

# --- Hàm căn giữa cửa sổ ---
def center_window(w, h):
    ws = root.winfo_screenwidth()
    hs = root.winfo_screenheight()
    x = (ws/2) - (w/2)
    y = (hs/2) - (h/2)
    root.geometry('%dx%d+%d+%d' % (w, h, x, y))

center_window(800, 600)
root.resizable(False, False)

# --- Cấu hình Style ---
style = ttk.Style()
style.configure("Title.TLabel", font=("Arial", 24, "bold"), foreground="#003366")
style.configure("Menu.TButton", font=("Arial", 14, "bold"), padding=20)
style.configure("Exit.TButton", font=("Arial", 14, "bold"), padding=20, foreground="red")
# Style cho nút bị vô hiệu hóa (dành cho Tài xế)
style.configure("Disabled.TButton", font=("Arial", 14, "bold"), padding=20, foreground="grey")


# --- Frame chính ---
main_frame = ttk.Frame(root, padding=20)
main_frame.pack(fill=tk.BOTH, expand=True)

# --- Tiêu đề ---
lbl_title = ttk.Label(main_frame, text="HỆ THỐNG QUẢN LÝ VẬN TẢI", 
                      style="Title.TLabel", anchor="center")
lbl_title.pack(pady=20)

ttk.Separator(main_frame, orient="horizontal").pack(fill="x", pady=10)

# --- Frame chứa các nút ---
button_frame = ttk.Frame(main_frame)
button_frame.pack(pady=10, fill="both", expand=True)

# Cấu hình grid 3 cột
button_frame.grid_columnconfigure(0, weight=1)
button_frame.grid_columnconfigure(1, weight=1)
button_frame.grid_columnconfigure(2, weight=1)
button_frame.grid_rowconfigure(0, weight=1)
button_frame.grid_rowconfigure(1, weight=1)
button_frame.grid_rowconfigure(2, weight=1)

# ================================================================
# PHÂN QUYỀN HIỂN THỊ NÚT (ĐÃ SỬA TÊN FILE)
# ================================================================

# --- Hàng 1 ---
# Quản lý Xe (Chỉ Admin)
if USER_ROLE == 'Admin':
    btn_xe = ttk.Button(button_frame, text="🚗\nQuản lý Xe", 
                        style="Menu.TButton", 
                        command=lambda: open_form("quanli_xe.py")) # <-- ĐÃ SỬA
    btn_xe.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
else:
    # Vô hiệu hóa nút
    btn_xe = ttk.Button(button_frame, text="🚗\nQuản lý Xe", 
                        style="Disabled.TButton", state="disabled")
    btn_xe.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

# Quản lý Tài Xế (Chỉ Admin)
if USER_ROLE == 'Admin':
    btn_taixe = ttk.Button(button_frame, text="👨‍✈️\nQuản lý Tài Xế", 
                           style="Menu.TButton", 
                           command=lambda: open_form("quanli_taixe.py")) # <-- ĐÃ SỬA
    btn_taixe.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
else:
    btn_taixe = ttk.Button(button_frame, text="👨‍✈️\nQuản lý Tài Xế", 
                           style="Disabled.TButton", state="disabled")
    btn_taixe.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

# Quản lý Nhân Viên (Chỉ Admin)
if USER_ROLE == 'Admin':
    btn_nhanvien = ttk.Button(button_frame, text="👥\nQuản lý Nhân Viên", 
                              style="Menu.TButton", 
                              command=lambda: open_form("quanli_nhanvien.py")) # <-- ĐÃ SỬA
    btn_nhanvien.grid(row=0, column=2, sticky="nsew", padx=10, pady=10)
else:
    btn_nhanvien = ttk.Button(button_frame, text="👥\nQuản lý Nhân Viên", 
                              style="Disabled.TButton", state="disabled")
    btn_nhanvien.grid(row=0, column=2, sticky="nsew", padx=10, pady=10)


# --- Hàng 2 ---
# Quản lý Chuyến Đi (Cả hai)
btn_chuyendi = ttk.Button(button_frame, text="🗺️\nQuản lý Chuyến Đi", 
                          style="Menu.TButton", 
                          command=lambda: open_form("quanli_chuyendi.py")) # <-- ĐÃ SỬA
btn_chuyendi.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

# Nhật ký Nhiên Liệu (Cả hai)
btn_nhienlieu = ttk.Button(button_frame, text="⛽\nNhật ký Nhiên Liệu", 
                           style="Menu.TButton", 
                           command=lambda: open_form("quanli_nhatkinguyenlieu.py")) # <-- ĐÃ SỬA
btn_nhienlieu.grid(row=1, column=1, sticky="nsew", padx=10, pady=10)

# Lịch sử Bảo Trì (Cả hai)
btn_baotri = ttk.Button(button_frame, text="🔧\nLịch sử Bảo Trì", 
                        style="Menu.TButton", 
                        command=lambda: open_form("quanli_lichsubaotri.py")) # <-- ĐÃ SỬA
btn_baotri.grid(row=1, column=2, sticky="nsew", padx=10, pady=10)


# --- Hàng 3 ---
# Quản lý Tài Khoản (Chỉ Admin)
if USER_ROLE == 'Admin':
    btn_taikhoan = ttk.Button(button_frame, text="🔑\nQuản lý Tài Khoản", 
                              style="Menu.TButton", 
                              command=lambda: open_form("quanli_taikhoan.py")) # <-- ĐÃ SỬA
    btn_taikhoan.grid(row=2, column=0, sticky="nsew", padx=10, pady=10)
else:
    btn_taikhoan = ttk.Button(button_frame, text="🔑\nQuản lý Tài Khoản", 
                              style="Disabled.TButton", state="disabled")
    btn_taikhoan.grid(row=2, column=0, sticky="nsew", padx=10, pady=10)

# Nút Thoát (Cả hai)
btn_thoat = ttk.Button(button_frame, text="🚪\nThoát", 
                       style="Exit.TButton", 
                       command=root.quit)
btn_thoat.grid(row=2, column=2, sticky="nsew", padx=10, pady=10)


# --- Footer ---
ttk.Separator(main_frame, orient="horizontal").pack(fill="x", pady=10)
lbl_footer = ttk.Label(main_frame, text="Phát triển bởi [Tên Nhóm Của Bạn]", anchor="center")
lbl_footer.pack(pady=5)

# ================================================================
# CHẠY ỨNG DỤNG
# ================================================================
root.mainloop()