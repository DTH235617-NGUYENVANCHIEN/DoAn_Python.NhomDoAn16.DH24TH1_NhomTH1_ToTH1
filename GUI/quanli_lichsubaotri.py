import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
import pyodbc 
from datetime import datetime

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
# PHẦN 2: CÁC HÀM TIỆN ÍCH (Tải Combobox)
# ================================================================
def load_xe_combobox():
    """Tải danh sách TẤT CẢ xe (BienSoXe) vào Combobox."""
    conn = connect_db()
    if conn is None:
        return []
    
    try:
        cur = conn.cursor()
        # Lấy tất cả xe, kể cả xe đang bảo trì
        sql = "SELECT BienSoXe FROM Xe ORDER BY BienSoXe"
        cur.execute(sql)
        rows = cur.fetchall()
        return [row[0] for row in rows]
    except Exception as e:
        print(f"Lỗi tải combobox xe: {e}")
        return []
    finally:
        if conn:
            conn.close()

# ================================================================
# PHẦN 3: CÁC HÀM CRUD (CHO BẢO TRÌ)
# ================================================================

def clear_input():
    """Xóa trắng các trường nhập liệu."""
    entry_mabaotri.config(state='normal')
    entry_mabaotri.delete(0, tk.END)
    entry_mabaotri.config(state='disabled')
    
    cbb_xe.set("")
    entry_chiphi.delete(0, tk.END)
    entry_mota.delete("1.0", tk.END) # Xóa Text widget
    
    now = datetime.now()
    date_ngaybaotri.set_date(now.strftime("%Y-%m-%d"))
    
    cbb_xe.focus()

# 
# HÀM ĐÃ SỬA LỖI
# 
def load_data():
    """Tải dữ liệu từ LichSuBaoTri lên Treeview."""
    for i in tree.get_children():
        tree.delete(i)
        
    conn = connect_db()
    if conn is None:
        return
        
    try:
        cur = conn.cursor()
        sql = """
        SELECT MaBaoTri, BienSoXe, NgayBaoTri, MoTa, ChiPhi
        FROM LichSuBaoTri
        ORDER BY NgayBaoTri DESC
        """
        cur.execute(sql)
        rows = cur.fetchall()
        
        for row in rows:
            ma_bt = row[0]
            bienso = row[1]
            
            # === ĐÃ SỬA LỖI TẠI ĐÂY ===
            # Dùng str() thay vì .strftime()
            ngay_bt = str(row[2]) if row[2] else "N/A" 
            # === KẾT THÚC SỬA ===
            
            mota = (row[3] or "")[:50] + "..." # Rút gọn mô tả
            chiphi = row[4]
            
            tree.insert("", tk.END, values=(ma_bt, bienso, ngay_bt, chiphi, mota))
            
    except pyodbc.Error as e:
        messagebox.showerror("Lỗi tải dữ liệu", f"Lỗi SQL: {str(e)}")
    except Exception as e:
        messagebox.showerror("Lỗi không xác định", f"Lỗi: {str(e)}")
    finally:
        if conn:
            conn.close()

def them_baotri():
    """Thêm một lịch sử bảo trì mới."""
    try:
        bienso = cbb_xe_var.get()
        ngay_bt = date_ngaybaotri.get()
        mota = entry_mota.get("1.0", tk.END).strip()
        chiphi = entry_chiphi.get()

        if not bienso or not ngay_bt:
            messagebox.showwarning("Thiếu dữ liệu", "Vui lòng nhập Xe và Ngày bảo trì")
            return

        chiphi_dec = float(chiphi) if chiphi else 0.0

    except Exception as e:
        messagebox.showerror("Lỗi định dạng", f"Chi phí không hợp lệ: {e}")
        return

    conn = connect_db()
    if conn is None:
        return

    try:
        cur = conn.cursor()
        
        sql = """
        INSERT INTO LichSuBaoTri (BienSoXe, NgayBaoTri, MoTa, ChiPhi) 
        VALUES (?, ?, ?, ?)
        """
        cur.execute(sql, (bienso, ngay_bt, mota, chiphi_dec))
        
        conn.commit()
        messagebox.showinfo("Thành công", "Đã thêm lịch sử bảo trì thành công")
        
        clear_input()
        load_data()
        
    except pyodbc.Error as e:
        conn.rollback() 
        messagebox.showerror("Lỗi SQL", f"Không thể thêm:\n{str(e)}")
    except Exception as e:
        conn.rollback()
        messagebox.showerror("Lỗi không xác định", f"Lỗi: {str(e)}")
    finally:
        if conn:
            conn.close()

#
# HÀM ĐÃ SỬA LỖI
#
def chon_baotri_de_sua():
    """Lấy thông tin bảo trì được chọn và điền vào form."""
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Chưa chọn", "Hãy chọn một mục để sửa")
        return

    selected_item = tree.item(selected[0])
    mabaotri = selected_item['values'][0]
    
    conn = connect_db()
    if conn is None:
        return

    try:
        cur = conn.cursor()
        sql = "SELECT * FROM LichSuBaoTri WHERE MaBaoTri = ?"
        cur.execute(sql, (mabaotri,))
        data = cur.fetchone()
        
        if not data:
            messagebox.showerror("Lỗi", "Không tìm thấy dữ liệu.")
            return

        clear_input()
        
        entry_mabaotri.config(state='normal')
        entry_mabaotri.insert(0, data.MaBaoTri)
        entry_mabaotri.config(state='disabled')
        
        cbb_xe.set(data.BienSoXe or "")
        
        # === ĐÃ SỬA LỖI TẠI ĐÂY ===
        # Dùng str() thay vì .strftime()
        if data.NgayBaoTri:
            date_ngaybaotri.set_date(str(data.NgayBaoTri))
        # === KẾT THÚC SỬA ===
            
        entry_chiphi.insert(0, str(data.ChiPhi or ""))
        entry_mota.insert("1.0", data.MoTa or "")

    except pyodbc.Error as e:
        messagebox.showerror("Lỗi SQL", f"Không thể lấy dữ liệu:\n{str(e)}")
    except Exception as e:
        messagebox.showerror("Lỗi không xác định", f"Lỗi: {str(e)}")
    finally:
        if conn:
            conn.close()

def luu_baotri_da_sua():
    """Lưu thay đổi (UPDATE) sau khi sửa."""
    mabaotri = entry_mabaotri.get()
    if not mabaotri:
        messagebox.showwarning("Thiếu dữ liệu", "Không có Mã bảo trì để cập nhật")
        return

    try:
        bienso = cbb_xe_var.get()
        ngay_bt = date_ngaybaotri.get()
        mota = entry_mota.get("1.0", tk.END).strip()
        chiphi = entry_chiphi.get()

        chiphi_dec = float(chiphi) if chiphi else 0.0

    except Exception as e:
        messagebox.showerror("Lỗi định dạng", f"Chi phí không hợp lệ: {e}")
        return

    conn = connect_db()
    if conn is None:
        return
        
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
        
        clear_input()
        load_data()
        
    except pyodbc.Error as e:
        conn.rollback()
        messagebox.showerror("Lỗi SQL", f"Không thể cập nhật:\n{str(e)}")
    except Exception as e:
        conn.rollback()
        messagebox.showerror("Lỗi không xác định", f"Lỗi: {str(e)}")
    finally:
        if conn:
            conn.close()

def xoa_baotri():
    """Xóa lịch sử bảo trì được chọn."""
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Chưa chọn", "Hãy chọn một mục để xóa")
        return

    selected_item = tree.item(selected[0])
    mabaotri = selected_item['values'][0]

    if not messagebox.askyesno("Xác nhận", f"Bạn có chắc chắn muốn xóa Lịch sử Mã: {mabaotri}?"):
        return

    conn = connect_db()
    if conn is None:
        return
        
    try:
        cur = conn.cursor()
        cur.execute("DELETE FROM LichSuBaoTri WHERE MaBaoTri=?", (mabaotri,))
        conn.commit()
        
        messagebox.showinfo("Thành công", "Đã xóa lịch sử bảo trì thành công")
        clear_input()
        load_data()
        
    except pyodbc.Error as e:
        conn.rollback()
        messagebox.showerror("Lỗi SQL", f"Không thể xóa:\n{str(e)}")
    except Exception as e:
        conn.rollback()
        messagebox.showerror("Lỗi không xác định", f"Lỗi: {str(e)}")
    finally:
        if conn:
            conn.close()

# ================================================================
# PHẦN 4: THIẾT KẾ GIAO DIỆN (CHO BẢO TRÌ)
# ================================================================

root = tk.Tk()
root.title("Quản lý Lịch sử Bảo trì (Database QL_VanTai)")

def center_window(w, h):
    ws = root.winfo_screenwidth()
    hs = root.winfo_screenheight()
    x = (ws/2) - (w/2)
    y = (hs/2) - (h/2)
    root.geometry('%dx%d+%d+%d' % (w, h, x, y))

center_window(950, 650) 
root.resizable(False, False)

lbl_title = tk.Label(root, text="QUẢN LÝ LỊCH SỬ BẢO TRÌ", font=("Arial", 18, "bold"))
lbl_title.pack(pady=10)

# Frame thông tin
frame_info = tk.Frame(root)
frame_info.pack(pady=5, padx=10, fill="x")

# --- Hàng 1 ---
tk.Label(frame_info, text="Mã bảo trì:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
entry_mabaotri = tk.Entry(frame_info, width=25, state='disabled')
entry_mabaotri.grid(row=0, column=1, padx=5, pady=5, sticky="w")

tk.Label(frame_info, text="Ngày bảo trì:").grid(row=0, column=2, padx=15, pady=5, sticky="w")
date_ngaybaotri = DateEntry(frame_info, width=30, background='darkblue', foreground='white', date_pattern='yyyy-MM-dd')
date_ngaybaotri.grid(row=0, column=3, padx=5, pady=5, sticky="w")

# --- Hàng 2 ---
tk.Label(frame_info, text="Xe:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
cbb_xe_var = tk.StringVar()
cbb_xe = ttk.Combobox(frame_info, textvariable=cbb_xe_var, width=22, state='readonly')
cbb_xe.grid(row=1, column=1, padx=5, pady=5, sticky="w")
cbb_xe['values'] = load_xe_combobox()

tk.Label(frame_info, text="Chi phí:").grid(row=1, column=2, padx=15, pady=5, sticky="w")
entry_chiphi = tk.Entry(frame_info, width=32)
entry_chiphi.grid(row=1, column=3, padx=5, pady=5, sticky="w")

# --- Hàng 3 (Mô tả) ---
tk.Label(frame_info, text="Mô tả công việc:").grid(row=2, column=0, padx=5, pady=5, sticky="nw")
# Dùng Text widget cho nhiều dòng
entry_mota = tk.Text(frame_info, width=60, height=4)
entry_mota.grid(row=2, column=1, columnspan=3, padx=5, pady=5, sticky="w")

# Cấu hình grid co giãn
frame_info.columnconfigure(1, weight=1)
frame_info.columnconfigure(3, weight=1)

# ===== Frame nút =====
frame_btn = tk.Frame(root)
frame_btn.pack(pady=10)

btn_them = tk.Button(frame_btn, text="Thêm", width=8, command=them_baotri)
btn_them.grid(row=0, column=0, padx=5)

btn_luu = tk.Button(frame_btn, text="Lưu", width=8, command=luu_baotri_da_sua)
btn_luu.grid(row=0, column=1, padx=5)

btn_sua = tk.Button(frame_btn, text="Sửa", width=8, command=chon_baotri_de_sua)
btn_sua.grid(row=0, column=2, padx=5)

btn_huy = tk.Button(frame_btn, text="Hủy", width=8, command=clear_input)
btn_huy.grid(row=0, column=3, padx=5)

btn_xoa = tk.Button(frame_btn, text="Xóa", width=8, command=xoa_baotri)
btn_xoa.grid(row=0, column=4, padx=5)

btn_thoat = tk.Button(frame_btn, text="Thoát", width=8, command=root.quit)
btn_thoat.grid(row=0, column=5, padx=5)


# ===== Bảng danh sách =====
lbl_ds = tk.Label(root, text="Danh sách bảo trì (Sắp xếp mới nhất)", font=("Arial", 10, "bold"))
lbl_ds.pack(pady=5, padx=10, anchor="w")

frame_tree = tk.Frame(root)
frame_tree.pack(pady=10, padx=10, fill="both", expand=True)

scrollbar_y = tk.Scrollbar(frame_tree, orient=tk.VERTICAL)
scrollbar_x = tk.Scrollbar(frame_tree, orient=tk.HORIZONTAL)

columns = ("ma_bt", "bienso", "ngay_bt", "chiphi", "mota")
tree = ttk.Treeview(frame_tree, columns=columns, show="headings", height=10,
                    yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)

scrollbar_y.config(command=tree.yview)
scrollbar_x.config(command=tree.xview)

scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)

# Định nghĩa các cột
tree.heading("ma_bt", text="Mã BT")
tree.column("ma_bt", width=60, anchor="center")

tree.heading("bienso", text="Biển số xe")
tree.column("bienso", width=100)

tree.heading("ngay_bt", text="Ngày bảo trì")
tree.column("ngay_bt", width=100)

tree.heading("chiphi", text="Chi phí")
tree.column("chiphi", width=100, anchor="e")

tree.heading("mota", text="Mô tả")
tree.column("mota", width=300)

tree.pack(fill="both", expand=True)

# ================================================================
# PHẦN 5: CHẠY ỨNG DỤNG
# ================================================================
clear_input() 
load_data() 
root.mainloop()