import tkinter as tk
from tkinter import ttk, messagebox
# Không cần DateEntry
import pyodbc 
from datetime import datetime
import hashlib 

# ================================================================
# BỘ MÀU "LIGHT MODE"
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

# Biến tạm để xử lý Mật khẩu
PASSWORD_PLACEHOLDER = "******"

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
# PHẦN 2: CÁC HÀM TIỆN ÍCH & LOGIC BẢO MẬT
# ================================================================
def hash_password(password):
    """Hàm băm mật khẩu bằng SHA-256."""
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def load_nhanvien_combobox():
    """Tải danh sách TẤT CẢ nhân viên (MaNhanVien - HoVaTen)."""
    conn = connect_db()
    if conn is None: return []
    
    try:
        cur = conn.cursor()
        sql = "SELECT MaNhanVien, HoVaTen FROM NhanVien ORDER BY HoVaTen"
        cur.execute(sql)
        rows = cur.fetchall()
        return [f"{row[0]} - {row[1]}" for row in rows]
    except Exception as e:
        print(f"Lỗi tải combobox nhân viên: {e}")
        return []
    finally:
        if conn: conn.close()

def set_form_state(is_enabled):
    """Bật (enable) hoặc Tắt (disable) các trường ngoại trừ PK."""
    # Trạng thái PK (entry_tendangnhap) được quản lý riêng
    if is_enabled:
        entry_matkhau.config(state='normal')
        cbb_nhanvien.config(state='readonly')
        cbb_vaitro.config(state='readonly')
    else:
        entry_matkhau.config(state='disabled')
        cbb_nhanvien.config(state='disabled')
        cbb_vaitro.config(state='disabled')
        # Khóa luôn trường Tên đăng nhập để tránh chỉnh sửa ngoài ý muốn
        entry_tendangnhap.config(state='disabled')

def clear_input():
    """(NÚT THÊM) Xóa trắng và Mở khóa PK."""
    set_form_state(is_enabled=True)
    
    # Mở khóa Tên đăng nhập
    entry_tendangnhap.config(state='normal')
    entry_tendangnhap.delete(0, tk.END)
    
    entry_matkhau.delete(0, tk.END)
    cbb_nhanvien.set("")
    cbb_vaitro.set("TaiXe") 
    
    entry_tendangnhap.focus()
    if tree.selection():
        tree.selection_remove(tree.selection()[0])

# ================================================================
# PHẦN 3: CÁC HÀM CRUD (CHO TÀI KHOẢN)
# ================================================================

def load_data():
    """Tải TOÀN BỘ dữ liệu Tài khoản VÀ LÀM MỜ FORM."""
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
            tk.TenDangNhap, tk.MaNhanVien, nv.HoVaTen, tk.VaiTro
        FROM TaiKhoan AS tk
        LEFT JOIN NhanVien AS nv ON tk.MaNhanVien = nv.MaNhanVien
        ORDER BY tk.TenDangNhap
        """
        cur.execute(sql)
        rows = cur.fetchall()
        
        for row in rows:
            tendn = row[0]
            manv = row[1]
            hoten = row[2] or "N/A"
            vaitro = row[3]
            
            tree.insert("", tk.END, values=(tendn, manv, hoten, vaitro))
            
        children = tree.get_children()
        if children:
            first_item = children[0]
            tree.selection_set(first_item) 
            tree.focus(first_item)         
            tree.event_generate("<<TreeviewSelect>>") # Kích hoạt on_item_select
        else:
            set_form_state(is_enabled=True)
            clear_input() 
            
    except pyodbc.Error as e:
        messagebox.showerror("Lỗi tải dữ liệu", f"Lỗi SQL: {str(e)}")
    except Exception as e:
        messagebox.showerror("Lỗi không xác định", f"Lỗi: {str(e)}")
    finally:
        if conn: conn.close()
        # LUÔN LUÔN KHÓA FORM VÀ PK SAU KHI TẢI
        set_form_state(is_enabled=False)
        entry_tendangnhap.config(state='disabled')


def them_taikhoan():
    """(LOGIC THÊM) Thêm một tài khoản mới."""
    try:
        tendn = entry_tendangnhap.get()
        matkhau = entry_matkhau.get()
        manv = cbb_nhanvien_var.get().split(' - ')[0]
        vaitro = cbb_vaitro_var.get()

        if not tendn or not matkhau:
            messagebox.showwarning("Thiếu dữ liệu", "Vui lòng nhập Tên đăng nhập và Mật khẩu")
            return False
        
        if matkhau == PASSWORD_PLACEHOLDER:
            messagebox.showwarning("Lỗi mật khẩu", "Vui lòng nhập mật khẩu mới")
            return False

    except Exception as e:
        messagebox.showerror("Lỗi định dạng", f"Dữ liệu nhập không hợp lệ (chưa chọn nhân viên?): {e}")
        return False

    conn = connect_db()
    if conn is None: return False

    try:
        cur = conn.cursor()
        hashed_mk = hash_password(matkhau)
        
        sql = "INSERT INTO TaiKhoan (TenDangNhap, MatKhau, MaNhanVien, VaiTro) VALUES (?, ?, ?, ?)"
        cur.execute(sql, (tendn, hashed_mk, manv, vaitro))
        
        conn.commit()
        messagebox.showinfo("Thành công", "Đã thêm tài khoản mới thành công")
        return True
        
    except pyodbc.IntegrityError as e:
        conn.rollback() 
        if "PRIMARY KEY" in str(e):
             messagebox.showerror("Lỗi Trùng lặp", f"Tên đăng nhập '{tendn}' đã tồn tại.")
        elif "FOREIGN KEY" in str(e):
             messagebox.showerror("Lỗi Trùng lặp", f"Nhân viên '{manv}' có thể đã có tài khoản.")
        else:
             messagebox.showerror("Lỗi SQL", f"Không thể thêm:\n{str(e)}")
        return False
    except Exception as e:
        conn.rollback()
        messagebox.showerror("Lỗi không xác định", f"Lỗi: {str(e)}")
        return False
    finally:
        if conn: conn.close()

def on_item_select(event=None):
    """(SỰ KIỆN CLICK) Lấy thông tin tài khoản và điền vào form (ở chế độ mờ)."""
    selected = tree.selection()
    if not selected: return 

    selected_item = tree.item(selected[0])
    tendn = selected_item['values'][0]
    
    conn = connect_db()
    if conn is None: return

    try:
        cur = conn.cursor()
        sql = "SELECT tk.*, nv.HoVaTen FROM TaiKhoan tk LEFT JOIN NhanVien nv ON tk.MaNhanVien = nv.MaNhanVien WHERE tk.TenDangNhap = ?"
        cur.execute(sql, (tendn,))
        data = cur.fetchone()
        
        if not data:
            messagebox.showerror("Lỗi", "Không tìm thấy dữ liệu tài khoản.")
            return

        # Tạm thời MỞ KHÓA form để đổ dữ liệu
        set_form_state(is_enabled=True)
        entry_tendangnhap.config(state='normal')
        
        # Xóa và Đổ dữ liệu
        entry_tendangnhap.delete(0, tk.END)
        entry_matkhau.delete(0, tk.END)
        cbb_nhanvien.set("")
        
        entry_tendangnhap.insert(0, data.TenDangNhap)
        
        # Đặt mật khẩu placeholder
        entry_matkhau.insert(0, PASSWORD_PLACEHOLDER)
        
        if data.MaNhanVien:
            cbb_nhanvien_val = f"{data.MaNhanVien} - {data.HoVaTen}"
            cbb_nhanvien.set(cbb_nhanvien_val)
        
        cbb_vaitro.set(data.VaiTro or "TaiXe")

    except pyodbc.Error as e:
        messagebox.showerror("Lỗi SQL", f"Không thể lấy dữ liệu:\n{str(e)}")
    except Exception as e:
        messagebox.showerror("Lỗi không xác định", f"Lỗi: {str(e)}")
    finally:
        if conn: conn.close()
        # KHÓA LẠI FORM SAU KHI ĐỔ DỮ LIỆU
        entry_tendangnhap.config(state='disabled') # PK luôn khóa
        set_form_state(is_enabled=False)


def chon_taikhoan_de_sua(event=None): 
    """(NÚT SỬA) Kích hoạt chế độ sửa, Mở khóa các ô nhập liệu (trừ Tên đăng nhập)."""
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Chưa chọn", "Hãy chọn một tài khoản trong danh sách trước khi nhấn 'Sửa'")
        return

    # Kiểm tra xem PK đã được điền và khóa (tức là đã ở chế độ xem)
    if not entry_tendangnhap.get():
         messagebox.showwarning("Lỗi", "Không tìm thấy Tên đăng nhập. Vui lòng chọn lại.")
         return

    # Mở khóa các ô nhập liệu khác
    set_form_state(is_enabled=True)
    entry_tendangnhap.config(state='disabled') # Giữ PK khóa
    entry_matkhau.focus() 

def luu_taikhoan_da_sua():
    """(LOGIC SỬA) Lưu thay đổi (UPDATE) sau khi sửa."""
    tendn = entry_tendangnhap.get()
    if not tendn:
        messagebox.showwarning("Thiếu dữ liệu", "Không có Tên đăng nhập để cập nhật")
        return False

    try:
        matkhau_moi = entry_matkhau.get()
        manv = cbb_nhanvien_var.get().split(' - ')[0]
        vaitro = cbb_vaitro_var.get()
    except Exception as e:
        messagebox.showerror("Lỗi định dạng", f"Dữ liệu nhập không hợp lệ (chưa chọn nhân viên?): {e}")
        return False

    conn = connect_db()
    if conn is None: return False
        
    try:
        cur = conn.cursor()
        
        # CÓ cập nhật mật khẩu
        if matkhau_moi != PASSWORD_PLACEHOLDER and matkhau_moi:
            hashed_mk_moi = hash_password(matkhau_moi)
            sql = "UPDATE TaiKhoan SET MatKhau = ?, MaNhanVien = ?, VaiTro = ? WHERE TenDangNhap = ?"
            cur.execute(sql, (hashed_mk_moi, manv, vaitro, tendn))
        # KHÔNG cập nhật mật khẩu
        else: 
            sql = "UPDATE TaiKhoan SET MaNhanVien = ?, VaiTro = ? WHERE TenDangNhap = ?"
            cur.execute(sql, (manv, vaitro, tendn))
        
        conn.commit()
        messagebox.showinfo("Thành công", "Đã cập nhật tài khoản")
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
    # Nếu Tên đăng nhập bị khóa (state='disabled') -> Sửa
    if entry_tendangnhap.cget('state') == 'disabled' and entry_tendangnhap.get():
        success = luu_taikhoan_da_sua()
    # Nếu Tên đăng nhập đang mở (state='normal') -> Thêm
    else:
        success = them_taikhoan()
    
    if success:
        load_data()

def xoa_taikhoan():
    """Xóa tài khoản được chọn."""
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Chưa chọn", "Hãy chọn một tài khoản để xóa")
        return

    # Lấy PK từ ô nhập liệu (đã được điền bởi on_item_select)
    tendn = entry_tendangnhap.get() 
    
    if not tendn:
        messagebox.showwarning("Lỗi", "Không tìm thấy Tên đăng nhập. Vui lòng chọn lại.")
        return

    if not messagebox.askyesno("Xác nhận", f"Bạn có chắc chắn muốn xóa tài khoản '{tendn}'?"):
        return

    conn = connect_db()
    if conn is None: return
        
    try:
        cur = conn.cursor()
        cur.execute("DELETE FROM TaiKhoan WHERE TenDangNhap=?", (tendn,))
        conn.commit()
        
        messagebox.showinfo("Thành công", "Đã xóa tài khoản thành công")
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
root.title("Quản lý Tài khoản (Database QL_VanTai)")
root.config(bg=theme_colors["bg_main"]) 

def center_window(w, h):
    """Hàm căn giữa cửa sổ."""
    ws = root.winfo_screenwidth()
    hs = root.winfo_screenheight()
    x = (ws/2) - (w/2)
    y = (hs/2) - (h/2)
    root.geometry('%dx%d+%d+%d' % (w, h, x, y))

center_window(900, 600) 
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


lbl_title = ttk.Label(root, text="QUẢN LÝ TÀI KHOẢN", style="Title.TLabel")
lbl_title.pack(pady=15) 

# Frame thông tin
frame_info = ttk.Frame(root, style="TFrame")
frame_info.pack(pady=5, padx=20, fill="x")

# --- Hàng 1 ---
ttk.Label(frame_info, text="Tên đăng nhập:").grid(row=0, column=0, padx=5, pady=8, sticky="w")
entry_tendangnhap = ttk.Entry(frame_info, width=30)
entry_tendangnhap.grid(row=0, column=1, padx=5, pady=8, sticky="w")

ttk.Label(frame_info, text="Mật khẩu:").grid(row=0, column=2, padx=15, pady=8, sticky="w")
entry_matkhau = ttk.Entry(frame_info, width=30, show="*") # Giữ show="*"
entry_matkhau.grid(row=0, column=3, padx=5, pady=8, sticky="w")

# --- Hàng 2 ---
ttk.Label(frame_info, text="Nhân viên:").grid(row=1, column=0, padx=5, pady=8, sticky="w")
cbb_nhanvien_var = tk.StringVar()
cbb_nhanvien = ttk.Combobox(frame_info, textvariable=cbb_nhanvien_var, width=28, state='readonly')
cbb_nhanvien.grid(row=1, column=1, padx=5, pady=8, sticky="w")
cbb_nhanvien['values'] = load_nhanvien_combobox()

ttk.Label(frame_info, text="Vai trò:").grid(row=1, column=2, padx=15, pady=8, sticky="w")
vaitro_options = ["Admin", "TaiXe"]
cbb_vaitro_var = tk.StringVar()
cbb_vaitro = ttk.Combobox(frame_info, textvariable=cbb_vaitro_var, values=vaitro_options, width=28, state='readonly')
cbb_vaitro.grid(row=1, column=3, padx=5, pady=8, sticky="w")
cbb_vaitro.set("TaiXe")

# Cấu hình grid co giãn
frame_info.columnconfigure(1, weight=1)
frame_info.columnconfigure(3, weight=1)

# ===== Frame nút (Đã cập nhật command) =====
frame_btn = ttk.Frame(root, style="TFrame")
frame_btn.pack(pady=15)

btn_them = ttk.Button(frame_btn, text="Thêm", width=8, command=clear_input)
btn_them.grid(row=0, column=0, padx=10)

btn_luu = ttk.Button(frame_btn, text="Lưu", width=8, command=save_data) # SỬ DỤNG HÀM MỚI
btn_luu.grid(row=0, column=1, padx=10)

btn_sua = ttk.Button(frame_btn, text="Sửa", width=8, command=chon_taikhoan_de_sua) 
btn_sua.grid(row=0, column=2, padx=10)

btn_huy = ttk.Button(frame_btn, text="Hủy", width=8, command=load_data) # HỦY là tải lại dữ liệu
btn_huy.grid(row=0, column=3, padx=10)

btn_xoa = ttk.Button(frame_btn, text="Xóa", width=8, command=xoa_taikhoan)
btn_xoa.grid(row=0, column=4, padx=10)

btn_thoat = ttk.Button(frame_btn, text="Thoát", width=8, command=root.quit)
btn_thoat.grid(row=0, column=5, padx=10)


# ===== Bảng danh sách =====
lbl_ds = ttk.Label(root, text="Danh sách tài khoản (Không hiển thị mật khẩu)", style="Header.TLabel")
lbl_ds.pack(pady=(10, 5), padx=20, anchor="w")

frame_tree = ttk.Frame(root, style="TFrame")
frame_tree.pack(pady=10, padx=20, fill="both", expand=True)

scrollbar_y = ttk.Scrollbar(frame_tree, orient=tk.VERTICAL, style="Vertical.TScrollbar")
scrollbar_x = ttk.Scrollbar(frame_tree, orient=tk.HORIZONTAL, style="Horizontal.TScrollbar")

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

# THÊM BINDING (SỰ KIỆN CLICK)
tree.bind("<<TreeviewSelect>>", on_item_select) 

# ================================================================
# PHẦN 5: CHẠY ỨNG DỤNG
# ================================================================
load_data() 
root.mainloop()