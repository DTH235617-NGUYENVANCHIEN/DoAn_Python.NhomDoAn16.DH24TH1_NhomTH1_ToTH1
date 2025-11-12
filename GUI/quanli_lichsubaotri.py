import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
import pyodbc 
from datetime import datetime
import datetime as dt

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
def load_xe_combobox():
    """Tải danh sách TẤT CẢ xe (BienSoXe) vào Combobox."""
    conn = connect_db()
    if conn is None: return []
    
    try:
        cur = conn.cursor()
        sql = "SELECT BienSoXe FROM Xe ORDER BY BienSoXe"
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
    # MaBaoTri luôn disabled
    entry_mabaotri.config(state='disabled')
    
    if is_enabled:
        # Chế độ Bật
        cbb_xe.config(state='readonly')
        date_ngaybaotri.config(state='normal')
        entry_chiphi.config(state='normal')
        # Style đặc biệt cho tk.Text
        entry_mota.config(state='normal', bg=theme_colors["bg_entry"], fg=theme_colors["text"])
    else:
        # Chế độ Tắt (Làm mờ)
        cbb_xe.config(state='disabled')
        date_ngaybaotri.config(state='disabled')
        entry_chiphi.config(state='disabled')
        # Style đặc biệt cho tk.Text
        entry_mota.config(state='disabled', bg=theme_colors["disabled_bg"], fg=theme_colors["text_disabled"])

def clear_input():
    """(NÚT THÊM) Xóa trắng và Mở khóa các trường nhập liệu (Chế độ Thêm mới)."""
    set_form_state(is_enabled=True)
    
    entry_mabaotri.config(state='normal')
    entry_mabaotri.delete(0, tk.END)
    entry_mabaotri.config(state='disabled')
    
    cbb_xe.set("")
    entry_chiphi.delete(0, tk.END)
    entry_mota.delete("1.0", tk.END) 
    
    date_ngaybaotri.set_date(datetime.now().strftime("%Y-%m-%d"))
    
    cbb_xe.focus()
    if tree.selection():
        tree.selection_remove(tree.selection()[0])

def load_data():
    """Tải TOÀN BỘ dữ liệu Bảo trì VÀ LÀM MỜ FORM."""
    for i in tree.get_children():
        tree.delete(i)
        
    conn = connect_db()
    if conn is None:
        set_form_state(is_enabled=False) 
        return
        
    try:
        cur = conn.cursor()
        sql = "SELECT MaBaoTri, BienSoXe, NgayBaoTri, ChiPhi, MoTa FROM LichSuBaoTri ORDER BY NgayBaoTri DESC"
        cur.execute(sql)
        rows = cur.fetchall()
        
        for row in rows:
            ma_bt = row[0]
            bienso = row[1]
            ngay_bt = str(row[2]) if row[2] else "N/A" # Giữ nguyên fix lỗi
            chiphi = row[3]
            mota = (row[4] or "")[:50] + "..." # Rút gọn
            
            tree.insert("", tk.END, values=(ma_bt, bienso, ngay_bt, chiphi, mota))
            
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

def them_baotri():
    """(LOGIC THÊM) Thêm một lịch sử bảo trì mới."""
    try:
        bienso = cbb_xe_var.get()
        ngay_bt = date_ngaybaotri.get_date().strftime('%Y-%m-%d')
        mota = entry_mota.get("1.0", tk.END).strip()
        chiphi = entry_chiphi.get()

        if not bienso or not ngay_bt:
            messagebox.showwarning("Thiếu dữ liệu", "Vui lòng nhập Xe và Ngày bảo trì")
            return False

        chiphi_dec = float(chiphi) if chiphi else 0.0

    except Exception as e:
        messagebox.showerror("Lỗi định dạng", f"Chi phí không hợp lệ: {e}")
        return False

    conn = connect_db()
    if conn is None: return False

    try:
        cur = conn.cursor()
        sql = "INSERT INTO LichSuBaoTri (BienSoXe, NgayBaoTri, MoTa, ChiPhi) VALUES (?, ?, ?, ?)"
        cur.execute(sql, (bienso, ngay_bt, mota, chiphi_dec))
        conn.commit()
        messagebox.showinfo("Thành công", "Đã thêm lịch sử bảo trì thành công")
        return True
        
    except pyodbc.Error as e:
        conn.rollback() 
        messagebox.showerror("Lỗi SQL", f"Không thể thêm:\n{str(e)}")
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
    mabaotri = selected_item['values'][0]
    
    conn = connect_db()
    if conn is None: return

    try:
        cur = conn.cursor()
        sql = "SELECT * FROM LichSuBaoTri WHERE MaBaoTri = ?"
        cur.execute(sql, (mabaotri,))
        data = cur.fetchone()
        
        if not data:
            messagebox.showerror("Lỗi", "Không tìm thấy dữ liệu.")
            return

        # Tạm thời MỞ KHÓA form để đổ dữ liệu
        set_form_state(is_enabled=True)
        entry_mabaotri.config(state='normal')
        
        # Xóa và Đổ dữ liệu
        entry_mabaotri.delete(0, tk.END)
        cbb_xe.set("")
        entry_chiphi.delete(0, tk.END)
        entry_mota.delete("1.0", tk.END)
        
        entry_mabaotri.insert(0, data.MaBaoTri)
        cbb_xe.set(data.BienSoXe or "")
        
        if data.NgayBaoTri:
            date_ngaybaotri.set_date(str(data.NgayBaoTri)) # Giữ nguyên fix lỗi
            
        entry_chiphi.insert(0, str(data.ChiPhi or ""))
        entry_mota.insert("1.0", data.MoTa or "")

    except pyodbc.Error as e:
        messagebox.showerror("Lỗi SQL", f"Không thể lấy dữ liệu:\n{str(e)}")
    except Exception as e:
        messagebox.showerror("Lỗi không xác định", f"Lỗi: {str(e)}")
    finally:
        if conn: conn.close()
        # KHÓA LẠI FORM sau khi đổ dữ liệu
        entry_mabaotri.config(state='disabled') # PK luôn khóa
        set_form_state(is_enabled=False)

def chon_baotri_de_sua(event=None): 
    """(NÚT SỬA) Kích hoạt chế độ sửa, Mở khóa form (trừ MaBaoTri)."""
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Chưa chọn", "Hãy chọn một mục trong danh sách trước khi nhấn 'Sửa'")
        return

    if not entry_mabaotri.get():
         messagebox.showwarning("Lỗi", "Không tìm thấy mã bảo trì. Vui lòng chọn lại.")
         return

    set_form_state(is_enabled=True)
    entry_mabaotri.config(state='disabled') # PK luôn khóa
    cbb_xe.focus() 

def luu_baotri_da_sua():
    """(LOGIC SỬA) Lưu thay đổi (UPDATE) sau khi sửa."""
    mabaotri = entry_mabaotri.get()
    if not mabaotri:
        messagebox.showwarning("Thiếu dữ liệu", "Không có Mã bảo trì để cập nhật")
        return False

    try:
        bienso = cbb_xe_var.get()
        ngay_bt = date_ngaybaotri.get_date().strftime('%Y-%m-%d')
        mota = entry_mota.get("1.0", tk.END).strip()
        chiphi = entry_chiphi.get()
        
        if not bienso or not ngay_bt:
            messagebox.showwarning("Thiếu dữ liệu", "Xe và Ngày bảo trì không được rỗng")
            return False

        chiphi_dec = float(chiphi) if chiphi else 0.0

    except Exception as e:
        messagebox.showerror("Lỗi định dạng", f"Chi phí không hợp lệ: {e}")
        return False

    conn = connect_db()
    if conn is None: return False
        
    try:
        cur = conn.cursor()
        sql = """
        UPDATE LichSuBaoTri SET 
            BienSoXe = ?, NgayBaoTri = ?, MoTa = ?, ChiPhi = ?
        WHERE MaBaoTri = ?
        """
        cur.execute(sql, (bienso, ngay_bt, mota, chiphi_dec, mabaotri))
        conn.commit()
        messagebox.showinfo("Thành công", "Đã cập nhật lịch sử bảo trì")
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
    if entry_mabaotri.get():
        success = luu_baotri_da_sua()
    else:
        success = them_baotri()
    
    if success:
        load_data()

def xoa_baotri():
    """Xóa lịch sử bảo trì được chọn."""
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Chưa chọn", "Hãy chọn một mục để xóa")
        return
        
    mabaotri = entry_mabaotri.get() # Lấy mã từ ô entry

    if not mabaotri:
        messagebox.showwarning("Lỗi", "Không tìm thấy mã bảo trì. Vui lòng chọn lại.")
        return

    if not messagebox.askyesno("Xác nhận", f"Bạn có chắc chắn muốn xóa Lịch sử Mã: {mabaotri}?"):
        return

    conn = connect_db()
    if conn is None: return
        
    try:
        cur = conn.cursor()
        cur.execute("DELETE FROM LichSuBaoTri WHERE MaBaoTri=?", (mabaotri,))
        conn.commit()
        
        messagebox.showinfo("Thành công", "Đã xóa lịch sử bảo trì thành công")
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
root.title("Quản lý Lịch sử Bảo trì (Database QL_VanTai)")
root.config(bg=theme_colors["bg_main"]) 

def center_window(w, h):
    """Hàm căn giữa cửa sổ."""
    ws = root.winfo_screenwidth()
    hs = root.winfo_screenheight()
    x = (ws/2) - (w/2)
    y = (hs/2) - (h/2)
    root.geometry('%dx%d+%d+%d' % (w, h, x, y))

center_window(950, 650) 
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


lbl_title = ttk.Label(root, text="QUẢN LÝ LỊCH SỬ BẢO TRÌ", style="Title.TLabel")
lbl_title.pack(pady=15) 

# Frame thông tin
frame_info = ttk.Frame(root, style="TFrame")
frame_info.pack(pady=5, padx=20, fill="x")

# --- Hàng 1 ---
ttk.Label(frame_info, text="Mã bảo trì:").grid(row=0, column=0, padx=5, pady=8, sticky="w")
entry_mabaotri = ttk.Entry(frame_info, width=30, state='disabled')
entry_mabaotri.grid(row=0, column=1, padx=5, pady=8, sticky="w")

ttk.Label(frame_info, text="Ngày bảo trì:").grid(row=0, column=2, padx=15, pady=8, sticky="w")
# Style DateEntry
date_entry_style_options = {
    'width': 38, 'date_pattern': 'yyyy-MM-dd',
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
date_ngaybaotri = DateEntry(frame_info, **date_entry_style_options)
date_ngaybaotri.grid(row=0, column=3, padx=5, pady=8, sticky="w")

# --- Hàng 2 ---
ttk.Label(frame_info, text="Xe:").grid(row=1, column=0, padx=5, pady=8, sticky="w")
cbb_xe_var = tk.StringVar()
cbb_xe = ttk.Combobox(frame_info, textvariable=cbb_xe_var, width=28, state='readonly')
cbb_xe.grid(row=1, column=1, padx=5, pady=8, sticky="w")
cbb_xe['values'] = load_xe_combobox()

ttk.Label(frame_info, text="Chi phí:").grid(row=1, column=2, padx=15, pady=8, sticky="w")
entry_chiphi = ttk.Entry(frame_info, width=40)
entry_chiphi.grid(row=1, column=3, padx=5, pady=8, sticky="w")

# --- Hàng 3 (Mô tả) ---
ttk.Label(frame_info, text="Mô tả công việc:").grid(row=2, column=0, padx=5, pady=8, sticky="nw")
# Dùng Text widget (style thủ công)
entry_mota = tk.Text(frame_info, width=60, height=4, 
    font=("Segoe UI", 10),
    bg=theme_colors["bg_entry"],
    fg=theme_colors["text"],
    relief="solid",
    borderwidth=1,
    insertbackground=theme_colors["text"],
    highlightthickness=1, # Viền khi không focus
    highlightbackground="#ACACAC",
    highlightcolor=theme_colors["accent"] # Viền khi focus
)
entry_mota.grid(row=2, column=1, columnspan=3, padx=5, pady=8, sticky="w")

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
btn_sua = ttk.Button(frame_btn, text="Sửa", width=8, command=chon_baotri_de_sua) 
btn_sua.grid(row=0, column=2, padx=10)
btn_huy = ttk.Button(frame_btn, text="Hủy", width=8, command=load_data) 
btn_huy.grid(row=0, column=3, padx=10)
btn_xoa = ttk.Button(frame_btn, text="Xóa", width=8, command=xoa_baotri) 
btn_xoa.grid(row=0, column=4, padx=10)
btn_thoat = ttk.Button(frame_btn, text="Thoát", width=8, command=root.quit)
btn_thoat.grid(row=0, column=5, padx=10)


# ===== Bảng danh sách =====
lbl_ds = ttk.Label(root, text="Danh sách bảo trì (Sắp xếp mới nhất)", style="Header.TLabel")
lbl_ds.pack(pady=(10, 5), padx=20, anchor="w")

frame_tree = ttk.Frame(root, style="TFrame")
frame_tree.pack(pady=10, padx=20, fill="both", expand=True) 

scrollbar_y = ttk.Scrollbar(frame_tree, orient=tk.VERTICAL, style="Vertical.TScrollbar")
scrollbar_x = ttk.Scrollbar(frame_tree, orient=tk.HORIZONTAL, style="Horizontal.TScrollbar")

columns = ("ma_bt", "bienso", "ngay_bt", "chiphi", "mota")
tree = ttk.Treeview(frame_tree, columns=columns, show="headings", height=10,
                    yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)

scrollbar_y.config(command=tree.yview)
scrollbar_x.config(command=tree.xview)

scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)

tree.heading("ma_bt", text="Mã BT")
tree.column("ma_bt", width=60, anchor="center")
tree.heading("bienso", text="Biển số xe")
tree.column("bienso", width=100)
tree.heading("ngay_bt", text="Ngày bảo trì")
tree.column("ngay_bt", width=100)
tree.heading("chiphi", text="Chi phí")
tree.column("chiphi", width=100, anchor="e") # anchor="e" (end) để căn lề phải
tree.heading("mota", text="Mô tả")
tree.column("mota", width=300)

tree.pack(fill="both", expand=True)

# THÊM BINDING (SỰ KIỆN CLICK)
tree.bind("<<TreeviewSelect>>", on_item_select) 

# ================================================================
# PHẦN 5: CHẠY ỨNG DỤNG
# ================================================================
load_data() 
root.mainloop()