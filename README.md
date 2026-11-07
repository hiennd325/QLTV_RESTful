# LibMaster RESTful API Server (new_python)

Dự án chuyển đổi toàn diện hệ thống Quản lý Thư viện sang mô hình **RESTful API** hiện đại bằng **FastAPI**, giữ nguyên 100% chức năng và quy tắc nghiệp vụ từ phiên bản gốc.

---

## 🚀 Tính Năng Chính (Full Features)

- **Authentication & RBAC**: Đăng nhập qua JWT/Bearer Token, phân quyền Admin / Staff, tự động bảo vệ tài khoản admin duy nhất và chặn xóa chính mình.
- **Quản Lý Sách (Books)**: CRUD sách, tìm kiếm theo từ khóa/mã, cập nhật tồn kho tự động, thống kê tồn kho (`/api/books/stats/inventory`).
- **Quản Lý Thể Loại (Categories)**: CRUD thể loại, đồng bộ tên thể loại trong toàn bộ sách liên quan, bảo vệ không cho xóa thể loại nếu còn sách.
- **Quản Lý Độc Giả (Members)**: CRUD bạn đọc, tự động đếm số sách đang mượn (`active_borrows`).
- **Quy Trình Mượn / Trả (Borrows)**: Ghi nhận mượn sách, tự động trừ số lượng sách sẵn có, ghi nhận trả sách, tính số ngày quá hạn và tiền phạt theo ngày (`fine_per_day`).
- **Cảnh Báo Quá Hạn & Gửi Email (Overdue)**: Danh sách phiếu mượn quá hạn, tiền phạt tích lũy, gửi email nhắc nhở đơn lẻ hoặc hàng loạt qua SMTP (chạy ngầm bất đồng bộ Background Tasks).
- **Dashboard & Báo Cáo (Dashboard & Reports)**: Tổng quan số liệu tức thời, danh sách mượn gần nhất, KPIs, Top sách và Top thể loại được mượn nhiều nhất.
- **Tài Liệu API Trực Quan**: Tự động sinh Swagger UI (`/docs`) và ReDoc (`/redoc`).

---

## 📦 Cài Đặt & Khởi Chạy

### 1. Cài đặt môi trường ảo và thư viện:
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Cấu hình CSDL (`.env`):
Kiểm tra thông tin MySQL trong file `.env` (mặc định trỏ tới `library_db`):
```env
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=Admin123
DB_NAME=library_db
FINE_PER_DAY=5000
```

### 3. Khởi tạo dữ liệu mẫu (Tùy chọn):
```bash
python reset_db.py
python seed_data.py
```

### 4. Khởi chạy Ứng Dụng

#### Cách A: Khởi chạy Máy chủ RESTful API (Backend)
```bash
python server.py
# hoặc: python app.py --server
# hoặc: uvicorn main:app --host 0.0.0.0 --port 8080 --reload
```
- **Tài liệu Swagger UI**: `http://localhost:8080/docs`
- **Tài liệu ReDoc**: `http://localhost:8080/redoc`

#### Cách B: Khởi chạy Giao diện Desktop (CustomTkinter GUI Client)
Giao diện giữ nguyên 100% đồ họa gốc, kết nối ngầm hoàn toàn qua RESTful API:
```bash
python app.py
# hoặc: python gui_app.py
```

#### Chạy kiểm tra kết nối API nhanh (Self-test):
```bash
python app.py --test
```

---

## 🧪 Chạy Kiểm Thử Tự Động (Unit & Integration Tests)

Dự án đi kèm bộ kiểm thử API toàn diện kiểm tra tất cả endpoint và mã trạng thái HTTP:
```bash
python -m unittest discover tests
```

---

## 📋 Danh Sách Endpoint RESTful API

### 🔐 Xác Thực (Auth)
| Phương thức | Endpoint | Mô tả | Quyền |
|---|---|---|---|
| `POST` | `/api/auth/login` | Đăng nhập lấy Bearer Token | Public |
| `GET` | `/api/auth/me` | Lấy thông tin tài khoản hiện tại | Đã đăng nhập |

### 👥 Người Dùng (Users)
| Phương thức | Endpoint | Mô tả | Quyền |
|---|---|---|---|
| `GET` | `/api/users` | Danh sách người dùng (hỗ trợ `keyword`) | Admin |
| `GET` | `/api/users/{id}` | Chi tiết người dùng | Admin |
| `POST` | `/api/users` | Tạo tài khoản người dùng | Admin |
| `PUT` | `/api/users/{id}` | Cập nhật thông tin & mật khẩu | Admin |
| `DELETE` | `/api/users/{id}` | Xóa tài khoản người dùng | Admin |

### 📚 Sách (Books)
| Phương thức | Endpoint | Mô tả | Quyền |
|---|---|---|---|
| `GET` | `/api/books` | Danh sách sách (hỗ trợ `keyword`) | Đã đăng nhập |
| `GET` | `/api/books/stats/inventory` | Thống kê số lượng tồn kho | Đã đăng nhập |
| `GET` | `/api/books/{id}` | Chi tiết sách | Đã đăng nhập |
| `POST` | `/api/books` | Thêm sách mới | Đã đăng nhập |
| `PUT` | `/api/books/{id}` | Cập nhật thông tin sách | Đã đăng nhập |
| `DELETE` | `/api/books/{id}` | Xóa sách | Đã đăng nhập |

### 🏷️ Thể Loại (Categories)
| Phương thức | Endpoint | Mô tả | Quyền |
|---|---|---|---|
| `GET` | `/api/categories` | Danh sách thể loại kèm số lượng sách | Đã đăng nhập |
| `GET` | `/api/categories/names` | Danh sách tên các thể loại | Đã đăng nhập |
| `GET` | `/api/categories/{id}` | Chi tiết thể loại | Đã đăng nhập |
| `POST` | `/api/categories` | Thêm thể loại mới | Đã đăng nhập |
| `PUT` | `/api/categories/{id}` | Sửa tên thể loại (đồng bộ vào sách) | Đã đăng nhập |
| `DELETE` | `/api/categories/{id}` | Xóa thể loại (chặn nếu còn sách) | Đã đăng nhập |

### 👤 Độc Giả (Members)
| Phương thức | Endpoint | Mô tả | Quyền |
|---|---|---|---|
| `GET` | `/api/members` | Danh sách độc giả kèm số sách đang mượn | Đã đăng nhập |
| `GET` | `/api/members/{id}` | Chi tiết độc giả | Đã đăng nhập |
| `POST` | `/api/members` | Thêm độc giả mới | Đã đăng nhập |
| `DELETE` | `/api/members/{id}` | Xóa độc giả | Đã đăng nhập |

### 🔄 Mượn / Trả (Borrows)
| Phương thức | Endpoint | Mô tả | Quyền |
|---|---|---|---|
| `GET` | `/api/borrows` | Danh sách phiếu mượn kèm trạng thái | Đã đăng nhập |
| `POST` | `/api/borrows` | Tạo phiếu mượn sách mới | Đã đăng nhập |
| `POST` | `/api/borrows/{id}/return` | Trả sách, tính phạt quá hạn | Đã đăng nhập |

### ⏰ Quá Hạn & Email (Overdue)
| Phương thức | Endpoint | Mô tả | Quyền |
|---|---|---|---|
| `GET` | `/api/overdue` | Danh sách phiếu quá hạn & tổng phạt | Đã đăng nhập |
| `POST` | `/api/overdue/send-reminder` | Gửi email nhắc nhở đơn lẻ | Đã đăng nhập |
| `POST` | `/api/overdue/send-bulk` | Gửi email nhắc nhở hàng loạt | Đã đăng nhập |

### 📊 Tổng Quan & Báo Cáo (Dashboard & Reports)
| Phương thức | Endpoint | Mô tả | Quyền |
|---|---|---|---|
| `GET` | `/api/dashboard` | Thống kê số lượng & giao dịch gần nhất | Đã đăng nhập |
| `GET` | `/api/reports` | KPIs, Top 10 sách & Top 10 thể loại | Đã đăng nhập |

---

## 📁 Cấu Trúc Dự Án `new_python`

```text
├── views/              # Giao diện người dùng CustomTkinter (giữ nguyên 100% đồ họa gốc)
├── routers/            # Các module RESTful API endpoints theo từng tài nguyên
│   ├── auth.py         # /api/auth
│   ├── users.py        # /api/users
│   ├── books.py        # /api/books
│   ├── categories.py   # /api/categories
│   ├── members.py      # /api/members
│   ├── borrows.py      # /api/borrows
│   ├── overdue.py      # /api/overdue
│   ├── dashboard.py    # /api/dashboard
│   └── reports.py      # /api/reports
├── models/             # Business models truy vấn MySQL
├── tests/              # Bộ kiểm thử tự động API & GUI Client
│   ├── test_api.py
│   └── test_gui_integration.py
├── api_client.py       # API Client & API Controllers kết nối HTTP RESTful
├── app.py              # Điểm khởi chạy chính (Desktop GUI Client / Server / Self-test)
├── gui_app.py          # Lớp giao diện chính ModernLibraryApp kết nối API
├── server.py           # Script khởi chạy máy chủ FastAPI Backend
├── main.py             # FastAPI App instance & OpenAPI Docs
├── theme.py            # Theme giao diện sáng, màu sắc Neon Purple & Slate
├── widgets.py          # Thành phần UI bảng dữ liệu, thanh tìm kiếm
├── auth_token.py       # HMAC-SHA256 Token generator & validator (stdlib)
├── config.py           # Đọc cấu hình từ .env
├── database.py         # Kết nối MySQL Connector
├── dependencies.py     # FastAPI dependencies (DB, Models, Auth, RBAC)
├── mailer.py           # Gửi email SMTP
├── schemas.py          # Pydantic schemas cho Request/Response validation
├── reset_db.py         # Tiện ích dọn dẹp CSDL
├── seed_data.py        # Tiện ích tạo dữ liệu mẫu
├── requirements.txt    # Danh sách thư viện Python
└── .env                # File cấu hình môi trường
```
