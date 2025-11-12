import tkinter as tk
from tkinter import ttk, messagebox
# Không cần PhotoImage
import subprocess
import sys
import os

# ================================================================
# LẤY VAI TRÒ (ROLE)
# ================================================================
try:
    USER_ROLE = sys.argv[1]
    print(f"Đang chạy Main Menu với vai trò (Từ Login): {USER_ROLE}")

except IndexError:
    msg = (
        "Bạn đang chạy file main.py trực tiếp (chế độ Test).\n"
        "Vui lòng chạy file 'login.py' để đăng nhập.\n\n"
        "Bạn muốn chạy Test với vai trò 'Admin' (Yes) hay 'TaiXe' (No)?"
    )
    if messagebox.askyesno("CHẾ ĐỘ TEST", msg):
        USER_ROLE = "Admin"
    else:
        USER_ROLE = "TaiXe"
    
    print(f"Đang chạy Main Menu với vai trò (TEST): {USER_ROLE}")

# ================================================================
# HÀM MỞ FORM / ĐĂNG XUẤT
# ================================================================

def open_form(form_filename):
    """Hàm này tìm và chạy một file Python khác."""
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

def open_login():
    """Đóng form main và mở lại form login."""
    print("Đăng xuất, mở lại login.py...")
    
    python_executable = sys.executable
    current_dir = os.path.dirname(os.path.abspath(__file__))
    login_path = os.path.join(current_dir, "login.py") 

    if not os.path.exists(login_path):
        messagebox.showerror("Lỗi", "Không tìm thấy file: login.py")
        return

    try:
        subprocess.Popen([python_executable, login_path])
        root.destroy() 
    except Exception as e:
        messagebox.showerror("Lỗi khi mở form", f"Không thể khởi chạy login.py:\n{e}")

# ================================================================
# THIẾT KẾ GIAO DIỆN CHÍNH (Dashboard)
# ================================================================

# --- Cửa sổ chính ---
root = tk.Tk()
root.title(f"Hệ Thống Quản Lý Vận Tải (Vai trò: {USER_ROLE})") 
root.geometry("900x600") # Kích thước lớn hơn cho dashboard
root.configure(bg="#ffffff") 

# --- Hàm căn giữa cửa sổ ---
def center_window(w, h):
    ws = root.winfo_screenwidth()
    hs = root.winfo_screenheight()
    x = (ws/2) - (w/2)
    y = (hs/2) - (h/2)
    root.geometry('%dx%d+%d+%d' % (w, h, x, y))

center_window(900, 600)
root.resizable(False, False)

# --- Cấu hình màu sắc & font chữ ---
SIDEBAR_BG = "#2c3e50" # Màu xanh đen (Nền Sidebar)
SIDEBAR_FG = "#ecf0f1" # Màu trắng (Chữ Sidebar)
HOVER_BG = "#34495e"   # Màu hover
ACTIVE_BG = "#415b71"  # Màu khi nhấn
CONTENT_BG = "#ffffff" # Nền trắng (Nội dung chính)
TITLE_FG = "#003366"   # Màu tiêu đề

button_font = ("Arial", 12, "bold")
title_font = ("Arial", 24, "bold")
welcome_font = ("Arial", 20, "bold")

# --- Bố cục chính (Sidebar + Content) ---
root.grid_rowconfigure(0, weight=1)
root.grid_columnconfigure(0, weight=0) # Sidebar (không co giãn)
root.grid_columnconfigure(1, weight=1) # Content (co giãn)

# --- Sidebar Frame ---
sidebar_frame = tk.Frame(root, bg=SIDEBAR_BG, width=250)
sidebar_frame.grid(row=0, column=0, sticky="nsw")
sidebar_frame.pack_propagate(False) # Ngăn sidebar co lại

# --- Content Frame ---
content_frame = tk.Frame(root, bg=CONTENT_BG)
content_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)


# ================================================================
# HÀM HIỆU ỨNG HOVER (Làm sinh động)
# ================================================================
def on_enter(e):
    e.widget.config(background=HOVER_BG, foreground=SIDEBAR_FG)

def on_leave(e):
    e.widget.config(background=SIDEBAR_BG, foreground=SIDEBAR_FG)

# ================================================================
# TẠO CÁC NÚT TRONG SIDEBAR
# ================================================================

def create_sidebar_button(text, command):
    """Hàm tạo nút chuẩn cho sidebar"""
    btn = tk.Button(sidebar_frame, 
                    text=text, 
                    font=button_font,
                    bg=SIDEBAR_BG, 
                    fg=SIDEBAR_FG, 
                    activebackground=ACTIVE_BG,
                    activeforeground=SIDEBAR_FG,
                    bd=0,
                    relief="flat",
                    anchor="w", # Căn chữ sang trái
                    padx=25,    # Tăng padding trái để thụt vào
                    pady=15,
                    command=command)
    
    btn.bind("<Enter>", on_enter)
    btn.bind("<Leave>", on_leave)
    return btn

# --- Tiêu đề Sidebar ---
lbl_menu = tk.Label(sidebar_frame, text="DANH MỤC", font=("Arial", 16, "bold"),
                    bg=SIDEBAR_BG, fg="#1abc9c") # Màu xanh ngọc
lbl_menu.pack(pady=20, padx=20)

# ================================================================
# PHÂN QUYỀN (ĐÃ SẮP XẾP LẠI)
# ================================================================

# --- Phân quyền (Chỉ Admin thấy) ---
if USER_ROLE == 'Admin':
    lbl_admin = tk.Label(sidebar_frame, text="Quản trị hệ thống", font=("Arial", 10, "italic"),
                         bg=SIDEBAR_BG, fg="#95a5a6")
    lbl_admin.pack(fill='x', padx=20, pady=(10, 5))
    
    # === THỨ TỰ ĐÃ SẮP XẾP ===
    btn_nhanvien = create_sidebar_button("👥 QL Nhân Viên", lambda: open_form("quanli_nhanvien.py"))
    btn_nhanvien.pack(fill='x')
    
    btn_taixe = create_sidebar_button("👨‍✈️ QL Tài Xế", lambda: open_form("quanli_taixe.py"))
    btn_taixe.pack(fill='x')
    
    btn_xe = create_sidebar_button("🚗 Quản lý Xe", lambda: open_form("quanli_xe.py"))
    btn_xe.pack(fill='x')
    
    btn_taikhoan = create_sidebar_button("🔑 QL Tài Khoản", lambda: open_form("quanli_taikhoan.py"))
    btn_taikhoan.pack(fill='x')

# --- Chức năng chung (Ai cũng thấy) ---
lbl_user = tk.Label(sidebar_frame, text="Nghiệp vụ", font=("Arial", 10, "italic"),
                     bg=SIDEBAR_BG, fg="#95a5a6")
lbl_user.pack(fill='x', padx=20, pady=(20, 5))

btn_chuyendi = create_sidebar_button("🗺️ QL Chuyến Đi", lambda: open_form("quanli_chuyendi.py"))
btn_chuyendi.pack(fill='x')

btn_nhienlieu = create_sidebar_button("⛽ Nhiên Liệu", lambda: open_form("quanli_nhatkinguyenlieu.py"))
btn_nhienlieu.pack(fill='x')

btn_baotri = create_sidebar_button("🔧 Bảo Trì", lambda: open_form("quanli_lichsubaotri.py"))
btn_baotri.pack(fill='x')

# --- Đăng xuất & Thoát (Luôn ở dưới cùng) ---
# Dùng pack(side="bottom") để đẩy xuống
btn_thoat = create_sidebar_button("❌ Thoát", root.quit)
btn_thoat.pack(fill='x', side="bottom", pady=(0, 20))

# === THÊM LẠI NÚT ĐĂNG XUẤT ===
btn_dangxuat = create_sidebar_button("📤 Đăng Xuất", open_login)
btn_dangxuat.pack(fill='x', side="bottom")


# ================================================================
# TẠO NỘI DUNG CHÍNH (Content Frame)
# ================================================================
lbl_title = tk.Label(content_frame, text="HỆ THỐNG QUẢN LÝ VẬN TẢI", 
                     font=title_font, fg=TITLE_FG, bg=CONTENT_BG)
lbl_title.pack(pady=(10, 20))

tk.Frame(content_frame, height=2, bg="#e0e0e0").pack(fill="x", pady=10)

lbl_welcome = tk.Label(content_frame, text=f"Chào mừng, {USER_ROLE}!", 
                       font=welcome_font, fg="#333", bg=CONTENT_BG)
lbl_welcome.pack(pady=40)

lbl_intro = tk.Label(content_frame, text="Vui lòng chọn một chức năng từ thanh menu bên trái.",
                     font=("Arial", 14), fg="#555", bg=CONTENT_BG)
lbl_intro.pack()

# ================================================================
# CHẠY ỨNG DỤNG
# ================================================================
root.mainloop()