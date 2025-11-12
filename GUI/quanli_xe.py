import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
import pyodbc 
import datetime

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
# PHẦN 2: CÁC HÀM CRUD (NÂNG CẤP THEO MẪU)
# ================================================================

def set_form_state(is_enabled):
    """Bật (enable) hoặc Tắt (disable) toàn bộ các trường nhập liệu."""
    if is_enabled:
        # Chế độ Bật
        entry_loaixe.config(state='normal')
        entry_hangsx.config(state='normal')
        entry_dongxe.config(state='normal')
        entry_namsx.config(state='normal')
        entry_vin.config(state='normal')
        date_dangkiem.config(state='normal')
        date_baohiem.config(state='normal')
        cbb_trangthai.config(state='readonly')
        entry_manv.config(state='normal')
    else:
        # Chế độ Tắt (Làm mờ)
        entry_bienso.config(state='disabled')
        entry_loaixe.config(state='disabled')
        entry_hangsx.config(state='disabled')
        entry_dongxe.config(state='disabled')
        entry_namsx.config(state='disabled')
        entry_vin.config(state='disabled')
        date_dangkiem.config(state='disabled')
        date_baohiem.config(state='disabled')
        cbb_trangthai.config(state='disabled')
        entry_manv.config(state='disabled')

def clear_input():
    """(NÚT THÊM) Xóa trắng và Mở khóa các trường nhập liệu (Chế độ Thêm mới)."""
    set_form_state(is_enabled=True)
    entry_bienso.config(state='normal') 
    
    entry_bienso.delete(0, tk.END)
    entry_loaixe.delete(0, tk.END)
    entry_hangsx.delete(0, tk.END)
    entry_dongxe.delete(0, tk.END)
    entry_namsx.delete(0, tk.END)
    entry_vin.delete(0, tk.END)
    entry_manv.delete(0, tk.END)
    
    # Set giá trị mặc định (đã bỏ tiền tố)
    default_date = datetime.date.today() + datetime.timedelta(days=365)
    date_dangkiem.set_date(default_date)
    date_baohiem.set_date(default_date)
    cbb_trangthai.set("Hoạt động")
    
    entry_bienso.focus()
    if tree.selection():
        tree.selection_remove(tree.selection()[0])

def load_data():
    """Tải TOÀN BỘ dữ liệu Xe VÀ LÀM MỜ FORM."""
    for i in tree.get_children():
        tree.delete(i)
        
    conn = connect_db()
    if conn is None:
        set_form_state(is_enabled=False) 
        return
        
    try:
        cur = conn.cursor()
        cur.execute("SELECT BienSoXe, LoaiXe, HangSanXuat, NamSanXuat, TrangThai, NgayHetHanDangKiem FROM Xe")
        rows = cur.fetchall()
        
        for row in rows:
            # CẬP NHẬT: Chuyển đổi trạng thái số sang chữ (Sạch)
            trang_thai_text = "Hoạt động"
            if row[4] == 0:
                trang_thai_text = "Bảo trì"
            elif row[4] == 2:
                trang_thai_text = "Hỏng"
            
            ngay_dk = str(row[5]) if row[5] else "N/A"
            
            tree.insert("", tk.END, values=(row[0], row[1], row[2], row[3], trang_thai_text, ngay_dk))
        
        children = tree.get_children()
        if children:
            first_item = children[0]
            tree.selection_set(first_item) 
            tree.focus(first_item)         
            tree.event_generate("<<TreeviewSelect>>") 
        else:
            # Nếu không có data, xóa trắng form
            entry_bienso.config(state='normal')
            set_form_state(is_enabled=True)
            # Gọi clear_input bản rút gọn
            entry_bienso.delete(0, tk.END)
            entry_loaixe.delete(0, tk.END)
            entry_hangsx.delete(0, tk.END)
            entry_dongxe.delete(0, tk.END)
            entry_namsx.delete(0, tk.END)
            entry_vin.delete(0, tk.END)
            entry_manv.delete(0, tk.END)
            cbb_trangthai.set("Hoạt động")
            
    except pyodbc.Error as e:
        messagebox.showerror("Lỗi tải dữ liệu", f"Lỗi SQL: {str(e)}")
    except Exception as e:
        messagebox.showerror("Lỗi không xác định", f"Lỗi: {str(e)}")
    finally:
        if conn:
            conn.close()
        # LUÔN LUÔN LÀM MỜ FORM SAU KHI TẢI DỮ LIỆU
        set_form_state(is_enabled=False)

def them_xe():
    """(LOGIC THÊM) Thêm một xe mới vào CSDL."""
    bienso = entry_bienso.get()
    loaixe = entry_loaixe.get()
    hangsx = entry_hangsx.get()
    dongxe = entry_dongxe.get()
    namsx = entry_namsx.get()
    vin = entry_vin.get()
    ngay_dk = date_dangkiem.get_date().strftime('%Y-%m-%d')
    ngay_bh = date_baohiem.get_date().strftime('%Y-%m-%d')
    manv = entry_manv.get()

    # CẬP NHẬT: Chuyển text từ Combobox về số
    trangthai_text = cbb_trangthai_var.get()
    trangthai_value = 1 # Hoạt động
    if trangthai_text == "Bảo trì":
        trangthai_value = 0
    elif trangthai_text == "Hỏng":
        trangthai_value = 2

    if not bienso or not loaixe:
        messagebox.showwarning("Thiếu dữ liệu", "Vui lòng nhập Biển số xe và Loại xe")
        return False

    manv_sql = manv if manv else None
    
    try:
        namsx_int = int(namsx) if namsx else None
    except ValueError:
        messagebox.showwarning("Sai định dạng", "Năm sản xuất phải là số")
        return False

    conn = connect_db()
    if conn is None: return False

    try:
        cur = conn.cursor()
        sql = """
        INSERT INTO Xe (
            BienSoXe, LoaiXe, HangSanXuat, DongXe, NamSanXuat, 
            SoKhungVIN, NgayHetHanDangKiem, NgayHetHanBaoHiem, 
            TrangThai, MaNhanVienHienTai
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        cur.execute(sql, (
            bienso, loaixe, hangsx, dongxe, namsx_int,
            vin, ngay_dk, ngay_bh, trangthai_value, manv_sql
        ))
        conn.commit()
        messagebox.showinfo("Thành công", "Đã thêm xe mới thành công")
        return True
        
    except pyodbc.IntegrityError:
        conn.rollback()
        messagebox.showerror("Lỗi Trùng lặp", f"Biển số xe '{bienso}' đã tồn tại.")
        return False
    except pyodbc.Error as e:
        conn.rollback()
        messagebox.showerror("Lỗi SQL", f"Không thể thêm xe:\n{str(e)}")
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
    bienso = selected_item['values'][0]
    
    conn = connect_db()
    if conn is None: return

    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM Xe WHERE BienSoXe=?", (bienso,))
        data = cur.fetchone()
        
        if not data:
            messagebox.showerror("Lỗi", "Không tìm thấy dữ liệu xe.")
            return

        # Tạm thời MỞ KHÓA form để đổ dữ liệu
        set_form_state(is_enabled=True)
        entry_bienso.config(state='normal')
        
        # Xóa và Đổ dữ liệu
        entry_bienso.delete(0, tk.END)
        entry_loaixe.delete(0, tk.END)
        entry_hangsx.delete(0, tk.END)
        entry_dongxe.delete(0, tk.END)
        entry_namsx.delete(0, tk.END)
        entry_vin.delete(0, tk.END)
        entry_manv.delete(0, tk.END)
        
        entry_bienso.insert(0, data.BienSoXe)
        entry_loaixe.insert(0, data.LoaiXe or "")
        entry_hangsx.insert(0, data.HangSanXuat or "")
        entry_dongxe.insert(0, data.DongXe or "")
        entry_namsx.insert(0, str(data.NamSanXuat or ""))
        entry_vin.insert(0, data.SoKhungVIN or "")
        entry_manv.insert(0, data.MaNhanVienHienTai or "")
        
        if data.NgayHetHanDangKiem:
            date_dangkiem.set_date(data.NgayHetHanDangKiem)
        if data.NgayHetHanBaoHiem:
            date_baohiem.set_date(data.NgayHetHanBaoHiem)
            
        # CẬP NHẬT: Set text mới (Hoạt động / Bảo trì / Hỏng)
        trang_thai_text = "Hoạt động"
        if data.TrangThai == 0:
            trang_thai_text = "Bảo trì"
        elif data.TrangThai == 2:
            trang_thai_text = "Hỏng"
        cbb_trangthai.set(trang_thai_text)

    except pyodbc.Error as e:
        messagebox.showerror("Lỗi SQL", f"Không thể lấy dữ liệu xe:\n{str(e)}")
    except Exception as e:
        messagebox.showerror("Lỗi không xác định", f"Lỗi: {str(e)}")
    finally:
        if conn: conn.close()
        # KHÓA LẠI FORM sau khi đổ dữ liệu
        set_form_state(is_enabled=False)

def chon_xe_de_sua(event=None): 
    """(NÚT SỬA) Kích hoạt chế độ sửa, Mở khóa form (trừ Biển số)."""
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Chưa chọn", "Hãy chọn một xe trong danh sách trước khi nhấn 'Sửa'")
        return

    if not entry_bienso.get():
         messagebox.showwarning("Lỗi", "Không tìm thấy biển số xe. Vui lòng chọn lại.")
         return

    set_form_state(is_enabled=True)
    entry_bienso.config(state='disabled') # Khóa Biển số (PK)
    entry_loaixe.focus() 

def luu_xe_da_sua():
    """(LOGIC SỬA) Lưu thay đổi (UPDATE) sau khi sửa."""
    bienso = entry_bienso.get()
    if not bienso:
        messagebox.showwarning("Thiếu dữ liệu", "Không có Biển số xe để cập nhật")
        return False

    loaixe = entry_loaixe.get()
    hangsx = entry_hangsx.get()
    dongxe = entry_dongxe.get()
    namsx = entry_namsx.get()
    vin = entry_vin.get()
    ngay_dk = date_dangkiem.get_date().strftime('%Y-%m-%d')
    ngay_bh = date_baohiem.get_date().strftime('%Y-%m-%d')
    manv = entry_manv.get()

    trangthai_text = cbb_trangthai_var.get()
    trangthai_value = 1 # Hoạt động
    if trangthai_text == "Bảo trì":
        trangthai_value = 0
    elif trangthai_text == "Hỏng":
        trangthai_value = 2
        
    if not loaixe:
        messagebox.showwarning("Thiếu dữ liệu", "Loại xe không được rỗng")
        return False

    manv_sql = manv if manv else None
    
    try:
        namsx_int = int(namsx) if namsx else None
    except ValueError:
        messagebox.showwarning("Sai định dạng", "Năm sản xuất phải là số")
        return False

    conn = connect_db()
    if conn is None: return False
        
    try:
        cur = conn.cursor()
        sql = """
        UPDATE Xe SET 
            LoaiXe = ?, HangSanXuat = ?, DongXe = ?, NamSanXuat = ?,
            SoKhungVIN = ?, NgayHetHanDangKiem = ?, NgayHetHanBaoHiem = ?,
            TrangThai = ?, MaNhanVienHienTai = ?
        WHERE BienSoXe = ?
        """
        cur.execute(sql, (
            loaixe, hangsx, dongxe, namsx_int,
            vin, ngay_dk, ngay_bh, trangthai_value, manv_sql,
            bienso 
        ))
        conn.commit()
        messagebox.showinfo("Thành công", "Đã cập nhật thông tin xe")
        return True
        
    except pyodbc.Error as e:
        conn.rollback()
        messagebox.showerror("Lỗi SQL", f"Không thể cập nhật xe:\n{str(e)}")
        return False
    except Exception as e:
        conn.rollback()
        messagebox.showerror("Lỗi không xác định", f"Lỗi: {str(e)}")
        return False
    finally:
        if conn: conn.close()

def save_data():
    """Lưu dữ liệu, tự động kiểm tra xem nên Thêm mới (INSERT) hay Cập nhật (UPDATE)."""
    if entry_bienso.cget('state') == 'disabled':
        success = luu_xe_da_sua()
    else:
        success = them_xe()
    
    if success:
        load_data()

def xoa_xe_vinhvien():
    """(NGUY HIỂM) Xóa vĩnh viễn xe và MỌI DỮ LIỆU LIÊN QUAN."""
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Chưa chọn", "Hãy chọn một xe trong danh sách để xóa")
        return
        
    bienso = entry_bienso.get() # Lấy bienso từ ô entry (đã được điền)

    if not bienso:
        messagebox.showwarning("Lỗi", "Không tìm thấy biển số xe. Vui lòng chọn lại.")
        return

    msg_xacnhan = (
        f"BẠN CÓ CHẮC CHẮN MUỐN XÓA VĨNH VIỄN XE '{bienso}'?\n\n"
        "CẢNH BÁO: Thao tác này KHÔNG THỂ hoàn tác.\n"
        "Tất cả Lịch sử chuyến đi, Lịch sử nhiên liệu, và Lịch sử bảo trì của xe này sẽ bị XÓA SẠCH."
    )
    if not messagebox.askyesno("XÁC NHẬN XÓA VĨNH VIỄN", msg_xacnhan):
        return

    conn = connect_db()
    if conn is None: return
        
    try:
        cur = conn.cursor()
        
        # --- BẮT ĐẦU XÓA TỪ BẢNG CON ---
        cur.execute("DELETE FROM NhatKyNhienLieu WHERE BienSoXe=?", (bienso,))
        cur.execute("DELETE FROM LichSuBaoTri WHERE BienSoXe=?", (bienso,))
        cur.execute("DELETE FROM ChuyenDi WHERE BienSoXe=?", (bienso,))
        
        # --- XÓA BẢNG CHA ---
        cur.execute("DELETE FROM Xe WHERE BienSoXe=?", (bienso,))
        
        conn.commit()
        
        messagebox.showinfo("Thành công", f"Đã xóa vĩnh viễn xe '{bienso}' và tất cả dữ liệu liên quan.")
        load_data()
        
    except pyodbc.Error as e:
        conn.rollback()
        messagebox.showerror("Lỗi SQL", f"Không thể xóa xe:\n{str(e)}")
    except Exception as e:
        conn.rollback()
        messagebox.showerror("Lỗi không xác định", f"Lỗi: {str(e)}")
    finally:
        if conn: conn.close()

# ================================================================
# PHẦN 3: THIẾT KẾ GIAO DIỆN (Bản Light Mode)
# ================================================================

root = tk.Tk()
root.title("Quản lý Xe (Database QL_VanTai)")
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


lbl_title = ttk.Label(root, text="QUẢN LÝ XE", style="Title.TLabel")
lbl_title.pack(pady=15) 

frame_info = ttk.Frame(root, style="TFrame")
frame_info.pack(pady=5, padx=20, fill="x")

# --- Cột 1 ---
ttk.Label(frame_info, text="Biển số xe:").grid(row=0, column=0, padx=5, pady=8, sticky="w")
entry_bienso = ttk.Entry(frame_info, width=30)
entry_bienso.grid(row=0, column=1, padx=5, pady=8, sticky="w")

ttk.Label(frame_info, text="Loại xe:").grid(row=1, column=0, padx=5, pady=8, sticky="w")
entry_loaixe = ttk.Entry(frame_info, width=30)
entry_loaixe.grid(row=1, column=1, padx=5, pady=8, sticky="w")

ttk.Label(frame_info, text="Hãng sản xuất:").grid(row=2, column=0, padx=5, pady=8, sticky="w")
entry_hangsx = ttk.Entry(frame_info, width=30)
entry_hangsx.grid(row=2, column=1, padx=5, pady=8, sticky="w")

ttk.Label(frame_info, text="Dòng xe:").grid(row=3, column=0, padx=5, pady=8, sticky="w")
entry_dongxe = ttk.Entry(frame_info, width=30)
entry_dongxe.grid(row=3, column=1, padx=5, pady=8, sticky="w")

ttk.Label(frame_info, text="Mã NV lái:").grid(row=4, column=0, padx=5, pady=8, sticky="w")
entry_manv = ttk.Entry(frame_info, width=30)
entry_manv.grid(row=4, column=1, padx=5, pady=8, sticky="w")

# --- Cột 2 ---
ttk.Label(frame_info, text="Năm sản xuất:").grid(row=0, column=2, padx=15, pady=8, sticky="w")
entry_namsx = ttk.Entry(frame_info, width=30)
entry_namsx.grid(row=0, column=3, padx=5, pady=8, sticky="w")

ttk.Label(frame_info, text="Số khung (VIN):").grid(row=1, column=2, padx=15, pady=8, sticky="w")
entry_vin = ttk.Entry(frame_info, width=30)
entry_vin.grid(row=1, column=3, padx=5, pady=8, sticky="w")

# Style DateEntry
date_entry_style_options = {
    'width': 28, 'date_pattern': 'yyyy-MM-dd',
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

ttk.Label(frame_info, text="Ngày hết hạn ĐK:").grid(row=2, column=2, padx=15, pady=8, sticky="w")
date_dangkiem = DateEntry(frame_info, **date_entry_style_options)
date_dangkiem.grid(row=2, column=3, padx=5, pady=8, sticky="w")

ttk.Label(frame_info, text="Ngày hết hạn BH:").grid(row=3, column=2, padx=15, pady=8, sticky="w")
date_baohiem = DateEntry(frame_info, **date_entry_style_options)
date_baohiem.grid(row=3, column=3, padx=5, pady=8, sticky="w")

ttk.Label(frame_info, text="Trạng thái:").grid(row=4, column=2, padx=15, pady=8, sticky="w")
# CẬP NHẬT: Tùy chọn Combobox sạch
trangthai_options = ["Bảo trì", "Hoạt động", "Hỏng"]
cbb_trangthai_var = tk.StringVar()
cbb_trangthai = ttk.Combobox(frame_info, textvariable=cbb_trangthai_var, values=trangthai_options, width=28, state='readonly')
cbb_trangthai.grid(row=4, column=3, padx=5, pady=8, sticky="w")
cbb_trangthai.set("Hoạt động") # Mặc định

frame_info.columnconfigure(1, weight=1)
frame_info.columnconfigure(3, weight=1)

# ===== Frame nút (Đã cập nhật command) =====
frame_btn = ttk.Frame(root, style="TFrame")
frame_btn.pack(pady=10)

btn_them = ttk.Button(frame_btn, text="Thêm", width=8, command=clear_input) 
btn_them.grid(row=0, column=0, padx=10)
btn_luu = ttk.Button(frame_btn, text="Lưu", width=8, command=save_data) 
btn_luu.grid(row=0, column=1, padx=10)
btn_sua = ttk.Button(frame_btn, text="Sửa", width=8, command=chon_xe_de_sua) 
btn_sua.grid(row=0, column=2, padx=10)
btn_huy = ttk.Button(frame_btn, text="Hủy", width=8, command=load_data) 
btn_huy.grid(row=0, column=3, padx=10)
btn_xoa = ttk.Button(frame_btn, text="Xóa", width=8, command=xoa_xe_vinhvien) 
btn_xoa.grid(row=0, column=4, padx=10)
btn_thoat = ttk.Button(frame_btn, text="Thoát", width=8, command=root.quit)
btn_thoat.grid(row=0, column=5, padx=10)


# ===== Bảng danh sách xe =====
lbl_ds = ttk.Label(root, text="Danh sách xe", style="Header.TLabel")
lbl_ds.pack(pady=(10, 5), padx=20, anchor="w")

frame_tree = ttk.Frame(root, style="TFrame")
frame_tree.pack(pady=10, padx=20, fill="both", expand=True) 

scrollbar_y = ttk.Scrollbar(frame_tree, orient=tk.VERTICAL, style="Vertical.TScrollbar")
scrollbar_x = ttk.Scrollbar(frame_tree, orient=tk.HORIZONTAL, style="Horizontal.TScrollbar")

columns = ("bienso", "loaixe", "hangsx", "namsx", "trangthai", "ngay_dk")
tree = ttk.Treeview(frame_tree, columns=columns, show="headings", height=10,
                    yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)

scrollbar_y.config(command=tree.yview)
scrollbar_x.config(command=tree.xview)

scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)

tree.heading("bienso", text="Biển số xe")
tree.column("bienso", width=100, anchor="center")
tree.heading("loaixe", text="Loại xe")
tree.column("loaixe", width=150)
tree.heading("hangsx", text="Hãng sản xuất")
tree.column("hangsx", width=150)
tree.heading("namsx", text="Năm SX")
tree.column("namsx", width=80, anchor="center")
tree.heading("trangthai", text="Trang thái")
tree.column("trangthai", width=100, anchor="center")
tree.heading("ngay_dk", text="Ngày hết hạn ĐK")
tree.column("ngay_dk", width=150, anchor="center")

tree.pack(fill="both", expand=True)

# THÊM BINDING (SỰ KIỆN CLICK)
tree.bind("<<TreeviewSelect>>", on_item_select) 

# ================================================================
# PHẦN 4: CHẠY ỨNG DỤNG
# ================================================================
load_data() 
root.mainloop()