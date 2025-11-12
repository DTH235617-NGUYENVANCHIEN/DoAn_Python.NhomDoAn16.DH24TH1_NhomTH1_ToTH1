import tkinter as tk
from tkinter import ttk, messagebox
import pyodbc 

# ================================================================
# BỘ MÀU "LIGHT MODE" MỚI
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
# PHẦN 2: CÁC HÀM CRUD (Giữ nguyên logic)
# ================================================================

def set_form_state(is_enabled):
    """Bật (enable) hoặc Tắt (disable) toàn bộ các trường nhập liệu."""
    if is_enabled:
        entry_hoten.config(state='normal')
        entry_sdt.config(state='normal')
        entry_diachi.config(state='normal')
        cbb_trangthai_nv.config(state='readonly')
    else:
        entry_manv.config(state='disabled')
        entry_hoten.config(state='disabled')
        entry_sdt.config(state='disabled')
        entry_diachi.config(state='disabled')
        cbb_trangthai_nv.config(state='disabled')

def clear_input():
    """(NÚT THÊM) Xóa trắng và Mở khóa các trường nhập liệu (Chế độ Thêm mới)."""
    set_form_state(is_enabled=True)
    entry_manv.config(state='normal') 
    entry_manv.delete(0, tk.END)
    entry_hoten.delete(0, tk.END)
    entry_sdt.delete(0, tk.END)
    entry_diachi.delete(0, tk.END)
    cbb_trangthai_nv.set("Đang làm việc")
    entry_manv.focus()
    if tree.selection():
        tree.selection_remove(tree.selection()[0])

def load_data():
    """Tải TOÀN BỘ dữ liệu từ NhanVien VÀ LÀM MỜ FORM."""
    for i in tree.get_children():
        tree.delete(i)
        
    conn = connect_db()
    if conn is None:
        set_form_state(is_enabled=False) 
        return
        
    try:
        cur = conn.cursor()
        sql = "SELECT MaNhanVien, HoVaTen, SoDienThoai, DiaChi, TrangThai FROM NhanVien"
        cur.execute(sql)
        rows = cur.fetchall()
        
        for row in rows:
            trang_thai_nv_text = "Đang làm việc" if row[4] == 1 else "Nghỉ"
            tree.insert("", tk.END, values=(
                row[0], row[1], row[2], row[3], trang_thai_nv_text
            ))
        
        children = tree.get_children()
        if children:
            first_item = children[0]
            tree.selection_set(first_item) 
            tree.focus(first_item)         
            tree.event_generate("<<TreeviewSelect>>") 
        else:
            entry_manv.config(state='normal')
            set_form_state(is_enabled=True)
            entry_manv.delete(0, tk.END)
            entry_hoten.delete(0, tk.END)
            entry_sdt.delete(0, tk.END)
            entry_diachi.delete(0, tk.END)
            cbb_trangthai_nv.set("Đang làm việc")
            
    except pyodbc.Error as e:
        messagebox.showerror("Lỗi tải dữ liệu", f"Lỗi SQL: {str(e)}")
    except Exception as e:
        messagebox.showerror("Lỗi không xác định", f"Lỗi: {str(e)}")
    finally:
        if conn:
            conn.close()
        set_form_state(is_enabled=False)

def them_nhanvien():
    """(LOGIC THÊM) Thêm một nhân viên mới (chỉ vào bảng NhanVien)."""
    manv = entry_manv.get()
    hoten = entry_hoten.get()
    sdt = entry_sdt.get()
    diachi = entry_diachi.get()
    
    trangthai_nv_text = cbb_trangthai_nv_var.get()
    trangthai_nv_value = 1 if trangthai_nv_text == "Đang làm việc" else 0

    if not manv or not hoten:
        messagebox.showwarning("Thiếu dữ liệu", "Vui lòng nhập Mã Nhân Viên và Họ Tên")
        return False

    conn = connect_db()
    if conn is None: return False

    try:
        cur = conn.cursor()
        sql_nhanvien = """
        INSERT INTO NhanVien (MaNhanVien, HoVaTen, SoDienThoai, DiaChi, TrangThai) 
        VALUES (?, ?, ?, ?, ?)
        """
        cur.execute(sql_nhanvien, (manv, hoten, sdt, diachi, trangthai_nv_value))
        conn.commit()
        messagebox.showinfo("Thành công", "Đã thêm nhân viên mới thành công.")
        return True
        
    except pyodbc.IntegrityError:
        messagebox.showerror("Lỗi Trùng lặp", f"Mã nhân viên '{manv}' đã tồn tại.")
        return False
    except pyodbc.Error as e:
        conn.rollback() 
        messagebox.showerror("Lỗi SQL", f"Không thể thêm nhân viên:\n{str(e)}")
        return False
    except Exception as e:
        conn.rollback()
        messagebox.showerror("Lỗi không xác định", f"Lỗi: {str(e)}")
        return False
    finally:
        if conn: conn.close()

def on_item_select(event=None):
    """(SỰ KIỆN CLICK) Khi click vào Treeview, chỉ đổ dữ liệu lên form (ở trạng thái mờ)."""
    selected = tree.selection()
    if not selected: return 

    selected_item = tree.item(selected[0])
    manv = selected_item['values'][0]
    
    conn = connect_db()
    if conn is None: return

    try:
        cur = conn.cursor()
        sql = "SELECT * FROM NhanVien WHERE MaNhanVien = ?"
        cur.execute(sql, (manv,))
        data = cur.fetchone()
        
        if not data:
            messagebox.showerror("Lỗi", "Không tìm thấy dữ liệu nhân viên.")
            return

        set_form_state(is_enabled=True)
        entry_manv.config(state='normal')
        
        entry_manv.delete(0, tk.END)
        entry_hoten.delete(0, tk.END)
        entry_sdt.delete(0, tk.END)
        entry_diachi.delete(0, tk.END)
        
        entry_manv.insert(0, data.MaNhanVien)
        entry_hoten.insert(0, data.HoVaTen or "")
        entry_sdt.insert(0, data.SoDienThoai or "")
        entry_diachi.insert(0, data.DiaChi or "")
        cbb_trangthai_nv.set("Đang làm việc" if data.TrangThai == 1 else "Nghỉ")

    except pyodbc.Error as e:
        messagebox.showerror("Lỗi SQL", f"Không thể lấy dữ liệu:\n{str(e)}")
    except Exception as e:
        messagebox.showerror("Lỗi không xác định", f"Lỗi: {str(e)}")
    finally:
        if conn: conn.close()
        set_form_state(is_enabled=False)

def chon_nhanvien_de_sua(event=None): 
    """(NÚT SỬA) Kích hoạt chế độ sửa, Mở khóa form (trừ MaNV)."""
    # Sửa logic kiểm tra: Dựa vào treeview selection
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Chưa chọn", "Hãy chọn một nhân viên trong danh sách trước khi nhấn 'Sửa'")
        return

    # Kiểm tra lại xem ô MaNV có rỗng không (phòng trường hợp)
    if not entry_manv.get():
         messagebox.showwarning("Lỗi", "Không tìm thấy mã nhân viên. Vui lòng chọn lại.")
         return

    set_form_state(is_enabled=True)
    entry_manv.config(state='disabled') 
    entry_hoten.focus() 

def luu_nhanvien_da_sua():
    """(LOGIC SỬA) Lưu thay đổi (UPDATE) sau khi sửa (chỉ bảng NhanVien)."""
    manv = entry_manv.get()
    if not manv:
        messagebox.showwarning("Thiếu dữ liệu", "Không có Mã Nhân Viên để cập nhật")
        return False

    hoten = entry_hoten.get()
    sdt = entry_sdt.get()
    diachi = entry_diachi.get()

    trangthai_nv_text = cbb_trangthai_nv_var.get()
    trangthai_nv_value = 1 if trangthai_nv_text == "Đang làm việc" else 0

    conn = connect_db()
    if conn is None: return False
        
    try:
        cur = conn.cursor()
        sql_nhanvien = """
        UPDATE NhanVien SET 
            HoVaTen = ?, SoDienThoai = ?, DiaChi = ?, TrangThai = ?
        WHERE MaNhanVien = ?
        """
        cur.execute(sql_nhanvien, (hoten, sdt, diachi, trangthai_nv_value, manv))
        conn.commit()
        messagebox.showinfo("Thành công", "Đã cập nhật thông tin nhân viên")
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
    if entry_manv.cget('state') == 'disabled':
        success = luu_nhanvien_da_sua()
    else:
        success = them_nhanvien()
    
    if success:
        load_data()

def xoa_nhanvien_vinhvien():
    """(NGUY HIỂM) Xóa vĩnh viễn nhân viên và MỌI DỮ LIỆU LIÊN QUAN."""
    # Sửa logic kiểm tra: Dựa vào treeview selection
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Chưa chọn", "Hãy chọn một nhân viên trong danh sách để xóa")
        return
        
    manv = entry_manv.get() # Lấy manv từ ô entry (đã được điền)

    msg_xacnhan = (
        f"BẠN CÓ CHẮC CHẮN MUỐN XÓA VĨNH VIỄN NHÂN VIÊN '{manv}'?\n\n"
        "CẢNH BÁO: Thao tác này KHÔNG THỂ hoàn tác.\n"
        "Tất cả dữ liệu liên quan (chuyến đi, nhiên liệu, tài khoản,...) sẽ bị XÓA SẠCH."
    )
    if not messagebox.askyesno("XÁC NHẬN XÓA VĨNH VIỄN", msg_xacnhan):
        return

    conn = connect_db()
    if conn is None: return
        
    try:
        cur = conn.cursor()
        
        cur.execute("DELETE FROM NhatKyNhienLieu WHERE MaNhanVien=?", (manv,))
        cur.execute("DELETE FROM ChuyenDi WHERE MaNhanVien=?", (manv,))
        cur.execute("DELETE FROM TaiKhoan WHERE MaNhanVien=?", (manv,))
        cur.execute("DELETE FROM TaiXe WHERE MaNhanVien=?", (manv,))
        cur.execute("UPDATE Xe SET MaNhanVienHienTai = NULL WHERE MaNhanVienHienTai = ?", (manv,))
        cur.execute("DELETE FROM NhanVien WHERE MaNhanVien=?", (manv,))
        
        conn.commit()
        messagebox.showinfo("Thành công", f"Đã xóa vĩnh viễn nhân viên '{manv}' và tất cả dữ liệu liên quan.")
        load_data()
        
    except pyodbc.Error as e:
        conn.rollback()
        messagebox.showerror("Lỗi SQL", f"Không thể xóa nhân viên:\n{str(e)}")
    except Exception as e:
        conn.rollback()
        messagebox.showerror("Lỗi không xác định", f"Lỗi: {str(e)}")
    finally:
        if conn: conn.close()

# ================================================================
# PHẦN 3: THIẾT KẾ GIAO DIỆN (Bản Light Mode)
# ================================================================

root = tk.Tk()
root.title("Quản lý Toàn Bộ Nhân Viên (Database QL_VanTai)")
root.config(bg=theme_colors["bg_main"]) # Nền chính

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
    bordercolor="#ACACAC", # Màu viền xám
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
# --- Entry và Combobox (Trường nhập liệu) ---
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
    background=[('selected', theme_colors["accent"])], # Màu khi chọn
    foreground=[('selected', theme_colors["accent_text"])] # Chữ khi chọn
)
# Tiêu đề cột
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
    background=[('active', "#C0C0C0")] # Màu xám nhạt khi active
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


lbl_title = ttk.Label(root, text="QUẢN LÝ TOÀN BỘ NHÂN VIÊN", style="Title.TLabel")
lbl_title.pack(pady=15) 

frame_info = ttk.Frame(root, style="TFrame")
frame_info.pack(pady=10, padx=20, fill="x")

ttk.Label(frame_info, text="Mã nhân viên:").grid(row=0, column=0, padx=5, pady=8, sticky="w")
entry_manv = ttk.Entry(frame_info, width=30)
entry_manv.grid(row=0, column=1, padx=5, pady=8, sticky="w")

ttk.Label(frame_info, text="Họ và tên:").grid(row=1, column=0, padx=5, pady=8, sticky="w")
entry_hoten = ttk.Entry(frame_info, width=30)
entry_hoten.grid(row=1, column=1, padx=5, pady=8, sticky="w")

ttk.Label(frame_info, text="Số điện thoại:").grid(row=2, column=0, padx=5, pady=8, sticky="w")
entry_sdt = ttk.Entry(frame_info, width=30)
entry_sdt.grid(row=2, column=1, padx=5, pady=8, sticky="w")

ttk.Label(frame_info, text="Địa chỉ:").grid(row=0, column=2, padx=15, pady=8, sticky="w")
entry_diachi = ttk.Entry(frame_info, width=40)
entry_diachi.grid(row=0, column=3, padx=5, pady=8, sticky="w")

ttk.Label(frame_info, text="Trạng thái NV:").grid(row=1, column=2, padx=15, pady=8, sticky="w")
trangthai_nv_options = ["Nghỉ", "Đang làm việc"]
cbb_trangthai_nv_var = tk.StringVar()
cbb_trangthai_nv = ttk.Combobox(frame_info, textvariable=cbb_trangthai_nv_var, values=trangthai_nv_options, width=38, state='readonly')
cbb_trangthai_nv.grid(row=1, column=3, padx=5, pady=8, sticky="w")
cbb_trangthai_nv.set("Đang làm việc") 

frame_info.columnconfigure(1, weight=1)
frame_info.columnconfigure(3, weight=1)

# ===== Frame nút =====
frame_btn = ttk.Frame(root, style="TFrame")
frame_btn.pack(pady=10)

btn_them = ttk.Button(frame_btn, text="Thêm", width=8, command=clear_input) 
btn_them.grid(row=0, column=0, padx=10)
btn_luu = ttk.Button(frame_btn, text="Lưu", width=8, command=save_data) 
btn_luu.grid(row=0, column=1, padx=10)
btn_sua = ttk.Button(frame_btn, text="Sửa", width=8, command=chon_nhanvien_de_sua) 
btn_sua.grid(row=0, column=2, padx=10)
btn_huy = ttk.Button(frame_btn, text="Hủy", width=8, command=load_data) 
btn_huy.grid(row=0, column=3, padx=10)
btn_xoa = ttk.Button(frame_btn, text="Xóa", width=8, command=xoa_nhanvien_vinhvien) 
btn_xoa.grid(row=0, column=4, padx=10)
btn_thoat = ttk.Button(frame_btn, text="Thoát", width=8, command=root.quit)
btn_thoat.grid(row=0, column=5, padx=10)


# ===== Bảng danh sách tài xế =====
lbl_ds = ttk.Label(root, text="Danh sách nhân viên (Tất cả)", style="Header.TLabel")
lbl_ds.pack(pady=(10, 5), padx=20, anchor="w")

frame_tree = ttk.Frame(root, style="TFrame")
frame_tree.pack(pady=10, padx=20, fill="both", expand=True) 

scrollbar_y = ttk.Scrollbar(frame_tree, orient=tk.VERTICAL, style="Vertical.TScrollbar")
scrollbar_x = ttk.Scrollbar(frame_tree, orient=tk.HORIZONTAL, style="Horizontal.TScrollbar")

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

tree.bind("<<TreeviewSelect>>", on_item_select) 

# ================================================================
# PHẦN 4: CHẠY ỨNG DỤNG
# ================================================================
load_data() 
root.mainloop()