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
# PHẦN 2: CÁC HÀM TIỆN ÍCH (Tải Combobox - Tái sử dụng)
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
    # MaNhatKy luôn disabled
    entry_manhatky.config(state='disabled')
    
    if is_enabled:
        # Chế độ Bật
        cbb_xe.config(state='readonly')
        cbb_taixe.config(state='readonly')
        date_ngaydo.config(state='normal')
        entry_giodo.config(state='normal')
        entry_solit.config(state='normal')
        entry_tongchiphi.config(state='normal')
        entry_soodo.config(state='normal')
        cbb_trangthai.config(state='readonly')
    else:
        # Chế độ Tắt (Làm mờ)
        cbb_xe.config(state='disabled')
        cbb_taixe.config(state='disabled')
        date_ngaydo.config(state='disabled')
        entry_giodo.config(state='disabled')
        entry_solit.config(state='disabled')
        entry_tongchiphi.config(state='disabled')
        entry_soodo.config(state='disabled')
        cbb_trangthai.config(state='disabled')

def clear_input():
    """(NÚT THÊM) Xóa trắng và Mở khóa các trường nhập liệu (Chế độ Thêm mới)."""
    set_form_state(is_enabled=True)
    
    entry_manhatky.config(state='normal')
    entry_manhatky.delete(0, tk.END)
    entry_manhatky.config(state='disabled')
    
    cbb_taixe.set("")
    cbb_xe.set("")
    entry_solit.delete(0, tk.END)
    entry_tongchiphi.delete(0, tk.END)
    entry_soodo.delete(0, tk.END)
    
    now = datetime.now()
    date_ngaydo.set_date(now.strftime("%Y-%m-%d"))
    entry_giodo.delete(0, tk.END)
    entry_giodo.insert(0, now.strftime("%H:%M"))
    
    cbb_trangthai.set("Chờ duyệt") # Giá trị text mới
    cbb_xe.focus()
    
    if tree.selection():
        tree.selection_remove(tree.selection()[0])

def load_data():
    """Tải TOÀN BỘ dữ liệu Nhiên liệu VÀ LÀM MỜ FORM."""
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
            nk.MaNhatKy, nk.BienSoXe, nv.HoVaTen, 
            nk.NgayDoNhienLieu, nk.SoLit, nk.TongChiPhi, nk.TrangThaiDuyet
        FROM NhatKyNhienLieu AS nk
        LEFT JOIN NhanVien AS nv ON nk.MaNhanVien = nv.MaNhanVien
        ORDER BY nk.NgayDoNhienLieu DESC
        """
        cur.execute(sql)
        rows = cur.fetchall()
        
        # CẬP NHẬT: Map text mới
        trangthai_map = { 0: "Chờ duyệt", 1: "Đã duyệt", 2: "Từ chối" }
        
        for row in rows:
            ma_nk = row[0]
            bienso = row[1]
            ten_tx = row[2] or "N/A"
            ngay_do = row[3].strftime("%Y-%m-%d %H:%M") if row[3] else "N/A"
            so_lit = row[4]
            tong_cp = row[5]
            trangthai_text = trangthai_map.get(row[6], "Không rõ")
            
            tree.insert("", tk.END, values=(ma_nk, bienso, ten_tx, ngay_do, so_lit, tong_cp, trangthai_text))
            
        children = tree.get_children()
        if children:
            first_item = children[0]
            tree.selection_set(first_item) 
            tree.focus(first_item)         
            tree.event_generate("<<TreeviewSelect>>") 
        else:
            set_form_state(is_enabled=True)
            clear_input() 
            
    except pyodbc.Error as e:
        messagebox.showerror("Lỗi tải dữ liệu", f"Lỗi SQL: {str(e)}")
    except Exception as e:
        messagebox.showerror("Lỗi không xác định", f"Lỗi: {str(e)}")
    finally:
        if conn:
            conn.close()
        # LUÔN LUÔN LÀM MỜ FORM SAU KHI TẢI DỮ LIỆU
        set_form_state(is_enabled=False)

def them_nhienlieu():
    """(LOGIC THÊM) Thêm một nhật ký nhiên liệu mới."""
    try:
        bienso = cbb_xe_var.get()
        manv = cbb_taixe_var.get().split(' - ')[0]
        
        ngay_do_str = date_ngaydo.get_date().strftime('%Y-%m-%d')
        gio_do_str = entry_giodo.get() or "00:00"
        tg_nhienlieu = f"{ngay_do_str} {gio_do_str}:00"
        
        solit = entry_solit.get()
        tongchiphi = entry_tongchiphi.get()
        soodo = entry_soodo.get()
        
        # CẬP NHẬT: Chuyển text về số
        trangthai_text = cbb_trangthai_var.get()
        trangthai_map = {"Chờ duyệt": 0, "Đã duyệt": 1, "Từ chối": 2}
        trangthai_value = trangthai_map.get(trangthai_text, 0)

        if not bienso or not manv or not solit or not tongchiphi:
            messagebox.showwarning("Thiếu dữ liệu", "Vui lòng nhập Xe, Tài xế, Số lít và Chi phí")
            return False

        solit_dec = float(solit) if solit else 0.0
        tongchiphi_dec = float(tongchiphi) if tongchiphi else 0.0
        soodo_int = int(soodo) if soodo else None

    except Exception as e:
        messagebox.showerror("Lỗi định dạng", f"Dữ liệu số (lít, chi phí, odo) không hợp lệ: {e}")
        return False

    conn = connect_db()
    if conn is None: return False

    try:
        cur = conn.cursor()
        sql = """
        INSERT INTO NhatKyNhienLieu (
            BienSoXe, MaNhanVien, NgayDoNhienLieu, SoLit, 
            TongChiPhi, SoOdo, TrangThaiDuyet
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        cur.execute(sql, (bienso, manv, tg_nhienlieu, solit_dec, tongchiphi_dec, soodo_int, trangthai_value))
        conn.commit()
        messagebox.showinfo("Thành công", "Đã thêm nhật ký nhiên liệu thành công")
        return True
        
    except pyodbc.Error as e:
        conn.rollback() 
        messagebox.showerror("Lỗi SQL", f"Không thể thêm nhật ký:\n{str(e)}")
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
    manhatky = selected_item['values'][0]
    
    conn = connect_db()
    if conn is None: return

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

        # Tạm thời MỞ KHÓA form để đổ dữ liệu
        set_form_state(is_enabled=True)
        entry_manhatky.config(state='normal')
        
        # Xóa và Đổ dữ liệu
        entry_manhatky.delete(0, tk.END)
        cbb_xe.set("")
        cbb_taixe.set("")
        entry_giodo.delete(0, tk.END)
        entry_solit.delete(0, tk.END)
        entry_tongchiphi.delete(0, tk.END)
        entry_soodo.delete(0, tk.END)
        
        entry_manhatky.insert(0, data.MaNhatKy)
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

        # CẬP NHẬT: Set text trạng thái
        trangthai_map = {0: "Chờ duyệt", 1: "Đã duyệt", 2: "Từ chối"}
        cbb_trangthai.set(trangthai_map.get(data.TrangThaiDuyet, "Chờ duyệt"))

    except pyodbc.Error as e:
        messagebox.showerror("Lỗi SQL", f"Không thể lấy dữ liệu:\n{str(e)}")
    except Exception as e:
        messagebox.showerror("Lỗi không xác định", f"Lỗi: {str(e)}")
    finally:
        if conn: conn.close()
        # KHÓA LẠI FORM sau khi đổ dữ liệu
        entry_manhatky.config(state='disabled') # PK luôn khóa
        set_form_state(is_enabled=False)

def chon_nhienlieu_de_sua(event=None): 
    """(NÚT SỬA) Kích hoạt chế độ sửa, Mở khóa form (trừ MaNhatKy)."""
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Chưa chọn", "Hãy chọn một nhật ký trong danh sách trước khi nhấn 'Sửa'")
        return

    if not entry_manhatky.get():
         messagebox.showwarning("Lỗi", "Không tìm thấy mã nhật ký. Vui lòng chọn lại.")
         return

    set_form_state(is_enabled=True)
    entry_manhatky.config(state='disabled') # PK luôn khóa
    cbb_xe.focus() 

def luu_nhienlieu_da_sua():
    """(LOGIC SỬA) Lưu thay đổi (UPDATE) sau khi sửa."""
    manhatky = entry_manhatky.get()
    if not manhatky:
        messagebox.showwarning("Thiếu dữ liệu", "Không có Mã nhật ký để cập nhật")
        return False

    try:
        bienso = cbb_xe_var.get()
        manv = cbb_taixe_var.get().split(' - ')[0]
        
        ngay_do_str = date_ngaydo.get_date().strftime('%Y-%m-%d')
        gio_do_str = entry_giodo.get() or "00:00"
        tg_nhienlieu = f"{ngay_do_str} {gio_do_str}:00"
        
        solit = entry_solit.get()
        tongchiphi = entry_tongchiphi.get()
        soodo = entry_soodo.get()
        
        trangthai_text = cbb_trangthai_var.get()
        trangthai_map = {"Chờ duyệt": 0, "Đã duyệt": 1, "Từ chối": 2}
        trangthai_value = trangthai_map.get(trangthai_text, 0)
        
        if not bienso or not manv or not solit or not tongchiphi:
            messagebox.showwarning("Thiếu dữ liệu", "Xe, Tài xế, Số lít và Chi phí không được rỗng")
            return False

        solit_dec = float(solit) if solit else 0.0
        tongchiphi_dec = float(tongchiphi) if tongchiphi else 0.0
        soodo_int = int(soodo) if soodo else None

    except Exception as e:
        messagebox.showerror("Lỗi định dạng", f"Dữ liệu nhập không hợp lệ: {e}")
        return False

    conn = connect_db()
    if conn is None: return False
        
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
            solit_dec, tongchiphi_dec, soodo_int, trangthai_value,
            manhatky
        ))
        conn.commit()
        messagebox.showinfo("Thành công", "Đã cập nhật nhật ký nhiên liệu")
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
    if entry_manhatky.get():
        success = luu_nhienlieu_da_sua()
    else:
        success = them_nhienlieu()
    
    if success:
        load_data()

def xoa_nhienlieu():
    """Xóa nhật ký được chọn."""
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Chưa chọn", "Hãy chọn một nhật ký để xóa")
        return
        
    manhatky = entry_manhatky.get() # Lấy mã từ ô entry

    if not manhatky:
        messagebox.showwarning("Lỗi", "Không tìm thấy mã nhật ký. Vui lòng chọn lại.")
        return

    if not messagebox.askyesno("Xác nhận", f"Bạn có chắc chắn muốn xóa Nhật ký Mã: {manhatky}?"):
        return

    conn = connect_db()
    if conn is None: return
        
    try:
        cur = conn.cursor()
        cur.execute("DELETE FROM NhatKyNhienLieu WHERE MaNhatKy=?", (manhatky,))
        conn.commit()
        
        messagebox.showinfo("Thành công", "Đã xóa nhật ký thành công")
        load_data()
        
    except pyodbc.Error as e:
        conn.rollback()
        messagebox.showerror("Lỗi SQL", f"Không thể xóa:\n{str(e)}")
    except Exception as e:
        conn.rollback()
        messagebox.showerror("Lỗi không xác định", f"Lỗi: {str(e)}")
    finally:
        if conn: conn.close()

# ================================================================
# PHẦN 4: THIẾT KẾ GIAO DIỆN (Bản Light Mode)
# ================================================================

root = tk.Tk()
root.title("Quản lý Nhiên liệu (Database QL_VanTai)")
root.config(bg=theme_colors["bg_main"]) 

def center_window(w, h):
    """Hàm căn giữa cửa sổ."""
    ws = root.winfo_screenwidth()
    hs = root.winfo_screenheight()
    x = (ws/2) - (w/2)
    y = (hs/2) - (h/2)
    root.geometry('%dx%d+%d+%d' % (w, h, x, y))

center_window(950, 700) 
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


lbl_title = ttk.Label(root, text="QUẢN LÝ NHẬT KÝ NHIÊN LIỆU", style="Title.TLabel")
lbl_title.pack(pady=15) 

frame_info = ttk.Frame(root, style="TFrame")
frame_info.pack(pady=5, padx=20, fill="x")

# --- Hàng 1 ---
ttk.Label(frame_info, text="Mã nhật ký:").grid(row=0, column=0, padx=5, pady=8, sticky="w")
entry_manhatky = ttk.Entry(frame_info, width=30, state='disabled')
entry_manhatky.grid(row=0, column=1, padx=5, pady=8, sticky="w")

ttk.Label(frame_info, text="Trạng thái:").grid(row=0, column=2, padx=15, pady=8, sticky="w")
# CẬP NHẬT: Tùy chọn Combobox sạch
trangthai_options = ["Chờ duyệt", "Đã duyệt", "Từ chối"]
cbb_trangthai_var = tk.StringVar()
cbb_trangthai = ttk.Combobox(frame_info, textvariable=cbb_trangthai_var, values=trangthai_options, width=38, state='readonly')
cbb_trangthai.grid(row=0, column=3, padx=5, pady=8, sticky="w")
cbb_trangthai.set("Chờ duyệt")

# --- Hàng 2 ---
ttk.Label(frame_info, text="Xe:").grid(row=1, column=0, padx=5, pady=8, sticky="w")
cbb_xe_var = tk.StringVar()
cbb_xe = ttk.Combobox(frame_info, textvariable=cbb_xe_var, width=28, state='readonly')
cbb_xe.grid(row=1, column=1, padx=5, pady=8, sticky="w")
cbb_xe['values'] = load_xe_combobox()

ttk.Label(frame_info, text="Tài xế đổ:").grid(row=1, column=2, padx=15, pady=8, sticky="w")
cbb_taixe_var = tk.StringVar()
cbb_taixe = ttk.Combobox(frame_info, textvariable=cbb_taixe_var, width=38, state='readonly')
cbb_taixe.grid(row=1, column=3, padx=5, pady=8, sticky="w")
cbb_taixe['values'] = load_taixe_combobox()

# --- Hàng 3 (Thời gian) ---
ttk.Label(frame_info, text="Ngày đổ:").grid(row=2, column=0, padx=5, pady=8, sticky="w")
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
date_ngaydo = DateEntry(frame_info, **date_entry_style_options)
date_ngaydo.grid(row=2, column=1, padx=5, pady=8, sticky="w")

ttk.Label(frame_info, text="Giờ đổ (HH:MM):").grid(row=2, column=2, padx=15, pady=8, sticky="w")
entry_giodo = ttk.Entry(frame_info, width=40)
entry_giodo.grid(row=2, column=3, padx=5, pady=8, sticky="w")

# --- Hàng 4 (Chi phí) ---
ttk.Label(frame_info, text="Số lít:").grid(row=3, column=0, padx=5, pady=8, sticky="w")
entry_solit = ttk.Entry(frame_info, width=30)
entry_solit.grid(row=3, column=1, padx=5, pady=8, sticky="w")

ttk.Label(frame_info, text="Tổng chi phí:").grid(row=3, column=2, padx=15, pady=8, sticky="w")
entry_tongchiphi = ttk.Entry(frame_info, width=40)
entry_tongchiphi.grid(row=3, column=3, padx=5, pady=8, sticky="w")

# --- Hàng 5 (Odo) ---
ttk.Label(frame_info, text="Số Odo (Km):").grid(row=4, column=0, padx=5, pady=8, sticky="w")
entry_soodo = ttk.Entry(frame_info, width=30)
entry_soodo.grid(row=4, column=1, padx=5, pady=8, sticky="w")


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
btn_sua = ttk.Button(frame_btn, text="Sửa", width=8, command=chon_nhienlieu_de_sua) 
btn_sua.grid(row=0, column=2, padx=10)
btn_huy = ttk.Button(frame_btn, text="Hủy", width=8, command=load_data) 
btn_huy.grid(row=0, column=3, padx=10)
btn_xoa = ttk.Button(frame_btn, text="Xóa", width=8, command=xoa_nhienlieu) 
btn_xoa.grid(row=0, column=4, padx=10)
btn_thoat = ttk.Button(frame_btn, text="Thoát", width=8, command=root.quit)
btn_thoat.grid(row=0, column=5, padx=10)


# ===== Bảng danh sách =====
lbl_ds = ttk.Label(root, text="Danh sách nhật ký nhiên liệu (Sắp xếp mới nhất)", style="Header.TLabel")
lbl_ds.pack(pady=(10, 5), padx=20, anchor="w")

frame_tree = ttk.Frame(root, style="TFrame")
frame_tree.pack(pady=10, padx=20, fill="both", expand=True) 

scrollbar_y = ttk.Scrollbar(frame_tree, orient=tk.VERTICAL, style="Vertical.TScrollbar")
scrollbar_x = ttk.Scrollbar(frame_tree, orient=tk.HORIZONTAL, style="Horizontal.TScrollbar")

columns = ("ma_nk", "bienso", "ten_tx", "ngay_do", "so_lit", "tong_cp", "trangthai")
tree = ttk.Treeview(frame_tree, columns=columns, show="headings", height=10,
                    yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)

scrollbar_y.config(command=tree.yview)
scrollbar_x.config(command=tree.xview)

scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)

tree.heading("ma_nk", text="Mã NK")
tree.column("ma_nk", width=60, anchor="center")
tree.heading("bienso", text="Biển số xe")
tree.column("bienso", width=100)
tree.heading("ten_tx", text="Tên Tài xế")
tree.column("ten_tx", width=150)
tree.heading("ngay_do", text="Ngày đổ")
tree.column("ngay_do", width=150)
tree.heading("so_lit", text="Số lít")
tree.column("so_lit", width=80, anchor="e") 
tree.heading("tong_cp", text="Tổng chi phí")
tree.column("tong_cp", width=100, anchor="e") 
tree.heading("trangthai", text="Trạng thái")
tree.column("trangthai", width=100, anchor="center")

tree.pack(fill="both", expand=True)

# THÊM BINDING (SỰ KIỆN CLICK)
tree.bind("<<TreeviewSelect>>", on_item_select) 

# ================================================================
# PHẦN 5: CHẠY ỨNG DỤNG
# ================================================================
load_data() 
root.mainloop()