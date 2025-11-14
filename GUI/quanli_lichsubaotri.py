# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
import utils # <-- IMPORT FILE DÙNG CHUNG
from datetime import datetime
import datetime as dt

# ================================================================
# PHẦN 2: CÁC HÀM TIỆN ÍCH
# ================================================================

# <-- SỬA: Thêm user_role và user_username
def load_xe_combobox(user_role, user_username):
    """Tải danh sách xe (BienSoXe) vào Combobox, LỌC theo tài xế."""
    conn = utils.connect_db() 
    if conn is None: return []
    
    try:
        cur = conn.cursor()
        sql = "SELECT BienSoXe FROM Xe"
        params = []
        
        # Nếu là Tài xế, chỉ tải xe của tài xế đó
        if user_role == "TaiXe":
            manv = get_manv_from_username(user_username)
            if manv:
                sql += " WHERE MaNhanVienHienTai = ?"
                params.append(manv)
            else:
                sql += " WHERE 1=0" # Không tìm thấy tài xế, trả về rỗng
        
        sql += " ORDER BY BienSoXe"
        cur.execute(sql, params)
        rows = cur.fetchall()
        return [row[0] for row in rows]
    except Exception as e:
        print(f"Lỗi tải combobox xe: {e}")
        return []
    finally:
        if conn: conn.close()

def get_manv_from_username(username):
    """Lấy MaNhanVien từ TenDangNhap."""
    conn = utils.connect_db()
    if conn is None: return None
    try:
        cur = conn.cursor()
        cur.execute("SELECT MaNhanVien FROM TaiKhoan WHERE TenDangNhap = ?", (username,))
        row = cur.fetchone()
        return row[0] if row else None
    except Exception as e:
        print(f"Lỗi get_manv_from_username: {e}")
        return None
    finally:
        if conn: conn.close()

# ================================================================
# PHẦN 3: CÁC HÀM CRUD
# ================================================================

def set_form_state(is_enabled, widgets):
    """Bật (enable) hoặc Tắt (disable) toàn bộ các trường nhập liệu."""
    widgets['entry_mabaotri'].config(state='disabled')
    
    if is_enabled:
        widgets['cbb_xe'].config(state='readonly')
        widgets['date_ngaybaotri'].config(state='normal')
        widgets['entry_chiphi'].config(state='normal')
        widgets['entry_mota'].config(state='normal', bg=utils.theme_colors["bg_entry"], fg=utils.theme_colors["text"])
    else:
        widgets['cbb_xe'].config(state='disabled')
        widgets['date_ngaybaotri'].config(state='disabled')
        widgets['entry_chiphi'].config(state='disabled')
        widgets['entry_mota'].config(state='disabled', bg=utils.theme_colors["disabled_bg"], fg=utils.theme_colors["text_disabled"])

def clear_input(widgets):
    """(NÚT THÊM) Xóa trắng và Mở khóa các trường nhập liệu (Chế độ Thêm mới)."""
    set_form_state(is_enabled=True, widgets=widgets)
    
    widgets['entry_mabaotri'].config(state='normal')
    widgets['entry_mabaotri'].delete(0, tk.END)
    widgets['entry_mabaotri'].config(state='disabled')
    
    widgets['cbb_xe'].set("")
    widgets['entry_chiphi'].delete(0, tk.END)
    widgets['entry_mota'].delete("1.0", tk.END) 
    
    widgets['date_ngaybaotri'].set_date(datetime.now().strftime("%Y-%m-%d"))
    
    widgets['cbb_xe'].focus()
    
    tree = widgets['tree']
    if tree.selection():
        tree.selection_remove(tree.selection()[0])
        
    widgets["current_mode"] = "ADD" # Đặt chế độ

def load_data(widgets, user_role, user_username):
    """Tải dữ liệu Bảo trì (LỌC THEO VAI TRÒ) VÀ LÀM MỜ FORM."""
    tree = widgets['tree']
    for i in tree.get_children():
        tree.delete(i)
        
    conn = utils.connect_db()
    if conn is None:
        set_form_state(is_enabled=False, widgets=widgets) 
        return
        
    try:
        cur = conn.cursor()
        
        sql = """
            SELECT 
                bt.MaBaoTri, bt.BienSoXe, bt.NgayBaoTri, bt.ChiPhi, bt.MoTa,
                nv.HoVaTen AS NguoiNhap
            FROM LichSuBaoTri AS bt
            LEFT JOIN NhanVien AS nv ON bt.MaNhanVienNhap = nv.MaNhanVien
        """
        params = []
        
        if user_role == "TaiXe":
            manv = get_manv_from_username(user_username)
            if manv:
                sql += """
                    WHERE bt.BienSoXe IN (
                        SELECT BienSoXe FROM Xe WHERE MaNhanVienHienTai = ?
                    )
                """
                params.append(manv)
            else:
                sql += " WHERE 1=0"
        
        sql += " ORDER BY bt.NgayBaoTri DESC"
        
        cur.execute(sql, params)
        rows = cur.fetchall()
        
        for row in rows:
            ma_bt = row[0]
            bienso = row[1]
            ngay_bt = str(row[2]) if row[2] else "N/A"
            chiphi = row[3]
            mota = (row[4] or "")[:50] + "..."
            nguoi_nhap = row[5] or "N/A"
            
            tree.insert("", tk.END, values=(ma_bt, bienso, ngay_bt, chiphi, mota, nguoi_nhap))
            
        children = tree.get_children()
        if children:
            first_item = children[0]
            tree.selection_set(first_item) 
            tree.focus(first_item)         
            tree.event_generate("<<TreeviewSelect>>") 
        else:
            clear_input(widgets) # Đặt chế độ Thêm nếu bảng trống
            
    except Exception as e:
        messagebox.showerror("Lỗi tải dữ liệu", f"Lỗi SQL: {str(e)}")
    finally:
        if conn:
            conn.close()
            
        if tree.get_children():
             set_form_state(is_enabled=False, widgets=widgets)
             widgets["current_mode"] = "VIEW"
        # (Nếu bảng trống, clear_input() đã set mode="ADD")


def them_baotri(widgets):
    """(LOGIC THÊM) Thêm một lịch sử bảo trì mới."""
    try:
        bienso = widgets['cbb_xe_var'].get()
        ngay_bt = widgets['date_ngaybaotri'].get_date().strftime('%Y-%m-%d')
        mota = widgets['entry_mota'].get("1.0", tk.END).strip()
        chiphi = widgets['entry_chiphi'].get()

        if not bienso or not ngay_bt:
            messagebox.showwarning("Thiếu dữ liệu", "Vui lòng nhập Xe và Ngày bảo trì")
            return False

        chiphi_dec = float(chiphi) if chiphi else 0.0
        
        user_username = widgets.get("user_username")
        manv_nhap = get_manv_from_username(user_username)
        if not manv_nhap:
            messagebox.showerror("Lỗi", "Không thể xác định người dùng. Vui lòng đăng nhập lại.")
            return False

    except Exception as e:
        messagebox.showerror("Lỗi định dạng", f"Chi phí không hợp lệ: {e}")
        return False

    conn = utils.connect_db()
    if conn is None: return False

    try:
        cur = conn.cursor()
        sql = "INSERT INTO LichSuBaoTri (BienSoXe, NgayBaoTri, MoTa, ChiPhi, MaNhanVienNhap) VALUES (?, ?, ?, ?, ?)"
        cur.execute(sql, (bienso, ngay_bt, mota, chiphi_dec, manv_nhap))
        conn.commit()
        messagebox.showinfo("Thành công", "Đã thêm lịch sử bảo trì thành công")
        return True
        
    except Exception as e:
        conn.rollback() 
        messagebox.showerror("Lỗi SQL", f"Không thể thêm:\n{str(e)}")
        return False
    finally:
        if conn: conn.close()

def on_item_select(event, widgets):
    """(SỰ KIỆN CLICK) Khi click vào Treeview, đổ dữ liệu đầy đủ lên form (ở trạng thái mờ)."""
    tree = widgets['tree']
    selected = tree.selection()
    if not selected: return 

    selected_item = tree.item(selected[0])
    mabaotri = selected_item['values'][0]
    
    conn = utils.connect_db()
    if conn is None: return

    try:
        cur = conn.cursor()
        sql = "SELECT * FROM LichSuBaoTri WHERE MaBaoTri = ?"
        cur.execute(sql, (mabaotri,))
        data = cur.fetchone()
        
        if not data:
            messagebox.showerror("Lỗi", "Không tìm thấy dữ liệu.")
            return

        set_form_state(is_enabled=True, widgets=widgets)
        widgets['entry_mabaotri'].config(state='normal')
        
        widgets['entry_mabaotri'].delete(0, tk.END)
        widgets['cbb_xe'].set("")
        widgets['entry_chiphi'].delete(0, tk.END)
        widgets['entry_mota'].delete("1.0", tk.END)
        
        widgets['entry_mabaotri'].insert(0, data.MaBaoTri)
        widgets['cbb_xe'].set(data.BienSoXe or "")
        
        if data.NgayBaoTri:
            widgets['date_ngaybaotri'].set_date(str(data.NgayBaoTri)) 
            
        widgets['entry_chiphi'].insert(0, str(data.ChiPhi or ""))
        widgets['entry_mota'].insert("1.0", data.MoTa or "")

    except Exception as e:
        messagebox.showerror("Lỗi không xác định", f"Lỗi: {str(e)}")
    finally:
        if conn: conn.close()
        widgets['entry_mabaotri'].config(state='disabled') 
        set_form_state(is_enabled=False, widgets=widgets)
        widgets["current_mode"] = "VIEW" # Đặt chế độ

def chon_baotri_de_sua(widgets): 
    """(NÚT SỬA) Kích hoạt chế độ sửa, Mở khóa form (trừ MaBaoTri)."""
    selected = widgets['tree'].selection()
    if not selected:
        messagebox.showwarning("Chưa chọn", "Hãy chọn một mục trong danh sách trước khi nhấn 'Sửa'")
        return

    if not widgets['entry_mabaotri'].get():
         messagebox.showwarning("Lỗi", "Không tìm thấy mã bảo trì. Vui lòng chọn lại.")
         return

    set_form_state(is_enabled=True, widgets=widgets)
    widgets['entry_mabaotri'].config(state='disabled')
    widgets['cbb_xe'].focus() 
    widgets["current_mode"] = "EDIT" # Đặt chế độ

def luu_baotri_da_sua(widgets):
    """(LOGIC SỬA) Lưu thay đổi (UPDATE) sau khi sửa."""
    mabaotri = widgets['entry_mabaotri'].get()
    if not mabaotri:
        messagebox.showwarning("Thiếu dữ liệu", "Không có Mã bảo trì để cập nhật")
        return False

    try:
        bienso = widgets['cbb_xe_var'].get()
        ngay_bt = widgets['date_ngaybaotri'].get_date().strftime('%Y-%m-%d')
        mota = widgets['entry_mota'].get("1.0", tk.END).strip()
        chiphi = widgets['entry_chiphi'].get()
        
        if not bienso or not ngay_bt:
            messagebox.showwarning("Thiếu dữ liệu", "Xe và Ngày bảo trì không được rỗng")
            return False

        chiphi_dec = float(chiphi) if chiphi else 0.0

    except Exception as e:
        messagebox.showerror("Lỗi định dạng", f"Chi phí không hợp lệ: {e}")
        return False

    conn = utils.connect_db()
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
        
    except Exception as e:
        conn.rollback()
        messagebox.showerror("Lỗi SQL", f"Không thể cập nhật:\n{str(e)}")
        return False
    finally:
        if conn: conn.close()

# ================================================================
# HÀM QUAN TRỌNG NHẤT (SỬA LỖI 2)
# ================================================================
def save_data(widgets):
    """Lưu dữ liệu, tự động kiểm tra xem nên Thêm mới (INSERT) hay Cập nhật (UPDATE)."""
    
    user_role = widgets.get("user_role", "Admin")
    user_username = widgets.get("user_username", "")
    
    # Sửa: Dùng logic 'current_mode'
    if widgets.get("current_mode") == "EDIT":
        success = luu_baotri_da_sua(widgets)
    elif widgets.get("current_mode") == "ADD":
        success = them_baotri(widgets)
    else:
        # Nếu đang ở VIEW (chưa nhấn Thêm/Sửa), thì dùng logic cũ
        if widgets['entry_mabaotri'].get():
            success = luu_baotri_da_sua(widgets)
        else:
            success = them_baotri(widgets)
    
    if success:
        # Sửa lỗi: Truyền tham số user vào load_data
        load_data(widgets, user_role, user_username)
# ================================================================


def xoa_baotri(widgets):
    """Xóa lịch sử bảo trì được chọn."""
    selected = widgets['tree'].selection()
    if not selected:
        messagebox.showwarning("Chưa chọn", "Hãy chọn một mục để xóa")
        return
        
    mabaotri = widgets['entry_mabaotri'].get() 

    if not mabaotri:
        messagebox.showwarning("Lỗi", "Không tìm thấy mã bảo trì. Vui lòng chọn lại.")
        return

    if not messagebox.askyesno("Xác nhận", f"Bạn có chắc chắn muốn xóa Lịch sử Mã: {mabaotri}?"):
        return

    conn = utils.connect_db()
    if conn is None: return
        
    try:
        cur = conn.cursor()
        cur.execute("DELETE FROM LichSuBaoTri WHERE MaBaoTri=?", (mabaotri,))
        conn.commit()
        messagebox.showinfo("Thành công", "Đã xóa lịch sử bảo trì thành công")
        
        user_role = widgets.get("user_role", "Admin")
        user_username = widgets.get("user_username", "")
        load_data(widgets, user_role, user_username)
        
    except Exception as e:
        conn.rollback()
        messagebox.showerror("Lỗi SQL", f"Không thể xóa:\n{str(e)}")
    finally:
        if conn: conn.close()

# ================================================================
# PHẦN 4: HÀM TẠO TRANG (HÀM CHÍNH ĐỂ MAIN.PY GỌI)
# ================================================================

def create_page(master, user_role, user_username):
    """
    Hàm này được main.py gọi. 
    Nó tạo ra toàn bộ nội dung trang và đặt vào 'master' (là main_frame).
    """
    
    page_frame = ttk.Frame(master, style="TFrame")
    utils.setup_theme(page_frame) 
    
    lbl_title_text = "QUẢN LÝ LỊCH SỬ BẢO TRÌ"
    if user_role == "TaiXe":
        lbl_title_text = "LỊCH SỬ BẢO TRÌ XE CỦA BẠN"
        
    lbl_title = ttk.Label(page_frame, text=lbl_title_text, style="Title.TLabel")
    lbl_title.pack(pady=15) 

    frame_info = ttk.Frame(page_frame, style="TFrame")
    frame_info.pack(pady=5, padx=20, fill="x")

    # --- Hàng 1 ---
    ttk.Label(frame_info, text="Mã bảo trì:").grid(row=0, column=0, padx=5, pady=8, sticky="w")
    entry_mabaotri = ttk.Entry(frame_info, width=30, state='disabled')
    entry_mabaotri.grid(row=0, column=1, padx=5, pady=8, sticky="w")

    ttk.Label(frame_info, text="Ngày bảo trì:").grid(row=0, column=2, padx=15, pady=8, sticky="w")
    date_entry_style_options = {
        'width': 38, 'date_pattern': 'yyyy-MM-dd',
        'background': utils.theme_colors["bg_entry"], 
        'foreground': utils.theme_colors["text"],
        'disabledbackground': utils.theme_colors["disabled_bg"],
        'disabledforeground': utils.theme_colors["text_disabled"],
        'bordercolor': utils.theme_colors["bg_entry"],
        'headersbackground': utils.theme_colors["accent"],
        'headersforeground': utils.theme_colors["accent_text"],
        'selectbackground': utils.theme_colors["accent"],
        'selectforeground': utils.theme_colors["accent_text"]
    }
    date_ngaybaotri = DateEntry(frame_info, **date_entry_style_options)
    date_ngaybaotri.grid(row=0, column=3, padx=5, pady=8, sticky="w")

    # --- Hàng 2 ---
    ttk.Label(frame_info, text="Xe:").grid(row=1, column=0, padx=5, pady=8, sticky="w")
    cbb_xe_var = tk.StringVar()
    cbb_xe = ttk.Combobox(frame_info, textvariable=cbb_xe_var, width=28, state='readonly')
    cbb_xe.grid(row=1, column=1, padx=5, pady=8, sticky="w")
    
    # <-- SỬA LỖI 3: Lọc combobox theo tài xế
    cbb_xe['values'] = load_xe_combobox(user_role, user_username) 

    ttk.Label(frame_info, text="Chi phí:").grid(row=1, column=2, padx=15, pady=8, sticky="w")
    entry_chiphi = ttk.Entry(frame_info, width=40)
    entry_chiphi.grid(row=1, column=3, padx=5, pady=8, sticky="w")

    # --- Hàng 3 (Mô tả) ---
    ttk.Label(frame_info, text="Mô tả công việc:").grid(row=2, column=0, padx=5, pady=8, sticky="nw")
    entry_mota = tk.Text(frame_info, width=60, height=4, 
        font=("Segoe UI", 10),
        bg=utils.theme_colors["bg_entry"],
        fg=utils.theme_colors["text"],
        relief="solid",
        borderwidth=1,
        insertbackground=utils.theme_colors["text"],
        highlightthickness=1, 
        highlightbackground="#ACACAC",
        highlightcolor=utils.theme_colors["accent"] 
    )
    entry_mota.grid(row=2, column=1, columnspan=3, padx=5, pady=8, sticky="w")

    frame_info.columnconfigure(1, weight=1)
    frame_info.columnconfigure(3, weight=1)

    # ===== Frame nút =====
    frame_btn = ttk.Frame(page_frame, style="TFrame")
    frame_btn.pack(pady=10)

    # ===== Bảng danh sách =====
    lbl_ds = ttk.Label(page_frame, text="Danh sách bảo trì (Sắp xếp mới nhất)", style="Header.TLabel")
    lbl_ds.pack(pady=(10, 5), padx=20, anchor="w")

    frame_tree = ttk.Frame(page_frame, style="TFrame")
    frame_tree.pack(pady=10, padx=20, fill="both", expand=True) 

    scrollbar_y = ttk.Scrollbar(frame_tree, orient=tk.VERTICAL, style="Vertical.TScrollbar")
    scrollbar_x = ttk.Scrollbar(frame_tree, orient=tk.HORIZONTAL, style="Horizontal.TScrollbar")

    columns = ("ma_bt", "bienso", "ngay_bt", "chiphi", "mota", "nguoi_nhap")
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
    tree.column("chiphi", width=100, anchor="e") 
    tree.heading("mota", text="Mô tả")
    tree.column("mota", width=250)
    
    tree.heading("nguoi_nhap", text="Người nhập")
    tree.column("nguoi_nhap", width=120)

    tree.pack(fill="both", expand=True)
    
    # 3. TẠO TỪ ĐIỂN 'widgets'
    widgets = {
        "tree": tree,
        "entry_mabaotri": entry_mabaotri,
        "date_ngaybaotri": date_ngaybaotri,
        "cbb_xe": cbb_xe,
        "entry_chiphi": entry_chiphi,
        "entry_mota": entry_mota,
        "cbb_xe_var": cbb_xe_var,
        "user_role": user_role,
        "user_username": user_username,
        "current_mode": "VIEW" # Thêm biến trạng thái
    }

    # (Code tạo nút)
    btn_them = ttk.Button(frame_btn, text="Thêm", width=8, command=lambda: clear_input(widgets)) 
    btn_them.grid(row=0, column=0, padx=10)
    btn_luu = ttk.Button(frame_btn, text="Lưu", width=8, command=lambda: save_data(widgets)) 
    btn_luu.grid(row=0, column=1, padx=10)
    btn_sua = ttk.Button(frame_btn, text="Sửa", width=8, command=lambda: chon_baotri_de_sua(widgets)) 
    btn_sua.grid(row=0, column=2, padx=10)
    
    btn_huy = ttk.Button(frame_btn, text="Hủy", width=8, 
                         command=lambda: load_data(widgets, user_role, user_username)) 
    btn_huy.grid(row=0, column=3, padx=10)
    
    btn_xoa = ttk.Button(frame_btn, text="Xóa", width=8, command=lambda: xoa_baotri(widgets)) 
    btn_xoa.grid(row=0, column=4, padx=10)
    
    if user_role == "TaiXe":
        btn_sua.config(state="disabled")
        btn_xoa.config(state="disabled")
    
    # 4. KẾT NỐI BINDING
    tree.bind("<<TreeviewSelect>>", lambda event: on_item_select(event, widgets)) 

    # 5. TẢI DỮ LIỆU LẦN ĐẦU
    load_data(widgets, user_role, user_username) 
    
    # 6. TRẢ VỀ FRAME CHÍNH
    return page_frame

# ================================================================
# PHẦN 5: CHẠY THỬ NGHIỆM
# ================================================================
if __name__ == "__main__":
    
    test_root = tk.Tk()
    test_root.title("Test Quản lý Bảo Trì")

    try:
        utils.center_window(test_root, 950, 650) 
    except Exception:
        test_root.geometry("950x650")
    
    page = create_page(test_root, "Admin", "admin")
    
    page.pack(fill="both", expand=True)
    
    test_root.mainloop()