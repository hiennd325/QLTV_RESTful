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
python -m scripts.reset_db
python -m scripts.seed_data
```

### 4. Khởi chạy Ứng Dụng

#### Cách A: Dùng file điều phối tổng hợp (`app.py`)
```bash
# Khởi chạy FastAPI Server (cổng 8080):
python app.py --server

# Khởi chạy Desktop GUI Client (CustomTkinter):
python app.py

# Kiểm tra nhanh kết nối Server API (Self-test):
python app.py --test
```

#### Cách B: Khởi chạy từng module độc lập
- **Khởi chạy Máy chủ RESTful API (Backend)**:
  ```bash
  python -m backend.main
  # hoặc dùng uvicorn trực tiếp:
  uvicorn backend.main:app --host 0.0.0.0 --port 8080 --reload
  ```
  - **Tài liệu Swagger UI**: `http://localhost:8080/docs`
  - **Tài liệu ReDoc**: `http://localhost:8080/redoc`

- **Khởi chạy Giao diện Desktop (CustomTkinter GUI Client)**:
  ```bash
  python -m client.main
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
new_python/
├── backend/                  # Toàn bộ mã nguồn RESTful API (FastAPI)
│   ├── models/               # Business models truy vấn MySQL
│   ├── routers/              # Các RESTful API router theo tài nguyên
│   ├── auth_token.py         # Xử lý JWT / HMAC token & Password hash
│   ├── database.py           # Kết nối & quản lý MySQL connection
│   ├── dependencies.py       # FastAPI dependency injection (DB, Auth, RBAC)
│   ├── mailer.py             # Dịch vụ gửi email thông báo / quá hạn
│   ├── schemas.py            # Pydantic schemas (Request & Response validation)
│   └── main.py               # FastAPI App instance & RESTful API entrypoint
│
├── client/                   # Toàn bộ ứng dụng Desktop GUI (CustomTkinter)
│   ├── views/                # Các view / màn hình giao diện người dùng
│   ├── api_client.py         # HTTP client & API Controllers kết nối Backend
│   ├── theme.py              # Bảng màu Neon Purple & Slate theme
│   ├── widgets.py            # Custom UI components (Bảng dữ liệu, Thanh tìm kiếm, ...)
│   └── main.py               # Giao diện chính ModernLibraryApp entrypoint
│
├── scripts/                  # Bộ tiện ích khởi tạo và quản lý dữ liệu CSDL
│   ├── schema.sql            # Cấu trúc bảng MySQL
│   ├── reset_db.py           # Dọn dẹp và đặt lại CSDL
│   └── seed_data.py          # Chèn dữ liệu mẫu thực tế
│
├── tests/                    # Bộ kiểm thử tự động API & GUI Client
│   ├── test_api.py
│   └── test_gui_integration.py
│
├── app.py                    # File điều phối khởi chạy tổng thể (GUI / Server / Test)
├── config.py                 # Tiện ích đọc cấu hình từ .env
├── requirements.txt          # Danh sách thư viện Python phụ thuộc
└── .env                      # File cấu hình biến môi trường
```

