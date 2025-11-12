import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
import pyodbc 
from datetime import datetime
import datetime as dt # Dùng cho default date

# ================================================================
# BỘ MÀU "LIGHT MODE" (Giữ nguyên)
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
# PHẦN 2: CÁC HÀM TIỆN ÍCH (Tải Combobox) - Giữ nguyên
# ================================================================
def load_taixe_combobox():
    """Tải danh sách tài xế (MaNhanVien - HoVaTen) vào Combobox."""
    conn = connect_db()
    if conn is None: return []
    
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
        # Format: "NV001 - Nguyễn Văn An"
        return [f"{row[0]} - {row[1]}" for row in rows]
    except Exception as e:
        print(f"Lỗi tải combobox tài xế: {e}")
        return []
    finally:
        if conn: conn.close()

def load_xe_combobox():
    """Tải danh sách xe (BienSoXe) vào Combobox."""
    conn = connect_db()
    if conn is None: return []
    
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
        if conn: conn.close()

# ================================================================
# PHẦN 3: CÁC HÀM CRUD (NÂNG CẤP THEO MẪU)
# ================================================================

def set_form_state(is_enabled):
    """Bật (enable) hoặc Tắt (disable) toàn bộ các trường nhập liệu."""
    # MaChuyenDi luôn disabled
    entry_machuyendi.config(state='disabled')
    
    if is_enabled:
        # Chế độ Bật
        cbb_taixe.config(state='readonly')
        cbb_xe.config(state='readonly')
        entry_diembd.config(state='normal')
        entry_diemkt.config(state='normal')
        date_bd.config(state='normal')
        entry_giobd.config(state='normal')
        date_kt.config(state='normal')
        entry_giokt.config(state='normal')
        cbb_trangthai.config(state='readonly')
    else:
        # Chế độ Tắt (Làm mờ)
        cbb_taixe.config(state='disabled')
        cbb_xe.config(state='disabled')
        entry_diembd.config(state='disabled')
        entry_diemkt.config(state='disabled')
        date_bd.config(state='disabled')
        entry_giobd.config(state='disabled')
        date_kt.config(state='disabled')
        entry_giokt.config(state='disabled')
        cbb_trangthai.config(state='disabled')

def clear_input():
    """(NÚT THÊM) Xóa trắng và Mở khóa các trường nhập liệu (Chế độ Thêm mới)."""
    set_form_state(is_enabled=True)
    
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
    
    cbb_trangthai.set("Đã gán") # Giá trị text mới
    cbb_taixe.focus()
    
    if tree.selection():
        tree.selection_remove(tree.selection()[0])

def load_data():
    """Tải TOÀN BỘ dữ liệu ChuyenDi VÀ LÀM MỜ FORM."""
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
            cd.MaChuyenDi, nv.HoVaTen, cd.BienSoXe, 
            cd.ThoiGianBatDau, cd.TrangThai
        FROM ChuyenDi AS cd
        LEFT JOIN NhanVien AS nv ON cd.MaNhanVien = nv.MaNhanVien
        ORDER BY cd.ThoiGianBatDau DESC
        """
        cur.execute(sql)
        rows = cur.fetchall()
        
        # CẬP NHẬT: Map text mới
        trangthai_map = { 0: "Đã gán", 1: "Đang thực hiện", 2: "Hoàn thành", 3: "Hủy" }
        
        for row in rows:
            ma_cd = row[0]
            ten_tx = row[1] or "N/A"
            bienso = row[2]
            tg_bd = row[3].strftime("%Y-%m-%d %H:%M") if row[3] else "N/A"
            trangthai_text = trangthai_map.get(row[4], "Không rõ")
            
            tree.insert("", tk.END, values=(ma_cd, ten_tx, bienso, tg_bd, trangthai_text))
            
        children = tree.get_children()
        if children:
            first_item = children[0]
            tree.selection_set(first_item) 
            tree.focus(first_item)         
            tree.event_generate("<<TreeviewSelect>>") 
        else:
            # Nếu không có data, xóa trắng form
            set_form_state(is_enabled=True)
            clear_input() # Gọi hàm clear để reset
            
    except pyodbc.Error as e:
        messagebox.showerror("Lỗi tải dữ liệu", f"Lỗi SQL: {str(e)}")
    except Exception as e:
        messagebox.showerror("Lỗi không xác định", f"Lỗi: {str(e)}")
    finally:
        if conn:
            conn.close()
        # LUÔN LUÔN LÀM MỜ FORM SAU KHI TẢI DỮ LIỆU
        set_form_state(is_enabled=False)

def them_chuyendi():
    """(LOGIC THÊM) Thêm một chuyến đi mới."""
    try:
        manv = cbb_taixe_var.get().split(' - ')[0]
        bienso = cbb_xe_var.get()
        diembd = entry_diembd.get()
        diemkt = entry_diemkt.get()
        
        ngay_bd_str = date_bd.get_date().strftime('%Y-%m-%d')
        gio_bd_str = entry_giobd.get() or "00:00"
        tg_batdau = f"{ngay_bd_str} {gio_bd_str}:00"
        
        ngay_kt_str = date_kt.get_date().strftime('%Y-%m-%d')
        gio_kt_str = entry_giokt.get()
        tg_ketthuc = None
        if gio_kt_str: 
            tg_ketthuc = f"{ngay_kt_str} {gio_kt_str}:00"
        
        # CẬP NHẬT: Chuyển text về số
        trangthai_text = cbb_trangthai_var.get()
        trangthai_map = {"Đã gán": 0, "Đang thực hiện": 1, "Hoàn thành": 2, "Hủy": 3}
        trangthai_value = trangthai_map.get(trangthai_text, 0)

        if not manv or not bienso or not diembd:
            messagebox.showwarning("Thiếu dữ liệu", "Vui lòng nhập Tài xế, Xe và Điểm bắt đầu")
            return False

    except Exception as e:
        messagebox.showerror("Lỗi định dạng", f"Dữ liệu nhập không hợp lệ: {e}")
        return False

    conn = connect_db()
    if conn is None: return False

    try:
        cur = conn.cursor()
        sql = """
        INSERT INTO ChuyenDi (
            MaNhanVien, BienSoXe, DiemBatDau, DiemKetThuc, 
            ThoiGianBatDau, ThoiGianKetThuc, TrangThai
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        cur.execute(sql, (manv, bienso, diembd, diemkt, tg_batdau, tg_ketthuc, trangthai_value))
        conn.commit()
        messagebox.showinfo("Thành công", "Đã thêm chuyến đi mới thành công")
        return True
        
    except pyodbc.Error as e:
        conn.rollback() 
        messagebox.showerror("Lỗi SQL", f"Không thể thêm chuyến đi:\n{str(e)}")
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
    machuyendi = selected_item['values'][0]
    
    conn = connect_db()
    if conn is None: return

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

        # Tạm thời MỞ KHÓA form để đổ dữ liệu
        set_form_state(is_enabled=True)
        entry_machuyendi.config(state='normal')
        
        # Xóa và Đổ dữ liệu
        entry_machuyendi.delete(0, tk.END)
        cbb_taixe.set("")
        cbb_xe.set("")
        entry_diembd.delete(0, tk.END)
        entry_diemkt.delete(0, tk.END)
        entry_giobd.delete(0, tk.END)
        entry_giokt.delete(0, tk.END)
        
        # Điền dữ liệu
        entry_machuyendi.insert(0, data.MaChuyenDi)
        
        cbb_taixe_val = f"{data.MaNhanVien} - {data.HoVaTen}" if data.MaNhanVien and data.HoVaTen else ""
        cbb_taixe.set(cbb_taixe_val)
        cbb_xe.set(data.BienSoXe or "")
        entry_diembd.insert(0, data.DiemBatDau or "")
        entry_diemkt.insert(0, data.DiemKetThuc or "")
        
        if data.ThoiGianBatDau:
            date_bd.set_date(data.ThoiGianBatDau.strftime("%Y-%m-%d"))
            entry_giobd.insert(0, data.ThoiGianBatDau.strftime("%H:%M"))
        if data.ThoiGianKetThuc:
            date_kt.set_date(data.ThoiGianKetThuc.strftime("%Y-%m-%d"))
            entry_giokt.insert(0, data.ThoiGianKetThuc.strftime("%H:%M"))

        # CẬP NHẬT: Set text trạng thái
        trangthai_map = {0: "Đã gán", 1: "Đang thực hiện", 2: "Hoàn thành", 3: "Hủy"}
        cbb_trangthai.set(trangthai_map.get(data.TrangThai, "Đã gán"))

    except pyodbc.Error as e:
        messagebox.showerror("Lỗi SQL", f"Không thể lấy dữ liệu:\n{str(e)}")
    except Exception as e:
        messagebox.showerror("Lỗi không xác định", f"Lỗi: {str(e)}")
    finally:
        if conn: conn.close()
        # KHÓA LẠI FORM sau khi đổ dữ liệu
        entry_machuyendi.config(state='disabled') # PK luôn khóa
        set_form_state(is_enabled=False)

def chon_chuyendi_de_sua(event=None): 
    """(NÚT SỬA) Kích hoạt chế độ sửa, Mở khóa form (trừ MaChuyenDi)."""
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Chưa chọn", "Hãy chọn một chuyến đi trong danh sách trước khi nhấn 'Sửa'")
        return

    if not entry_machuyendi.get():
         messagebox.showwarning("Lỗi", "Không tìm thấy mã chuyến đi. Vui lòng chọn lại.")
         return

    set_form_state(is_enabled=True)
    entry_machuyendi.config(state='disabled') # PK luôn khóa
    cbb_taixe.focus() 

def luu_chuyendi_da_sua():
    """(LOGIC SỬA) Lưu thay đổi (UPDATE) sau khi sửa."""
    machuyendi = entry_machuyendi.get()
    if not machuyendi:
        messagebox.showwarning("Thiếu dữ liệu", "Không có Mã chuyến đi để cập nhật")
        return False

    try:
        manv = cbb_taixe_var.get().split(' - ')[0]
        bienso = cbb_xe_var.get()
        diembd = entry_diembd.get()
        diemkt = entry_diemkt.get()
        
        ngay_bd_str = date_bd.get_date().strftime('%Y-%m-%d')
        gio_bd_str = entry_giobd.get() or "00:00"
        tg_batdau = f"{ngay_bd_str} {gio_bd_str}:00"
        
        ngay_kt_str = date_kt.get_date().strftime('%Y-%m-%d')
        gio_kt_str = entry_giokt.get()
        tg_ketthuc = None
        if gio_kt_str: 
            tg_ketthuc = f"{ngay_kt_str} {gio_kt_str}:00"
        
        trangthai_text = cbb_trangthai_var.get()
        trangthai_map = {"Đã gán": 0, "Đang thực hiện": 1, "Hoàn thành": 2, "Hủy": 3}
        trangthai_value = trangthai_map.get(trangthai_text, 0)
        
        if not manv or not bienso or not diembd:
            messagebox.showwarning("Thiếu dữ liệu", "Tài xế, Xe và Điểm bắt đầu không được rỗng")
            return False

    except Exception as e:
        messagebox.showerror("Lỗi định dạng", f"Dữ liệu nhập không hợp lệ: {e}")
        return False

    conn = connect_db()
    if conn is None: return False
        
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
            tg_batdau, tg_ketthuc, trangthai_value,
            machuyendi
        ))
        conn.commit()
        messagebox.showinfo("Thành công", "Đã cập nhật thông tin chuyến đi")
        return True
        
    except pyodbc.Error as e:
        conn.rollback()
        messagebox.showerror("Lỗi SQL", f"Không thể cập nhật:\n{str(e)}")
        return False
    except Exception as e:
        conn.rollback()
        messagebox.showerror("Lỗi không xác định", f"Lỗi: {str(e)}")
        return False
    finally:
        if conn: conn.close()

def save_data():
    """Lưu dữ liệu, tự động kiểm tra xem nên Thêm mới (INSERT) hay Cập nhật (UPDATE)."""
    # Nếu ô MaChuyenDi có SỐ (được điền từ on_select) -> Sửa
    # Nếu rỗng (được xóa từ clear_input) -> Thêm
    if entry_machuyendi.get():
        success = luu_chuyendi_da_sua()
    else:
        success = them_chuyendi()
    
    if success:
        load_data()

def xoa_chuyendi_vinhvien():
    """(NGUY HIỂM) Xóa vĩnh viễn chuyến đi và MỌI DỮ LIỆU LIÊN QUAN."""
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Chưa chọn", "Hãy chọn một chuyến đi trong danh sách để xóa")
        return
        
    machuyendi = entry_machuyendi.get() # Lấy mã từ ô entry

    if not machuyendi:
        messagebox.showwarning("Lỗi", "Không tìm thấy mã chuyến đi. Vui lòng chọn lại.")
        return

    msg_xacnhan = (
        f"BẠN CÓ CHẮC CHẮN MUỐN XÓA VĨNH VIỄN CHUYẾN ĐI '{machuyendi}'?\n\n"
        "CẢNH BÁO: Thao tác này KHÔNG THỂ hoàn tác.\n"
        "Tất cả Lịch sử nhiên liệu của chuyến đi này sẽ bị XÓA SẠCH."
    )
    if not messagebox.askyesno("XÁC NHẬN XÓA VĨNH VIỄN", msg_xacnhan):
        return

    conn = connect_db()
    if conn is None: return
        
    try:
        cur = conn.cursor()
        
        # --- BẮT ĐẦU XÓA TỪ BẢNG CON ---
        cur.execute("DELETE FROM NhatKyNhienLieu WHERE MaChuyenDi=?", (machuyendi,))
        
        # --- XÓA BẢNG CHA ---
        cur.execute("DELETE FROM ChuyenDi WHERE MaChuyenDi=?", (machuyendi,))
        
        conn.commit()
        
        messagebox.showinfo("Thành công", f"Đã xóa vĩnh viễn chuyến đi '{machuyendi}' và dữ liệu liên quan.")
        load_data()
        
    except pyodbc.Error as e:
        conn.rollback()
        messagebox.showerror("Lỗi SQL", f"Không thể xóa chuyến đi:\n{str(e)}")
    except Exception as e:
        conn.rollback()
        messagebox.showerror("Lỗi không xác định", f"Lỗi: {str(e)}")
    finally:
        if conn: conn.close()

# ================================================================
# PHẦN 4: THIẾT KẾ GIAO DIỆN (Bản Light Mode)
# ================================================================

root = tk.Tk()
root.title("Quản lý Chuyến đi (Database QL_VanTai)")
root.config(bg=theme_colors["bg_main"]) 

# !!! DÁN HÀM BỊ THIẾU VÀO ĐÂY !!!
def center_window(w, h):
    """Hàm căn giữa cửa sổ."""
    ws = root.winfo_screenwidth()
    hs = root.winfo_screenheight()
    x = (ws/2) - (w/2)
    y = (hs/2) - (h/2)
    root.geometry('%dx%d+%d+%d' % (w, h, x, y))

# Sau đó gọi hàm
center_window(950, 700) # Cửa sổ lớn hơn
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


lbl_title = ttk.Label(root, text="QUẢN LÝ CHUYẾN ĐI", style="Title.TLabel")
lbl_title.pack(pady=15) 

# Frame nhập thông tin
frame_info = ttk.Frame(root, style="TFrame")
frame_info.pack(pady=5, padx=20, fill="x")

# --- Hàng 1 ---
ttk.Label(frame_info, text="Mã chuyến đi:").grid(row=0, column=0, padx=5, pady=8, sticky="w")
entry_machuyendi = ttk.Entry(frame_info, width=30, state='disabled')
entry_machuyendi.grid(row=0, column=1, padx=5, pady=8, sticky="w")

ttk.Label(frame_info, text="Trạng thái:").grid(row=0, column=2, padx=15, pady=8, sticky="w")
# CẬP NHẬT: Tùy chọn Combobox sạch
trangthai_options = ["Đã gán", "Đang thực hiện", "Hoàn thành", "Hủy"]
cbb_trangthai_var = tk.StringVar()
cbb_trangthai = ttk.Combobox(frame_info, textvariable=cbb_trangthai_var, values=trangthai_options, width=38, state='readonly')
cbb_trangthai.grid(row=0, column=3, padx=5, pady=8, sticky="w")
cbb_trangthai.set("Đã gán")

# --- Hàng 2 ---
ttk.Label(frame_info, text="Tài xế:").grid(row=1, column=0, padx=5, pady=8, sticky="w")
cbb_taixe_var = tk.StringVar()
cbb_taixe = ttk.Combobox(frame_info, textvariable=cbb_taixe_var, width=28, state='readonly')
cbb_taixe.grid(row=1, column=1, padx=5, pady=8, sticky="w")
cbb_taixe['values'] = load_taixe_combobox()

ttk.Label(frame_info, text="Xe:").grid(row=1, column=2, padx=15, pady=8, sticky="w")
cbb_xe_var = tk.StringVar()
cbb_xe = ttk.Combobox(frame_info, textvariable=cbb_xe_var, width=38, state='readonly')
cbb_xe.grid(row=1, column=3, padx=5, pady=8, sticky="w")
cbb_xe['values'] = load_xe_combobox()

# --- Hàng 3 ---
ttk.Label(frame_info, text="Điểm bắt đầu:").grid(row=2, column=0, padx=5, pady=8, sticky="w")
entry_diembd = ttk.Entry(frame_info, width=30)
entry_diembd.grid(row=2, column=1, padx=5, pady=8, sticky="w")

ttk.Label(frame_info, text="Điểm kết thúc:").grid(row=2, column=2, padx=15, pady=8, sticky="w")
entry_diemkt = ttk.Entry(frame_info, width=40)
entry_diemkt.grid(row=2, column=3, padx=5, pady=8, sticky="w")

# --- Hàng 4 (Thời gian) ---
frame_time = ttk.Frame(frame_info, style="TFrame")
frame_time.grid(row=3, column=0, columnspan=4, pady=10)

# Style DateEntry
date_entry_style_options = {
    'width': 12, 'date_pattern': 'yyyy-MM-dd',
    'background': theme_colors["bg_entry"], 
    'foreground': theme_colors["text"],
    'disabledbackground': theme_colors["disabled_bg"],
    'disabledforeground': theme_colors["text_disabled"],
    'bordercolor': theme_colors["bg_entry"],
    'headersbackground': theme_colors["accent"],
    'headersforeground': theme_colors["accent_text"],
    'selectbackground': theme_colors["accent"],
    'selectforeground': theme_colors["accent_text"]
}

ttk.Label(frame_time, text="Thời gian BĐ:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
date_bd = DateEntry(frame_time, **date_entry_style_options)
date_bd.grid(row=0, column=1, padx=5, pady=5, sticky="w")

ttk.Label(frame_time, text="Giờ BĐ (HH:MM):").grid(row=0, column=2, padx=5, pady=5, sticky="w")
entry_giobd = ttk.Entry(frame_time, width=10)
entry_giobd.grid(row=0, column=3, padx=5, pady=5, sticky="w")

ttk.Label(frame_time, text="Thời gian KT:").grid(row=0, column=4, padx=15, pady=5, sticky="w")
date_kt = DateEntry(frame_time, **date_entry_style_options)
date_kt.grid(row=0, column=5, padx=5, pady=5, sticky="w")

ttk.Label(frame_time, text="Giờ KT (HH:MM):").grid(row=0, column=6, padx=5, pady=5, sticky="w")
entry_giokt = ttk.Entry(frame_time, width=10)
entry_giokt.grid(row=0, column=7, padx=5, pady=5, sticky="w")

# Cấu hình grid co giãn
frame_info.columnconfigure(1, weight=1)
frame_info.columnconfigure(3, weight=1)

# ===== Frame nút (Đã cập nhật command) =====
frame_btn = ttk.Frame(root, style="TFrame")
frame_btn.pack(pady=10)

btn_them = ttk.Button(frame_btn, text="Thêm", width=8, command=clear_input) 
btn_them.grid(row=0, column=0, padx=10)
btn_luu = ttk.Button(frame_btn, text="Lưu", width=8, command=save_data) 
btn_luu.grid(row=0, column=1, padx=10)
btn_sua = ttk.Button(frame_btn, text="Sửa", width=8, command=chon_chuyendi_de_sua) 
btn_sua.grid(row=0, column=2, padx=10)
btn_huy = ttk.Button(frame_btn, text="Hủy", width=8, command=load_data) 
btn_huy.grid(row=0, column=3, padx=10)
btn_xoa = ttk.Button(frame_btn, text="Xóa", width=8, command=xoa_chuyendi_vinhvien) 
btn_xoa.grid(row=0, column=4, padx=10)
btn_thoat = ttk.Button(frame_btn, text="Thoát", width=8, command=root.quit)
btn_thoat.grid(row=0, column=5, padx=10)


# ===== Bảng danh sách chuyến đi =====
lbl_ds = ttk.Label(root, text="Danh sách chuyến đi (Sắp xếp mới nhất)", style="Header.TLabel")
lbl_ds.pack(pady=(10, 5), padx=20, anchor="w")

frame_tree = ttk.Frame(root, style="TFrame")
frame_tree.pack(pady=10, padx=20, fill="both", expand=True) 

scrollbar_y = ttk.Scrollbar(frame_tree, orient=tk.VERTICAL, style="Vertical.TScrollbar")
scrollbar_x = ttk.Scrollbar(frame_tree, orient=tk.HORIZONTAL, style="Horizontal.TScrollbar")

columns = ("ma_cd", "ten_tx", "bienso", "tg_bd", "trangthai")
tree = ttk.Treeview(frame_tree, columns=columns, show="headings", height=10,
                    yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)

scrollbar_y.config(command=tree.yview)
scrollbar_x.config(command=tree.xview)

scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)

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

# THÊM BINDING (SỰ KIỆN CLICK)
tree.bind("<<TreeviewSelect>>", on_item_select) 

# ================================================================
# PHẦN 5: CHẠY ỨNG DỤNG
# ================================================================
load_data() # Tải dữ liệu ban đầu
root.mainloop()