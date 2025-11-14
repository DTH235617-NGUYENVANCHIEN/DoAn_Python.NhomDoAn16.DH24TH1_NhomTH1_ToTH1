# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
import utils # <-- IMPORT FILE DÙNG CHUNG
from datetime import datetime
import datetime as dt
import pyodbc # Để bắt lỗi

# ================================================================
# PHẦN 2: CÁC HÀM TIỆN ÍCH (Tải Combobox và Helper)
# ================================================================

# === HELPER: Lấy Mã Nhân Viên từ Tên Đăng Nhập ===
def get_manv_from_username(username):
    """Lấy MaNhanVien từ TenDangNhap để lọc dữ liệu."""
    conn = utils.connect_db()
    if conn is None: return (None, None)
    try:
        cur = conn.cursor()
        cur.execute("SELECT NV.MaNhanVien, NV.HoVaTen FROM TaiKhoan TK JOIN NhanVien NV ON TK.MaNhanVien = NV.MaNhanVien WHERE TK.TenDangNhap = ?", (username,))
        row = cur.fetchone()
        return (row[0], f"{row[0]} - {row[1]}") if row else (None, None) # Trả về (MaNhanVien, TenHienThi)
    except Exception as e:
        print(f"Lỗi get_manv_from_username: {e}")
        return (None, None)
    finally:
        if conn: conn.close()
        
# === HELPER: Lấy Mã Nhật Ký đang chọn trong bảng (Sau khi bỏ field trên UI) ===
def get_manhatky_from_tree(widgets):
    """Lấy MaNhatKy từ hàng đang được chọn trong Treeview."""
    tree = widgets['tree']
    selected = tree.selection()
    if not selected: return None
    # Giá trị MaNK là cột đầu tiên (index 0) trong values
    return tree.item(selected[0])['values'][0]

# ================================================================
# PHẦN 3: CÁC HÀM CRUD (ĐÃ CẬP NHẬT PHÂN QUYỀN VÀ BỎ Mã NK)
# ================================================================

def set_form_state(is_enabled, widgets, user_role):
    """Bật (enable) hoặc Tắt (disable) toàn bộ các trường nhập liệu."""
    if is_enabled:
        # === TÀI XẾ CẦN BẬT CÁC Ô NÀY ĐỂ THÊM MỚI/SỬA ===
        widgets['cbb_xe'].config(state='readonly')
        widgets['date_ngaydo'].config(state='normal')
        widgets['entry_giodo'].config(state='normal')
        widgets['entry_solit'].config(state='normal')
        widgets['entry_tongchiphi'].config(state='normal')
        widgets['entry_soodo'].config(state='normal')

        if user_role == "Admin":
            widgets['cbb_taixe'].config(state='readonly')
            widgets['cbb_trangthai'].config(state='readonly')
        else: # Nếu là TaiXe
            widgets['cbb_taixe'].config(state='disabled')
            widgets['cbb_trangthai'].config(state='disabled')
    else:
        widgets['cbb_xe'].config(state='disabled')
        widgets['cbb_taixe'].config(state='disabled')
        widgets['date_ngaydo'].config(state='disabled')
        widgets['entry_giodo'].config(state='disabled')
        widgets['entry_solit'].config(state='disabled')
        widgets['entry_tongchiphi'].config(state='disabled')
        widgets['entry_soodo'].config(state='disabled')
        widgets['cbb_trangthai'].config(state='disabled')

def clear_input(widgets, user_role, user_username):
    """(NÚT THÊM) Xóa trắng và Mở khóa các trường nhập liệu (Chế độ Thêm mới)."""
    if user_role == "Admin":
        messagebox.showwarning("Thông báo", "Admin chỉ có thể Duyệt hoặc Từ chối.")
        return
        
    set_form_state(is_enabled=True, widgets=widgets, user_role=user_role)
    
    widgets['cbb_xe'].set("")
    widgets['entry_solit'].delete(0, tk.END)
    widgets['entry_tongchiphi'].delete(0, tk.END)
    widgets['entry_soodo'].delete(0, tk.END)
    
    now = datetime.now()
    widgets['date_ngaydo'].set_date(now.strftime("%Y-%m-%d"))
    widgets['entry_giodo'].delete(0, tk.END)
    widgets['entry_giodo'].insert(0, now.strftime("%H:%M"))
    
    widgets['cbb_trangthai'].set("Chờ duyệt")
    
    # TỰ ĐỘNG ĐIỀN THÔNG TIN TÀI XẾ
    if user_role == "TaiXe":
        manv, ten_hien_thi = get_manv_from_username(user_username)
        if ten_hien_thi:
            widgets['cbb_taixe'].set(ten_hien_thi)
    else:
        widgets['cbb_taixe'].set("")
        
    widgets['cbb_xe'].focus()
    
    tree = widgets['tree']
    if tree.selection():
        tree.selection_remove(tree.selection()[0])
        
    widgets["current_mode"] = "ADD" # Sửa lỗi logic Sửa/Lưu

def load_data(widgets, user_role, user_username):
    tree = widgets['tree']
    for i in tree.get_children():
        tree.delete(i)
        
    conn = utils.connect_db()
    if conn is None:
        set_form_state(is_enabled=False, widgets=widgets, user_role=user_role)
        return
        
    try:
        cur = conn.cursor()
        sql = """
        SELECT
            nk.MaNhatKy, nk.BienSoXe, nv.HoVaTen,
            nk.NgayDoNhienLieu, nk.SoLit, nk.TongChiPhi, nk.TrangThaiDuyet
        FROM NhatKyNhienLieu AS nk
        LEFT JOIN NhanVien AS nv ON nk.MaNhanVien = nv.MaNhanVien
        """
        
        params = []
        if user_role == "TaiXe":
            manv, _ = get_manv_from_username(user_username)
            if manv:
                sql += " WHERE nk.MaNhanVien = ?"
                params.append(manv)
            else:
                sql += " WHERE 1=0"
        
        sql += " ORDER BY nk.NgayDoNhienLieu DESC"
        
        cur.execute(sql, params)
        rows = cur.fetchall()
        
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
        elif user_role == "TaiXe":
            clear_input(widgets, user_role, user_username)
            
    except Exception as e:
        messagebox.showerror("Lỗi tải dữ liệu", f"Lỗi SQL: {str(e)}")
    finally:
        if conn:
            conn.close()
        
        # Sửa: Luôn khóa form sau khi tải xong
        set_form_state(is_enabled=False, widgets=widgets, user_role=user_role)
        widgets["current_mode"] = "VIEW" # Đặt lại trạng thái

def them_nhienlieu(widgets, user_role, user_username):
    try:
        bienso = widgets['cbb_xe_var'].get()
        
        manv = ""
        if user_role == "TaiXe":
            manv, _ = get_manv_from_username(user_username)
            if not manv:
                messagebox.showerror("Lỗi", "Không tìm thấy mã nhân viên của bạn.")
                return False
        else:
            messagebox.showerror("Lỗi", "Admin không thể thêm nhật ký.")
            return False
        
        ngay_do_str = widgets['date_ngaydo'].get_date().strftime('%Y-%m-%d')
        gio_do_str = widgets['entry_giodo'].get() or "00:00"
        tg_nhienlieu = f"{ngay_do_str} {gio_do_str}:00"
        
        solit = widgets['entry_solit'].get()
        tongchiphi = widgets['entry_tongchiphi'].get()
        soodo = widgets['entry_soodo'].get()
        
        trangthai_value = 0 # Tài xế thêm luôn là "Chờ duyệt"
        
        if not bienso or not manv or not solit or not tongchiphi:
            messagebox.showwarning("Thiếu dữ liệu", "Vui lòng nhập Xe, Số lít và Chi phí")
            return False

        solit_dec = float(solit) if solit else 0.0
        tongchiphi_dec = float(tongchiphi) if tongchiphi else 0.0
        soodo_int = int(soodo) if soodo else None

    except Exception as e:
        messagebox.showerror("Lỗi định dạng", f"Dữ liệu số (lít, chi phí, odo) không hợp lệ: {e}")
        return False

    conn = utils.connect_db()
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
        messagebox.showinfo("Thành công", "Đã thêm nhật ký nhiên liệu (chờ duyệt).")
        return True
        
    except Exception as e:
        conn.rollback()
        messagebox.showerror("Lỗi SQL", f"Không thể thêm nhật ký:\n{str(e)}")
        return False
    finally:
        if conn: conn.close()

def on_item_select(event, widgets):
    """(SỰ KIỆN CLICK) Đổ dữ liệu lên form (phân quyền)."""
    tree = widgets['tree']
    selected = tree.selection()
    if not selected: return

    selected_item = tree.item(selected[0])
    manhatky = selected_item['values'][0]
    
    user_role = widgets.get("user_role", "Admin")
    
    conn = utils.connect_db()
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

        # Sửa: Tắt form trước, chỉ bật nếu thỏa điều kiện
        set_form_state(is_enabled=False, widgets=widgets, user_role=user_role)
        widgets["current_mode"] = "VIEW" # Đặt trạng thái xem

        # Xóa các fields
        widgets['cbb_xe'].set("")
        widgets['cbb_taixe'].set("")
        widgets['entry_giodo'].delete(0, tk.END)
        widgets['entry_solit'].delete(0, tk.END)
        widgets['entry_tongchiphi'].delete(0, tk.END)
        widgets['entry_soodo'].delete(0, tk.END)
        
        # Điền
        widgets['cbb_xe'].set(data.BienSoXe or "")
        
        if data.MaNhanVien:
            cbb_taixe_val = f"{data.MaNhanVien} - {data.HoVaTen}"
            widgets['cbb_taixe'].set(cbb_taixe_val)
        
        if data.NgayDoNhienLieu:
            widgets['date_ngaydo'].set_date(data.NgayDoNhienLieu)
            widgets['entry_giodo'].insert(0, data.NgayDoNhienLieu.strftime("%H:%M"))
            
        widgets['entry_solit'].insert(0, str(data.SoLit or ""))
        widgets['entry_tongchiphi'].insert(0, str(data.TongChiPhi or ""))
        widgets['entry_soodo'].insert(0, str(data.SoOdo or ""))

        trangthai_map = {0: "Chờ duyệt", 1: "Đã duyệt", 2: "Từ chối"}
        trangthai_text = trangthai_map.get(data.TrangThaiDuyet, "Chờ duyệt")
        widgets['cbb_trangthai'].set(trangthai_text)
        
        # KHÓA FORM NẾU LÀ TÀI XẾ VÀ ĐÃ DUYỆT (hoặc Admin)
        if user_role == "TaiXe" and data.TrangThaiDuyet == 0: # 0 = Chờ duyệt
             # Cho phép sửa
            pass
        else:
            set_form_state(is_enabled=False, widgets=widgets, user_role=user_role)

    except Exception as e:
        messagebox.showerror("Lỗi không xác định", f"Lỗi: {str(e)}")
    finally:
        if conn: conn.close()

def chon_nhienlieu_de_sua(widgets, user_role):
    """(NÚT SỬA) Kích hoạt chế độ sửa (phân quyền)."""
    if user_role == "Admin":
        messagebox.showwarning("Thông báo", "Admin chỉ có thể Duyệt hoặc Từ chối.")
        return
        
    selected = widgets['tree'].selection()
    if not selected:
        messagebox.showwarning("Chưa chọn", "Hãy chọn một nhật ký trong danh sách trước khi nhấn 'Sửa'")
        return

    manhatky = get_manhatky_from_tree(widgets)
    if not manhatky:
        messagebox.showwarning("Lỗi", "Không tìm thấy mã nhật ký. Vui lòng chọn lại.")
        return

    trangthai_text = widgets['cbb_trangthai_var'].get()
    if trangthai_text != "Chờ duyệt":
        messagebox.showwarning("Không thể sửa", "Tài xế chỉ có thể sửa nhật ký đang 'Chờ duyệt'.")
        return

    set_form_state(is_enabled=True, widgets=widgets, user_role=user_role)
    widgets['cbb_xe'].focus()
    widgets["current_mode"] = "EDIT" # Sửa lỗi logic Sửa/Lưu

def luu_nhienlieu_da_sua(widgets, user_role, user_username):
    """(LOGIC SỬA) Lưu thay đổi (UPDATE) sau khi sửa (phân quyền)."""
    if user_role == "Admin":
        messagebox.showwarning("Thông báo", "Admin chỉ có thể Duyệt hoặc Từ chối.")
        return False
        
    manhatky = get_manhatky_from_tree(widgets)
    if not manhatky:
        messagebox.showwarning("Thiếu dữ liệu", "Không có Mã nhật ký để cập nhật")
        return False

    try:
        bienso = widgets['cbb_xe_var'].get()
        manv, _ = get_manv_from_username(user_username)
        
        ngay_do_str = widgets['date_ngaydo'].get_date().strftime('%Y-%m-%d')
        gio_do_str = widgets['entry_giodo'].get() or "00:00"
        tg_nhienlieu = f"{ngay_do_str} {gio_do_str}:00"
        
        solit = widgets['entry_solit'].get()
        tongchiphi = widgets['entry_tongchiphi'].get()
        soodo = widgets['entry_soodo'].get()
        
        trangthai_value = 0 # Tài xế sửa thì luôn là "Chờ duyệt"
            
        if not bienso or not manv or not solit or not tongchiphi:
            messagebox.showwarning("Thiếu dữ liệu", "Xe, Tài xế, Số lít và Chi phí không được rỗng")
            return False

        solit_dec = float(solit) if solit else 0.0
        tongchiphi_dec = float(tongchiphi) if tongchiphi else 0.0
        soodo_int = int(soodo) if soodo else None

    except Exception as e:
        messagebox.showerror("Lỗi định dạng", f"Dữ liệu nhập không hợp lệ: {e}")
        return False

    conn = utils.connect_db()
    if conn is None: return False
        
    try:
        cur = conn.cursor()
        
        # Kiểm tra lần nữa: Tài xế chỉ được sửa khi "Chờ duyệt"
        cur.execute("SELECT TrangThaiDuyet FROM NhatKyNhienLieu WHERE MaNhatKy = ?", (manhatky,))
        status = cur.fetchone()
        if status and status[0] != 0:
            messagebox.showwarning("Không thể sửa", "Tài xế chỉ có thể sửa nhật ký đang 'Chờ duyệt'.")
            return False
        
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
        
    except Exception as e:
        conn.rollback()
        messagebox.showerror("Lỗi SQL", f"Không thể cập nhật:\n{str(e)}")
        return False
    finally:
        if conn: conn.close()

def save_data(widgets, user_role, user_username):
    """Lưu dữ liệu, tự động kiểm tra xem nên Thêm mới (INSERT) hay Cập nhật (UPDATE)."""
    
    success = False
    current_mode = widgets.get("current_mode", "VIEW")

    if current_mode == "EDIT":
        success = luu_nhienlieu_da_sua(widgets, user_role, user_username)
    elif current_mode == "ADD":
        success = them_nhienlieu(widgets, user_role, user_username)
    else: # Đang ở chế độ VIEW
        messagebox.showwarning("Chưa Sửa/Thêm", "Vui lòng nhấn 'Thêm' hoặc 'Sửa' trước khi Lưu.")
        return

    if success:
        load_data(widgets, user_role, user_username)

def xoa_nhienlieu(widgets, user_role, user_username):
    """Xóa nhật ký được chọn (phân quyền)."""
    if user_role == "Admin":
        messagebox.showwarning("Thông báo", "Admin chỉ có thể Duyệt hoặc Từ chối.")
        return
        
    selected = widgets['tree'].selection()
    if not selected:
        messagebox.showwarning("Chưa chọn", "Hãy chọn một nhật ký để xóa")
        return
        
    manhatky = get_manhatky_from_tree(widgets)
    if not manhatky:
        messagebox.showwarning("Lỗi", "Không tìm thấy mã nhật ký. Vui lòng chọn lại.")
        return

    trangthai_text = widgets['cbb_trangthai_var'].get()
    if trangthai_text != "Chờ duyệt":
        messagebox.showwarning("Không thể xóa", "Tài xế chỉ có thể xóa nhật ký đang 'Chờ duyệt'.")
        return

    if not messagebox.askyesno("Xác nhận", f"Bạn có chắc chắn muốn xóa Nhật ký Mã: {manhatky}?"):
        return

    conn = utils.connect_db()
    if conn is None: return
        
    try:
        cur = conn.cursor()
        cur.execute("DELETE FROM NhatKyNhienLieu WHERE MaNhatKy=?", (manhatky,))
        conn.commit()
        
        messagebox.showinfo("Thành công", "Đã xóa nhật ký thành công")
        load_data(widgets, user_role, user_username)
        
    except Exception as e:
        conn.rollback()
        messagebox.showerror("Lỗi SQL", f"Không thể xóa:\n{str(e)}")
    finally:
        if conn: conn.close()

def duyet_nhienlieu(widgets, user_role, user_username, new_status):
    """(Admin) Cập nhật trạng thái nhật ký (1 = Duyệt, 2 = Từ chối)."""
    
    manhatky = get_manhatky_from_tree(widgets)
    if not manhatky:
        messagebox.showwarning("Chưa chọn", "Vui lòng chọn một nhật ký từ danh sách.")
        return

    trangthai_hientai = widgets['cbb_trangthai_var'].get()
    
    if new_status == 1: # Duyệt
        if trangthai_hientai == "Đã duyệt":
            messagebox.showinfo("Thông báo", "Nhật ký này đã được duyệt rồi.")
            return
        action_text = "DUYỆT"
    else: # Từ chối
        if trangthai_hientai == "Từ chối":
            messagebox.showinfo("Thông báo", "Nhật ký này đã bị từ chối rồi.")
            return
        action_text = "TỪ CHỐI"

    if not messagebox.askyesno("Xác nhận", f"Bạn có chắc chắn muốn {action_text} nhật ký Mã: {manhatky}?"):
        return

    conn = utils.connect_db()
    if conn is None: return

    try:
        cur = conn.cursor()
        sql = "UPDATE NhatKyNhienLieu SET TrangThaiDuyet = ? WHERE MaNhatKy = ?"
        cur.execute(sql, (new_status, manhatky))
        conn.commit()
        messagebox.showinfo("Thành công", f"Đã {action_text} nhật ký.")
    except Exception as e:
        conn.rollback()
        messagebox.showerror("Lỗi SQL", f"Không thể cập nhật:\n{str(e)}")
    finally:
        if conn: conn.close()
        load_data(widgets, user_role, user_username)

# ================================================================
# PHẦN 4: HÀM TẠO TRANG
# ================================================================

def create_page(master, user_role, user_username):
    """
    Hàm này tạo ra toàn bộ nội dung trang.
    """
    
    # 1. TẠO FRAME CHÍNH
    page_frame = ttk.Frame(master, style="TFrame")
    utils.setup_theme(page_frame)
    
    # === Xử lý LỌC XE theo Tài xế ===
    manv_logged_in, ten_hien_thi_logged_in = get_manv_from_username(user_username)
    
    # Sửa: Admin thấy hết xe, Tài xế chỉ thấy xe của mình
    xe_options = []
    if user_role == "Admin":
        xe_options = utils.load_xe_combobox() # Giả định hàm này tải tất cả xe
    elif manv_logged_in:
        xe_options = utils.load_xe_by_manv(manv_logged_in)
    
    # 2. TẠO GIAO DIỆN
    lbl_title = ttk.Label(page_frame, text="QUẢN LÝ NHẬT KÝ NHIÊN LIỆU", style="Title.TLabel")
    lbl_title.pack(pady=15)

    frame_info = ttk.Frame(page_frame, style="TFrame")
    # Sửa: Chỉ hiện form cho Tài xế
    if user_role == "TaiXe":
        frame_info.pack(pady=5, padx=20, fill="x")
    
    # --- Định nghĩa Style DateEntry ---
    date_entry_style_options = {
        'width': 28, 'date_pattern': 'yyyy-MM-dd',
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
    
    # --- Hàng 0 (Xe và Trạng thái) ---
    ttk.Label(frame_info, text="Xe:").grid(row=0, column=0, padx=5, pady=8, sticky="w")
    cbb_xe_var = tk.StringVar()
    cbb_xe = ttk.Combobox(frame_info, textvariable=cbb_xe_var, values=xe_options, width=28, state='readonly')
    cbb_xe.grid(row=0, column=1, padx=5, pady=8, sticky="w")
    
    ttk.Label(frame_info, text="Trạng thái:").grid(row=0, column=2, padx=15, pady=8, sticky="w")
    trangthai_options = ["Chờ duyệt", "Đã duyệt", "Từ chối"]
    cbb_trangthai_var = tk.StringVar()
    cbb_trangthai = ttk.Combobox(frame_info, textvariable=cbb_trangthai_var, values=trangthai_options, width=38, state='readonly')
    cbb_trangthai.grid(row=0, column=3, padx=5, pady=8, sticky="w")
    cbb_trangthai.set("Chờ duyệt")

    # --- Hàng 1 (Ngày đổ và Tài xế đổ) ---
    ttk.Label(frame_info, text="Ngày đổ:").grid(row=1, column=0, padx=5, pady=8, sticky="w")
    date_ngaydo = DateEntry(frame_info, **date_entry_style_options)
    date_ngaydo.grid(row=1, column=1, padx=5, pady=8, sticky="w")
    
    ttk.Label(frame_info, text="Tài xế đổ:").grid(row=1, column=2, padx=15, pady=8, sticky="w")
    cbb_taixe_var = tk.StringVar()
    # Sửa: Admin mới cần load hết tài xế, tài xế chỉ cần 1
    taixe_options = [ten_hien_thi_logged_in] if user_role == "TaiXe" else utils.load_taixe_combobox()
    
    cbb_taixe = ttk.Combobox(frame_info, textvariable=cbb_taixe_var, values=taixe_options, width=38, state='readonly')
    cbb_taixe.grid(row=1, column=3, padx=5, pady=8, sticky="w")
    if user_role == "TaiXe":
        cbb_taixe.set(ten_hien_thi_logged_in) # Tự động chọn

    # --- Hàng 2 (Số lít và Giờ đổ) ---
    ttk.Label(frame_info, text="Số lít:").grid(row=2, column=0, padx=5, pady=8, sticky="w")
    entry_solit = ttk.Entry(frame_info, width=30)
    entry_solit.grid(row=2, column=1, padx=5, pady=8, sticky="w")
    
    ttk.Label(frame_info, text="Giờ đổ (HH:MM):").grid(row=2, column=2, padx=15, pady=8, sticky="w")
    entry_giodo = ttk.Entry(frame_info, width=40)
    entry_giodo.grid(row=2, column=3, padx=5, pady=8, sticky="w")

    # --- Hàng 3 (Số Odo và Tổng chi phí) ---
    ttk.Label(frame_info, text="Số Odo (Km):").grid(row=3, column=0, padx=5, pady=8, sticky="w")
    entry_soodo = ttk.Entry(frame_info, width=30)
    entry_soodo.grid(row=3, column=1, padx=5, pady=8, sticky="w")
    
    ttk.Label(frame_info, text="Tổng chi phí:").grid(row=3, column=2, padx=15, pady=8, sticky="w")
    entry_tongchiphi = ttk.Entry(frame_info, width=40)
    entry_tongchiphi.grid(row=3, column=3, padx=5, pady=8, sticky="w")
    
    frame_info.columnconfigure(1, weight=1)
    frame_info.columnconfigure(3, weight=1)

    # ===== Frame nút =====
    frame_btn = ttk.Frame(page_frame, style="TFrame")
    frame_btn.pack(pady=10)

    # ===== Bảng danh sách =====
    lbl_ds_text = "Danh sách nhật ký nhiên liệu (Sắp xếp mới nhất)"
    if user_role == "TaiXe":
        lbl_ds_text = "Danh sách nhật ký của bạn"
    lbl_ds = ttk.Label(page_frame, text=lbl_ds_text, style="Header.TLabel")
    lbl_ds.pack(pady=(10, 5), padx=20, anchor="w")

    frame_tree = ttk.Frame(page_frame, style="TFrame")
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
    
    # 3. TẠO TỪ ĐIỂN 'widgets'
    widgets = {
        "tree": tree,
        "cbb_xe": cbb_xe,
        "cbb_taixe": cbb_taixe,
        "date_ngaydo": date_ngaydo,
        "entry_giodo": entry_giodo,
        "entry_solit": entry_solit,
        "entry_tongchiphi": entry_tongchiphi,
        "entry_soodo": entry_soodo,
        "cbb_trangthai": cbb_trangthai,
        "cbb_xe_var": cbb_xe_var,
        "cbb_taixe_var": cbb_taixe_var,
        "cbb_trangthai_var": cbb_trangthai_var,
        "user_role": user_role,
        "user_username": user_username,
        "current_mode": "VIEW" # Thêm biến trạng thái
    }

    # === TẠO NÚT DỰA TRÊN VAI TRÒ ===
    if user_role == "Admin":
        btn_duyet = ttk.Button(frame_btn, text="Duyệt", width=10, style="Accent.TButton",
                               command=lambda: duyet_nhienlieu(widgets, user_role, user_username, 1))
        btn_duyet.grid(row=0, column=0, padx=10)
        
        try:
            style = ttk.Style()
            danger_color = "#DC3545"
            danger_active = "#B02A37"
            style.configure("Danger.TButton", font=("Calibri", 11, "bold"), background=danger_color, foreground="white", relief="flat", padding=5)
            style.map("Danger.TButton", background=[('active', danger_active)], relief=[('pressed', 'sunken')])
        except Exception:
            pass
            
        btn_tuchoi = ttk.Button(frame_btn, text="Từ chối", width=10, style="Danger.TButton",
                                  command=lambda: duyet_nhienlieu(widgets, user_role, user_username, 2))
        btn_tuchoi.grid(row=0, column=1, padx=10)
    
    else: # Nếu là TaiXe
        btn_them = ttk.Button(frame_btn, text="Thêm", width=8, command=lambda: clear_input(widgets, user_role, user_username))
        btn_them.grid(row=0, column=0, padx=10)
        
        btn_luu = ttk.Button(frame_btn, text="Lưu", width=8, command=lambda: save_data(widgets, user_role, user_username))
        btn_luu.grid(row=0, column=1, padx=10)
        
        btn_sua = ttk.Button(frame_btn, text="Sửa", width=8, command=lambda: chon_nhienlieu_de_sua(widgets, user_role))
        btn_sua.grid(row=0, column=2, padx=10)

        btn_huy = ttk.Button(frame_btn, text="Hủy", width=8, command=lambda: load_data(widgets, user_role, user_username))
        btn_huy.grid(row=0, column=3, padx=10)
        
        btn_xoa = ttk.Button(frame_btn, text="Xóa", width=8, command=lambda: xoa_nhienlieu(widgets, user_role, user_username))
        btn_xoa.grid(row=0, column=4, padx=10)

        widgets["btn_sua"] = btn_sua
    
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
    test_root.title("Test Quản lý Nhiên liệu")

    # Giả định utils đã được import và có hàm center_window
    try:
        utils.center_window(test_root, 950, 700)
    except Exception:
        print("Lỗi center_window, dùng kích thước mặc định.")
        test_root.geometry("950x700")
    
    # Sửa: Thay "taixe_A" bằng username tài xế CÓ THẬT của bạn để test lọc xe
    # page = create_page(test_root, "TaiXe", "an.nv")
    page = create_page(test_root, "Admin", "admin")
    page.pack(fill="both", expand=True)
    
    test_root.mainloop()