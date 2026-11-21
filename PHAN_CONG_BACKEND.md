# PHÂN CÔNG CÔNG VIỆC BACKEND LIBMASTER CHO 6 THÀNH VIÊN
*(Đã loại bỏ tính năng gửi email theo yêu cầu)*

> **Dự án**: LibMaster RESTful API Server (FastAPI + MySQL + Pydantic v2)  
> **Nguyên tắc phân chia**: Mỗi thành viên phụ trách trọn vẹn 1 phân hệ nghiệp vụ độc lập tương ứng với 1 bảng CSDL chính (riêng thành viên 6 phụ trách tổng hợp, báo cáo và kiểm thử toàn hệ thống). Đảm bảo không bị chồng chéo code khi làm việc nhóm qua Git.

---

## 📊 BẢNG TỔNG QUAN PHÂN CHIA (6 THÀNH VIÊN)

| STT | Thành Viên | Phân Hệ / Chức Năng Đảm Nhiệm | Các File Phụ Trách | Bảng DB Chính | Độ Khó |
|:---:|:---|:---|:---|:---:|:---:|
| **1** | **Thành viên 1** | **Xác thực, Phân quyền & Quản lý Tài khoản (Auth & Users)** | `backend/routers/auth.py`<br>`backend/routers/users.py`<br>`backend/auth_token.py`<br>`backend/dependencies.py`<br>`backend/models/user.py` | `users` | ⭐⭐⭐⭐ |
| **2** | **Thành viên 2** | **Quản lý Kho Sách & Tồn Kho (Books & Inventory)** | `backend/routers/books.py`<br>`backend/models/book.py` | `books` | ⭐⭐⭐ |
| **3** | **Thành viên 3** | **Quản lý Thể Loại Sách & Đồng Bộ Danh Mục (Categories)** | `backend/routers/categories.py`<br>`backend/models/category.py` | `categories`<br>*(liên kết `books`)* | ⭐⭐⭐ |
| **4** | **Thành viên 4** | **Quản lý Độc Giả & Hồ Sơ Bạn Đọc (Members)** | `backend/routers/members.py`<br>`backend/models/member.py` | `members`<br>*(kiểm tra `borrows`)* | ⭐⭐⭐ |
| **5** | **Thành viên 5** | **Mượn - Trả Sách, Xử Lý Quá Hạn & Tiền Phạt (Borrows & Overdue)** *(Không dùng Email)* | `backend/routers/borrows.py`<br>`backend/routers/overdue.py`<br>`backend/models/borrow.py` | `borrows`<br>*(liên kết `books`, `members`)* | ⭐⭐⭐⭐⭐ |
| **6** | **Thành viên 6** | **Dashboard, Thống Kê Báo Cáo & Kiểm Thử Tự Động (Reports & Testing)** | `backend/routers/dashboard.py`<br>`backend/routers/reports.py`<br>`backend/models/report.py`<br>`backend/database.py`<br>`backend/main.py`<br>`tests/test_api.py` | Tất cả các bảng | ⭐⭐⭐⭐ |

---

## 👤 CHI TIẾT NHIỆM VỤ TỪNG THÀNH VIÊN

---

### 1. THÀNH VIÊN 1: XÁC THỰC, PHÂN QUYỀN & TÀI KHOẢN (AUTH & USERS)

#### a. Chức năng đảm nhiệm
- **Đăng nhập (`POST /api/auth/login`)**: Xác thực tài khoản/mật khẩu, sinh Bearer Token (chặn đăng nhập nếu tài khoản bị khóa `is_locked = 1`).
- **Xác thực phiên (`GET /api/auth/me`)**: Giải mã token, kiểm tra phiên làm việc hiện tại của người dùng.
- **Quản lý người dùng (`/api/users`)**: Toàn bộ CRUD tài khoản thủ thư/nhân viên (Staff/Admin).
- **Khóa & Mở khóa tài khoản (`PUT /api/users/{id}/lock`)**: Cho phép Admin khóa/mở khóa tài khoản nhân viên; chặn tự khóa chính mình và chặn khóa Admin duy nhất đang hoạt động.
- **Phân quyền RBAC**: Cơ chế bảo vệ endpoint bằng dependency `require_admin`; bảo vệ tài khoản admin duy nhất, không cho tự xóa tài khoản của chính mình.

#### b. Luồng hoạt động (Workflow)
```
[Client] 
   │  1. POST /api/auth/login (username, password)
   ▼
[routers/auth.py] ──> [models/user.py] (Tìm user theo username)
   │                      │
   │  2. So khớp hash     ▼
   ├──────────────── [auth_token.py: verify_password]
   │  3. Tạo Bearer Token
   ├──────────────── [auth_token.py: create_access_token]
   ▼
[Client nhận Token] ──> Gửi Header: Authorization: Bearer <token>
   │
   ▼
[Mọi Request API khác] ──> [dependencies.py: get_current_user] (Decode token & xác thực)
                           └──> [dependencies.py: require_admin] (Nếu cần quyền Admin)
```

#### c. File phụ trách
- Router: `backend/routers/auth.py`, `backend/routers/users.py`
- Model: `backend/models/user.py`
- Token & Bảo mật: `backend/auth_token.py`, `backend/dependencies.py`
- Schema: Các class User & Login trong `backend/schemas.py`
- Test liên quan: `tests/test_api.py` (Method `test_02_auth_flow`, `test_09_user_endpoints`)

#### d. Bảng DB liên quan
- **Bảng `users`**:
  - `id`: Khóa chính (INT, Auto Increment)
  - `username`: Tên đăng nhập duy nhất (VARCHAR 50, UNIQUE)
  - `password_hash`: Chuỗi mật khẩu băm bảo mật (VARCHAR 255)
  - `full_name`: Họ và tên (VARCHAR 100)
  - `role`: Vai trò (`admin` hoặc `staff`)
  - `is_locked`: Trạng thái khóa tài khoản (TINYINT 1: 0 = hoạt động, 1 = bị khóa)

#### e. Cần học gì & Học ở đâu?
- **Kiến thức cần học**:
  - Cơ chế xác thực HTTP Authorization Header (Bearer Token).
  - FastAPI Security: `OAuth2PasswordBearer`, Dependency Injection với `Depends()`.
  - Thuật toán băm mật khẩu an toàn (`hashlib`, `bcrypt`, `secrets`).
  - Xử lý mã lỗi HTTP: `401 Unauthorized`, `403 Forbidden`, `409 Conflict`.
- **Tài liệu tham khảo**:
  - [FastAPI Security & OAuth2](https://fastapi.tiangolo.com/tutorial/security/)
  - [FastAPI Dependencies](https://fastapi.tiangolo.com/tutorial/dependencies/)
  - [Password Hashing Best Practices (OWASP)](https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html)

---

### 2. THÀNH VIÊN 2: QUẢN LÝ KHO SÁCH & TỒN KHO (BOOKS & INVENTORY)

#### a. Chức năng đảm nhiệm
- **Danh sách & Tìm kiếm sách (`GET /api/books`)**: Hỗ trợ tìm kiếm theo từ khóa `keyword` (tìm theo tên sách, tác giả, thể loại).
- **CRUD Sách (`/api/books/{id}`)**: Thêm sách mới, xem chi tiết, sửa thông tin, xóa sách.
- **Ràng buộc tồn kho**: Đảm bảo số lượng sách sẵn có (`available`) không vượt quá tổng số sách (`total`), không được âm.
- **Thống kê tồn kho (`GET /api/books/stats/inventory`)**: Báo cáo tổng đầu sách, tổng lượng sách hiện có, số lượng đang mượn.

#### b. Luồng hoạt động (Workflow)
```
[Client] 
   │  GET /api/books?keyword=python
   ▼
[routers/books.py] (Validate tham số query, kiểm tra Token)
   │
   ▼
[models/book.py] ──> Chạy query SQL:
   │                  SELECT * FROM books 
   │                  WHERE title LIKE %kw% OR author LIKE %kw% OR category LIKE %kw%
   ▼
[backend/schemas.py] ──> Ép kiểu & Validate cấu trúc trả về List[BookResponse]
   ▼
[Client nhận JSON danh sách sách]
```

#### c. File phụ trách
- Router: `backend/routers/books.py`
- Model: `backend/models/book.py`
- Schema: `BookCreate`, `BookUpdate`, `BookResponse`, `InventoryStatsResponse` trong `backend/schemas.py`
- Test liên quan: `tests/test_api.py` (Method `test_04_book_endpoints`)

#### d. Bảng DB liên quan
- **Bảng `books`**:
  - `id`: Khóa chính (INT, Auto Increment)
  - `title`: Tựa đề sách (VARCHAR 255)
  - `author`: Tác giả (VARCHAR 255)
  - `category`: Tên thể loại (VARCHAR 100)
  - `total`: Tổng số sách thư viện có (INT >= 1)
  - `available`: Số sách hiện còn trong kho (INT >= 0, available <= total)
  - `cover_image`: Đường dẫn ảnh bìa (VARCHAR 255, nullable)

#### e. Cần học gì & Học ở đâu?
- **Kiến thức cần học**:
  - FastAPI Query Parameters (`keyword: Optional[str] = None`) và Path Parameters (`id: int`).
  - Pydantic Model Validation: Custom validator kiểm tra `available <= total`.
  - Truy vấn MySQL: `LIKE %keyword%`, `SUM()`, `COUNT()`.
- **Tài liệu tham khảo**:
  - [FastAPI Query Parameters and String Validations](https://fastapi.tiangolo.com/tutorial/query-params/)
  - [Pydantic Field Validation](https://docs.pydantic.dev/latest/concepts/validators/)
  - [MySQL LIKE Syntax & Pattern Matching](https://dev.mysql.com/doc/refman/8.0/en/pattern-matching.html)

---

### 3. THÀNH VIÊN 3: QUẢN LÝ THỂ LOẠI SÁCH & ĐỒNG BỘ DANH MỤC (CATEGORIES)

#### a. Chức năng đảm nhiệm
- **Danh sách thể loại (`GET /api/categories`)**: Trả về danh sách thể loại kèm số lượng sách tương ứng (`book_count`).
- **Danh sách tên thể loại (`GET /api/categories/names`)**: Phục vụ dropdown chọn thể loại bên client.
- **Thêm thể loại mới (`POST /api/categories`)**: Kiểm tra không cho phép tạo trùng tên thể loại.
- **Sửa thể loại (`PUT /api/categories/{id}`)**: Cập nhật tên thể loại và **đồng bộ cập nhật tên mới vào toàn bộ các sách** đang thuộc thể loại đó trong bảng `books`.
- **Xóa thể loại (`DELETE /api/categories/{id}`)**: Kiểm tra ràng buộc toàn vẹn, chặn xóa nếu vẫn còn sách thuộc thể loại này.

#### b. Luồng hoạt động (Workflow)
```
[Client] 
   │  PUT /api/categories/3 (Đổi "CNTT" -> "Công Nghệ Thông Tin")
   ▼
[routers/categories.py]
   │
   ▼
[models/category.py: update_category]
   ├── 1. Kiểm tra ID thể loại có tồn tại không.
   ├── 2. Bắt đầu Transaction CSDL:
   │      - UPDATE categories SET name = 'Công Nghệ Thông Tin' WHERE id = 3;
   │      - UPDATE books SET category = 'Công Nghệ Thông Tin' WHERE category = 'CNTT';
   └── 3. Commit Transaction -> Trả về 200 OK.
```

#### c. File phụ trách
- Router: `backend/routers/categories.py`
- Model: `backend/models/category.py`
- Schema: `CategoryCreate`, `CategoryUpdate`, `CategoryResponse` trong `backend/schemas.py`
- Test liên quan: `tests/test_api.py` (Method `test_03_category_endpoints`)

#### d. Bảng DB liên quan
- **Bảng `categories`**:
  - `id`: Khóa chính (INT, Auto Increment)
  - `name`: Tên thể loại (VARCHAR 100, UNIQUE)
- **Bảng `books` (liên kết)**: Đồng bộ trường `category` và đếm số lượng sách (`COUNT(books.id)`).

#### e. Cần học gì & Học ở đâu?
- **Kiến thức cần học**:
  - Quản lý MySQL Transaction (Commit/Rollback khi cập nhật đồng thời nhiều bảng).
  - Truy vấn `LEFT JOIN` và `GROUP BY` để đếm số sách thuộc từng thể loại.
  - Xử lý mã lỗi HTTP: `409 Conflict` (trùng tên), `400 Bad Request` (chặn xóa khi còn sách).
- **Tài liệu tham khảo**:
  - [MySQL Transactions in Python](https://dev.mysql.com/doc/connector-python/en/connector-python-api-mysqlconnection-commit.html)
  - [FastAPI Handling Errors (HTTPException)](https://fastapi.tiangolo.com/tutorial/handling-errors/)
  - [SQL Joins & Group By Guide](https://www.w3schools.com/sql/sql_join.asp)

---

### 4. THÀNH VIÊN 4: QUẢN LÝ ĐỘC GIẢ & HỒ SƠ BẠN ĐỌC (MEMBERS)

#### a. Chức năng đảm nhiệm
- **Danh sách độc giả (`GET /api/members`)**: Lấy danh sách bạn đọc kèm số lượng sách đang mượn thực tế (`active_borrows`).
- **Chi tiết độc giả (`GET /api/members/{id}`)**: Xem thông tin chi tiết độc giả.
- **Thêm/sửa độc giả (`POST / PUT /api/members`)**: Validate định dạng email hợp lệ và số điện thoại.
- **Xóa độc giả (`DELETE /api/members/{id}`)**: Chặn xóa nếu độc giả vẫn đang mượn sách chưa trả (`active_borrows > 0`).

#### b. Luồng hoạt động (Workflow)
```
[Client] 
   │  1. DELETE /api/members/10
   ▼
[routers/members.py]
   │
   ▼
[models/member.py: delete_member]
   ├── 1. Kiểm tra số sách đang mượn:
   │      SELECT COUNT(*) FROM borrows WHERE member_id = 10 AND status = 'borrowed';
   ├── 2. Nếu active_borrows > 0:
   │      Báo lỗi 400 Bad Request: "Không thể xóa độc giả đang mượn sách!"
   └── 3. Nếu active_borrows == 0:
          DELETE FROM members WHERE id = 10;
          Trả về 200 OK.
```

#### c. File phụ trách
- Router: `backend/routers/members.py`
- Model: `backend/models/member.py`
- Schema: `MemberCreate`, `MemberUpdate`, `MemberResponse` trong `backend/schemas.py`
- Test liên quan: `tests/test_api.py` (Method `test_05_member_endpoints`)

#### d. Bảng DB liên quan
- **Bảng `members`**:
  - `id`: Khóa chính (INT, Auto Increment)
  - `name`: Tên bạn đọc (VARCHAR 255)
  - `email`: Email liên hệ (VARCHAR 255)
  - `phone`: Số điện thoại (VARCHAR 50)
- **Bảng `borrows` (liên kết)**: Đếm số phiếu mượn có `status = 'borrowed'` của bạn đọc.

#### e. Cần học gì & Học ở đâu?
- **Kiến thức cần học**:
  - Pydantic Validation: `EmailStr`, regex kiểm tra số điện thoại.
  - Subquery hoặc JOIN để tính toán trường động `active_borrows`.
  - Quy tắc toàn vẹn dữ liệu trong thiết kế RESTful API.
- **Tài liệu tham khảo**:
  - [Pydantic EmailStr & String Constraints](https://docs.pydantic.dev/latest/concepts/types/#extra-data-types)
  - [FastAPI Request Body & Data Validation](https://fastapi.tiangolo.com/tutorial/body/)
  - [Database Integrity Rules Tutorial](https://dev.mysql.com/doc/refman/8.0/en/constraint-foreign-key.html)

---

### 5. THÀNH VIÊN 5: MƯỢN - TRẢ SÁCH, QUÁ HẠN & TIỀN PHẠT (BORROWS & OVERDUE)
*(Hoàn toàn không sử dụng Email/Mailer)*

#### a. Chức năng đảm nhiệm
- **Tạo phiếu mượn (`POST /api/borrows`)**:
  - Kiểm tra độc giả và sách có tồn tại.
  - Kiểm tra số lượng sách còn trong kho (`available > 0`).
  - Tạo phiếu mượn (ngày mượn `borrow_date`, hạn trả `due_date`, trạng thái `borrowed`).
  - Tự động trừ số lượng sách sẵn có: `books.available -= 1`.
- **Ghi nhận trả sách (`POST /api/borrows/{id}/return`)**:
  - Kiểm tra phiếu mượn hợp lệ và chưa trả.
  - Tự động cộng trả lại sách vào kho: `books.available += 1`.
  - **Tính tiền phạt trễ hạn**: So sánh ngày trả thực tế với hạn trả. Nếu trễ `N` ngày thì tính `fine_amount = N * FINE_PER_DAY` (lấy từ `config.py`).
  - Đổi trạng thái phiếu thành `returned`.
- **Gia hạn sách (`POST /api/borrows/{id}/renew`)**: Tăng ngày hẹn trả nếu chưa quá hạn.
- **Danh sách quá hạn & Tiền phạt (`GET /api/overdue`)**:
  - Lọc toàn bộ phiếu có `status = 'borrowed'` và `due_date < CURRENT_DATE()`.
  - Tính số ngày quá hạn và tiền phạt tạm tính theo thời gian thực.
  - Thống kê tổng số phiếu quá hạn và tổng tiền phạt đang nợ.

#### b. Luồng hoạt động (Workflow)
```
--- 1. LUỒNG MƯỢN SÁCH ---
[Client] ──> POST /api/borrows (book_id=3, member_id=2, due_date="2026-12-01")
   │
   ▼
[models/borrow.py: create_borrow]
   ├── Kiểm tra books.available > 0 (Nếu hết sách báo lỗi 400)
   ├── INSERT INTO borrows (book_id, member_id, borrow_date, due_date, status='borrowed')
   ├── UPDATE books SET available = available - 1 WHERE id = 3;
   └── Trả về 201 Created.

--- 2. LUỒNG TRẢ SÁCH & PHẠT ---
[Client] ──> POST /api/borrows/7/return
   │
   ▼
[models/borrow.py: return_book]
   ├── Lấy due_date. Overdue days = max(0, (today - due_date).days)
   ├── fine_amount = overdue_days * FINE_PER_DAY (ví dụ: 3 ngày * 5000 = 15000 VNĐ)
   ├── UPDATE borrows SET return_date=today, fine_amount=..., status='returned' WHERE id=7;
   ├── UPDATE books SET available = available + 1 WHERE id = borrow.book_id;
   └── Trả về thông tin phiếu trả và tiền phạt.

--- 3. LUỒNG DANH SÁCH QUÁ HẠN ---
[Client] ──> GET /api/overdue
   │
   ▼
[models/borrow.py: get_overdue_borrows]
   ├── Query JOIN borrows + members + books WHERE status='borrowed' AND due_date < CURDATE()
   └── Tính overdue_days và fine_amount tạm tính cho từng bạn đọc.
```

#### c. File phụ trách
- Router: `backend/routers/borrows.py`, `backend/routers/overdue.py`
- Model: `backend/models/borrow.py` (phối hợp cập nhật `backend/models/book.py`)
- Schema: `BorrowCreate`, `BorrowResponse`, `BorrowReturnResponse`, `OverdueResponse` trong `backend/schemas.py`
- Cấu hình: `config.py` (biến `FINE_PER_DAY`)
- Test liên quan: `tests/test_api.py` (Method `test_06_borrow_endpoints`, `test_07_overdue_endpoints`)

#### d. Bảng DB liên quan
- **Bảng `borrows`**:
  - `id`: Khóa chính (INT, Auto Increment)
  - `book_id`: Khóa ngoại -> `books(id)`
  - `member_id`: Khóa ngoại -> `members(id)`
  - `borrow_date`: Ngày mượn (DATE)
  - `due_date`: Hạn trả (DATE)
  - `return_date`: Ngày trả thực tế (DATE, NULL khi đang mượn)
  - `fine_amount`: Tiền phạt (INT, mặc định 0)
  - `renew_count`: Số lần gia hạn (INT, mặc định 0)
  - `status`: Trạng thái (`borrowed` hoặc `returned`)
- **Bảng `books`**: Tự động trừ/cộng cột `available`.

#### e. Cần học gì & Học ở đâu?
- **Kiến thức cần học**:
  - Xử lý ngày tháng trong Python: Thư viện `datetime.date`, tính khoảng cách ngày (`delta.days`).
  - Giao dịch CSDL an toàn (Transaction ACID: Mượn sách và trừ kho phải đồng bộ).
  - Lập trình State Machine: Chuyển đổi trạng thái mượn -> trả, chặn trả 2 lần.
- **Tài liệu tham khảo**:
  - [Python datetime — Basic date and time types](https://docs.python.org/3/library/datetime.html)
  - [FastAPI Response Status Codes](https://fastapi.tiangolo.com/tutorial/response-status-code/)
  - [Database Transactions Tutorial](https://www.geeksforgeeks.org/sql-transactions/)

---

### 6. THÀNH VIÊN 6: DASHBOARD, BÁO CÁO THỐNG KÊ & HẠ TẦNG TEST (REPORTS & TESTING)

#### a. Chức năng đảm nhiệm
- **Tổng quan Dashboard (`GET /api/dashboard`)**:
  - Thống kê các chỉ số thời gian thực: Tổng đầu sách, sách đang mượn, tổng bạn đọc, số phiếu quá hạn, tổng tiền phạt đã thu.
  - Danh sách 5-10 giao dịch mượn/trả gần nhất.
- **Báo cáo & Phân tích (`GET /api/reports`)**:
  - KPIs hoạt động thư viện.
  - Top 10 cuốn sách được mượn nhiều nhất.
  - Top các thể loại sách được mượn nhiều nhất.
- **Hạ tầng Server & Database Pool**:
  - Quản lý MySQL Connection Pool trong `backend/database.py`.
  - Khởi tạo FastAPI App, cấu hình CORS Middleware trong `backend/main.py`.
- **Kiểm thử tự động toàn diện (Integration Testing)**:
  - Duy trì và mở rộng bộ test `tests/test_api.py`.
  - Đảm bảo toàn bộ 100% test cases pass sau khi các thành viên ghép code.

#### b. Luồng hoạt động (Workflow)
```
[Client] ──> GET /api/dashboard
   │
   ▼
[routers/dashboard.py] ──> [models/report.py]
   │
   ├── Query 1: COUNT(*) FROM books; SUM(available); SUM(total - available)
   ├── Query 2: COUNT(*) FROM members;
   ├── Query 3: COUNT(*) FROM borrows WHERE status = 'borrowed' AND due_date < CURDATE();
   ├── Query 4: SUM(fine_amount) FROM borrows WHERE status = 'returned';
   └── Query 5: SELECT * FROM borrows ORDER BY borrow_date DESC LIMIT 5;
   │
   ▼
[Tổng hợp thành DashboardResponse] ──> Trả JSON cho Client hiển thị biểu đồ
```

#### c. File phụ trách
- Router: `backend/routers/dashboard.py`, `backend/routers/reports.py`
- Model: `backend/models/report.py`
- Cấu hình & Hạ tầng: `backend/database.py`, `backend/main.py`
- Schema: `DashboardResponse`, `ReportResponse` trong `backend/schemas.py`
- Bộ test tự động: `tests/test_api.py`, `tests/test_gui_integration.py`

#### d. Bảng DB liên quan
- **Truy vấn tổng hợp trên tất cả các bảng**:
  - `books`, `categories`, `members`, `borrows`, `users`.
  - Áp dụng kỹ thuật SQL nâng cao: `COUNT()`, `SUM()`, `GROUP BY`, `ORDER BY ... DESC LIMIT 10`, `DATEDIFF()`.

#### e. Cần học gì & Học ở đâu?
- **Kiến thức cần học**:
  - Truy vấn phân tích và tổng hợp số liệu SQL (`GROUP BY`, `ORDER BY`, Aggregate Functions).
  - Viết Unit Test & Integration Test trong Python với `unittest` và `fastapi.testclient.TestClient`.
  - Quản lý vòng đời ứng dụng FastAPI (`lifespan`, middleware CORS).
  - MySQL Connection Pool và xử lý ngoại lệ mất kết nối (Auto reconnect).
- **Tài liệu tham khảo**:
  - [FastAPI Testing Tutorial](https://fastapi.tiangolo.com/tutorial/testing/)
  - [Python unittest framework](https://docs.python.org/3/library/unittest.html)
  - [MySQL Aggregate Functions & Analytics](https://dev.mysql.com/doc/refman/8.0/en/aggregate-functions.html)
  - [FastAPI CORS Guide](https://fastapi.tiangolo.com/tutorial/cors/)

---

## 🛠️ TIÊU CHUẨN NGHIỆM THU & QUY TRÌNH GHÉP CODE

### 1. Phân chia nhánh Git (Branching Strategy)
- Mỗi thành viên làm việc độc lập trên 1 nhánh tính năng:
  - Thành viên 1: `feature/auth-and-users`
  - Thành viên 2: `feature/books-inventory`
  - Thành viên 3: `feature/categories-management`
  - Thành viên 4: `feature/members-management`
  - Thành viên 5: `feature/borrows-and-overdue`
  - Thành viên 6: `feature/dashboard-reports-tests`

### 2. Tiêu chí hoàn thành (Definition of Done)
1. **Kiểm tra Swagger UI**: Truy cập `http://localhost:8080/docs`, test các endpoint của module mình đảm bảo trả về đúng mã HTTP (200, 201, 400, 401, 404, 409).
2. **Schema đầy đủ**: 100% Request và Response đều có schema rõ ràng trong `schemas.py`.
3. **Chạy test tự động**: Trước khi tạo Pull Request, chạy lệnh test toàn diện và đảm bảo **OK** 100%:
   ```bash
   python -m unittest discover tests
   ```
