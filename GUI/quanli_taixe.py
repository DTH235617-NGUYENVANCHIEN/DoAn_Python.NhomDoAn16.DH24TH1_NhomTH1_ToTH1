import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
import pyodbc 

# ================================================================
# PHẦN 1: KẾT NỐI CSDL (Giữ nguyên từ mẫu)
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
# PHẦN 2: CÁC HÀM CRUD (CHO TÀI XẾ)
# ================================================================

def clear_input():
    """Xóa trắng các trường nhập liệu."""
    entry_manv.config(state='normal') # Mở khóa trường Mã NV
    entry_manv.delete(0, tk.END)
    entry_hoten.delete(0, tk.END)
    entry_sdt.delete(0, tk.END)
    entry_diachi.delete(0, tk.END)
    entry_banglai.delete(0, tk.END)
    
    date_banglai.set_date("2025-01-01")
    
    cbb_trangthai_nv.set("1 = Đang làm việc")
    cbb_trangthai_lx.set("1 = Rảnh")
    
    entry_manv.focus()

def load_data():
    """Tải dữ liệu từ NhanVien JOIN TaiXe lên Treeview."""
    for i in tree.get_children():
        tree.delete(i)
        
    conn = connect_db()
    if conn is None:
        return
        
    try:
        cur = conn.cursor()
        # Cần JOIN 2 bảng NhanVien (nv) và TaiXe (tx)
        sql = """
        SELECT 
            nv.MaNhanVien, 
            nv.HoVaTen, 
            nv.SoDienThoai, 
            tx.HangBangLai, 
            nv.TrangThai, 
            tx.TrangThaiTaiXe
        FROM NhanVien AS nv
        JOIN TaiXe AS tx ON nv.MaNhanVien = tx.MaNhanVien
        """
        cur.execute(sql)
        rows = cur.fetchall()
        
        for row in rows:
            # Chuyển đổi TrangThai (NhanVien)
            trang_thai_nv_text = "Đang làm việc" if row[4] == 1 else "Nghỉ"
            
            # Chuyển đổi TrangThaiTaiXe (TaiXe)
            trang_thai_lx_text = "Rảnh" if row[5] == 1 else "Đang lái"
            
            tree.insert("", tk.END, values=(
                row[0], # MaNhanVien
                row[1], # HoVaTen
                row[2], # SoDienThoai
                row[3], # HangBangLai
                trang_thai_nv_text, # TrangThai (NhanVien)
                trang_thai_lx_text  # TrangThaiTaiXe
            ))
            
    except pyodbc.Error as e:
        messagebox.showerror("Lỗi tải dữ liệu", f"Lỗi SQL: {str(e)}")
    except Exception as e:
        messagebox.showerror("Lỗi không xác định", f"Lỗi: {str(e)}")
    finally:
        if conn:
            conn.close()

def them_taixe():
    """Thêm một tài xế mới (vào cả 2 bảng NhanVien và TaiXe)."""
    # Lấy dữ liệu từ form
    manv = entry_manv.get()
    hoten = entry_hoten.get()
    sdt = entry_sdt.get()
    diachi = entry_diachi.get()
    banglai = entry_banglai.get()
    ngay_bl = date_banglai.get()
    
    trangthai_nv = cbb_trangthai_nv_var.get().split('=')[0].strip()
    trangthai_lx = cbb_trangthai_lx_var.get().split('=')[0].strip()

    if not manv or not hoten:
        messagebox.showwarning("Thiếu dữ liệu", "Vui lòng nhập Mã Nhân Viên và Họ Tên")
        return

    conn = connect_db()
    if conn is None:
        return

    try:
        cur = conn.cursor()
        
        # Thao tác 1: INSERT vào NhanVien (bảng cha)
        sql_nhanvien = """
        INSERT INTO NhanVien (MaNhanVien, HoVaTen, SoDienThoai, DiaChi, TrangThai) 
        VALUES (?, ?, ?, ?, ?)
        """
        cur.execute(sql_nhanvien, (manv, hoten, sdt, diachi, int(trangthai_nv)))
        
        # Thao tác 2: INSERT vào TaiXe (bảng con)
        # Bỏ qua DiemDanhGia (để lấy default)
        sql_taixe = """
        INSERT INTO TaiXe (MaNhanVien, HangBangLai, NgayHetHanBangLai, TrangThaiTaiXe) 
        VALUES (?, ?, ?, ?)
        """
        cur.execute(sql_taixe, (manv, banglai, ngay_bl, int(trangthai_lx)))
        
        conn.commit()
        messagebox.showinfo("Thành công", "Đã thêm tài xế mới thành công")
        
        clear_input()
        load_data()
        
    except pyodbc.IntegrityError:
        messagebox.showerror("Lỗi Trùng lặp", f"Mã nhân viên '{manv}' đã tồn tại.")
    except pyodbc.Error as e:
        # Nếu lỗi, rollback để tránh thêm dữ liệu 1/2
        conn.rollback() 
        messagebox.showerror("Lỗi SQL", f"Không thể thêm tài xế:\n{str(e)}")
    except Exception as e:
        conn.rollback()
        messagebox.showerror("Lỗi không xác định", f"Lỗi: {str(e)}")
    finally:
        if conn:
            conn.close()

def chon_taixe_de_sua():
    """Lấy thông tin tài xế được chọn và điền vào form."""
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Chưa chọn", "Hãy chọn một tài xế để sửa")
        return

    selected_item = tree.item(selected[0])
    manv = selected_item['values'][0]
    
    conn = connect_db()
    if conn is None:
        return

    try:
        cur = conn.cursor()
        # Lấy TOÀN BỘ dữ liệu (JOIN cả 2 bảng)
        sql = """
        SELECT * FROM NhanVien nv
        JOIN TaiXe tx ON nv.MaNhanVien = tx.MaNhanVien
        WHERE nv.MaNhanVien = ?
        """
        cur.execute(sql, (manv,))
        data = cur.fetchone()
        
        if not data:
            messagebox.showerror("Lỗi", "Không tìm thấy dữ liệu tài xế.")
            return

        clear_input()
        
        # Điền dữ liệu vào form
        entry_manv.insert(0, data.MaNhanVien)
        entry_manv.config(state='disabled') # Khóa Mã NV khi sửa
        
        # Bảng NhanVien
        entry_hoten.insert(0, data.HoVaTen or "")
        entry_sdt.insert(0, data.SoDienThoai or "")
        entry_diachi.insert(0, data.DiaChi or "")
        cbb_trangthai_nv.set(f"{data.TrangThai} = {'Đang làm việc' if data.TrangThai == 1 else 'Nghỉ'}")

        # Bảng TaiXe
        entry_banglai.insert(0, data.HangBangLai or "")
        if data.NgayHetHanBangLai:
            date_banglai.set_date(data.NgayHetHanBangLai)
        cbb_trangthai_lx.set(f"{data.TrangThaiTaiXe} = {'Rảnh' if data.TrangThaiTaiXe == 1 else 'Đang lái'}")

    except pyodbc.Error as e:
        messagebox.showerror("Lỗi SQL", f"Không thể lấy dữ liệu tài xế:\n{str(e)}")
    except Exception as e:
        messagebox.showerror("Lỗi không xác định", f"Lỗi: {str(e)}")
    finally:
        if conn:
            conn.close()

def luu_taixe_da_sua():
    """Lưu thay đổi (UPDATE) sau khi sửa (vào cả 2 bảng)."""
    manv = entry_manv.get()
    if not manv:
        messagebox.showwarning("Thiếu dữ liệu", "Không có Mã Nhân Viên để cập nhật")
        return

    # Lấy dữ liệu từ form
    hoten = entry_hoten.get()
    sdt = entry_sdt.get()
    diachi = entry_diachi.get()
    banglai = entry_banglai.get()
    ngay_bl = date_banglai.get()
    
    trangthai_nv = cbb_trangthai_nv_var.get().split('=')[0].strip()
    trangthai_lx = cbb_trangthai_lx_var.get().split('=')[0].strip()

    conn = connect_db()
    if conn is None:
        return
        
    try:
        cur = conn.cursor()
        
        # Thao tác 1: UPDATE NhanVien
        sql_nhanvien = """
        UPDATE NhanVien SET 
            HoVaTen = ?, SoDienThoai = ?, DiaChi = ?, TrangThai = ?
        WHERE MaNhanVien = ?
        """
        cur.execute(sql_nhanvien, (hoten, sdt, diachi, int(trangthai_nv), manv))
        
        # Thao tác 2: UPDATE TaiXe
        sql_taixe = """
        UPDATE TaiXe SET 
            HangBangLai = ?, NgayHetHanBangLai = ?, TrangThaiTaiXe = ?
        WHERE MaNhanVien = ?
        """
        cur.execute(sql_taixe, (banglai, ngay_bl, int(trangthai_lx), manv))
        
        conn.commit()
        messagebox.showinfo("Thành công", "Đã cập nhật thông tin tài xế")
        
        clear_input()
        load_data()
        
    except pyodbc.Error as e:
        conn.rollback()
        messagebox.showerror("Lỗi SQL", f"Không thể cập nhật tài xế:\n{str(e)}")
    except Exception as e:
        conn.rollback()
        messagebox.showerror("Lỗi không xác định", f"Lỗi: {str(e)}")
    finally:
        if conn:
            conn.close()

def xoa_taixe():
    """Xóa tài xế được chọn (khỏi cả 2 bảng)."""
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Chưa chọn", "Hãy chọn một tài xế để xóa")
        return

    selected_item = tree.item(selected[0])
    manv = selected_item['values'][0]
    hoten = selected_item['values'][1]

    if not messagebox.askyesno("Xác nhận", f"Bạn có chắc chắn muốn xóa tài xế '{hoten}' (Mã: {manv})?"):
        return

    conn = connect_db()
    if conn is None:
        return
        
    try:
        cur = conn.cursor()
        
        # Thao tác 1: Xóa khỏi TaiXe (bảng con)
        # BẮT BUỘC xóa bảng con trước
        cur.execute("DELETE FROM TaiXe WHERE MaNhanVien=?", (manv,))
        
        # Thao tác 2: Xóa khỏi NhanVien (bảng cha)
        cur.execute("DELETE FROM NhanVien WHERE MaNhanVien=?", (manv,))
        
        conn.commit()
        
        messagebox.showinfo("Thành công", "Đã xóa tài xế thành công")
        clear_input()
        load_data()
        
    except pyodbc.IntegrityError:
        conn.rollback()
        messagebox.showerror("Lỗi Ràng buộc", "Không thể xóa nhân viên này.\nNgười này có thể đã được gán cho một Chuyến đi, Tài khoản, hoặc đang lái một Xe.")
    except pyodbc.Error as e:
        conn.rollback()
        messagebox.showerror("Lỗi SQL", f"Không thể xóa tài xế:\n{str(e)}")
    except Exception as e:
        conn.rollback()
        messagebox.showerror("Lỗi không xác định", f"Lỗi: {str(e)}")
    finally:
        if conn:
            conn.close()

# ================================================================
# PHẦN 3: THIẾT KẾ GIAO DIỆN (CHO TÀI XẾ)
# ================================================================

# ===== Cửa sổ chính =====
root = tk.Tk()
root.title("Quản lý Tài xế (Database QL_VanTai)")

def center_window(w, h):
    ws = root.winfo_screenwidth()
    hs = root.winfo_screenheight()
    x = (ws/2) - (w/2)
    y = (hs/2) - (h/2)
    root.geometry('%dx%d+%d+%d' % (w, h, x, y))

center_window(900, 650) 
root.resizable(False, False)

# ===== Tiêu đề =====
lbl_title = tk.Label(root, text="QUẢN LÝ TÀI XẾ", font=("Arial", 18, "bold"))
lbl_title.pack(pady=10)

# ===== Frame nhập thông tin (2 cột) =====
frame_info = tk.Frame(root)
frame_info.pack(pady=5, padx=10, fill="x")

# --- Cột 1 ---
tk.Label(frame_info, text="Mã nhân viên:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
entry_manv = tk.Entry(frame_info, width=25)
entry_manv.grid(row=0, column=1, padx=5, pady=5, sticky="w")

tk.Label(frame_info, text="Họ và tên:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
entry_hoten = tk.Entry(frame_info, width=25)
entry_hoten.grid(row=1, column=1, padx=5, pady=5, sticky="w")

tk.Label(frame_info, text="Số điện thoại:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
entry_sdt = tk.Entry(frame_info, width=25)
entry_sdt.grid(row=2, column=1, padx=5, pady=5, sticky="w")

tk.Label(frame_info, text="Địa chỉ:").grid(row=3, column=0, padx=5, pady=5, sticky="w")
entry_diachi = tk.Entry(frame_info, width=25)
entry_diachi.grid(row=3, column=1, padx=5, pady=5, sticky="w")

# --- Cột 2 ---
tk.Label(frame_info, text="Hạng bằng lái:").grid(row=0, column=2, padx=15, pady=5, sticky="w")
entry_banglai = tk.Entry(frame_info, width=25)
entry_banglai.grid(row=0, column=3, padx=5, pady=5, sticky="w")

tk.Label(frame_info, text="Ngày hết hạn BL:").grid(row=1, column=2, padx=15, pady=5, sticky="w")
date_banglai = DateEntry(frame_info, width=22, background='darkblue', foreground='white', date_pattern='yyyy-MM-dd')
date_banglai.grid(row=1, column=3, padx=5, pady=5, sticky="w")

tk.Label(frame_info, text="Trạng thái NV:").grid(row=2, column=2, padx=15, pady=5, sticky="w")
trangthai_nv_options = ["0 = Nghỉ", "1 = Đang làm việc"]
cbb_trangthai_nv_var = tk.StringVar()
cbb_trangthai_nv = ttk.Combobox(frame_info, textvariable=cbb_trangthai_nv_var, values=trangthai_nv_options, width=22, state='readonly')
cbb_trangthai_nv.grid(row=2, column=3, padx=5, pady=5, sticky="w")
cbb_trangthai_nv.set("1 = Đang làm việc") # Mặc định

tk.Label(frame_info, text="Trạng thái Lái:").grid(row=3, column=2, padx=15, pady=5, sticky="w")
trangthai_lx_options = ["1 = Rảnh", "2 = Đang lái"]
cbb_trangthai_lx_var = tk.StringVar()
cbb_trangthai_lx = ttk.Combobox(frame_info, textvariable=cbb_trangthai_lx_var, values=trangthai_lx_options, width=22, state='readonly')
cbb_trangthai_lx.grid(row=3, column=3, padx=5, pady=5, sticky="w")
cbb_trangthai_lx.set("1 = Rảnh") # Mặc định

# Cấu hình grid co giãn
frame_info.columnconfigure(1, weight=1)
frame_info.columnconfigure(3, weight=1)

# ===== Frame nút =====
frame_btn = tk.Frame(root)
frame_btn.pack(pady=10)

# Cập nhật command cho các nút
btn_them = tk.Button(frame_btn, text="Thêm", width=8, command=them_taixe)
btn_them.grid(row=0, column=0, padx=5)

btn_luu = tk.Button(frame_btn, text="Lưu", width=8, command=luu_taixe_da_sua)
btn_luu.grid(row=0, column=1, padx=5)

btn_sua = tk.Button(frame_btn, text="Sửa", width=8, command=chon_taixe_de_sua)
btn_sua.grid(row=0, column=2, padx=5)

btn_huy = tk.Button(frame_btn, text="Hủy", width=8, command=clear_input)
btn_huy.grid(row=0, column=3, padx=5)

btn_xoa = tk.Button(frame_btn, text="Xóa", width=8, command=xoa_taixe)
btn_xoa.grid(row=0, column=4, padx=5)

btn_thoat = tk.Button(frame_btn, text="Thoát", width=8, command=root.quit)
btn_thoat.grid(row=0, column=5, padx=5)


# ===== Bảng danh sách tài xế =====
lbl_ds = tk.Label(root, text="Danh sách tài xế", font=("Arial", 10, "bold"))
lbl_ds.pack(pady=5, padx=10, anchor="w")

frame_tree = tk.Frame(root)
frame_tree.pack(pady=10, padx=10, fill="both", expand=True)

scrollbar_y = tk.Scrollbar(frame_tree, orient=tk.VERTICAL)
scrollbar_x = tk.Scrollbar(frame_tree, orient=tk.HORIZONTAL)

# Cập nhật cột cho Treeview
columns = ("manv", "hoten", "sdt", "banglai", "trangthai_nv", "trangthai_lx")
tree = ttk.Treeview(frame_tree, columns=columns, show="headings", height=10,
                    yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)

scrollbar_y.config(command=tree.yview)
scrollbar_x.config(command=tree.xview)

scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)

# Định nghĩa các cột
tree.heading("manv", text="Mã NV")
tree.column("manv", width=80, anchor="center")

tree.heading("hoten", text="Họ Tên")
tree.column("hoten", width=150)

tree.heading("sdt", text="Số điện thoại")
tree.column("sdt", width=120)

tree.heading("banglai", text="Hạng Bằng Lái")
tree.column("banglai", width=100, anchor="center")

tree.heading("trangthai_nv", text="Trạng thái NV")
tree.column("trangthai_nv", width=120, anchor="center")

tree.heading("trangthai_lx", text="Trạng thái Lái")
tree.column("trangthai_lx", width=120, anchor="center")

tree.pack(fill="both", expand=True)

# ================================================================
# PHẦN 4: CHẠY ỨNG DỤNG
# ================================================================
load_data() # Tải dữ liệu ban đầu
root.mainloop()