/* ================================================================
SCRIPT TẠO DATABASE QUẢN LÝ XE VÀ LÁI XE (ĐÃ CHUẨN HÓA)
Ngôn ngữ: T-SQL (SQL Server)

*** SỬA LỖI: Đã thêm logic DROP DATABASE để đảm bảo chạy "Ctrl+A"
luôn thành công, ngay cả khi DB cũ bị lỗi.
================================================================
*/

-- PHẦN 0: DỌN SẠCH VÀ TẠO DATABASE
-- Chuyển về database 'master' để có thể thao tác với [QL_VanTai]
USE master;
GO

-- Kiểm tra xem DB [QL_VanTai] có tồn tại không và xóa nó đi
IF DB_ID('QL_VanTai') IS NOT NULL
BEGIN
    PRINT 'Database [QL_VanTai] đã tồn tại. Đang xóa để tạo lại...';
    -- Đóng tất cả các kết nối đang mở tới DB
    ALTER DATABASE [QL_VanTai] SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
    -- Xóa DB
    DROP DATABASE [QL_VanTai];
    PRINT 'Đã xóa database [QL_VanTai].';
END
GO

-- Tạo database mới
PRINT 'Tạo database [QL_VanTai]...';
CREATE DATABASE [QL_VanTai];
GO

-- Luôn chuyển sang context của [QL_VanTai] để chạy phần còn lại
USE [QL_VanTai];
GO
PRINT 'Đã chuyển sang database [QL_VanTai].';
GO

/* ================================================================
PHẦN 1: DỌN DẸP (BỎ QUA VÌ ĐÃ LÀM Ở TRÊN)
================================================================
*/

/* ================================================================
PHẦN 2: TẠO CÁC BẢNG
================================================================
*/
PRINT '--- Bắt đầu tạo các bảng ---'
GO
-- BẢNG CHA: Quản lý tất cả nhân viên
CREATE TABLE NhanVien (
    MaNhanVien Nvarchar(10) NOT NULL PRIMARY KEY,
    HoVaTen NVARCHAR(100) NOT NULL,
    SoDienThoai VARCHAR(15) NOT NULL,
    DiaChi NVARCHAR(255),
    TrangThai INT DEFAULT 1 NOT NULL -- 0=Nghỉ, 1=Đang làm việc
);
GO
PRINT 'Đã tạo bảng NhanVien'
GO

-- MODULE 2: Bảng quản lý Lái xe (Thông tin chuyên biệt)
CREATE TABLE TaiXe (
    MaNhanVien Nvarchar(10) NOT NULL PRIMARY KEY,
    HangBangLai VARCHAR(10),
    NgayHetHanBangLai DATE,
    DiemDanhGia FLOAT DEFAULT 5.0,
    TrangThaiTaiXe INT DEFAULT 1 NOT NULL, -- 1=Rảnh, 2=Đang lái
    FOREIGN KEY (MaNhanVien) REFERENCES NhanVien(MaNhanVien)
);
GO
PRINT 'Đã tạo bảng TaiXe'
GO

-- BẢNG TÀI KHOẢN (LIÊN KẾT VỚI NHÂN VIÊN)
CREATE TABLE TaiKhoan (
    TenDangNhap NVARCHAR(50) PRIMARY KEY,
    MatKhau NVARCHAR(255) NOT NULL, 
    MaNhanVien Nvarchar(10) NOT NULL,
    VaiTro NVARCHAR(20) DEFAULT 'TaiXe' NOT NULL, -- Ví dụ: 'TaiXe', 'Admin'
    FOREIGN KEY (MaNhanVien) REFERENCES NhanVien(MaNhanVien)
);
GO
PRINT 'Đã tạo bảng TaiKhoan'
GO


-- MODULE 3: Bảng quản lý Phương tiện
CREATE TABLE Xe (
    BienSoXe VARCHAR(15) PRIMARY KEY,
    LoaiXe NVARCHAR(50),
    HangSanXuat NVARCHAR(50),
    DongXe NVARCHAR(50),
    NamSanXuat INT,
    SoKhungVIN VARCHAR(17),
    NgayHetHanDangKiem DATE,
    NgayHetHanBaoHiem DATE,
    TrangThai INT DEFAULT 1 NOT NULL, -- 0=Bảo trì, 1=Hoạt động, 2=Hỏng
    MaNhanVienHienTai Nvarchar(10) NULL, 
    FOREIGN KEY (MaNhanVienHienTai) REFERENCES NhanVien(MaNhanVien)
);
GO
PRINT 'Đã tạo bảng Xe'
GO

-- MODULE 4: Chuyến đi
CREATE TABLE ChuyenDi (
    MaChuyenDi INT PRIMARY KEY IDENTITY(1,1),
    MaNhanVien Nvarchar(10) NOT NULL, 
    BienSoXe VARCHAR(15) NOT NULL,
    DiemBatDau NVARCHAR(MAX),
    DiemKetThuc NVARCHAR(MAX),
    ThoiGianBatDau DATETIME,
    ThoiGianKetThuc DATETIME NULL,
    TrangThai INT DEFAULT 0 NOT NULL, -- 0=Đã gán, 1=Đang thực hiện, 2=Hoàn thành, 3=Hủy
    FOREIGN KEY (MaNhanVien) REFERENCES NhanVien(MaNhanVien),
    FOREIGN KEY (BienSoXe) REFERENCES Xe(BienSoXe)
);
GO
PRINT 'Đã tạo bảng ChuyenDi'
GO

-- MODULE 5: Bảo trì
CREATE TABLE LichSuBaoTri (
    MaBaoTri INT PRIMARY KEY IDENTITY(1,1),
    BienSoXe VARCHAR(15) NOT NULL,
    NgayBaoTri DATE NOT NULL,
    MoTa NVARCHAR(MAX),
    ChiPhi DECIMAL(18, 2),
    FOREIGN KEY (BienSoXe) REFERENCES Xe(BienSoXe)
);
GO
PRINT 'Đã tạo bảng LichSuBaoTri'
GO

-- MODULE 5: Nhiên liệu
CREATE TABLE NhatKyNhienLieu (
    MaNhatKy INT PRIMARY KEY IDENTITY(1,1),
    BienSoXe VARCHAR(15) NOT NULL,
    MaNhanVien Nvarchar(10) NULL, 
    NgayDoNhienLieu DATETIME DEFAULT GETDATE(),
    SoLit DECIMAL(10, 2),
    TongChiPhi DECIMAL(18, 2),
    SoOdo INT,
    FOREIGN KEY (BienSoXe) REFERENCES Xe(BienSoXe),
    FOREIGN KEY (MaNhanVien) REFERENCES NhanVien(MaNhanVien)
);
GO
ALTER TABLE NhatKyNhienLieu
ADD TrangThaiDuyet INT DEFAULT 0 NOT NULL; -- 0=Chờ, 1=Duyệt, 2=Từ chối
PRINT 'Đã tạo bảng NhatKyNhienLieu và thêm cột TrangThaiDuyet'
GO
PRINT '--- Tạo bảng hoàn tất ---'
GO

/* ================================================================
PHẦN 3: THÊM DỮ LIỆU MẪU (ĐÃ CẬP NHẬT)
================================================================
*/

PRINT '--- Bắt đầu thêm dữ liệu mẫu ---'
GO
BEGIN TRY
    -- 1. Thêm Nhân Viên (Bảng cha - Gồm cả Admin và Tài xế)
  INSERT INTO NhanVien (MaNhanVien, HoVaTen, SoDienThoai, DiaChi, TrangThai)
    VALUES
    ('AD001', N'Trần Văn Quản Trị', '0909999999', N'123 Đường Quản Lý, Q. 1, TP. HCM', 1), -- Admin
    ('NV001', N'Nguyễn Văn An', '0901112221', N'456 Đường Tài Xế, Q. Bình Thạnh, TP. HCM', 1),     -- Tài xế
    ('NV002', N'Trần Thị Bình', '0902223332', N'789 Đường Vận Tải, Q. 7, TP. HCM', 1),     -- Tài xế
    ('NV003', N'Lê Văn Cường', '0903334443', N'101 Đường Cũ, Q. 3, TP. HCM', 0);    -- Tài xế (Nghỉ)
    PRINT 'Đã thêm (NhanVien)';

    -- 2. Thêm thông tin chuyên biệt cho Tài xế
    INSERT INTO TaiXe (MaNhanVien, HangBangLai, NgayHetHanBangLai, TrangThaiTaiXe)
    VALUES
    ('NV001', 'B2', '2028-10-20', 1), -- Rảnh
    ('NV002', 'C', '2027-05-15', 2), -- Đang lái
    ('NV003', 'B2', '2026-01-30', 1); -- Đã nghỉ việc (TrangThaiTaiXe vẫn là Rảnh, nhưng NhanVien.TrangThai = 0)
    PRINT 'Đã thêm (TaiXe)';

    -- 3. Thêm Tài khoản (Liên kết với NhanVien)
    INSERT INTO TaiKhoan (TenDangNhap, MatKhau, MaNhanVien, VaiTro)
    VALUES
    ('admin', 'a665a45920422f9d417e48671c3b87588b498f41334b3e83b87f98a846c82006', 'AD001', 'Admin'),
    ('an.nv', 'a665a45920422f9d417e48671c3b87588b498f41334b3e83b87f98a846c82006', 'NV001', 'TaiXe'),
    ('binh.tt', 'a665a45920422f9d417e48671c3b87588b498f41334b3e83b87f98a846c82006', 'NV002', 'TaiXe'),
    ('cuong.lv', 'a665a45920422f9d417e48671c3b87588b498f41334b3e83b87f98a846c82006', 'NV003', 'TaiXe');
    PRINT 'Đã thêm (TaiKhoan)';


    -- 4. Thêm 3 Xe (gán xe cho 2 tài xế)
    INSERT INTO Xe (BienSoXe, LoaiXe, HangSanXuat, DongXe, NamSanXuat, SoKhungVIN, NgayHetHanDangKiem, NgayHetHanBaoHiem, TrangThai, MaNhanVienHienTai)
    VALUES
    ('51G-123.45', N'4 chỗ', 'Toyota', 'Vios', 2022, 'VIN123456789ABC1', '2026-11-01', '2026-11-01', 1, NULL),
    ('29H-678.90', N'Xe tải 1.5T', 'Hyundai', 'Porter', 2021, 'VIN123456789ABC2', '2026-05-01', '2026-05-01', 1, 'NV002'), -- NV002 đang lái xe này
    ('51F-555.55', N'7 chỗ', 'Ford', 'Everest', 2020, 'VIN123456789ABC3', '2025-12-25', '2025-12-25', 0, NULL);
    PRINT 'Đã thêm (Xe)';

    
    -- 5. Thêm Chuyến đi (Đã gộp và đổi thứ tự)
    INSERT INTO ChuyenDi (MaNhanVien, BienSoXe, DiemBatDau, DiemKetThuc, ThoiGianBatDau, ThoiGianKetThuc, TrangThai)
    VALUES
    -- Thêm chuyến đi ĐÃ HOÀN THÀNH cho NV001 (khớp với nhật ký nhiên liệu 5 ngày trước)
    ('NV001', '51G-123.45', N'Sân bay Tân Sơn Nhất', N'Quận 1', DATEADD(day, -5, GETDATE()), DATEADD(hour, 4, DATEADD(day, -5, GETDATE())), 2), -- 2 = Hoàn thành
    -- Thêm chuyến đi ĐANG THỰC HIỆN cho NV002 (khớp với trạng thái "Đang lái")
    ('NV002', '29H-678.90', N'Kho A, Quận 7', N'Kho B, Thủ Đức', DATEADD(hour, -2, GETDATE()), NULL, 1); -- 1 = Đang thực hiện
    PRINT 'Đã thêm (ChuyenDi)';

    -- 6. Thêm Log Bảo trì (cho xe 51F)
    INSERT INTO LichSuBaoTri (BienSoXe, NgayBaoTri, MoTa, ChiPhi)
    VALUES
    ('51F-555.55', GETDATE(), N'Bảo dưỡng định kỳ, thay dầu', 3500000);
    PRINT 'Đã thêm (LichSuBaoTri)';

    -- 7. Thêm Nhật Ký Nhiên Liệu (Đã gộp và đổi thứ tự)
    INSERT INTO NhatKyNhienLieu (BienSoXe, MaNhanVien, NgayDoNhienLieu, SoLit, TongChiPhi, SoOdo, TrangThaiDuyet)
    VALUES
    -- Thêm một nhật ký đã duyệt (khớp với chuyến đi 5 ngày trước của NV001)
    ('51G-123.45', 'NV001', DATEADD(day, -5, GETDATE()), 30.0, 750000, 45200, 1), -- 1 = Đã duyệt
    -- Thêm một nhật ký đang chờ duyệt cho chuyến đi hiện tại của NV002
    ('29H-678.90', 'NV002', GETDATE(), 50.0, 1250000, 85000, 0); -- 0 = Chờ duyệt
    PRINT 'Đã thêm (NhatKyNhienLieu)';

END TRY
BEGIN CATCH

    -- In ra thông tin lỗi chi tiết
    PRINT '!!! GẶP LỖI KHI THÊM DỮ LIỆU MẪU !!!';
    PRINT 'Error Number: ' + CAST(ERROR_NUMBER() AS VARCHAR(10));
    PRINT 'Error Message: ' + ERROR_MESSAGE();
    PRINT 'Error Line: ' + CAST(ERROR_LINE() AS VARCHAR(10));
END CATCH
GO

PRINT '--- Script hoàn tất ---'
GO


-- Lệnh kiểm tra nhanh dữ liệu đã vào
SELECT * FROM NhanVien;
SELECT * FROM TaiXe;
SELECT * FROM TaiKhoan;
SELECT * FROM Xe;
SELECT * FROM ChuyenDi;
SELECT * FROM NhatKyNhienLieu;


DELETE FROM NhatKyNhienLieu;
DELETE FROM LichSuBaoTri;
DELETE FROM ChuyenDi;
DELETE FROM Xe;
DELETE FROM TaiKhoan;
DELETE FROM TaiXe;
DELETE FROM NhanVien;


UPDATE TaiKhoan
SET MatKhau = 'a665a45920422f9d417e48671c3b87588b498f41334b3e83b87f98a846c82006'
WHERE MatKhau = 'hashed_password_123';


/* Thêm cột mới để lưu ai là người nhập */
ALTER TABLE LichSuBaoTri
ADD MaNhanVienNhap NVARCHAR(10) NULL;
GO

/* Tạo khóa ngoại (tùy chọn nhưng nên làm) */
ALTER TABLE LichSuBaoTri
ADD CONSTRAINT FK_BaoTri_NguoiNhap
FOREIGN KEY (MaNhanVienNhap) REFERENCES NhanVien(MaNhanVien);
GO