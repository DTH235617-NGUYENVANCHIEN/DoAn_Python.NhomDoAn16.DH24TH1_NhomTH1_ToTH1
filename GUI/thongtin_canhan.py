# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk, messagebox
import utils # Dùng chung

# ================================================================
# HÀM TẢI DỮ LIỆU (ĐÃ SỬA)
# ================================================================
def load_user_info(username, widgets):
    """
    Tải thông tin TỔNG HỢP (NhanVien + TaiXe) từ CSDL
    và điền vào các Label.
    """
    conn = utils.connect_db()
    if conn is None:
        messagebox.showerror("Lỗi", "Không thể kết nối CSDL.")
        return

    try:
        cur = conn.cursor()
        
        # ================================================================
        # SỬA LỖI SQL:
        # JOIN cả 3 bảng để lấy đủ 8 thông tin cần thiết
        # ================================================================
        sql = """
            SELECT 
                NV.MaNhanVien, NV.HoVaTen, NV.SoDienThoai, NV.DiaChi,
                TX.HangBangLai, TX.NgayHetHanBangLai, TX.DiemDanhGia, TX.TrangThaiTaiXe
            FROM TaiKhoan TK
            JOIN NhanVien NV ON TK.MaNhanVien = NV.MaNhanVien
            JOIN TaiXe TX ON NV.MaNhanVien = TX.MaNhanVien 
            WHERE TK.TenDangNhap = ?
        """
        cur.execute(sql, (username,))
        data = cur.fetchone()

        if not data:
            messagebox.showerror("Lỗi", f"Không tìm thấy thông tin nhân viên/tài xế cho tài khoản: {username}")
            for key, widget in widgets.items():
                widget.config(text="N/A")
            return

        # SỬA: LẤY DỮ LIỆU BẰNG SỐ THỨ TỰ (INDEX)
        # data[0] = MaNhanVien
        # data[1] = HoVaTen
        # data[2] = SoDienThoai
        # data[3] = DiaChi
        # data[4] = HangBangLai
        # data[5] = NgayHetHanBangLai
        # data[6] = DiemDanhGia
        # data[7] = TrangThaiTaiXe
        
        # Điền 4 thông tin cơ bản
        widgets['label_manv'].config(text=data[0] or "N/A")
        widgets['label_hoten'].config(text=data[1] or "N/A")
        widgets['label_sdt'].config(text=data[2] or "N/A")
        widgets['label_diachi'].config(text=data[3] or "N/A")
        
        # Điền 4 thông tin tài xế
        widgets['label_hang_bl'].config(text=data[4] or "N/A")
        widgets['label_ngay_het_han_bl'].config(text=str(data[5]) if data[5] else "N/A")
        widgets['label_diem_dg'].config(text=str(data[6]) if data[6] else "N/A")
        
        # Xử lý TrangThaiTaiXe (từ file SQL của bạn: 1=Rảnh, 2=Đang lái)
        trang_thai_text = "Rảnh" if data[7] == 1 else ("Đang lái" if data[7] == 2 else "N/A")
        widgets['label_trang_thai_tx'].config(text=trang_thai_text)
        
    except Exception as e:
        messagebox.showerror("Lỗi SQL", f"Không thể tải thông tin:\n{str(e)}")
    finally:
        if conn:
            conn.close()

# ================================================================
# HÀM TẠO TRANG (ĐÃ SỬA GIAO DIỆN)
# ================================================================
def create_page(master, username):
    """
    Hàm này được main.py gọi.
    Tạo trang 'Thông tin cá nhân' (dùng LabelFrame và Label).
    """
    
    # 1. TẠO FRAME CHÍNH
    page_frame = ttk.Frame(master, style="TFrame")
    utils.setup_theme(page_frame)

    # === Định nghĩa Style mới cho dữ liệu (Tùy chọn) ===
    try:
        style = ttk.Style()
        style.configure("Header.TLabel", font=("Calibri", 12)) 
        style.configure("Data.TLabel", font=("Calibri", 12, "bold"), foreground=utils.theme_colors["accent"])
    except Exception:
        pass 
    
    # 2. TẠO GIAO DIỆN
    lbl_title = ttk.Label(page_frame, text="THÔNG TIN CÁ NHÂN", style="Title.TLabel")
    lbl_title.pack(pady=15, padx=20)

    # DÙNG LabelFrame (Group Box)
    frame_info = ttk.LabelFrame(page_frame, text="Thông tin chi tiết", style="TLabelframe")
    frame_info.pack(pady=10, padx=20, fill="x", anchor="n")

    widgets = {} # Từ điển để lưu các Label động (để điền dữ liệu)

    # --- Hàm trợ giúp tạo dòng (dùng Label) ---
    def create_info_row(label_text, row_index, col_index=0):
        col_label = col_index * 2 # Cột 0 hoặc 2
        col_data = col_label + 1  # Cột 1 hoặc 3
        
        ttk.Label(frame_info, text=label_text, style="Header.TLabel").grid(row=row_index, column=col_label, padx=(15 if col_index > 0 else 10), pady=8, sticky="e")
        
        # SỬA: ĐỔI CHỮ "Đang tải..." thành "Đang cập nhật..."
        data_label = ttk.Label(frame_info, text="Đang cập nhật...", style="Data.TLabel", width=35) 
        
        data_label.grid(row=row_index, column=col_data, padx=5, pady=8, sticky="w")
        return data_label 

    # --- SỬA: Tạo các dòng (2 cột) ---
    # Cột 1 (Thông tin cơ bản)
    widgets['label_manv'] = create_info_row("Mã nhân viên:", 0)
    widgets['label_hoten'] = create_info_row("Họ và tên:", 1)
    widgets['label_sdt'] = create_info_row("Số điện thoại:", 2)
    widgets['label_diachi'] = create_info_row("Địa chỉ:", 3)

    # Cột 2 (Thông tin tài xế)
    widgets['label_hang_bl'] = create_info_row("Hạng bằng lái:", 0, col_index=1)
    widgets['label_ngay_het_han_bl'] = create_info_row("Ngày hết hạn BL:", 1, col_index=1)
    widgets['label_diem_dg'] = create_info_row("Điểm đánh giá:", 2, col_index=1)
    widgets['label_trang_thai_tx'] = create_info_row("Trạng thái:", 3, col_index=1)
    
    frame_info.grid_rowconfigure(4, minsize=10) 
    frame_info.columnconfigure(1, weight=1) 
    frame_info.columnconfigure(3, weight=1)

    # 3. TẢI DỮ LIỆU
    page_frame.after(100, lambda: load_user_info(username, widgets))

    # 4. TRẢ VỀ FRAME CHÍNH
    return page_frame

# ================================================================
# PHẦN CHẠY THỬ NGHIỆM
# ================================================================
if __name__ == "__main__":
    
    # THAY "an.nv" BẰNG TÊN ĐĂNG NHẬP CỦA BẠN ĐỂ TEST
    USERNAME_TO_TEST = "an.nv" 
    
    test_root = tk.Tk()
    test_root.title("Test Trang Thông Tin Cá Nhân")
    
    try:
        utils.center_window(test_root, 900, 400)
    except Exception as e:
        print(f"Lỗi utils.py: {e}")
        test_root.geometry("900x400")

    page = create_page(test_root, USERNAME_TO_TEST)
    page.pack(fill="both", expand=True)
    
    test_root.mainloop()