import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
import pyodbc 
from datetime import datetime

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
# PHẦN 2: CÁC HÀM TIỆN ÍCH (Tải Combobox - Tái sử dụng)
# ================================================================
def load_taixe_combobox():
    """Tải danh sách tài xế (MaNhanVien - HoVaTen) vào Combobox."""
    conn = connect_db()
    if conn is None:
        return []
    
    try:
        cur = conn.cursor()
        sql = """
        SELECT tx.MaNhanVien, nv.HoVaTen 
        FROM TaiXe tx
        JOIN NhanVien nv ON tx.MaNhanVien = nv.MaNhanVien
        WHERE nv.TrangThai = 1
        ORDER BY nv.HoVaTen
        """
        cur.execute(sql)
        rows = cur.fetchall()
        return [f"{row[0]} - {row[1]}" for row in rows]
    except Exception as e:
        print(f"Lỗi tải combobox tài xế: {e}")
        return []
    finally:
        if conn:
            conn.close()

def load_xe_combobox():
    """Tải danh sách xe (BienSoXe) vào Combobox."""
    conn = connect_db()
    if conn is None:
        return []
    
    try:
        cur = conn.cursor()
        sql = "SELECT BienSoXe FROM Xe WHERE TrangThai = 1 ORDER BY BienSoXe"
        cur.execute(sql)
        rows = cur.fetchall()
        return [row[0] for row in rows]
    except Exception as e:
        print(f"Lỗi tải combobox xe: {e}")
        return []
    finally:
        if conn:
            conn.close()

# ================================================================
# PHẦN 3: CÁC HÀM CRUD (CHO NHIÊN LIỆU)
# ================================================================

def clear_input():
    """Xóa trắng các trường nhập liệu."""
    entry_manhatky.config(state='normal')
    entry_manhatky.delete(0, tk.END)
    entry_manhatky.config(state='disabled')
    
    cbb_taixe.set("")
    cbb_xe.set("")
    entry_solit.delete(0, tk.END)
    entry_tongchiphi.delete(0, tk.END)
    entry_soodo.delete(0, tk.END)
    
    # Đặt lại ngày/giờ
    now = datetime.now()
    date_ngaydo.set_date(now.strftime("%Y-%m-%d"))
    entry_giodo.delete(0, tk.END)
    entry_giodo.insert(0, now.strftime("%H:%M"))
    
    cbb_trangthai.set("0 = Chờ duyệt")
    cbb_xe.focus()

def load_data():
    """Tải dữ liệu từ NhatKyNhienLieu lên Treeview."""
    for i in tree.get_children():
        tree.delete(i)
        
    conn = connect_db()
    if conn is None:
        return
        
    try:
        cur = conn.cursor()
        sql = """
        SELECT 
            nk.MaNhatKy, 
            nk.BienSoXe, 
            nv.HoVaTen, 
            nk.NgayDoNhienLieu, 
            nk.SoLit, 
            nk.TongChiPhi,
            nk.TrangThaiDuyet
        FROM NhatKyNhienLieu AS nk
        LEFT JOIN NhanVien AS nv ON nk.MaNhanVien = nv.MaNhanVien
        ORDER BY nk.NgayDoNhienLieu DESC
        """
        cur.execute(sql)
        rows = cur.fetchall()
        
        trangthai_map = {
            0: "Chờ duyệt",
            1: "Đã duyệt",
            2: "Từ chối"
        }
        
        for row in rows:
            ma_nk = row[0]
            bienso = row[1]
            ten_tx = row[2] or "N/A"
            ngay_do = row[3].strftime("%Y-%m-%d %H:%M") if row[3] else "N/A"
            so_lit = row[4]
            tong_cp = row[5]
            trangthai_text = trangthai_map.get(row[6], "Không rõ")
            
            tree.insert("", tk.END, values=(ma_nk, bienso, ten_tx, ngay_do, so_lit, tong_cp, trangthai_text))
            
    except pyodbc.Error as e:
        messagebox.showerror("Lỗi tải dữ liệu", f"Lỗi SQL: {str(e)}")
    except Exception as e:
        messagebox.showerror("Lỗi không xác định", f"Lỗi: {str(e)}")
    finally:
        if conn:
            conn.close()

def them_nhienlieu():
    """Thêm một nhật ký nhiên liệu mới."""
    try:
        bienso = cbb_xe_var.get()
        manv = cbb_taixe_var.get().split(' - ')[0]
        
        ngay_do_str = date_ngaydo.get()
        gio_do_str = entry_giodo.get() or "00:00"
        tg_nhienlieu = f"{ngay_do_str} {gio_do_str}:00"
        
        solit = entry_solit.get()
        tongchiphi = entry_tongchiphi.get()
        soodo = entry_soodo.get()
        
        trangthai = cbb_trangthai_var.get().split('=')[0].strip()

        if not bienso or not manv or not solit or not tongchiphi:
            messagebox.showwarning("Thiếu dữ liệu", "Vui lòng nhập Xe, Tài xế, Số lít và Chi phí")
            return

        # Chuyển đổi kiểu dữ liệu
        solit_dec = float(solit) if solit else 0.0
        tongchiphi_dec = float(tongchiphi) if tongchiphi else 0.0
        soodo_int = int(soodo) if soodo else None

    except Exception as e:
        messagebox.showerror("Lỗi định dạng", f"Dữ liệu số (lít, chi phí, odo) không hợp lệ: {e}")
        return

    conn = connect_db()
    if conn is None:
        return

    try:
        cur = conn.cursor()
        
        sql = """
        INSERT INTO NhatKyNhienLieu (
            BienSoXe, MaNhanVien, NgayDoNhienLieu, SoLit, 
            TongChiPhi, SoOdo, TrangThaiDuyet
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        cur.execute(sql, (bienso, manv, tg_nhienlieu, solit_dec, tongchiphi_dec, soodo_int, int(trangthai)))
        
        conn.commit()
        messagebox.showinfo("Thành công", "Đã thêm nhật ký nhiên liệu thành công")
        
        clear_input()
        load_data()
        
    except pyodbc.Error as e:
        conn.rollback() 
        messagebox.showerror("Lỗi SQL", f"Không thể thêm nhật ký:\n{str(e)}")
    except Exception as e:
        conn.rollback()
        messagebox.showerror("Lỗi không xác định", f"Lỗi: {str(e)}")
    finally:
        if conn:
            conn.close()

def chon_nhienlieu_de_sua():
    """Lấy thông tin nhật ký được chọn và điền vào form."""
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Chưa chọn", "Hãy chọn một nhật ký để sửa")
        return

    selected_item = tree.item(selected[0])
    manhatky = selected_item['values'][0]
    
    conn = connect_db()
    if conn is None:
        return

    try:
        cur = conn.cursor()
        sql = """
        SELECT nk.*, nv.HoVaTen 
        FROM NhatKyNhienLieu nk
        LEFT JOIN NhanVien nv ON nk.MaNhanVien = nv.MaNhanVien
        WHERE nk.MaNhatKy = ?
        """
        cur.execute(sql, (manhatky,))
        data = cur.fetchone()
        
        if not data:
            messagebox.showerror("Lỗi", "Không tìm thấy dữ liệu nhật ký.")
            return

        clear_input()
        
        entry_manhatky.config(state='normal')
        entry_manhatky.insert(0, data.MaNhatKy)
        entry_manhatky.config(state='disabled')
        
        cbb_xe.set(data.BienSoXe or "")
        
        if data.MaNhanVien:
            cbb_taixe_val = f"{data.MaNhanVien} - {data.HoVaTen}"
            cbb_taixe.set(cbb_taixe_val)
        
        if data.NgayDoNhienLieu:
            date_ngaydo.set_date(data.NgayDoNhienLieu.strftime("%Y-%m-%d"))
            entry_giodo.insert(0, data.NgayDoNhienLieu.strftime("%H:%M"))
            
        entry_solit.insert(0, str(data.SoLit or ""))
        entry_tongchiphi.insert(0, str(data.TongChiPhi or ""))
        entry_soodo.insert(0, str(data.SoOdo or ""))

        trangthai_map = {0: "0 = Chờ duyệt", 1: "1 = Đã duyệt", 2: "2 = Từ chối"}
        cbb_trangthai.set(trangthai_map.get(data.TrangThaiDuyet, "0 = Chờ duyệt"))

    except pyodbc.Error as e:
        messagebox.showerror("Lỗi SQL", f"Không thể lấy dữ liệu:\n{str(e)}")
    except Exception as e:
        messagebox.showerror("Lỗi không xác định", f"Lỗi: {str(e)}")
    finally:
        if conn:
            conn.close()

def luu_nhienlieu_da_sua():
    """Lưu thay đổi (UPDATE) sau khi sửa."""
    manhatky = entry_manhatky.get()
    if not manhatky:
        messagebox.showwarning("Thiếu dữ liệu", "Không có Mã nhật ký để cập nhật")
        return

    try:
        bienso = cbb_xe_var.get()
        manv = cbb_taixe_var.get().split(' - ')[0]
        
        ngay_do_str = date_ngaydo.get()
        gio_do_str = entry_giodo.get() or "00:00"
        tg_nhienlieu = f"{ngay_do_str} {gio_do_str}:00"
        
        solit = entry_solit.get()
        tongchiphi = entry_tongchiphi.get()
        soodo = entry_soodo.get()
        
        trangthai = cbb_trangthai_var.get().split('=')[0].strip()

        solit_dec = float(solit) if solit else 0.0
        tongchiphi_dec = float(tongchiphi) if tongchiphi else 0.0
        soodo_int = int(soodo) if soodo else None

    except Exception as e:
        messagebox.showerror("Lỗi định dạng", f"Dữ liệu nhập không hợp lệ: {e}")
        return

    conn = connect_db()
    if conn is None:
        return
        
    try:
        cur = conn.cursor()
        
        sql = """
        UPDATE NhatKyNhienLieu SET 
            BienSoXe = ?, MaNhanVien = ?, NgayDoNhienLieu = ?, 
            SoLit = ?, TongChiPhi = ?, SoOdo = ?, TrangThaiDuyet = ?
        WHERE MaNhatKy = ?
        """
        cur.execute(sql, (
            bienso, manv, tg_nhienlieu, 
            solit_dec, tongchiphi_dec, soodo_int, int(trangthai),
            manhatky
        ))
        
        conn.commit()
        messagebox.showinfo("Thành công", "Đã cập nhật nhật ký nhiên liệu")
        
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

def xoa_nhienlieu():
    """Xóa nhật ký được chọn."""
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Chưa chọn", "Hãy chọn một nhật ký để xóa")
        return

    selected_item = tree.item(selected[0])
    manhatky = selected_item['values'][0]

    if not messagebox.askyesno("Xác nhận", f"Bạn có chắc chắn muốn xóa Nhật ký Mã: {manhatky}?"):
        return

    conn = connect_db()
    if conn is None:
        return
        
    try:
        cur = conn.cursor()
        cur.execute("DELETE FROM NhatKyNhienLieu WHERE MaNhatKy=?", (manhatky,))
        conn.commit()
        
        messagebox.showinfo("Thành công", "Đã xóa nhật ký thành công")
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
# PHẦN 4: THIẾT KẾ GIAO DIỆN (CHO NHIÊN LIỆU)
# ================================================================

root = tk.Tk()
root.title("Quản lý Nhiên liệu (Database QL_VanTai)")

def center_window(w, h):
    ws = root.winfo_screenwidth()
    hs = root.winfo_screenheight()
    x = (ws/2) - (w/2)
    y = (hs/2) - (h/2)
    root.geometry('%dx%d+%d+%d' % (w, h, x, y))

center_window(950, 700) 
root.resizable(False, False)

lbl_title = tk.Label(root, text="QUẢN LÝ NHẬT KÝ NHIÊN LIỆU", font=("Arial", 18, "bold"))
lbl_title.pack(pady=10)

frame_info = tk.Frame(root)
frame_info.pack(pady=5, padx=10, fill="x")

# --- Hàng 1 ---
tk.Label(frame_info, text="Mã nhật ký:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
entry_manhatky = tk.Entry(frame_info, width=25, state='disabled')
entry_manhatky.grid(row=0, column=1, padx=5, pady=5, sticky="w")

tk.Label(frame_info, text="Trạng thái:").grid(row=0, column=2, padx=15, pady=5, sticky="w")
trangthai_options = [
    "0 = Chờ duyệt",
    "1 = Đã duyệt",
    "2 = Từ chối"
]
cbb_trangthai_var = tk.StringVar()
cbb_trangthai = ttk.Combobox(frame_info, textvariable=cbb_trangthai_var, values=trangthai_options, width=30, state='readonly')
cbb_trangthai.grid(row=0, column=3, padx=5, pady=5, sticky="w")
cbb_trangthai.set("0 = Chờ duyệt")

# --- Hàng 2 ---
tk.Label(frame_info, text="Xe:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
cbb_xe_var = tk.StringVar()
cbb_xe = ttk.Combobox(frame_info, textvariable=cbb_xe_var, width=22, state='readonly')
cbb_xe.grid(row=1, column=1, padx=5, pady=5, sticky="w")
cbb_xe['values'] = load_xe_combobox()

tk.Label(frame_info, text="Tài xế đổ:").grid(row=1, column=2, padx=15, pady=5, sticky="w")
cbb_taixe_var = tk.StringVar()
cbb_taixe = ttk.Combobox(frame_info, textvariable=cbb_taixe_var, width=30, state='readonly')
cbb_taixe.grid(row=1, column=3, padx=5, pady=5, sticky="w")
cbb_taixe['values'] = load_taixe_combobox()


# --- Hàng 3 (Thời gian) ---
tk.Label(frame_info, text="Ngày đổ:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
date_ngaydo = DateEntry(frame_info, width=22, background='darkblue', foreground='white', date_pattern='yyyy-MM-dd')
date_ngaydo.grid(row=2, column=1, padx=5, pady=5, sticky="w")

tk.Label(frame_info, text="Giờ đổ (HH:MM):").grid(row=2, column=2, padx=15, pady=5, sticky="w")
entry_giodo = tk.Entry(frame_info, width=32)
entry_giodo.grid(row=2, column=3, padx=5, pady=5, sticky="w")

# --- Hàng 4 (Chi phí) ---
tk.Label(frame_info, text="Số lít:").grid(row=3, column=0, padx=5, pady=5, sticky="w")
entry_solit = tk.Entry(frame_info, width=25)
entry_solit.grid(row=3, column=1, padx=5, pady=5, sticky="w")

tk.Label(frame_info, text="Tổng chi phí:").grid(row=3, column=2, padx=15, pady=5, sticky="w")
entry_tongchiphi = tk.Entry(frame_info, width=32)
entry_tongchiphi.grid(row=3, column=3, padx=5, pady=5, sticky="w")

# --- Hàng 5 (Odo) ---
tk.Label(frame_info, text="Số Odo (Km):").grid(row=4, column=0, padx=5, pady=5, sticky="w")
entry_soodo = tk.Entry(frame_info, width=25)
entry_soodo.grid(row=4, column=1, padx=5, pady=5, sticky="w")


# Cấu hình grid co giãn
frame_info.columnconfigure(1, weight=1)
frame_info.columnconfigure(3, weight=1)

# ===== Frame nút =====
frame_btn = tk.Frame(root)
frame_btn.pack(pady=10)

btn_them = tk.Button(frame_btn, text="Thêm", width=8, command=them_nhienlieu)
btn_them.grid(row=0, column=0, padx=5)

btn_luu = tk.Button(frame_btn, text="Lưu", width=8, command=luu_nhienlieu_da_sua)
btn_luu.grid(row=0, column=1, padx=5)

btn_sua = tk.Button(frame_btn, text="Sửa", width=8, command=chon_nhienlieu_de_sua)
btn_sua.grid(row=0, column=2, padx=5)

btn_huy = tk.Button(frame_btn, text="Hủy", width=8, command=clear_input)
btn_huy.grid(row=0, column=3, padx=5)

btn_xoa = tk.Button(frame_btn, text="Xóa", width=8, command=xoa_nhienlieu)
btn_xoa.grid(row=0, column=4, padx=5)

btn_thoat = tk.Button(frame_btn, text="Thoát", width=8, command=root.quit)
btn_thoat.grid(row=0, column=5, padx=5)


# ===== Bảng danh sách =====
lbl_ds = tk.Label(root, text="Danh sách nhật ký nhiên liệu (Sắp xếp mới nhất)", font=("Arial", 10, "bold"))
lbl_ds.pack(pady=5, padx=10, anchor="w")

frame_tree = tk.Frame(root)
frame_tree.pack(pady=10, padx=10, fill="both", expand=True)

scrollbar_y = tk.Scrollbar(frame_tree, orient=tk.VERTICAL)
scrollbar_x = tk.Scrollbar(frame_tree, orient=tk.HORIZONTAL)

columns = ("ma_nk", "bienso", "ten_tx", "ngay_do", "so_lit", "tong_cp", "trangthai")
tree = ttk.Treeview(frame_tree, columns=columns, show="headings", height=10,
                    yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)

scrollbar_y.config(command=tree.yview)
scrollbar_x.config(command=tree.xview)

scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)

# Định nghĩa các cột
tree.heading("ma_nk", text="Mã NK")
tree.column("ma_nk", width=60, anchor="center")

tree.heading("bienso", text="Biển số xe")
tree.column("bienso", width=100)

tree.heading("ten_tx", text="Tên Tài xế")
tree.column("ten_tx", width=150)

tree.heading("ngay_do", text="Ngày đổ")
tree.column("ngay_do", width=150)

tree.heading("so_lit", text="Số lít")
tree.column("so_lit", width=80, anchor="e") # Căn phải (end)

tree.heading("tong_cp", text="Tổng chi phí")
tree.column("tong_cp", width=100, anchor="e") # Căn phải

tree.heading("trangthai", text="Trạng thái")
tree.column("trangthai", width=100, anchor="center")

tree.pack(fill="both", expand=True)

# ================================================================
# PHẦN 5: CHẠY ỨNG DỤNG
# ================================================================
clear_input() 
load_data() 
root.mainloop()