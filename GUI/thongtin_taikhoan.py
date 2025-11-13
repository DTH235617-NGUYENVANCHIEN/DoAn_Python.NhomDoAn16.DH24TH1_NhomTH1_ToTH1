# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk, messagebox
import utils # Dùng chung
import hashlib # Để hash mật khẩu
import pyodbc  # Để bắt lỗi
import subprocess # Để gọi lại login.py
import sys
import os

# ================================================================
# HÀM LOGIC (GIỮ NGUYÊN HASH, LOGOUT)
# ================================================================

def hash_password(password):
    """Hàm băm mật khẩu bằng SHA-256 (COPY TỪ login.py)."""
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def do_logout(root, force=False):
    """Đóng cửa sổ chính (root) và mở lại login.py."""
    
    # SỬA: Chỉ hỏi nếu force=False (không bị bắt buộc)
    if not force:
        if not messagebox.askyesno("Xác nhận Đăng xuất", "Bạn có chắc chắn muốn đăng xuất?"):
            return
        
    try:
        root.destroy() # Đóng cửa sổ main.py

        # (Code còn lại để mở login.py giữ nguyên)
        python_executable = sys.executable
        script_dir = os.path.dirname(os.path.abspath(__file__))
        login_py_path = os.path.join(script_dir, "login.py") 
        
        if not os.path.exists(login_py_path):
             # Hiển thị lỗi này nếu login.py không nằm cùng thư mục
            messagebox.showerror("Lỗi", "Không tìm thấy file login.py!")
            return

        subprocess.Popen([python_executable, login_py_path])
        
    except Exception as e:
        messagebox.showerror("Lỗi Đăng xuất", f"Không thể khởi động lại login.py:\n{e}")

# ================================================================
# HÀM LOGIC (SỬA ĐỔI ĐỂ ẨN FRAME SAU KHI LƯU)
# ================================================================
# ================================================================
# HÀM LOGIC (SỬA ĐỔI ĐỂ ẨN FRAME SAU KHI LƯU)
# ================================================================
def do_change_password(username, entry_old, entry_new, entry_confirm, frame_pass, toggle_button, root):
    """
    Kiểm tra, cập nhật mật khẩu,
    sau đó thông báo và bắt đăng xuất.
    """
    old_pass = entry_old.get()
    new_pass = entry_new.get()
    confirm_pass = entry_confirm.get()

    # 1. Kiểm tra đầu vào
    if not old_pass or not new_pass or not confirm_pass:
        messagebox.showwarning("Thiếu thông tin", "Vui lòng nhập đủ 3 trường mật khẩu.")
        return

    if new_pass != confirm_pass:
        messagebox.showerror("Lỗi", "Mật khẩu mới và mật khẩu xác nhận không khớp!")
        entry_new.delete(0, tk.END)
        entry_confirm.delete(0, tk.END)
        return

    # 2. Hash mật khẩu
    hashed_old_pass = hash_password(old_pass)
    hashed_new_pass = hash_password(new_pass)

    conn = utils.connect_db()
    if conn is None: return

    try:
        cur = conn.cursor()
        
        # 3. Kiểm tra mật khẩu cũ có đúng không
        sql_check = "SELECT MatKhau FROM TaiKhoan WHERE TenDangNhap = ?"
        cur.execute(sql_check, (username,))
        record = cur.fetchone()

        if not record or record[0] != hashed_old_pass:
            messagebox.showerror("Sai mật khẩu", "Mật khẩu cũ không chính xác.")
            return

        # 4. Cập nhật mật khẩu mới
        sql_update = "UPDATE TaiKhoan SET MatKhau = ? WHERE TenDangNhap = ?"
        cur.execute(sql_update, (hashed_new_pass, username))
        conn.commit()

        # ==================================
        # === SỬA THEO YÊU CẦU CỦA BẠN ===
        # ==================================
        messagebox.showinfo("Thành công", "Đã đổi mật khẩu thành công! Vui lòng đăng nhập lại.")
        
        # Gọi hàm đăng xuất
        do_logout(root, force=True)

    except Exception as e:
        conn.rollback()
        messagebox.showerror("Lỗi SQL", f"Không thể đổi mật khẩu:\n{str(e)}")
    finally:
        if conn:
            conn.close()

# ================================================================
# HÀM LOGIC MỚI (ĐỂ HIỆN/ẨN FRAME)
# ================================================================
def toggle_password_frame(frame_pass, toggle_button):
    """Hiện hoặc Ẩn khung đổi mật khẩu."""
    if frame_pass.winfo_ismapped():
        # Nếu đang Hiện -> thì Ẩn đi
        frame_pass.pack_forget()
        toggle_button.config(text="Đổi mật khẩu")
    else:
        # Nếu đang Ẩn -> thì Hiện ra
        frame_pass.pack(pady=10, padx=20, fill="x", anchor="n")
        toggle_button.config(text="Hủy đổi mật khẩu")

# ================================================================
# HÀM TẠO TRANG (SẮP XẾP LẠI GIAO DIỆN)
# ================================================================
def create_page(master, root, username, role):
    """
    Hàm này được main.py gọi.
    master: frame cha
    root: cửa sổ chính (để đăng xuất)
    username: tên đăng nhập (ví dụ 'an.nv')
    role: vai trò (ví dụ 'TaiXe')
    """
    
    # 1. TẠO FRAME CHÍNH
    page_frame = ttk.Frame(master, style="TFrame")
    utils.setup_theme(page_frame)

    try:
        style = ttk.Style()
        style.configure("Header.TLabel", font=("Calibri", 12)) 
        style.configure("Data.TLabel", font=("Calibri", 12, "bold"), foreground=utils.theme_colors["accent"])
    except Exception:
        pass 
    
    # 2. TẠO GIAO DIỆN
    lbl_title = ttk.Label(page_frame, text="TÀI KHOẢN CÁ NHÂN", style="Title.TLabel")
    lbl_title.pack(pady=15, padx=20)

    # --- Group Box 1: Thông tin tài khoản (HIỆN LUÔN) ---
    frame_info = ttk.LabelFrame(page_frame, text="Thông tin tài khoản", style="TLabelframe")
    frame_info.pack(pady=10, padx=20, fill="x", anchor="n")
    
    ttk.Label(frame_info, text="Tên đăng nhập:", style="Header.TLabel").grid(row=0, column=0, padx=10, pady=8, sticky="e")
    ttk.Label(frame_info, text=username, style="Data.TLabel").grid(row=0, column=1, padx=5, pady=8, sticky="w")
    
    ttk.Label(frame_info, text="Chức vụ:", style="Header.TLabel").grid(row=1, column=0, padx=10, pady=8, sticky="e")
    ttk.Label(frame_info, text=role, style="Data.TLabel").grid(row=1, column=1, padx=5, pady=8, sticky="w")
    
    frame_info.columnconfigure(1, weight=1)

    # --- SỬA: BỎ Group Box "Hành động" ---
    # Dùng Frame trơn (TFrame) thay vì LabelFrame
    frame_action = ttk.Frame(page_frame, style="TFrame")
    frame_action.pack(pady=10, padx=20, fill="x", anchor="n")
    
    # Frame con để chứa 2 nút (để .pack() vào giữa)
    frame_action_buttons = ttk.Frame(frame_action, style="TFrame")
    frame_action_buttons.pack(pady=10)

    
    # --- Group Box 3: Đổi mật khẩu (BỊ ẨN) ---
    # (Tạo frame này, nhưng chưa .pack() nó)
    frame_pass = ttk.LabelFrame(page_frame, text="Đổi mật khẩu", style="TLabelframe")
    # KHÔNG .pack() ở đây. Sẽ .pack() khi nhấn nút

    ttk.Label(frame_pass, text="Mật khẩu cũ:", style="Header.TLabel").grid(row=0, column=0, padx=10, pady=8, sticky="e")
    entry_old_pass = ttk.Entry(frame_pass, width=40, show="*")
    entry_old_pass.grid(row=0, column=1, padx=5, pady=8, sticky="w")
    
    ttk.Label(frame_pass, text="Mật khẩu mới:", style="Header.TLabel").grid(row=1, column=0, padx=10, pady=8, sticky="e")
    entry_new_pass = ttk.Entry(frame_pass, width=40, show="*")
    entry_new_pass.grid(row=1, column=1, padx=5, pady=8, sticky="w")

    ttk.Label(frame_pass, text="Xác nhận MK mới:", style="Header.TLabel").grid(row=2, column=0, padx=10, pady=8, sticky="e")
    entry_confirm_pass = ttk.Entry(frame_pass, width=40, show="*")
    entry_confirm_pass.grid(row=2, column=1, padx=5, pady=8, sticky="w")
    
    frame_pass_btn = ttk.Frame(frame_pass, style="TFrame")
    frame_pass_btn.grid(row=3, column=0, columnspan=2, pady=10)
    
    # --- SỬA: ĐỔI THỨ TỰ NÚT ---
    
    # Nút "Đổi mật khẩu" (TẠO VÀ PACK TRƯỚC)
    btn_show_pass_frame = ttk.Button(frame_action_buttons, text="Đổi mật khẩu", 
                                     command=lambda: toggle_password_frame(frame_pass, btn_show_pass_frame))
    btn_show_pass_frame.pack(side=tk.LEFT, padx=20)
    
    # Nút "Đăng xuất" (TẠO VÀ PACK SAU)
    btn_logout = ttk.Button(frame_action_buttons, text="Đăng xuất", 
                            command=lambda: do_logout(root))
    btn_logout.pack(side=tk.LEFT, padx=20) # Sửa thành side=tk.LEFT
    
    
    # Nút "Lưu thay đổi" (nằm trong frame_pass)
    btn_save_pass = ttk.Button(frame_pass_btn, text="Lưu thay đổi", style="Accent.TButton", 
                               
        # === SỬA DÒNG COMMAND NÀY ===
        command=lambda: do_change_password(
            username, 
            entry_old_pass, entry_new_pass, entry_confirm_pass, 
            frame_pass, btn_show_pass_frame, 
            root  # <-- Thêm 'root' vào cuối
        )
    )
    btn_save_pass.pack()

    frame_pass.columnconfigure(1, weight=1)
    
    # 3. TRẢ VỀ FRAME CHÍNH
    return page_frame

# ================================================================
# PHẦN CHẠY THỬ NGHIỆM
# (Giữ nguyên)
# ================================================================
if __name__ == "__main__":
    
    test_root = tk.Tk()
    test_root.title("Test Trang Tài khoản")
    
    try:
        utils.center_window(test_root, 700, 600)
    except Exception as e:
        print(f"Lỗi utils.py: {e}")
        test_root.geometry("700x600")

    page = create_page(test_root, test_root, "an.nv", "TaiXe")
    page.pack(fill="both", expand=True)
    
    test_root.mainloop()