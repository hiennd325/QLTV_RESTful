"""
Kiểm thử toàn diện RESTful API cho LibMaster (new_python)
"""
import unittest
from fastapi.testclient import TestClient
from backend.main import app


class TestLibraryAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

        # Đăng nhập lấy admin token
        res = cls.client.post("/api/auth/login", json={"username": "admin", "password": "admin123"})
        if res.status_code != 200:
            raise RuntimeError(f"Admin login failed: {res.text}")
        cls.admin_token = res.json()["access_token"]
        cls.admin_headers = {"Authorization": f"Bearer {cls.admin_token}"}

        # Đăng nhập lấy staff token
        res_s = cls.client.post("/api/auth/login", json={"username": "staff", "password": "staff123"})
        if res_s.status_code != 200:
            raise RuntimeError(f"Staff login failed: {res_s.text}")
        cls.staff_token = res_s.json()["access_token"]
        cls.staff_headers = {"Authorization": f"Bearer {cls.staff_token}"}

    def test_01_root_and_health(self):
        r = self.client.get("/")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json()["status"], "running")

        r_health = self.client.get("/health")
        self.assertEqual(r_health.status_code, 200)
        self.assertEqual(r_health.json()["status"], "healthy")

    def test_02_auth_flow(self):
        # 1. Login sai mật khẩu -> 401
        res = self.client.post("/api/auth/login", json={"username": "admin", "password": "wrongpassword"})
        self.assertEqual(res.status_code, 401)

        # 2. Get me có token -> 200
        res_me = self.client.get("/api/auth/me", headers=self.admin_headers)
        self.assertEqual(res_me.status_code, 200)
        self.assertEqual(res_me.json()["username"], "admin")
        self.assertEqual(res_me.json()["role"], "admin")

        # 3. Get me không token -> 401
        res_no_tok = self.client.get("/api/auth/me")
        self.assertEqual(res_no_tok.status_code, 401)

    def test_03_category_endpoints(self):
        test_cat = "Thể Loại API Test"
        # 1. Thêm thể loại mới
        r_add = self.client.post("/api/categories", json={"name": test_cat}, headers=self.staff_headers)
        self.assertEqual(r_add.status_code, 201)
        cat_id = r_add.json()["data"]["category_id"]

        # 2. Thêm trùng tên -> 409
        r_dup = self.client.post("/api/categories", json={"name": test_cat}, headers=self.staff_headers)
        self.assertEqual(r_dup.status_code, 409)

        # 3. Lấy danh sách tên
        r_names = self.client.get("/api/categories/names", headers=self.staff_headers)
        self.assertEqual(r_names.status_code, 200)
        self.assertIn(test_cat, r_names.json())

        # 4. Lấy chi tiết theo ID
        r_get = self.client.get(f"/api/categories/{cat_id}", headers=self.staff_headers)
        self.assertEqual(r_get.status_code, 200)
        self.assertEqual(r_get.json()["name"], test_cat)

        # 5. Cập nhật thể loại
        renamed_cat = "Thể Loại API Test Đã Sửa"
        r_up = self.client.put(f"/api/categories/{cat_id}", json={"name": renamed_cat}, headers=self.staff_headers)
        self.assertEqual(r_up.status_code, 200)

        # 6. Xóa thể loại
        r_del = self.client.delete(f"/api/categories/{cat_id}", headers=self.staff_headers)
        self.assertEqual(r_del.status_code, 200)

    def test_04_book_endpoints(self):
        # 1. Thêm sách
        payload = {
            "title": "Sách Lập Trình RESTful",
            "author": "Chuyên Gia API",
            "category": "Công Nghệ",
            "total": 6
        }
        r_add = self.client.post("/api/books", json=payload, headers=self.staff_headers)
        self.assertEqual(r_add.status_code, 201)
        book_id = r_add.json()["data"]["book_id"]

        # 2. Tìm kiếm sách
        r_search = self.client.get("/api/books?keyword=RESTful", headers=self.staff_headers)
        self.assertEqual(r_search.status_code, 200)
        books = r_search.json()
        self.assertGreater(len(books), 0)
        self.assertEqual(books[0]["id"], book_id)

        # 3. Cập nhật sách
        update_payload = {
            "title": "Sách Lập Trình RESTful Nâng Cao",
            "author": "Chuyên Gia API",
            "category": "Công Nghệ",
            "total": 10
        }
        r_up = self.client.put(f"/api/books/{book_id}", json=update_payload, headers=self.staff_headers)
        self.assertEqual(r_up.status_code, 200)

        # 3b. Kiểm tra upload ảnh bìa độc lập
        fake_img = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15c4"
        r_upload = self.client.post(
            "/api/books/upload-cover",
            files={"file": ("cover.png", fake_img, "image/png")},
            headers=self.staff_headers
        )
        self.assertEqual(r_upload.status_code, 200)
        cover_path = r_upload.json()["data"]["cover_image"]
        self.assertTrue(cover_path.startswith("/uploads/covers/"))

        # Kiểm tra file tĩnh có tải được không
        r_static = self.client.get(cover_path)
        self.assertEqual(r_static.status_code, 200)

        # Kiểm tra upload ảnh bìa trực tiếp cho sách
        r_book_cover = self.client.post(
            f"/api/books/{book_id}/cover",
            files={"file": ("book_cover.jpg", fake_img, "image/jpeg")},
            headers=self.staff_headers
        )
        self.assertEqual(r_book_cover.status_code, 200)
        book_cover_path = r_book_cover.json()["data"]["cover_image"]

        # Kiểm tra chi tiết sách đã có cover_image
        r_detail = self.client.get(f"/api/books/{book_id}", headers=self.staff_headers)
        self.assertEqual(r_detail.status_code, 200)
        self.assertEqual(r_detail.json()["cover_image"], book_cover_path)

        # Kiểm tra định dạng không hợp lệ -> 400
        r_bad_ext = self.client.post(
            "/api/books/upload-cover",
            files={"file": ("bad.exe", b"binary", "application/octet-stream")},
            headers=self.staff_headers
        )
        self.assertEqual(r_bad_ext.status_code, 400)

        # 4. Kiểm tra thống kê tồn kho
        r_stats = self.client.get("/api/books/stats/inventory", headers=self.staff_headers)
        self.assertEqual(r_stats.status_code, 200)
        self.assertIn("books_total", r_stats.json())
        self.assertIn("books_available", r_stats.json())

        # 5. Xóa sách
        r_del = self.client.delete(f"/api/books/{book_id}", headers=self.staff_headers)
        self.assertEqual(r_del.status_code, 200)

        # Kiểm tra sau xóa -> 404
        r_get = self.client.get(f"/api/books/{book_id}", headers=self.staff_headers)
        self.assertEqual(r_get.status_code, 404)

    def test_05_member_endpoints(self):
        # 1. Thêm độc giả
        mem_payload = {
            "name": "Độc Giả RESTful",
            "email": "restful_member@example.com",
            "phone": "0987654321"
        }
        r_add = self.client.post("/api/members", json=mem_payload, headers=self.staff_headers)
        self.assertEqual(r_add.status_code, 201)
        member_id = r_add.json()["data"]["member_id"]

        # 2. Lấy danh sách độc giả
        r_list = self.client.get("/api/members?keyword=restful_member@example.com", headers=self.staff_headers)
        self.assertEqual(r_list.status_code, 200)
        mems = r_list.json()
        self.assertGreater(len(mems), 0)
        self.assertEqual(mems[0]["id"], member_id)

        # 3. Lấy chi tiết
        r_get = self.client.get(f"/api/members/{member_id}", headers=self.staff_headers)
        self.assertEqual(r_get.status_code, 200)
        self.assertEqual(r_get.json()["name"], "Độc Giả RESTful")

        # 4. Xóa độc giả
        r_del = self.client.delete(f"/api/members/{member_id}", headers=self.staff_headers)
        self.assertEqual(r_del.status_code, 200)

    def test_06_borrow_and_return_flow(self):
        # Tạo sách và độc giả
        r_b = self.client.post("/api/books", json={
            "title": "Sách Mượn Trả API",
            "author": "Tác giả",
            "category": "Khoa Học",
            "total": 3
        }, headers=self.staff_headers)
        book_id = r_b.json()["data"]["book_id"]

        r_m = self.client.post("/api/members", json={
            "name": "Bạn Mượn API",
            "email": "borrower_api@example.com",
            "phone": "0912345678"
        }, headers=self.staff_headers)
        member_id = r_m.json()["data"]["member_id"]

        # 1. Mượn sách
        r_borrow = self.client.post("/api/borrows", json={
            "member_id": member_id,
            "book_id": book_id,
            "days": 14
        }, headers=self.staff_headers)
        self.assertEqual(r_borrow.status_code, 201)
        borrow_id = r_borrow.json()["data"]["borrow_id"]

        # 2. Kiểm tra sách tồn kho đã giảm
        b_info = self.client.get(f"/api/books/{book_id}", headers=self.staff_headers).json()
        self.assertEqual(b_info["available"], 2)

        # 3. Lấy danh sách mượn
        r_borrows = self.client.get(f"/api/borrows?keyword={borrow_id}", headers=self.staff_headers)
        self.assertEqual(r_borrows.status_code, 200)
        items = r_borrows.json()
        self.assertTrue(any(i["id"] == borrow_id for i in items))

        # 4. Trả sách
        r_ret = self.client.post(f"/api/borrows/{borrow_id}/return", headers=self.staff_headers)
        self.assertEqual(r_ret.status_code, 200)
        self.assertEqual(r_ret.json()["borrow_id"], borrow_id)

        # 5. Kiểm tra sách tồn kho đã hồi phục
        b_info_restored = self.client.get(f"/api/books/{book_id}", headers=self.staff_headers).json()
        self.assertEqual(b_info_restored["available"], 3)

        # Dọn dẹp
        self.client.delete(f"/api/books/{book_id}", headers=self.staff_headers)
        self.client.delete(f"/api/members/{member_id}", headers=self.staff_headers)

    def test_07_overdue_and_emails(self):
        # 1. Lấy danh sách quá hạn
        r_over = self.client.get("/api/overdue", headers=self.staff_headers)
        self.assertEqual(r_over.status_code, 200)
        data = r_over.json()
        self.assertIn("items", data)
        self.assertIn("total_fine", data)

        # 2. Lên lịch gửi email nhắc nhở đơn lẻ
        r_mail = self.client.post("/api/overdue/send-reminder", json={
            "recipient": "test_reader@example.com",
            "name": "Độc Giả Thử Nghiệm",
            "book_title": "Sách Mượn Quá Hạn",
            "due_date": "2026-10-01",
            "fine": 15000
        }, headers=self.staff_headers)
        self.assertEqual(r_mail.status_code, 200)
        self.assertTrue(r_mail.json()["success"])

        # 3. Lên lịch gửi email hàng loạt
        r_bulk = self.client.post("/api/overdue/send-bulk", headers=self.staff_headers)
        self.assertEqual(r_bulk.status_code, 200)
        self.assertTrue(r_bulk.json()["success"])

    def test_08_dashboard_and_reports(self):
        # 1. Dashboard
        r_dash = self.client.get("/api/dashboard", headers=self.staff_headers)
        self.assertEqual(r_dash.status_code, 200)
        d = r_dash.json()
        self.assertIn("books_total", d)
        self.assertIn("books_available", d)
        self.assertIn("recent_borrows", d)

        # 2. Reports
        r_rep = self.client.get("/api/reports?limit=5", headers=self.staff_headers)
        self.assertEqual(r_rep.status_code, 200)
        rep = r_rep.json()
        self.assertIn("kpis", rep)
        self.assertIn("top_books", rep)
        self.assertIn("top_categories", rep)

    def test_09_users_and_rbac(self):
        # 1. Staff không được phép truy cập /api/users -> 403 Forbidden
        r_forbidden = self.client.get("/api/users", headers=self.staff_headers)
        self.assertEqual(r_forbidden.status_code, 403)

        # 2. Admin truy cập /api/users -> 200
        r_users = self.client.get("/api/users", headers=self.admin_headers)
        self.assertEqual(r_users.status_code, 200)

        # 3. Admin tạo user mới
        u_payload = {
            "username": "api_new_staff",
            "password": "staff_pass_123",
            "full_name": "Nhân Viên Mới API",
            "role": "staff"
        }
        r_create = self.client.post("/api/users", json=u_payload, headers=self.admin_headers)
        self.assertEqual(r_create.status_code, 201)
        new_uid = r_create.json()["data"]["user_id"]

        # 4. User mới đăng nhập thành công
        r_login_new = self.client.post("/api/auth/login", json={"username": "api_new_staff", "password": "staff_pass_123"})
        self.assertEqual(r_login_new.status_code, 200)

        # 5. Cập nhật user
        r_up = self.client.put(f"/api/users/{new_uid}", json={
            "full_name": "Nhân Viên Đã Đổi Tên",
            "role": "staff",
            "password": "new_staff_pass"
        }, headers=self.admin_headers)
        self.assertEqual(r_up.status_code, 200)

        # 5.1. Admin tự khóa chính mình -> 400
        admin_info = self.client.get("/api/auth/me", headers=self.admin_headers).json()
        r_lock_self = self.client.put(f"/api/users/{admin_info['id']}/lock", json={"is_locked": True}, headers=self.admin_headers)
        self.assertEqual(r_lock_self.status_code, 400)

        # 5.2. Khóa tài khoản user mới -> 200
        r_lock = self.client.put(f"/api/users/{new_uid}/lock", json={"is_locked": True}, headers=self.admin_headers)
        self.assertEqual(r_lock.status_code, 200)

        # 5.3. Tài khoản bị khóa đăng nhập -> 403
        r_login_locked = self.client.post("/api/auth/login", json={"username": "api_new_staff", "password": "new_staff_pass"})
        self.assertEqual(r_login_locked.status_code, 403)

        # 5.4. Mở khóa tài khoản -> 200
        r_unlock = self.client.put(f"/api/users/{new_uid}/lock", json={"is_locked": False}, headers=self.admin_headers)
        self.assertEqual(r_unlock.status_code, 200)

        # 5.5. Đăng nhập lại sau khi mở khóa -> 200
        r_login_unlocked = self.client.post("/api/auth/login", json={"username": "api_new_staff", "password": "new_staff_pass"})
        self.assertEqual(r_login_unlocked.status_code, 200)

        # 6. Admin tự xóa chính mình -> 400
        r_del_self = self.client.delete(f"/api/users/{admin_info['id']}", headers=self.admin_headers)
        self.assertEqual(r_del_self.status_code, 400)

        # 7. Xóa user mới tạo -> 200
        r_del = self.client.delete(f"/api/users/{new_uid}", headers=self.admin_headers)
        self.assertEqual(r_del.status_code, 200)


if __name__ == "__main__":
    unittest.main()
