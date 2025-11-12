import tkinter as tk
from tkinter import ttk, messagebox
# Bỏ DateEntry vì form này không cần
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
# PHẦN 2: CÁC HÀM CRUD (CHO NHÂN VIÊN CHUNG)
# ================================================================

def clear_input():
    """Xóa trắng các trường nhập liệu."""
    entry_manv.config(state='normal') # Mở khóa trường Mã NV
    entry_manv.delete(0, tk.END)
    entry_hoten.delete(0, tk.END)
    entry_sdt.delete(0, tk.END)
    entry_diachi.delete(0, tk.END)
    
    cbb_trangthai_nv.set("1 = Đang làm việc")
    
    entry_manv.focus()

def load_data():
    """Tải dữ liệu từ NhanVien (CHỈ NHỮNG NGƯỜI KHÔNG PHẢI TÀI XẾ)."""
    for i in tree.get_children():
        tree.delete(i)
        
    conn = connect_db()
    if conn is None:
        return
        
    try:
        cur = conn.cursor()
        # Lấy NV KHÔNG CÓ trong bảng TaiXe
        sql = "SELECT MaNhanVien, HoVaTen, SoDienThoai, DiaChi, TrangThai FROM NhanVien"
        cur.execute(sql)
        rows = cur.fetchall()
        
        for row in rows:
            trang_thai_nv_text = "Đang làm việc" if row[4] == 1 else "Nghỉ"
            
            tree.insert("", tk.END, values=(
                row[0], # MaNhanVien
                row[1], # HoVaTen
                row[2], # SoDienThoai
                row[3], # DiaChi
                trang_thai_nv_text # TrangThai
            ))
            
    except pyodbc.Error as e:
        messagebox.showerror("Lỗi tải dữ liệu", f"Lỗi SQL: {str(e)}")
    except Exception as e:
        messagebox.showerror("Lỗi không xác định", f"Lỗi: {str(e)}")
    finally:
        if conn:
            conn.close()

def them_nhanvien():
    """Thêm một nhân viên mới (chỉ vào bảng NhanVien)."""
    manv = entry_manv.get()
    hoten = entry_hoten.get()
    sdt = entry_sdt.get()
    diachi = entry_diachi.get()
    trangthai_nv = cbb_trangthai_nv_var.get().split('=')[0].strip()

    if not manv or not hoten:
        messagebox.showwarning("Thiếu dữ liệu", "Vui lòng nhập Mã Nhân Viên và Họ Tên")
        return

    conn = connect_db()
    if conn is None:
        return

    try:
        cur = conn.cursor()
        
        # Chỉ INSERT vào NhanVien
        sql_nhanvien = """
        INSERT INTO NhanVien (MaNhanVien, HoVaTen, SoDienThoai, DiaChi, TrangThai) 
        VALUES (?, ?, ?, ?, ?)
        """
        cur.execute(sql_nhanvien, (manv, hoten, sdt, diachi, int(trangthai_nv)))
        
        conn.commit()
        messagebox.showinfo("Thành công", "Đã thêm nhân viên mới thành công")
        
        clear_input()
        load_data()
        
    except pyodbc.IntegrityError:
        messagebox.showerror("Lỗi Trùng lặp", f"Mã nhân viên '{manv}' đã tồn tại.")
    except pyodbc.Error as e:
        conn.rollback() 
        messagebox.showerror("Lỗi SQL", f"Không thể thêm nhân viên:\n{str(e)}")
    except Exception as e:
        conn.rollback()
        messagebox.showerror("Lỗi không xác định", f"Lỗi: {str(e)}")
    finally:
        if conn:
            conn.close()

def chon_nhanvien_de_sua():
    """Lấy thông tin nhân viên được chọn và điền vào form."""
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Chưa chọn", "Hãy chọn một nhân viên để sửa")
        return

    selected_item = tree.item(selected[0])
    manv = selected_item['values'][0]
    
    conn = connect_db()
    if conn is None:
        return

    try:
        cur = conn.cursor()
        sql = "SELECT * FROM NhanVien WHERE MaNhanVien = ?"
        cur.execute(sql, (manv,))
        data = cur.fetchone()
        
        if not data:
            messagebox.showerror("Lỗi", "Không tìm thấy dữ liệu nhân viên.")
            return

        clear_input()
        
        entry_manv.insert(0, data.MaNhanVien)
        entry_manv.config(state='disabled') # Khóa Mã NV khi sửa
        
        entry_hoten.insert(0, data.HoVaTen or "")
        entry_sdt.insert(0, data.SoDienThoai or "")
        entry_diachi.insert(0, data.DiaChi or "")
        cbb_trangthai_nv.set(f"{data.TrangThai} = {'Đang làm việc' if data.TrangThai == 1 else 'Nghỉ'}")

    except pyodbc.Error as e:
        messagebox.showerror("Lỗi SQL", f"Không thể lấy dữ liệu:\n{str(e)}")
    except Exception as e:
        messagebox.showerror("Lỗi không xác định", f"Lỗi: {str(e)}")
    finally:
        if conn:
            conn.close()

def luu_nhanvien_da_sua():
    """Lưu thay đổi (UPDATE) sau khi sửa (chỉ bảng NhanVien)."""
    manv = entry_manv.get()
    if not manv:
        messagebox.showwarning("Thiếu dữ liệu", "Không có Mã Nhân Viên để cập nhật")
        return

    hoten = entry_hoten.get()
    sdt = entry_sdt.get()
    diachi = entry_diachi.get()
    trangthai_nv = cbb_trangthai_nv_var.get().split('=')[0].strip()

    conn = connect_db()
    if conn is None:
        return
        
    try:
        cur = conn.cursor()
        
        sql_nhanvien = """
        UPDATE NhanVien SET 
            HoVaTen = ?, SoDienThoai = ?, DiaChi = ?, TrangThai = ?
        WHERE MaNhanVien = ?
        """
        cur.execute(sql_nhanvien, (hoten, sdt, diachi, int(trangthai_nv), manv))
        
        conn.commit()
        messagebox.showinfo("Thành công", "Đã cập nhật thông tin nhân viên")
        
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

def xoa_nhanvien():
    """Xóa nhân viên (chỉ dành cho nhân viên không phải tài xế)."""
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Chưa chọn", "Hãy chọn một nhân viên để xóa")
        return

    selected_item = tree.item(selected[0])
    manv = selected_item['values'][0]
    hoten = selected_item['values'][1]

    if not messagebox.askyesno("Xác nhận", f"Bạn có chắc chắn muốn xóa nhân viên '{hoten}' (Mã: {manv})?"):
        return

    conn = connect_db()
    if conn is None:
        return
        
    try:
        cur = conn.cursor()
        
        # XỬ LÝ RÀNG BUỘC
        # 1. Xóa khỏi TaiKhoan (nếu có)
        cur.execute("DELETE FROM TaiKhoan WHERE MaNhanVien=?", (manv,))
        
        # 2. Gán NULL cho Xe (nếu nhân viên này đang giữ xe)
        cur.execute("UPDATE Xe SET MaNhanVienHienTai = NULL WHERE MaNhanVienHienTai = ?", (manv,))
        
        # 3. Cuối cùng, xóa khỏi NhanVien
        cur.execute("DELETE FROM NhanVien WHERE MaNhanVien=?", (manv,))
        
        conn.commit()
        
        messagebox.showinfo("Thành công", "Đã xóa nhân viên thành công")
        clear_input()
        load_data()
        
    except pyodbc.IntegrityError:
        conn.rollback()
        messagebox.showerror("Lỗi Ràng buộc", "Không thể xóa nhân viên này.\nNgười này có thể đang được gán cho một Chuyến đi hoặc có Nhật ký nhiên liệu.")
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
# PHẦN 3: THIẾT KẾ GIAO DIỆN (CHO NHÂN VIÊN CHUNG)
# ================================================================

root = tk.Tk()
root.title("Quản lý Nhân viên chung (Database QL_VanTai)")

def center_window(w, h):
    ws = root.winfo_screenwidth()
    hs = root.winfo_screenheight()
    x = (ws/2) - (w/2)
    y = (hs/2) - (h/2)
    root.geometry('%dx%d+%d+%d' % (w, h, x, y))

center_window(900, 600) # Cửa sổ nhỏ hơn 1 chút
root.resizable(False, False)

lbl_title = tk.Label(root, text="QUẢN LÝ NHÂN VIÊN CHUNG", font=("Arial", 18, "bold"))
lbl_title.pack(pady=10)

# Frame thông tin (chỉ 1 cột là đủ)
frame_info = tk.Frame(root)
frame_info.pack(pady=5, padx=10, fill="x")

tk.Label(frame_info, text="Mã nhân viên:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
entry_manv = tk.Entry(frame_info, width=30)
entry_manv.grid(row=0, column=1, padx=5, pady=5, sticky="w")

tk.Label(frame_info, text="Họ và tên:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
entry_hoten = tk.Entry(frame_info, width=30)
entry_hoten.grid(row=1, column=1, padx=5, pady=5, sticky="w")

tk.Label(frame_info, text="Số điện thoại:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
entry_sdt = tk.Entry(frame_info, width=30)
entry_sdt.grid(row=2, column=1, padx=5, pady=5, sticky="w")

tk.Label(frame_info, text="Địa chỉ:").grid(row=0, column=2, padx=15, pady=5, sticky="w")
entry_diachi = tk.Entry(frame_info, width=40)
entry_diachi.grid(row=0, column=3, padx=5, pady=5, sticky="w")

tk.Label(frame_info, text="Trạng thái NV:").grid(row=1, column=2, padx=15, pady=5, sticky="w")
trangthai_nv_options = ["0 = Nghỉ", "1 = Đang làm việc"]
cbb_trangthai_nv_var = tk.StringVar()
cbb_trangthai_nv = ttk.Combobox(frame_info, textvariable=cbb_trangthai_nv_var, values=trangthai_nv_options, width=30, state='readonly')
cbb_trangthai_nv.grid(row=1, column=3, padx=5, pady=5, sticky="w")
cbb_trangthai_nv.set("1 = Đang làm việc") # Mặc định

frame_info.columnconfigure(1, weight=1)
frame_info.columnconfigure(3, weight=1)

# ===== Frame nút =====
frame_btn = tk.Frame(root)
frame_btn.pack(pady=10)

btn_them = tk.Button(frame_btn, text="Thêm", width=8, command=them_nhanvien)
btn_them.grid(row=0, column=0, padx=5)

btn_luu = tk.Button(frame_btn, text="Lưu", width=8, command=luu_nhanvien_da_sua)
btn_luu.grid(row=0, column=1, padx=5)

btn_sua = tk.Button(frame_btn, text="Sửa", width=8, command=chon_nhanvien_de_sua)
btn_sua.grid(row=0, column=2, padx=5)

btn_huy = tk.Button(frame_btn, text="Hủy", width=8, command=clear_input)
btn_huy.grid(row=0, column=3, padx=5)

btn_xoa = tk.Button(frame_btn, text="Xóa", width=8, command=xoa_nhanvien)
btn_xoa.grid(row=0, column=4, padx=5)

btn_thoat = tk.Button(frame_btn, text="Thoát", width=8, command=root.quit)
btn_thoat.grid(row=0, column=5, padx=5)


# ===== Bảng danh sách tài xế =====
lbl_ds = tk.Label(root, text="Danh sách nhân viên (không phải tài xế)", font=("Arial", 10, "bold"))
lbl_ds.pack(pady=5, padx=10, anchor="w")

frame_tree = tk.Frame(root)
frame_tree.pack(pady=10, padx=10, fill="both", expand=True)

scrollbar_y = tk.Scrollbar(frame_tree, orient=tk.VERTICAL)
scrollbar_x = tk.Scrollbar(frame_tree, orient=tk.HORIZONTAL)

columns = ("manv", "hoten", "sdt", "diachi", "trangthai_nv")
tree = ttk.Treeview(frame_tree, columns=columns, show="headings", height=10,
                    yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)

scrollbar_y.config(command=tree.yview)
scrollbar_x.config(command=tree.xview)

scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)

tree.heading("manv", text="Mã NV")
tree.column("manv", width=80, anchor="center")

tree.heading("hoten", text="Họ Tên")
tree.column("hoten", width=150)

tree.heading("sdt", text="Số điện thoại")
tree.column("sdt", width=120)

tree.heading("diachi", text="Địa chỉ")
tree.column("diachi", width=200)

tree.heading("trangthai_nv", text="Trạng thái NV")
tree.column("trangthai_nv", width=120, anchor="center")

tree.pack(fill="both", expand=True)

# ================================================================
# PHẦN 4: CHẠY ỨNG DỤNG
# ================================================================
load_data() # Tải dữ liệu ban đầu
root.mainloop()