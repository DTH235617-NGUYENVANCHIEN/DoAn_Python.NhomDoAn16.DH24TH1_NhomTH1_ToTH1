import tkinter as tk
from tkinter import ttk, messagebox
# Không cần DateEntry
import pyodbc 
from datetime import datetime
import hashlib # <-- Thư viện để băm mật khẩu

# ================================================================
# PHẦN 1: KẾT NỐI CSDL (Giữ nguyên)
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
# PHẦN 2: CÁC HÀM TIỆN ÍCH (Tải Combobox)
# ================================================================
def load_nhanvien_combobox():
    """Tải danh sách TẤT CẢ nhân viên (MaNhanVien - HoVaTen)."""
    conn = connect_db()
    if conn is None:
        return []
    
    try:
        cur = conn.cursor()
        sql = "SELECT MaNhanVien, HoVaTen FROM NhanVien ORDER BY HoVaTen"
        cur.execute(sql)
        rows = cur.fetchall()
        # Format: "NV001 - Nguyễn Văn An"
        return [f"{row[0]} - {row[1]}" for row in rows]
    except Exception as e:
        print(f"Lỗi tải combobox nhân viên: {e}")
        return []
    finally:
        if conn:
            conn.close()

# ================================================================
# PHẦN 3: CÁC HÀM CRUD (CHO TÀI KHOẢN)
# ================================================================

# Biến tạm để xử lý Mật khẩu
PASSWORD_PLACEHOLDER = "******"

def hash_password(password):
    """Hàm băm mật khẩu bằng SHA-256."""
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def clear_input():
    """Xóa trắng các trường nhập liệu."""
    entry_tendangnhap.config(state='normal')
    entry_tendangnhap.delete(0, tk.END)
    
    entry_matkhau.delete(0, tk.END)
    cbb_nhanvien.set("")
    cbb_vaitro.set("TaiXe") # Mặc định
    
    entry_tendangnhap.focus()

def load_data():
    """Tải dữ liệu từ TaiKhoan lên Treeview."""
    for i in tree.get_children():
        tree.delete(i)
        
    conn = connect_db()
    if conn is None:
        return
        
    try:
        cur = conn.cursor()
        # KHÔNG LẤY MẬT KHẨU
        sql = """
        SELECT 
            tk.TenDangNhap, 
            tk.MaNhanVien, 
            nv.HoVaTen, 
            tk.VaiTro
        FROM TaiKhoan AS tk
        LEFT JOIN NhanVien AS nv ON tk.MaNhanVien = nv.MaNhanVien
        ORDER BY tk.TenDangNhap
        """
        cur.execute(sql)
        rows = cur.fetchall()
        
        for row in rows:
            tendn = row[0]
            manv = row[1]
            hoten = row[2] or "N/A" # Nếu NV bị xóa
            vaitro = row[3]
            
            tree.insert("", tk.END, values=(tendn, manv, hoten, vaitro))
            
    except pyodbc.Error as e:
        messagebox.showerror("Lỗi tải dữ liệu", f"Lỗi SQL: {str(e)}")
    except Exception as e:
        messagebox.showerror("Lỗi không xác định", f"Lỗi: {str(e)}")
    finally:
        if conn:
            conn.close()

#
# HÀM ĐÃ SỬA (HASHING)
#
def them_taikhoan():
    """Thêm một tài khoản mới."""
    try:
        tendn = entry_tendangnhap.get()
        matkhau = entry_matkhau.get()
        # Lấy Mã NV từ combobox
        manv = cbb_nhanvien_var.get().split(' - ')[0]
        vaitro = cbb_vaitro_var.get()

        if not tendn or not matkhau:
            messagebox.showwarning("Thiếu dữ liệu", "Vui lòng nhập Tên đăng nhập và Mật khẩu")
            return
        
        if matkhau == PASSWORD_PLACEHOLDER:
            messagebox.showwarning("Lỗi mật khẩu", "Vui lòng nhập mật khẩu mới")
            return

    except Exception as e:
        messagebox.showerror("Lỗi định dạng", f"Dữ liệu nhập không hợp lệ (chưa chọn nhân viên?): {e}")
        return

    conn = connect_db()
    if conn is None:
        return

    try:
        cur = conn.cursor()
        
        # Băm mật khẩu trước khi lưu
        hashed_mk = hash_password(matkhau)
        
        sql = """
        INSERT INTO TaiKhoan (TenDangNhap, MatKhau, MaNhanVien, VaiTro) 
        VALUES (?, ?, ?, ?)
        """
        # Lưu mật khẩu đã băm
        cur.execute(sql, (tendn, hashed_mk, manv, vaitro))
        
        conn.commit()
        messagebox.showinfo("Thành công", "Đã thêm tài khoản mới thành công")
        
        clear_input()
        load_data()
        
    except pyodbc.IntegrityError as e:
        conn.rollback() 
        if "PRIMARY KEY" in str(e):
             messagebox.showerror("Lỗi Trùng lặp", f"Tên đăng nhập '{tendn}' đã tồn tại.")
        elif "FOREIGN KEY" in str(e):
             messagebox.showerror("Lỗi Trùng lặp", f"Nhân viên '{manv}' có thể đã có tài khoản.")
        else:
             messagebox.showerror("Lỗi SQL", f"Không thể thêm:\n{str(e)}")
    except Exception as e:
        conn.rollback()
        messagebox.showerror("Lỗi không xác định", f"Lỗi: {str(e)}")
    finally:
        if conn:
            conn.close()

def chon_taikhoan_de_sua():
    """Lấy thông tin tài khoản được chọn và điền vào form."""
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Chưa chọn", "Hãy chọn một tài khoản để sửa")
        return

    selected_item = tree.item(selected[0])
    tendn = selected_item['values'][0]
    
    conn = connect_db()
    if conn is None:
        return

    try:
        cur = conn.cursor()
        sql = """
        SELECT tk.*, nv.HoVaTen 
        FROM TaiKhoan tk
        LEFT JOIN NhanVien nv ON tk.MaNhanVien = nv.MaNhanVien
        WHERE tk.TenDangNhap = ?
        """
        cur.execute(sql, (tendn,))
        data = cur.fetchone()
        
        if not data:
            messagebox.showerror("Lỗi", "Không tìm thấy dữ liệu tài khoản.")
            return

        clear_input()
        
        # Khóa Tên đăng nhập (PK)
        entry_tendangnhap.insert(0, data.TenDangNhap)
        entry_tendangnhap.config(state='disabled')
        
        # Đặt mật khẩu placeholder
        entry_matkhau.insert(0, PASSWORD_PLACEHOLDER)
        
        # Tìm và set combobox nhân viên
        if data.MaNhanVien:
            cbb_nhanvien_val = f"{data.MaNhanVien} - {data.HoVaTen}"
            cbb_nhanvien.set(cbb_nhanvien_val)
        
        cbb_vaitro.set(data.VaiTro or "TaiXe")

    except pyodbc.Error as e:
        messagebox.showerror("Lỗi SQL", f"Không thể lấy dữ liệu:\n{str(e)}")
    except Exception as e:
        messagebox.showerror("Lỗi không xác định", f"Lỗi: {str(e)}")
    finally:
        if conn:
            conn.close()

#
# HÀM ĐÃ SỬA (HASHING)
#
def luu_taikhoan_da_sua():
    """Lưu thay đổi (UPDATE) sau khi sửa."""
    tendn = entry_tendangnhap.get()
    if not tendn:
        messagebox.showwarning("Thiếu dữ liệu", "Không có Tên đăng nhập để cập nhật")
        return

    try:
        matkhau_moi = entry_matkhau.get()
        manv = cbb_nhanvien_var.get().split(' - ')[0]
        vaitro = cbb_vaitro_var.get()
    except Exception as e:
        messagebox.showerror("Lỗi định dạng", f"Dữ liệu nhập không hợp lệ (chưa chọn nhân viên?): {e}")
        return

    conn = connect_db()
    if conn is None:
        return
        
    try:
        cur = conn.cursor()
        
        # Kiểm tra xem có cần cập nhật mật khẩu không
        if matkhau_moi == PASSWORD_PLACEHOLDER or not matkhau_moi:
            # KHÔNG cập nhật mật khẩu
            sql = """
            UPDATE TaiKhoan SET 
                MaNhanVien = ?, VaiTro = ?
            WHERE TenDangNhap = ?
            """
            cur.execute(sql, (manv, vaitro, tendn))
        else:
            # CÓ cập nhật mật khẩu, băm nó
            hashed_mk_moi = hash_password(matkhau_moi)
            
            sql = """
            UPDATE TaiKhoan SET 
                MatKhau = ?, MaNhanVien = ?, VaiTro = ?
            WHERE TenDangNhap = ?
            """
            # Lưu mật khẩu đã băm
            cur.execute(sql, (hashed_mk_moi, manv, vaitro, tendn))
        
        conn.commit()
        messagebox.showinfo("Thành công", "Đã cập nhật tài khoản")
        
        clear_input()
        load_data()
        
    except pyodbc.Error as e:
        conn.rollback()
        messagebox.showerror("Lỗi SQL", f"Không thể cập nhật:\n{str(e)}")
    except Exception as e:
        conn.rollback()
        messagebox.showerror("Lỗi không xác định", f"Lỗi: {str(e)}")
    finally:
        if conn:
            conn.close()

def xoa_taikhoan():
    """Xóa tài khoản được chọn."""
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Chưa chọn", "Hãy chọn một tài khoản để xóa")
        return

    selected_item = tree.item(selected[0])
    tendn = selected_item['values'][0]

    if not messagebox.askyesno("Xác nhận", f"Bạn có chắc chắn muốn xóa tài khoản '{tendn}'?"):
        return

    conn = connect_db()
    if conn is None:
        return
        
    try:
        cur = conn.cursor()
        cur.execute("DELETE FROM TaiKhoan WHERE TenDangNhap=?", (tendn,))
        conn.commit()
        
        messagebox.showinfo("Thành công", "Đã xóa tài khoản thành công")
        clear_input()
        load_data()
        
    except pyodbc.Error as e:
        conn.rollback()
        messagebox.showerror("Lỗi SQL", f"Không thể xóa:\n{str(e)}")
    except Exception as e:
        conn.rollback()
        messagebox.showerror("Lỗi không xác định", f"Lỗi: {str(e)}")
    finally:
        if conn:
            conn.close()

# ================================================================
# PHẦN 4: THIẾT KẾ GIAO DIỆN (CHO TÀI KHOẢN)
# ================================================================

root = tk.Tk()
root.title("Quản lý Tài khoản (Database QL_VanTai)")

def center_window(w, h):
    ws = root.winfo_screenwidth()
    hs = root.winfo_screenheight()
    x = (ws/2) - (w/2)
    y = (hs/2) - (h/2)
    root.geometry('%dx%d+%d+%d' % (w, h, x, y))

center_window(900, 600) 
root.resizable(False, False)

lbl_title = tk.Label(root, text="QUẢN LÝ TÀI KHOẢN", font=("Arial", 18, "bold"))
lbl_title.pack(pady=10)

# Frame thông tin
frame_info = tk.Frame(root)
frame_info.pack(pady=5, padx=10, fill="x")

# --- Hàng 1 ---
tk.Label(frame_info, text="Tên đăng nhập:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
entry_tendangnhap = tk.Entry(frame_info, width=30)
entry_tendangnhap.grid(row=0, column=1, padx=5, pady=5, sticky="w")

tk.Label(frame_info, text="Mật khẩu:").grid(row=0, column=2, padx=15, pady=5, sticky="w")
entry_matkhau = tk.Entry(frame_info, width=30, show="*")
entry_matkhau.grid(row=0, column=3, padx=5, pady=5, sticky="w")

# --- Hàng 2 ---
tk.Label(frame_info, text="Nhân viên:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
cbb_nhanvien_var = tk.StringVar()
cbb_nhanvien = ttk.Combobox(frame_info, textvariable=cbb_nhanvien_var, width=28, state='readonly')
cbb_nhanvien.grid(row=1, column=1, padx=5, pady=5, sticky="w")
cbb_nhanvien['values'] = load_nhanvien_combobox()

tk.Label(frame_info, text="Vai trò:").grid(row=1, column=2, padx=15, pady=5, sticky="w")
vaitro_options = ["Admin", "TaiXe"]
cbb_vaitro_var = tk.StringVar()
cbb_vaitro = ttk.Combobox(frame_info, textvariable=cbb_vaitro_var, values=vaitro_options, width=28, state='readonly')
cbb_vaitro.grid(row=1, column=3, padx=5, pady=5, sticky="w")
cbb_vaitro.set("TaiXe")

# Cấu hình grid co giãn
frame_info.columnconfigure(1, weight=1)
frame_info.columnconfigure(3, weight=1)

# ===== Frame nút =====
frame_btn = tk.Frame(root)
frame_btn.pack(pady=15)

btn_them = tk.Button(frame_btn, text="Thêm", width=8, command=them_taikhoan)
btn_them.grid(row=0, column=0, padx=5)

btn_luu = tk.Button(frame_btn, text="Lưu", width=8, command=luu_taikhoan_da_sua)
btn_luu.grid(row=0, column=1, padx=5)

# === ĐÂY LÀ DÒNG ĐÃ SỬA LỖI TYPO ===
btn_sua = tk.Button(frame_btn, text="Sửa", width=8, command=chon_taikhoan_de_sua) 
# ==================================
btn_sua.grid(row=0, column=2, padx=5)

btn_huy = tk.Button(frame_btn, text="Hủy", width=8, command=clear_input)
btn_huy.grid(row=0, column=3, padx=5)

btn_xoa = tk.Button(frame_btn, text="Xóa", width=8, command=xoa_taikhoan)
btn_xoa.grid(row=0, column=4, padx=5)

btn_thoat = tk.Button(frame_btn, text="Thoát", width=8, command=root.quit)
btn_thoat.grid(row=0, column=5, padx=5)


# ===== Bảng danh sách =====
lbl_ds = tk.Label(root, text="Danh sách tài khoản (Không hiển thị mật khẩu)", font=("Arial", 10, "bold"))
lbl_ds.pack(pady=5, padx=10, anchor="w")

frame_tree = tk.Frame(root)
frame_tree.pack(pady=10, padx=10, fill="both", expand=True)

scrollbar_y = tk.Scrollbar(frame_tree, orient=tk.VERTICAL)
scrollbar_x = tk.Scrollbar(frame_tree, orient=tk.HORIZONTAL)

columns = ("tendn", "manv", "hoten", "vaitro")
tree = ttk.Treeview(frame_tree, columns=columns, show="headings", height=10,
                    yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)

scrollbar_y.config(command=tree.yview)
scrollbar_x.config(command=tree.xview)

scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)

# Định nghĩa các cột
tree.heading("tendn", text="Tên đăng nhập")
tree.column("tendn", width=150)

tree.heading("manv", text="Mã NV")
tree.column("manv", width=100, anchor="center")

tree.heading("hoten", text="Họ Tên Nhân Viên")
tree.column("hoten", width=200)

tree.heading("vaitro", text="Vai trò")
tree.column("vaitro", width=100, anchor="center")

tree.pack(fill="both", expand=True)

# ================================================================
# PHẦN 5: CHẠY ỨNG DỤNG
# ================================================================
clear_input() 
load_data() 
root.mainloop()