# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk, messagebox
import pyodbc # Để bắt lỗi
import utils # <-- IMPORT FILE DÙNG CHUNG

# ================================================================
# PHẦN 2: CÁC HÀM CRUD
# ================================================================

def set_form_state(is_enabled, widgets):
    """Bật (enable) hoặc Tắt (disable) toàn bộ các trường nhập liệu."""
    if is_enabled:
        widgets['entry_hoten'].config(state='normal')
        widgets['entry_sdt'].config(state='normal')
        widgets['entry_diachi'].config(state='normal')
        widgets['cbb_trangthai_nv'].config(state='readonly')
    else:
        widgets['entry_manv'].config(state='disabled')
        widgets['entry_hoten'].config(state='disabled')
        widgets['entry_sdt'].config(state='disabled')
        widgets['entry_diachi'].config(state='disabled')
        widgets['cbb_trangthai_nv'].config(state='disabled')

def clear_input(widgets):
    """(NÚT THÊM) Xóa trắng và Mở khóa các trường nhập liệu (Chế độ Thêm mới)."""
    set_form_state(is_enabled=True, widgets=widgets)
    widgets['entry_manv'].config(state='normal') 
    
    widgets['entry_manv'].delete(0, tk.END)
    widgets['entry_hoten'].delete(0, tk.END)
    widgets['entry_sdt'].delete(0, tk.END)
    widgets['entry_diachi'].delete(0, tk.END)
    widgets['cbb_trangthai_nv'].set("Đang làm việc")
    
    # Xóa luôn ô tìm kiếm để tránh nhầm lẫn
    if 'entry_timkiem' in widgets:
        widgets['entry_timkiem'].delete(0, tk.END)
        
    widgets['entry_manv'].focus()
    
    tree = widgets['tree']
    if tree.selection():
        tree.selection_remove(tree.selection()[0])
        
    widgets["current_mode"] = "ADD" # <-- THAY ĐỔI: Đặt chế độ

def load_data(widgets, search_term=None):
    """
    THAY ĐỔI: Tải dữ liệu (TOÀN BỘ hoặc THEO TÌM KIẾM) từ NhanVien VÀ LÀM MỜ FORM.
    """
    tree = widgets['tree']
    for i in tree.get_children():
        tree.delete(i)
        
    conn = utils.connect_db()
    if conn is None:
        set_form_state(is_enabled=False, widgets=widgets) 
        return
        
    try:
        cur = conn.cursor()
        
        # === THAY ĐỔI SQL ĐỂ HỖ TRỢ TÌM KIẾM ===
        sql = "SELECT MaNhanVien, HoVaTen, SoDienThoai, DiaChi, TrangThai FROM NhanVien"
        params = []
        
        if search_term:
            # Tìm kiếm theo MaNV, HoTen, hoặc SDT
            sql += " WHERE HoVaTen LIKE ? OR MaNhanVien LIKE ? OR SoDienThoai LIKE ?"
            search_like = f"%{search_term}%"
            params = [search_like, search_like, search_like]
        
        cur.execute(sql, params) # <-- Luôn dùng params (kể cả khi nó rỗng)
        # === KẾT THÚC THAY ĐỔI SQL ===
        
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
            # Nếu không có dữ liệu (kể cả khi tìm kiếm), kích hoạt chế độ Thêm
            clear_input(widgets)
            
    except Exception as e:
        # Nếu tìm kiếm không ra kết quả (rows rỗng) thì không báo lỗi
        if not 'rows' in locals() or not rows:
             clear_input(widgets) # Xóa form nếu không tìm thấy gì
        else:
            messagebox.showerror("Lỗi tải dữ liệu", f"Lỗi SQL: {str(e)}")
            
    finally:
        if conn:
            conn.close()
            
        # Chỉ khóa form và đặt chế độ VIEW nếu có dữ liệu
        if tree.get_children():
            set_form_state(is_enabled=False, widgets=widgets)
            widgets["current_mode"] = "VIEW" 
        # (Nếu không có children, clear_input() đã được gọi và set mode="ADD")

def them_nhanvien(widgets):
    """(LOGIC THÊM) Thêm một nhân viên mới (chỉ vào bảng NhanVien)."""
    manv = widgets['entry_manv'].get()
    hoten = widgets['entry_hoten'].get()
    sdt = widgets['entry_sdt'].get()
    diachi = widgets['entry_diachi'].get()
    
    trangthai_nv_text = widgets['cbb_trangthai_nv_var'].get()
    trangthai_nv_value = 1 if trangthai_nv_text == "Đang làm việc" else 0

    if not manv or not hoten:
        messagebox.showwarning("Thiếu dữ liệu", "Vui lòng nhập Mã Nhân Viên và Họ Tên")
        return False

    conn = utils.connect_db()
    if conn is None: return False

    try:
        cur = conn.cursor()
        sql_nhanvien = "INSERT INTO NhanVien (MaNhanVien, HoVaTen, SoDienThoai, DiaChi, TrangThai) VALUES (?, ?, ?, ?, ?)"
        cur.execute(sql_nhanvien, (manv, hoten, sdt, diachi, trangthai_nv_value))
        conn.commit()
        messagebox.showinfo("Thành công", "Đã thêm nhân viên mới thành công.")
        return True
        
    except pyodbc.IntegrityError:
        conn.rollback()
        messagebox.showerror("Lỗi Trùng lặp", f"Mã nhân viên '{manv}' đã tồn tại.")
        return False
    except Exception as e:
        conn.rollback() 
        messagebox.showerror("Lỗi SQL", f"Không thể thêm nhân viên:\n{str(e)}")
        return False
    finally:
        if conn: conn.close()

def on_item_select(event, widgets):
    """(SỰ KIỆN CLICK) Khi click vào Treeview, chỉ đổ dữ liệu lên form (ở trạng thái mờ)."""
    tree = widgets['tree']
    selected = tree.selection()
    if not selected: return 

    selected_item = tree.item(selected[0])
    manv = selected_item['values'][0]
    
    conn = utils.connect_db()
    if conn is None: return

    try:
        cur = conn.cursor()
        sql = "SELECT * FROM NhanVien WHERE MaNhanVien = ?"
        cur.execute(sql, (manv,))
        data = cur.fetchone()
        
        if not data:
            messagebox.showerror("Lỗi", "Không tìm thấy dữ liệu nhân viên.")
            return

        set_form_state(is_enabled=True, widgets=widgets)
        widgets['entry_manv'].config(state='normal')
        
        widgets['entry_manv'].delete(0, tk.END)
        widgets['entry_hoten'].delete(0, tk.END)
        widgets['entry_sdt'].delete(0, tk.END)
        widgets['entry_diachi'].delete(0, tk.END)
        
        widgets['entry_manv'].insert(0, data.MaNhanVien)
        widgets['entry_hoten'].insert(0, data.HoVaTen or "")
        widgets['entry_sdt'].insert(0, data.SoDienThoai or "")
        widgets['entry_diachi'].insert(0, data.DiaChi or "")
        widgets['cbb_trangthai_nv'].set("Đang làm việc" if data.TrangThai == 1 else "Nghỉ")

    except Exception as e:
        messagebox.showerror("Lỗi không xác định", f"Lỗi: {str(e)}")
    finally:
        if conn: conn.close()
        set_form_state(is_enabled=False, widgets=widgets)
        widgets["current_mode"] = "VIEW" # <-- THAY ĐỔI: Đặt chế độ

def chon_nhanvien_de_sua(widgets): 
    """(NÚT SỬA) Kích hoạt chế độ sửa, Mở khóa form (trừ MaNV)."""
    selected = widgets['tree'].selection()
    if not selected:
        messagebox.showwarning("Chưa chọn", "Hãy chọn một nhân viên trong danh sách trước khi nhấn 'Sửa'")
        return

    if not widgets['entry_manv'].get():
         messagebox.showwarning("Lỗi", "Không tìm thấy mã nhân viên. Vui lòng chọn lại.")
         return

    set_form_state(is_enabled=True, widgets=widgets)
    widgets['entry_manv'].config(state='disabled') 
    widgets['entry_hoten'].focus() 
    widgets["current_mode"] = "EDIT" # <-- THAY ĐỔI: Đặt chế độ

def luu_nhanvien_da_sua(widgets):
    """(LOGIC SỬA) Lưu thay đổi (UPDATE) sau khi sửa (chỉ bảng NhanVien)."""
    manv = widgets['entry_manv'].get()
    if not manv:
        messagebox.showwarning("Thiếu dữ liệu", "Không có Mã Nhân Viên để cập nhật")
        return False

    hoten = widgets['entry_hoten'].get()
    sdt = widgets['entry_sdt'].get()
    diachi = widgets['entry_diachi'].get()

    trangthai_nv_text = widgets['cbb_trangthai_nv_var'].get()
    trangthai_nv_value = 1 if trangthai_nv_text == "Đang làm việc" else 0

    conn = utils.connect_db()
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
        
    except Exception as e:
        conn.rollback()
        messagebox.showerror("Lỗi SQL", f"Không thể cập nhật:\n{str(e)}")
        return False
    finally:
        if conn: conn.close()

# ================================================================
# HÀM LOGIC TÌM KIẾM (THÊM MỚI)
# ================================================================
def tim_kiem_nhanvien(widgets):
    """(LOGIC TÌM KIẾM) Lấy text từ ô tìm kiếm và gọi lại load_data."""
    search_term = widgets['entry_timkiem'].get()
    
    # Nút Hủy cũng sẽ gọi load_data(widgets) (search_term=None), 
    # nên hàm này chỉ cần gọi khi có search_term hoặc gọi từ nút "Tìm"
    load_data(widgets, search_term=search_term)

# ================================================================
# HÀM QUAN TRỌNG NHẤT (SỬA LỖI)
# ================================================================
def save_data(widgets):
    """Lưu dữ liệu, tự động kiểm tra xem nên Thêm mới (INSERT) hay Cập nhật (UPDATE)."""
    
    success = False
    
    # THAY ĐỔI: Kiểm tra biến trạng thái, KHÔNG kiểm tra widget
    if widgets.get("current_mode") == "EDIT":
        success = luu_nhanvien_da_sua(widgets)
    elif widgets.get("current_mode") == "ADD":
        success = them_nhanvien(widgets)
    else: 
        messagebox.showwarning("Chưa Sửa/Thêm", "Vui lòng nhấn 'Thêm' hoặc 'Sửa' trước khi Lưu.")
        return

    if success:
        # THAY ĐỔI: Tải lại toàn bộ dữ liệu (không tìm kiếm nữa)
        widgets['entry_timkiem'].delete(0, tk.END) # Xóa ô tìm kiếm
        load_data(widgets) # Tải lại toàn bộ
# ================================================================


def xoa_nhanvien_vinhvien(widgets):
    """(NGUY HIỂM) Xóa vĩnh viễn nhân viên và MỌI DỮ LIỆU LIÊN QUAN."""
    selected = widgets['tree'].selection()
    if not selected:
        messagebox.showwarning("Chưa chọn", "Hãy chọn một nhân viên trong danh sách để xóa")
        return
        
    manv = widgets['entry_manv'].get() 
    if not manv:
         messagebox.showwarning("Lỗi", "Không tìm thấy mã nhân viên. Vui lòng chọn lại.")
         return

    msg_xacnhan = (
        f"BẠN CÓ CHẮC CHẮN MUỐN XÓA VĨNH VIỄN NHÂN VIÊN '{manv}'?\n\n"
        "CẢNH BÁO: Thao tác này KHÔNG THỂ hoàn tác.\n"
        "Tất cả dữ liệu liên quan (chuyến đi, nhiên liệu, tài khoản,...) sẽ bị XÓA SẠCH."
    )
    if not messagebox.askyesno("XÁC NHẬN XÓA VĨNH VIỄN", msg_xacnhan):
        return

    conn = utils.connect_db()
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
        
        # Tải lại dữ liệu sau khi xóa
        widgets['entry_timkiem'].delete(0, tk.END) # Xóa ô tìm kiếm
        load_data(widgets) 
        
    except Exception as e:
        conn.rollback()
        messagebox.showerror("Lỗi SQL", f"Không thể xóa nhân viên:\n{str(e)}")
    finally:
        if conn: conn.close()

# ================================================================
# PHẦN 4: HÀM TẠO TRANG (HÀM CHÍNH ĐỂ MAIN.PY GỌI)
# ================================================================

def create_page(master):
    """
    Hàm này được main.py gọi. 
    Nó tạo ra toàn bộ nội dung trang và đặt vào 'master' (là main_frame).
    """
    
    # 1. TẠO FRAME CHÍNH
    page_frame = ttk.Frame(master, style="TFrame")
    
    # === CÀI ĐẶT STYLE (CHỈ CẦN 1 DÒNG) ===
    utils.setup_theme(page_frame) 
    # ==================================

    
    # 2. TẠO GIAO DIỆN (ĐẶT VÀO 'page_frame')
    lbl_title = ttk.Label(page_frame, text="QUẢN LÝ TOÀN BỘ NHÂN VIÊN", style="Title.TLabel")
    lbl_title.pack(pady=15) 

    frame_info = ttk.Frame(page_frame, style="TFrame")
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
    frame_btn = ttk.Frame(page_frame, style="TFrame")
    frame_btn.pack(pady=10)

    # ===== Frame tìm kiếm (THÊM MỚI) =====
    frame_search = ttk.Frame(page_frame, style="TFrame")
    frame_search.pack(pady=(0, 10), padx=20, fill="x") # Đặt ngay sau frame_btn

    lbl_timkiem = ttk.Label(frame_search, text="Tìm kiếm (Tên, Mã, SĐT):")
    lbl_timkiem.grid(row=0, column=0, padx=5, pady=5)
    
    entry_timkiem = ttk.Entry(frame_search, width=40)
    entry_timkiem.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
    
    # Nút Tìm kiếm sẽ được gán lệnh sau khi có 'widgets'
    btn_timkiem = ttk.Button(frame_search, text="Tìm kiếm", width=10) 
    btn_timkiem.grid(row=0, column=2, padx=10, pady=5)
    
    frame_search.columnconfigure(1, weight=1) # Cho ô entry co giãn
    # ===== Kết thúc thêm Frame tìm kiếm =====

    # ===== Bảng danh sách =====
    lbl_ds = ttk.Label(page_frame, text="Danh sách nhân viên (Tất cả)", style="Header.TLabel")
    lbl_ds.pack(pady=(10, 5), padx=20, anchor="w")

    frame_tree = ttk.Frame(page_frame, style="TFrame")
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
    
    # 3. TẠO TỪ ĐIỂN 'widgets'
    widgets = {
        "tree": tree,
        "entry_manv": entry_manv,
        "entry_hoten": entry_hoten,
        "entry_sdt": entry_sdt,
        "entry_diachi": entry_diachi,
        "cbb_trangthai_nv": cbb_trangthai_nv,
        "cbb_trangthai_nv_var": cbb_trangthai_nv_var,
        "entry_timkiem": entry_timkiem, # <-- THÊM MỚI
        "current_mode": "VIEW" # <-- THAY ĐỔI: Thêm biến trạng thái
    }

    # (Code tạo nút)
    btn_them = ttk.Button(frame_btn, text="Thêm", width=8, command=lambda: clear_input(widgets)) 
    btn_them.grid(row=0, column=0, padx=10)
    btn_luu = ttk.Button(frame_btn, text="Lưu", width=8, command=lambda: save_data(widgets)) 
    btn_luu.grid(row=0, column=1, padx=10)
    btn_sua = ttk.Button(frame_btn, text="Sửa", width=8, command=lambda: chon_nhanvien_de_sua(widgets)) 
    btn_sua.grid(row=0, column=2, padx=10)
    
    # THAY ĐỔI: Nút Hủy giờ sẽ gọi load_data (không có tham số) để tải lại toàn bộ
    btn_huy = ttk.Button(frame_btn, text="Hủy", width=8, command=lambda: (
        widgets['entry_timkiem'].delete(0, tk.END), # Xóa ô tìm kiếm
        load_data(widgets) # Tải lại toàn bộ
    ))
    btn_huy.grid(row=0, column=3, padx=10)
    
    btn_xoa = ttk.Button(frame_btn, text="Xóa", width=8, command=lambda: xoa_nhanvien_vinhvien(widgets)) 
    btn_xoa.grid(row=0, column=4, padx=10)
    
    # === GÁN LỆNH CHO NÚT TÌM KIẾM (THÊM MỚI) ===
    btn_timkiem.config(command=lambda: tim_kiem_nhanvien(widgets))
    # Thêm binding phím Enter cho ô tìm kiếm
    entry_timkiem.bind("<Return>", lambda event: tim_kiem_nhanvien(widgets))
    # === KẾT THÚC GÁN LỆNH ===
    
    # 4. KẾT NỐI BINDING (SỰ KIỆN CLICK)
    tree.bind("<<TreeviewSelect>>", lambda event: on_item_select(event, widgets)) 

    # 5. TẢI DỮ LIỆU LẦN ĐẦU
    load_data(widgets) 
    
    # 6. TRẢ VỀ FRAME CHÍNH
    return page_frame

# ================================================================
# PHẦN 5: CHẠY THỬ NGHIỆM
# ================================================================
if __name__ == "__main__":
    
    test_root = tk.Tk()
    test_root.title("Test Quản lý Nhân Viên")
    
    try:
        utils.center_window(test_root, 900, 650) 
    except AttributeError:
        print("Lưu ý: Chạy test không có file utils.py. Đang dùng kích thước mặc định.")
        test_root.geometry("900x650")
    except Exception as e:
         print(f"Lỗi: {e}. Đặt kích thước cửa sổ mặc định.")
         test_root.geometry("900x650")
    
    page = create_page(test_root) 
    page.pack(fill="both", expand=True)
    
    test_root.mainloop()