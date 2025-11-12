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
# PHẦN 2: CÁC HÀM TIỆN ÍCH (Tải Combobox)
# ================================================================
def load_taixe_combobox():
    """Tải danh sách tài xế (MaNhanVien - HoVaTen) vào Combobox."""
    conn = connect_db()
    if conn is None:
        return []
    
    try:
        cur = conn.cursor()
        # Lấy các tài xế đang làm việc
        sql = """
        SELECT tx.MaNhanVien, nv.HoVaTen 
        FROM TaiXe tx
        JOIN NhanVien nv ON tx.MaNhanVien = nv.MaNhanVien
        WHERE nv.TrangThai = 1
        ORDER BY nv.HoVaTen
        """
        cur.execute(sql)
        rows = cur.fetchall()
        # Format: "NV001 - Nguyễn Văn An"
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
        # Lấy các xe đang hoạt động
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
# PHẦN 3: CÁC HÀM CRUD (CHO CHUYẾN ĐI)
# ================================================================

def clear_input():
    """Xóa trắng các trường nhập liệu."""
    entry_machuyendi.config(state='normal')
    entry_machuyendi.delete(0, tk.END)
    entry_machuyendi.config(state='disabled')
    
    cbb_taixe.set("")
    cbb_xe.set("")
    entry_diembd.delete(0, tk.END)
    entry_diemkt.delete(0, tk.END)
    
    # Đặt lại ngày/giờ
    now = datetime.now()
    date_bd.set_date(now.strftime("%Y-%m-%d"))
    entry_giobd.delete(0, tk.END)
    entry_giobd.insert(0, now.strftime("%H:%M"))
    
    date_kt.set_date(now.strftime("%Y-%m-%d"))
    entry_giokt.delete(0, tk.END)
    entry_giokt.insert(0, "") # Giờ kết thúc để trống
    
    cbb_trangthai.set("0 = Đã gán")
    cbb_taixe.focus()

def load_data():
    """Tải dữ liệu từ ChuyenDi lên Treeview."""
    for i in tree.get_children():
        tree.delete(i)
        
    conn = connect_db()
    if conn is None:
        return
        
    try:
        cur = conn.cursor()
        # JOIN để lấy Tên tài xế thay vì Mã
        sql = """
        SELECT 
            cd.MaChuyenDi, 
            nv.HoVaTen, 
            cd.BienSoXe, 
            cd.ThoiGianBatDau, 
            cd.TrangThai
        FROM ChuyenDi AS cd
        LEFT JOIN NhanVien AS nv ON cd.MaNhanVien = nv.MaNhanVien
        ORDER BY cd.ThoiGianBatDau DESC
        """
        cur.execute(sql)
        rows = cur.fetchall()
        
        trangthai_map = {
            0: "Đã gán",
            1: "Đang thực hiện",
            2: "Hoàn thành",
            3: "Hủy"
        }
        
        for row in rows:
            ma_cd = row[0]
            ten_tx = row[1] or "N/A"
            bienso = row[2]
            tg_bd = row[3].strftime("%Y-%m-%d %H:%M") if row[3] else "N/A"
            trangthai_text = trangthai_map.get(row[4], "Không rõ")
            
            tree.insert("", tk.END, values=(ma_cd, ten_tx, bienso, tg_bd, trangthai_text))
            
    except pyodbc.Error as e:
        messagebox.showerror("Lỗi tải dữ liệu", f"Lỗi SQL: {str(e)}")
    except Exception as e:
        messagebox.showerror("Lỗi không xác định", f"Lỗi: {str(e)}")
    finally:
        if conn:
            conn.close()

def them_chuyendi():
    """Thêm một chuyến đi mới."""
    try:
        # Lấy Mã NV và Biển số từ combobox
        manv = cbb_taixe_var.get().split(' - ')[0]
        bienso = cbb_xe_var.get()
        
        diembd = entry_diembd.get()
        diemkt = entry_diemkt.get()
        
        # Ghép ngày + giờ
        ngay_bd_str = date_bd.get()
        gio_bd_str = entry_giobd.get() or "00:00"
        tg_batdau = f"{ngay_bd_str} {gio_bd_str}:00"
        
        # Xử lý thời gian kết thúc (có thể NULL)
        ngay_kt_str = date_kt.get()
        gio_kt_str = entry_giokt.get()
        tg_ketthuc = None
        if gio_kt_str: # Chỉ lưu nếu nhập giờ
            tg_ketthuc = f"{ngay_kt_str} {gio_kt_str}:00"
        
        trangthai = cbb_trangthai_var.get().split('=')[0].strip()

        if not manv or not bienso or not diembd:
            messagebox.showwarning("Thiếu dữ liệu", "Vui lòng nhập Tài xế, Xe và Điểm bắt đầu")
            return

    except Exception as e:
        messagebox.showerror("Lỗi định dạng", f"Dữ liệu nhập không hợp lệ: {e}")
        return

    conn = connect_db()
    if conn is None:
        return

    try:
        cur = conn.cursor()
        
        sql = """
        INSERT INTO ChuyenDi (
            MaNhanVien, BienSoXe, DiemBatDau, DiemKetThuc, 
            ThoiGianBatDau, ThoiGianKetThuc, TrangThai
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        cur.execute(sql, (manv, bienso, diembd, diemkt, tg_batdau, tg_ketthuc, int(trangthai)))
        
        conn.commit()
        messagebox.showinfo("Thành công", "Đã thêm chuyến đi mới thành công")
        
        clear_input()
        load_data()
        
    except pyodbc.Error as e:
        conn.rollback() 
        messagebox.showerror("Lỗi SQL", f"Không thể thêm chuyến đi:\n{str(e)}")
    except Exception as e:
        conn.rollback()
        messagebox.showerror("Lỗi không xác định", f"Lỗi: {str(e)}")
    finally:
        if conn:
            conn.close()

def chon_chuyendi_de_sua():
    """Lấy thông tin chuyến đi được chọn và điền vào form."""
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Chưa chọn", "Hãy chọn một chuyến đi để sửa")
        return

    selected_item = tree.item(selected[0])
    machuyendi = selected_item['values'][0]
    
    conn = connect_db()
    if conn is None:
        return

    try:
        cur = conn.cursor()
        sql = """
        SELECT cd.*, nv.HoVaTen 
        FROM ChuyenDi cd
        LEFT JOIN NhanVien nv ON cd.MaNhanVien = nv.MaNhanVien
        WHERE cd.MaChuyenDi = ?
        """
        cur.execute(sql, (machuyendi,))
        data = cur.fetchone()
        
        if not data:
            messagebox.showerror("Lỗi", "Không tìm thấy dữ liệu chuyến đi.")
            return

        clear_input()
        
        # Điền dữ liệu vào form
        entry_machuyendi.config(state='normal')
        entry_machuyendi.insert(0, data.MaChuyenDi)
        entry_machuyendi.config(state='disabled')
        
        # Tìm và set combobox tài xế
        cbb_taixe_val = f"{data.MaNhanVien} - {data.HoVaTen}"
        cbb_taixe.set(cbb_taixe_val)
        
        cbb_xe.set(data.BienSoXe or "")
        entry_diembd.insert(0, data.DiemBatDau or "")
        entry_diemkt.insert(0, data.DiemKetThuc or "")
        
        # Tách ngày và giờ (Bắt đầu)
        if data.ThoiGianBatDau:
            date_bd.set_date(data.ThoiGianBatDau.strftime("%Y-%m-%d"))
            entry_giobd.insert(0, data.ThoiGianBatDau.strftime("%H:%M"))
            
        # Tách ngày và giờ (Kết thúc)
        if data.ThoiGianKetThuc:
            date_kt.set_date(data.ThoiGianKetThuc.strftime("%Y-%m-%d"))
            entry_giokt.insert(0, data.ThoiGianKetThuc.strftime("%H:%M"))

        # Set trạng thái
        trangthai_map = {0: "0 = Đã gán", 1: "1 = Đang thực hiện", 2: "2 = Hoàn thành", 3: "3 = Hủy"}
        cbb_trangthai.set(trangthai_map.get(data.TrangThai, "0 = Đã gán"))

    except pyodbc.Error as e:
        messagebox.showerror("Lỗi SQL", f"Không thể lấy dữ liệu:\n{str(e)}")
    except Exception as e:
        messagebox.showerror("Lỗi không xác định", f"Lỗi: {str(e)}")
    finally:
        if conn:
            conn.close()

def luu_chuyendi_da_sua():
    """Lưu thay đổi (UPDATE) sau khi sửa."""
    machuyendi = entry_machuyendi.get()
    if not machuyendi:
        messagebox.showwarning("Thiếu dữ liệu", "Không có Mã chuyến đi để cập nhật")
        return

    try:
        # Lấy Mã NV và Biển số từ combobox
        manv = cbb_taixe_var.get().split(' - ')[0]
        bienso = cbb_xe_var.get()
        
        diembd = entry_diembd.get()
        diemkt = entry_diemkt.get()
        
        # Ghép ngày + giờ
        ngay_bd_str = date_bd.get()
        gio_bd_str = entry_giobd.get() or "00:00"
        tg_batdau = f"{ngay_bd_str} {gio_bd_str}:00"
        
        # Xử lý thời gian kết thúc (có thể NULL)
        ngay_kt_str = date_kt.get()
        gio_kt_str = entry_giokt.get()
        tg_ketthuc = None
        if gio_kt_str: # Chỉ lưu nếu nhập giờ
            tg_ketthuc = f"{ngay_kt_str} {gio_kt_str}:00"
        
        trangthai = cbb_trangthai_var.get().split('=')[0].strip()

    except Exception as e:
        messagebox.showerror("Lỗi định dạng", f"Dữ liệu nhập không hợp lệ: {e}")
        return

    conn = connect_db()
    if conn is None:
        return
        
    try:
        cur = conn.cursor()
        
        sql = """
        UPDATE ChuyenDi SET 
            MaNhanVien = ?, BienSoXe = ?, DiemBatDau = ?, DiemKetThuc = ?,
            ThoiGianBatDau = ?, ThoiGianKetThuc = ?, TrangThai = ?
        WHERE MaChuyenDi = ?
        """
        cur.execute(sql, (
            manv, bienso, diembd, diemkt, 
            tg_batdau, tg_ketthuc, int(trangthai),
            machuyendi
        ))
        
        conn.commit()
        messagebox.showinfo("Thành công", "Đã cập nhật thông tin chuyến đi")
        
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

def xoa_chuyendi():
    """Xóa chuyến đi được chọn."""
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Chưa chọn", "Hãy chọn một chuyến đi để xóa")
        return

    selected_item = tree.item(selected[0])
    machuyendi = selected_item['values'][0]

    if not messagebox.askyesno("Xác nhận", f"Bạn có chắc chắn muốn xóa Chuyến đi Mã: {machuyendi}?"):
        return

    conn = connect_db()
    if conn is None:
        return
        
    try:
        cur = conn.cursor()
        
        # Bảng ChuyenDi không phải là bảng cha của bảng nào
        # nên có thể xóa an toàn (trừ khi có trigger)
        cur.execute("DELETE FROM ChuyenDi WHERE MaChuyenDi=?", (machuyendi,))
        
        conn.commit()
        
        messagebox.showinfo("Thành công", "Đã xóa chuyến đi thành công")
        clear_input()
        load_data()
        
    except pyodbc.IntegrityError:
        conn.rollback()
        messagebox.showerror("Lỗi Ràng buộc", "Không thể xóa chuyến đi này (Lỗi không xác định).")
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
# PHẦN 4: THIẾT KẾ GIAO DIỆN (CHO CHUYẾN ĐI)
# ================================================================

root = tk.Tk()
root.title("Quản lý Chuyến đi (Database QL_VanTai)")

def center_window(w, h):
    ws = root.winfo_screenwidth()
    hs = root.winfo_screenheight()
    x = (ws/2) - (w/2)
    y = (hs/2) - (h/2)
    root.geometry('%dx%d+%d+%d' % (w, h, x, y))

center_window(950, 700) # Cửa sổ lớn hơn
root.resizable(False, False)

lbl_title = tk.Label(root, text="QUẢN LÝ CHUYẾN ĐI", font=("Arial", 18, "bold"))
lbl_title.pack(pady=10)

# Frame nhập thông tin
frame_info = tk.Frame(root)
frame_info.pack(pady=5, padx=10, fill="x")

# --- Hàng 1 ---
tk.Label(frame_info, text="Mã chuyến đi:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
entry_machuyendi = tk.Entry(frame_info, width=25, state='disabled')
entry_machuyendi.grid(row=0, column=1, padx=5, pady=5, sticky="w")

tk.Label(frame_info, text="Trạng thái:").grid(row=0, column=2, padx=15, pady=5, sticky="w")
trangthai_options = [
    "0 = Đã gán",
    "1 = Đang thực hiện",
    "2 = Hoàn thành",
    "3 = Hủy"
]
cbb_trangthai_var = tk.StringVar()
cbb_trangthai = ttk.Combobox(frame_info, textvariable=cbb_trangthai_var, values=trangthai_options, width=30, state='readonly')
cbb_trangthai.grid(row=0, column=3, padx=5, pady=5, sticky="w")
cbb_trangthai.set("0 = Đã gán")

# --- Hàng 2 ---
tk.Label(frame_info, text="Tài xế:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
cbb_taixe_var = tk.StringVar()
cbb_taixe = ttk.Combobox(frame_info, textvariable=cbb_taixe_var, width=22, state='readonly')
cbb_taixe.grid(row=1, column=1, padx=5, pady=5, sticky="w")
# Tải dữ liệu vào combobox
cbb_taixe['values'] = load_taixe_combobox()

tk.Label(frame_info, text="Xe:").grid(row=1, column=2, padx=15, pady=5, sticky="w")
cbb_xe_var = tk.StringVar()
cbb_xe = ttk.Combobox(frame_info, textvariable=cbb_xe_var, width=30, state='readonly')
cbb_xe.grid(row=1, column=3, padx=5, pady=5, sticky="w")
# Tải dữ liệu vào combobox
cbb_xe['values'] = load_xe_combobox()


# --- Hàng 3 ---
tk.Label(frame_info, text="Điểm bắt đầu:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
entry_diembd = tk.Entry(frame_info, width=25)
entry_diembd.grid(row=2, column=1, padx=5, pady=5, sticky="w")

tk.Label(frame_info, text="Điểm kết thúc:").grid(row=2, column=2, padx=15, pady=5, sticky="w")
entry_diemkt = tk.Entry(frame_info, width=32)
entry_diemkt.grid(row=2, column=3, padx=5, pady=5, sticky="w")


# --- Hàng 4 (Thời gian) ---
# Frame con cho thời gian
frame_time = tk.Frame(frame_info)
frame_time.grid(row=3, column=0, columnspan=4, pady=10)

tk.Label(frame_time, text="Thời gian BĐ:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
date_bd = DateEntry(frame_time, width=12, background='darkblue', foreground='white', date_pattern='yyyy-MM-dd')
date_bd.grid(row=0, column=1, padx=5, pady=5, sticky="w")

tk.Label(frame_time, text="Giờ BĐ (HH:MM):").grid(row=0, column=2, padx=5, pady=5, sticky="w")
entry_giobd = tk.Entry(frame_time, width=8)
entry_giobd.grid(row=0, column=3, padx=5, pady=5, sticky="w")

tk.Label(frame_time, text="Thời gian KT:").grid(row=0, column=4, padx=15, pady=5, sticky="w")
date_kt = DateEntry(frame_time, width=12, background='darkblue', foreground='white', date_pattern='yyyy-MM-dd')
date_kt.grid(row=0, column=5, padx=5, pady=5, sticky="w")

tk.Label(frame_time, text="Giờ KT (HH:MM):").grid(row=0, column=6, padx=5, pady=5, sticky="w")
entry_giokt = tk.Entry(frame_time, width=8)
entry_giokt.grid(row=0, column=7, padx=5, pady=5, sticky="w")


# Cấu hình grid co giãn
frame_info.columnconfigure(1, weight=1)
frame_info.columnconfigure(3, weight=1)

# ===== Frame nút =====
frame_btn = tk.Frame(root)
frame_btn.pack(pady=10)

btn_them = tk.Button(frame_btn, text="Thêm", width=8, command=them_chuyendi)
btn_them.grid(row=0, column=0, padx=5)

btn_luu = tk.Button(frame_btn, text="Lưu", width=8, command=luu_chuyendi_da_sua)
btn_luu.grid(row=0, column=1, padx=5)

btn_sua = tk.Button(frame_btn, text="Sửa", width=8, command=chon_chuyendi_de_sua)
btn_sua.grid(row=0, column=2, padx=5)

btn_huy = tk.Button(frame_btn, text="Hủy", width=8, command=clear_input)
btn_huy.grid(row=0, column=3, padx=5)

btn_xoa = tk.Button(frame_btn, text="Xóa", width=8, command=xoa_chuyendi)
btn_xoa.grid(row=0, column=4, padx=5)

btn_thoat = tk.Button(frame_btn, text="Thoát", width=8, command=root.quit)
btn_thoat.grid(row=0, column=5, padx=5)


# ===== Bảng danh sách chuyến đi =====
lbl_ds = tk.Label(root, text="Danh sách chuyến đi (Sắp xếp mới nhất)", font=("Arial", 10, "bold"))
lbl_ds.pack(pady=5, padx=10, anchor="w")

frame_tree = tk.Frame(root)
frame_tree.pack(pady=10, padx=10, fill="both", expand=True)

scrollbar_y = tk.Scrollbar(frame_tree, orient=tk.VERTICAL)
scrollbar_x = tk.Scrollbar(frame_tree, orient=tk.HORIZONTAL)

columns = ("ma_cd", "ten_tx", "bienso", "tg_bd", "trangthai")
tree = ttk.Treeview(frame_tree, columns=columns, show="headings", height=10,
                    yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)

scrollbar_y.config(command=tree.yview)
scrollbar_x.config(command=tree.xview)

scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)

# Định nghĩa các cột
tree.heading("ma_cd", text="Mã CĐ")
tree.column("ma_cd", width=60, anchor="center")

tree.heading("ten_tx", text="Tên Tài xế")
tree.column("ten_tx", width=150)

tree.heading("bienso", text="Biển số xe")
tree.column("bienso", width=100)

tree.heading("tg_bd", text="Thời gian bắt đầu")
tree.column("tg_bd", width=150)

tree.heading("trangthai", text="Trạng thái")
tree.column("trangthai", width=120, anchor="center")

tree.pack(fill="both", expand=True)

# ================================================================
# PHẦN 5: CHẠY ỨNG DỤNG
# ================================================================
clear_input() # Đặt giờ mặc định
load_data() # Tải dữ liệu ban đầu
root.mainloop()