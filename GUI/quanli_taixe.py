import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
import pyodbc 

# ================================================================
# BỘ MÀU "LIGHT MODE" MỚI (Giữ nguyên)
# ================================================================
theme_colors = {
    "bg_main": "#F0F0F0",      # Nền chính (xám rất nhạt)
    "bg_entry": "#FFFFFF",     # Nền cho Entry, Treeview (trắng)
    "text": "#000000",         # Màu chữ chính (đen)
    "text_disabled": "#A0A0A0", # Màu chữ khi bị mờ
    "accent": "#0078D4",       # Màu nhấn (xanh dương)
    "accent_text": "#FFFFFF",   # Màu chữ trên nền màu nhấn (trắng)
    "accent_active": "#005A9E",  # Màu nhấn khi click
    "disabled_bg": "#E0E0E0"   # Nền khi bị mờ
}

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
# PHẦN 2: CÁC HÀM CRUD (NÂNG CẤP THEO MẪU)
# ================================================================

def set_form_state(is_enabled):
    """Bật (enable) hoặc Tắt (disable) toàn bộ các trường nhập liệu."""
    if is_enabled:
        # Chế độ Bật
        entry_hoten.config(state='normal')
        entry_sdt.config(state='normal')
        entry_diachi.config(state='normal')
        entry_banglai.config(state='normal')
        date_banglai.config(state='normal')
        cbb_trangthai_nv.config(state='readonly')
        cbb_trangthai_lx.config(state='readonly')
    else:
        # Chế độ Tắt (Làm mờ)
        entry_manv.config(state='disabled')
        entry_hoten.config(state='disabled')
        entry_sdt.config(state='disabled')
        entry_diachi.config(state='disabled')
        entry_banglai.config(state='disabled')
        date_banglai.config(state='disabled')
        cbb_trangthai_nv.config(state='disabled')
        cbb_trangthai_lx.config(state='disabled')

def clear_input():
    """(NÚT THÊM) Xóa trắng và Mở khóa các trường nhập liệu (Chế độ Thêm mới)."""
    set_form_state(is_enabled=True)
    entry_manv.config(state='normal') 
    
    entry_manv.delete(0, tk.END)
    entry_hoten.delete(0, tk.END)
    entry_sdt.delete(0, tk.END)
    entry_diachi.delete(0, tk.END)
    entry_banglai.delete(0, tk.END)
    
    # Set giá trị mặc định (đã bỏ tiền tố)
    date_banglai.set_date("2025-01-01")
    cbb_trangthai_nv.set("Đang làm việc")
    cbb_trangthai_lx.set("Rảnh")
    
    entry_manv.focus()
    if tree.selection():
        tree.selection_remove(tree.selection()[0])

def load_data():
    """Tải TOÀN BỘ dữ liệu tài xế (JOIN) VÀ LÀM MỜ FORM."""
    for i in tree.get_children():
        tree.delete(i)
        
    conn = connect_db()
    if conn is None:
        set_form_state(is_enabled=False) 
        return
        
    try:
        cur = conn.cursor()
        sql = """
        SELECT 
            nv.MaNhanVien, nv.HoVaTen, nv.SoDienThoai, 
            tx.HangBangLai, nv.TrangThai, tx.TrangThaiTaiXe
        FROM NhanVien AS nv
        JOIN TaiXe AS tx ON nv.MaNhanVien = tx.MaNhanVien
        """
        cur.execute(sql)
        rows = cur.fetchall()
        
        for row in rows:
            # Chuyển đổi TrangThai (NhanVien)
            trang_thai_nv_text = "Đang làm việc" if row[4] == 1 else "Nghỉ"
            # Chuyển đổi TrangThaiTaiXe (TaiXe) (Giả sử 1=Rảnh, 2=Đang lái)
            trang_thai_lx_text = "Rảnh" if row[5] == 1 else "Đang lái"
            
            tree.insert("", tk.END, values=(
                row[0], # MaNhanVien
                row[1], # HoVaTen
                row[2], # SoDienThoai
                row[3], # HangBangLai
                trang_thai_nv_text, # TrangThai (NhanVien)
                trang_thai_lx_text  # TrangThaiTaiXe
            ))
        
        children = tree.get_children()
        if children:
            first_item = children[0]
            tree.selection_set(first_item) 
            tree.focus(first_item)         
            tree.event_generate("<<TreeviewSelect>>") 
        else:
            # Nếu không có data, xóa trắng form
            entry_manv.config(state='normal')
            set_form_state(is_enabled=True)
            # Gọi clear_input bản rút gọn
            entry_manv.delete(0, tk.END)
            entry_hoten.delete(0, tk.END)
            entry_sdt.delete(0, tk.END)
            entry_diachi.delete(0, tk.END)
            entry_banglai.delete(0, tk.END)
            date_banglai.set_date("2025-01-01")
            cbb_trangthai_nv.set("Đang làm việc")
            cbb_trangthai_lx.set("Rảnh")
            
    except pyodbc.Error as e:
        messagebox.showerror("Lỗi tải dữ liệu", f"Lỗi SQL: {str(e)}")
    except Exception as e:
        messagebox.showerror("Lỗi không xác định", f"Lỗi: {str(e)}")
    finally:
        if conn:
            conn.close()
        # LUÔN LUÔN LÀM MỜ FORM SAU KHI TẢI DỮ LIỆU
        set_form_state(is_enabled=False)

def them_taixe():
    """(LOGIC THÊM) Thêm một tài xế mới (vào cả 2 bảng NhanVien và TaiXe)."""
    manv = entry_manv.get()
    hoten = entry_hoten.get()
    sdt = entry_sdt.get()
    diachi = entry_diachi.get()
    banglai = entry_banglai.get()
    ngay_bl = date_banglai.get_date().strftime('%Y-%m-%d') # Lấy đúng định dạng YYYY-MM-DD
    
    # Chuyển text từ Combobox về số
    trangthai_nv_text = cbb_trangthai_nv_var.get()
    trangthai_nv_value = 1 if trangthai_nv_text == "Đang làm việc" else 0
    
    trangthai_lx_text = cbb_trangthai_lx_var.get()
    trangthai_lx_value = 1 if trangthai_lx_text == "Rảnh" else 2 # 1=Rảnh, 2=Đang lái

    if not manv or not hoten or not banglai:
        messagebox.showwarning("Thiếu dữ liệu", "Vui lòng nhập Mã NV, Họ Tên và Hạng Bằng Lái")
        return False

    conn = connect_db()
    if conn is None: return False

    try:
        cur = conn.cursor()
        
        # Thao tác 1: INSERT vào NhanVien (bảng cha)
        sql_nhanvien = """
        INSERT INTO NhanVien (MaNhanVien, HoVaTen, SoDienThoai, DiaChi, TrangThai) 
        VALUES (?, ?, ?, ?, ?)
        """
        cur.execute(sql_nhanvien, (manv, hoten, sdt, diachi, trangthai_nv_value))
        
        # Thao tác 2: INSERT vào TaiXe (bảng con)
        sql_taixe = """
        INSERT INTO TaiXe (MaNhanVien, HangBangLai, NgayHetHanBangLai, TrangThaiTaiXe) 
        VALUES (?, ?, ?, ?)
        """
        cur.execute(sql_taixe, (manv, banglai, ngay_bl, trangthai_lx_value))
        
        conn.commit()
        messagebox.showinfo("Thành công", "Đã thêm tài xế mới thành công")
        return True
        
    except pyodbc.IntegrityError:
        conn.rollback()
        messagebox.showerror("Lỗi Trùng lặp", f"Mã nhân viên '{manv}' đã tồn tại.")
        return False
    except pyodbc.Error as e:
        conn.rollback() 
        messagebox.showerror("Lỗi SQL", f"Không thể thêm tài xế:\n{str(e)}")
        return False
    except Exception as e:
        conn.rollback()
        messagebox.showerror("Lỗi không xác định", f"Lỗi: {str(e)}")
        return False
    finally:
        if conn: conn.close()

def on_item_select(event=None):
    """(SỰ KIỆN CLICK) Khi click vào Treeview, đổ dữ liệu đầy đủ lên form (ở trạng thái mờ)."""
    selected = tree.selection()
    if not selected: return 

    selected_item = tree.item(selected[0])
    manv = selected_item['values'][0]
    
    conn = connect_db()
    if conn is None: return

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

        # Tạm thời MỞ KHÓA form để đổ dữ liệu
        set_form_state(is_enabled=True)
        entry_manv.config(state='normal')
        
        # Xóa và Đổ dữ liệu
        entry_manv.delete(0, tk.END)
        entry_hoten.delete(0, tk.END)
        entry_sdt.delete(0, tk.END)
        entry_diachi.delete(0, tk.END)
        entry_banglai.delete(0, tk.END)
        
        # Bảng NhanVien
        entry_manv.insert(0, data.MaNhanVien)
        entry_hoten.insert(0, data.HoVaTen or "")
        entry_sdt.insert(0, data.SoDienThoai or "")
        entry_diachi.insert(0, data.DiaChi or "")
        cbb_trangthai_nv.set("Đang làm việc" if data.TrangThai == 1 else "Nghỉ")

        # Bảng TaiXe
        entry_banglai.insert(0, data.HangBangLai or "")
        if data.NgayHetHanBangLai:
            date_banglai.set_date(data.NgayHetHanBangLai)
        else:
            date_banglai.set_date("2025-01-01") # Hoặc một ngày mặc định
        
        cbb_trangthai_lx.set("Rảnh" if data.TrangThaiTaiXe == 1 else "Đang lái")

    except pyodbc.Error as e:
        messagebox.showerror("Lỗi SQL", f"Không thể lấy dữ liệu tài xế:\n{str(e)}")
    except Exception as e:
        messagebox.showerror("Lỗi không xác định", f"Lỗi: {str(e)}")
    finally:
        if conn: conn.close()
        # KHÓA LẠI FORM sau khi đổ dữ liệu
        set_form_state(is_enabled=False)

def chon_taixe_de_sua(event=None): 
    """(NÚT SỬA) Kích hoạt chế độ sửa, Mở khóa form (trừ MaNV)."""
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Chưa chọn", "Hãy chọn một tài xế trong danh sách trước khi nhấn 'Sửa'")
        return

    if not entry_manv.get():
         messagebox.showwarning("Lỗi", "Không tìm thấy mã nhân viên. Vui lòng chọn lại.")
         return

    set_form_state(is_enabled=True)
    entry_manv.config(state='disabled') 
    entry_hoten.focus() 

def luu_taixe_da_sua():
    """(LOGIC SỬA) Lưu thay đổi (UPDATE) sau khi sửa (vào cả 2 bảng)."""
    manv = entry_manv.get()
    if not manv:
        messagebox.showwarning("Thiếu dữ liệu", "Không có Mã Nhân Viên để cập nhật")
        return False

    # Lấy dữ liệu từ form
    hoten = entry_hoten.get()
    sdt = entry_sdt.get()
    diachi = entry_diachi.get()
    banglai = entry_banglai.get()
    ngay_bl = date_banglai.get_date().strftime('%Y-%m-%d')
    
    # Chuyển text từ Combobox về số
    trangthai_nv_text = cbb_trangthai_nv_var.get()
    trangthai_nv_value = 1 if trangthai_nv_text == "Đang làm việc" else 0
    
    trangthai_lx_text = cbb_trangthai_lx_var.get()
    trangthai_lx_value = 1 if trangthai_lx_text == "Rảnh" else 2 # 1=Rảnh, 2=Đang lái

    if not hoten or not banglai:
        messagebox.showwarning("Thiếu dữ liệu", "Họ Tên và Hạng Bằng Lái không được rỗng")
        return False

    conn = connect_db()
    if conn is None: return False
        
    try:
        cur = conn.cursor()
        
        # Thao tác 1: UPDATE NhanVien
        sql_nhanvien = """
        UPDATE NhanVien SET 
            HoVaTen = ?, SoDienThoai = ?, DiaChi = ?, TrangThai = ?
        WHERE MaNhanVien = ?
        """
        cur.execute(sql_nhanvien, (hoten, sdt, diachi, trangthai_nv_value, manv))
        
        # Thao tác 2: UPDATE TaiXe
        sql_taixe = """
        UPDATE TaiXe SET 
            HangBangLai = ?, NgayHetHanBangLai = ?, TrangThaiTaiXe = ?
        WHERE MaNhanVien = ?
        """
        cur.execute(sql_taixe, (banglai, ngay_bl, trangthai_lx_value, manv))
        
        conn.commit()
        messagebox.showinfo("Thành công", "Đã cập nhật thông tin tài xế")
        return True
        
    except pyodbc.Error as e:
        conn.rollback()
        messagebox.showerror("Lỗi SQL", f"Không thể cập nhật tài xế:\n{str(e)}")
        return False
    except Exception as e:
        conn.rollback()
        messagebox.showerror("Lỗi không xác định", f"Lỗi: {str(e)}")
        return False
    finally:
        if conn: conn.close()

def save_data():
    """Lưu dữ liệu, tự động kiểm tra xem nên Thêm mới (INSERT) hay Cập nhật (UPDATE)."""
    if entry_manv.cget('state') == 'disabled':
        # Chế độ Sửa (Mã NV bị khóa)
        success = luu_taixe_da_sua()
    else:
        # Chế độ Thêm (Mã NV đang mở)
        success = them_taixe()
    
    if success:
        load_data() # Tải lại dữ liệu và làm mờ form

def xoa_taixe_vinhvien():
    """(NGUY HIỂM) Xóa vĩnh viễn tài xế và MỌI DỮ LIỆU LIÊN QUAN."""
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Chưa chọn", "Hãy chọn một tài xế trong danh sách để xóa")
        return
        
    manv = entry_manv.get() # Lấy manv từ ô entry (đã được điền)

    if not manv:
        messagebox.showwarning("Lỗi", "Không tìm thấy mã nhân viên. Vui lòng chọn lại.")
        return

    msg_xacnhan = (
        f"BẠN CÓ CHẮC CHẮN MUỐN XÓA VĨNH VIỄN TÀI XẾ '{manv}'?\n\n"
        "CẢNH BÁO: Thao tác này KHÔNG THỂ hoàn tác.\n"
        "Tất cả Lịch sử chuyến đi, Lịch sử nhiên liệu, Tài khoản, và thông tin Tài xế/Nhân viên sẽ bị XÓA SẠCH."
    )
    if not messagebox.askyesno("XÁC NHẬN XÓA VĨNH VIỄN", msg_xacnhan):
        return

    conn = connect_db()
    if conn is None: return
        
    try:
        cur = conn.cursor()
        
        # --- BẮT ĐẦU XÓA TỪ BẢNG CON ---
        cur.execute("DELETE FROM NhatKyNhienLieu WHERE MaNhanVien=?", (manv,))
        cur.execute("DELETE FROM ChuyenDi WHERE MaNhanVien=?", (manv,))
        cur.execute("DELETE FROM TaiKhoan WHERE MaNhanVien=?", (manv,))
        cur.execute("DELETE FROM TaiXe WHERE MaNhanVien=?", (manv,))
        
        # --- CẬP NHẬT BẢNG KHÁC ---
        cur.execute("UPDATE Xe SET MaNhanVienHienTai = NULL WHERE MaNhanVienHienTai = ?", (manv,))
        
        # --- XÓA BẢNG CHA ---
        cur.execute("DELETE FROM NhanVien WHERE MaNhanVien=?", (manv,))
        
        conn.commit()
        
        messagebox.showinfo("Thành công", f"Đã xóa vĩnh viễn tài xế '{manv}' và tất cả dữ liệu liên quan.")
        load_data()
        
    except pyodbc.Error as e:
        conn.rollback()
        messagebox.showerror("Lỗi SQL", f"Không thể xóa tài xế:\n{str(e)}")
    except Exception as e:
        conn.rollback()
        messagebox.showerror("Lỗi không xác định", f"Lỗi: {str(e)}")
    finally:
        if conn: conn.close()

# ================================================================
# PHẦN 3: THIẾT KẾ GIAO DIỆN (Bản Light Mode)
# ================================================================

root = tk.Tk()
root.title("Quản lý Tài xế (Database QL_VanTai)")
root.config(bg=theme_colors["bg_main"]) 

def center_window(w, h):
    ws = root.winfo_screenwidth()
    hs = root.winfo_screenheight()
    x = (ws/2) - (w/2)
    y = (hs/2) - (h/2)
    root.geometry('%dx%d+%d+%d' % (w, h, x, y))

center_window(900, 650) 
root.resizable(False, False)

# === CÀI ĐẶT STYLE (QUAN TRỌNG) ===
style = ttk.Style(root)
style.theme_use("clam") 

# --- Cấu hình chung ---
style.configure(".", 
    background=theme_colors["bg_main"],
    foreground=theme_colors["text"],
    fieldbackground=theme_colors["bg_entry"],
    bordercolor="#ACACAC", 
    lightcolor=theme_colors["bg_main"],
    darkcolor=theme_colors["bg_main"]
)
# --- Frame ---
style.configure("TFrame", 
    background=theme_colors["bg_main"]
)
# --- Label ---
style.configure("TLabel", 
    background=theme_colors["bg_main"],
    foreground=theme_colors["text"],
    font=("Segoe UI", 10)
)
style.configure("Title.TLabel", 
    background=theme_colors["bg_main"],
    foreground=theme_colors["accent"], 
    font=("Segoe UI", 20, "bold")
)
style.configure("Header.TLabel", 
    background=theme_colors["bg_main"],
    foreground=theme_colors["text"], 
    font=("Segoe UI", 11, "bold")
)
# --- Entry và Combobox ---
style.configure("TEntry",
    font=("Segoe UI", 10),
    fieldbackground=theme_colors["bg_entry"],
    foreground=theme_colors["text"],
    insertcolor=theme_colors["text"] 
)
style.map("TEntry",
    fieldbackground=[('disabled', theme_colors["disabled_bg"])],
    foreground=[('disabled', theme_colors["text_disabled"])]
)
style.configure("TCombobox",
    font=("Segoe UI", 10),
    fieldbackground=theme_colors["bg_entry"],
    background=theme_colors["bg_entry"],
    foreground=theme_colors["text"]
)
root.option_add("*TCombobox*Listbox*background", theme_colors["bg_entry"])
root.option_add("*TCombobox*Listbox*foreground", theme_colors["text"])
root.option_add("*TCombobox*Listbox*selectBackground", theme_colors["accent"])
root.option_add("*TCombobox*Listbox*selectForeground", theme_colors["accent_text"])
style.map("TCombobox",
    fieldbackground=[('disabled', theme_colors["disabled_bg"])],
    foreground=[('disabled', theme_colors["text_disabled"])]
)
# --- Button ---
style.configure("TButton",
    background=theme_colors["accent"],
    foreground=theme_colors["accent_text"],
    font=("Segoe UI", 10, "bold"),
    padding=5,
    relief="flat",
    bordercolor=theme_colors["accent"]
)
style.map("TButton",
    background=[('active', theme_colors["accent_active"])] 
)
# --- Treeview (Bảng) ---
style.configure("Treeview",
    background=theme_colors["bg_entry"],
    foreground=theme_colors["text"],
    fieldbackground=theme_colors["bg_entry"],
    rowheight=25, 
    font=("Segoe UI", 10)
)
style.map("Treeview",
    background=[('selected', theme_colors["accent"])], 
    foreground=[('selected', theme_colors["accent_text"])]
)
style.configure("Treeview.Heading",
    background=theme_colors["accent"],
    foreground=theme_colors["accent_text"],
    font=("Segoe UI", 10, "bold"),
    relief="flat"
)
style.map("Treeview.Heading",
    background=[('active', theme_colors["accent_active"])]
)
# --- Scrollbar ---
style.configure("Vertical.TScrollbar", 
    background=theme_colors["bg_entry"],
    troughcolor=theme_colors["bg_main"],
    arrowcolor=theme_colors["text"]
)
style.map("Vertical.TScrollbar",
    background=[('active', "#C0C0C0")]
)
style.configure("Horizontal.TScrollbar", 
    background=theme_colors["bg_entry"],
    troughcolor=theme_colors["bg_main"],
    arrowcolor=theme_colors["text"]
)
style.map("Horizontal.TScrollbar",
    background=[('active', "#C0C0C0")]
)
# ==================================


lbl_title = ttk.Label(root, text="QUẢN LÝ TÀI XẾ", style="Title.TLabel")
lbl_title.pack(pady=15) 

frame_info = ttk.Frame(root, style="TFrame")
frame_info.pack(pady=5, padx=20, fill="x")

# --- Cột 1 ---
ttk.Label(frame_info, text="Mã nhân viên:").grid(row=0, column=0, padx=5, pady=8, sticky="w")
entry_manv = ttk.Entry(frame_info, width=30)
entry_manv.grid(row=0, column=1, padx=5, pady=8, sticky="w")

ttk.Label(frame_info, text="Họ và tên:").grid(row=1, column=0, padx=5, pady=8, sticky="w")
entry_hoten = ttk.Entry(frame_info, width=30)
entry_hoten.grid(row=1, column=1, padx=5, pady=8, sticky="w")

ttk.Label(frame_info, text="Số điện thoại:").grid(row=2, column=0, padx=5, pady=8, sticky="w")
entry_sdt = ttk.Entry(frame_info, width=30)
entry_sdt.grid(row=2, column=1, padx=5, pady=8, sticky="w")

ttk.Label(frame_info, text="Địa chỉ:").grid(row=3, column=0, padx=5, pady=8, sticky="w")
entry_diachi = ttk.Entry(frame_info, width=30)
entry_diachi.grid(row=3, column=1, padx=5, pady=8, sticky="w")

# --- Cột 2 ---
ttk.Label(frame_info, text="Hạng bằng lái:").grid(row=0, column=2, padx=15, pady=8, sticky="w")
entry_banglai = ttk.Entry(frame_info, width=30)
entry_banglai.grid(row=0, column=3, padx=5, pady=8, sticky="w")

ttk.Label(frame_info, text="Ngày hết hạn BL:").grid(row=1, column=2, padx=15, pady=8, sticky="w")
# Style DateEntry
date_banglai = DateEntry(frame_info, width=28, date_pattern='yyyy-MM-dd',
    background=theme_colors["bg_entry"], 
    foreground=theme_colors["text"],
    disabledbackground=theme_colors["disabled_bg"],
    disabledforeground=theme_colors["text_disabled"],
    bordercolor=theme_colors["bg_entry"],
    headersbackground=theme_colors["accent"],
    headersforeground=theme_colors["accent_text"],
    selectbackground=theme_colors["accent"],
    selectforeground=theme_colors["accent_text"]
)
date_banglai.grid(row=1, column=3, padx=5, pady=8, sticky="w")

ttk.Label(frame_info, text="Trạng thái NV:").grid(row=2, column=2, padx=15, pady=8, sticky="w")
trangthai_nv_options = ["Nghỉ", "Đang làm việc"]
cbb_trangthai_nv_var = tk.StringVar()
cbb_trangthai_nv = ttk.Combobox(frame_info, textvariable=cbb_trangthai_nv_var, values=trangthai_nv_options, width=28, state='readonly')
cbb_trangthai_nv.grid(row=2, column=3, padx=5, pady=8, sticky="w")
cbb_trangthai_nv.set("Đang làm việc") 

ttk.Label(frame_info, text="Trạng thái Lái:").grid(row=3, column=2, padx=15, pady=8, sticky="w")
trangthai_lx_options = ["Rảnh", "Đang lái"]
cbb_trangthai_lx_var = tk.StringVar()
cbb_trangthai_lx = ttk.Combobox(frame_info, textvariable=cbb_trangthai_lx_var, values=trangthai_lx_options, width=28, state='readonly')
cbb_trangthai_lx.grid(row=3, column=3, padx=5, pady=8, sticky="w")
cbb_trangthai_lx.set("Rảnh") 

frame_info.columnconfigure(1, weight=1)
frame_info.columnconfigure(3, weight=1)

# ===== Frame nút (Đã cập nhật command) =====
frame_btn = ttk.Frame(root, style="TFrame")
frame_btn.pack(pady=10)

btn_them = ttk.Button(frame_btn, text="Thêm", width=8, command=clear_input) 
btn_them.grid(row=0, column=0, padx=10)
btn_luu = ttk.Button(frame_btn, text="Lưu", width=8, command=save_data) 
btn_luu.grid(row=0, column=1, padx=10)
btn_sua = ttk.Button(frame_btn, text="Sửa", width=8, command=chon_taixe_de_sua) 
btn_sua.grid(row=0, column=2, padx=10)
btn_huy = ttk.Button(frame_btn, text="Hủy", width=8, command=load_data) 
btn_huy.grid(row=0, column=3, padx=10)
btn_xoa = ttk.Button(frame_btn, text="Xóa", width=8, command=xoa_taixe_vinhvien) 
btn_xoa.grid(row=0, column=4, padx=10)
btn_thoat = ttk.Button(frame_btn, text="Thoát", width=8, command=root.quit)
btn_thoat.grid(row=0, column=5, padx=10)


# ===== Bảng danh sách tài xế =====
lbl_ds = ttk.Label(root, text="Danh sách tài xế", style="Header.TLabel")
lbl_ds.pack(pady=(10, 5), padx=20, anchor="w")

frame_tree = ttk.Frame(root, style="TFrame")
frame_tree.pack(pady=10, padx=20, fill="both", expand=True) 

scrollbar_y = ttk.Scrollbar(frame_tree, orient=tk.VERTICAL, style="Vertical.TScrollbar")
scrollbar_x = ttk.Scrollbar(frame_tree, orient=tk.HORIZONTAL, style="Horizontal.TScrollbar")

columns = ("manv", "hoten", "sdt", "banglai", "trangthai_nv", "trangthai_lx")
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
tree.heading("banglai", text="Hạng Bằng Lái")
tree.column("banglai", width=100, anchor="center")
tree.heading("trangthai_nv", text="Trạng thái NV")
tree.column("trangthai_nv", width=120, anchor="center")
tree.heading("trangthai_lx", text="Trạng thái Lái")
tree.column("trangthai_lx", width=120, anchor="center")

tree.pack(fill="both", expand=True)

# THÊM BINDING (SỰ KIỆN CLICK)
tree.bind("<<TreeviewSelect>>", on_item_select) 

# ================================================================
# PHẦN 4: CHẠY ỨNG DỤNG
# ================================================================
load_data() 
root.mainloop()