"""
Kiểm thử tích hợp API Controllers và Giao diện cho LibMaster
"""
import unittest
from unittest.mock import MagicMock
from fastapi.testclient import TestClient
from main import app
from api_client import (
    APIClient,
    UserAPIController,
    BookAPIController,
    CategoryAPIController,
    MemberAPIController,
    BorrowAPIController,
    OverdueAPIController,
    DashboardAPIController,
    ReportAPIController
)
from views import (
    DashboardView,
    BooksView,
    CategoriesView,
    MembersView,
    BorrowsView,
    OverdueView,
    ReportsView,
    UsersView,
    LoginView
)


class TestGUIIntegration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Dùng TestClient để giả lập HTTP server
        cls.test_client = TestClient(app)

        # Tạo APIClient bọc TestClient
        cls.api = APIClient()
        cls.api.client = cls.test_client

        cls.user_ctrl = UserAPIController(cls.api)
        cls.book_ctrl = BookAPIController(cls.api)
        cls.cat_ctrl = CategoryAPIController(cls.api)
        cls.member_ctrl = MemberAPIController(cls.api)
        cls.borrow_ctrl = BorrowAPIController(cls.api)
        cls.overdue_ctrl = OverdueAPIController(cls.api)
        cls.dash_ctrl = DashboardAPIController(cls.api)
        cls.report_ctrl = ReportAPIController(cls.api)

        # 1. Login qua API Controller
        user, msg = cls.user_ctrl.login("admin", "admin123")
        if not user:
            raise RuntimeError(f"Login failed: {msg}")
        cls.admin_user = user

    def test_01_user_controller_api(self):
        # Thêm user
        ok, msg = self.user_ctrl.add_user("test_gui_user", "pass123", "Người Dùng GUI", "staff")
        self.assertTrue(ok, msg)

        # Lấy danh sách user
        users = self.user_ctrl.get_users("test_gui_user")
        self.assertGreater(len(users), 0)
        uid = users[0]["id"]

        # Cập nhật user
        ok, msg = self.user_ctrl.update_user(uid, "Người Dùng GUI Sửa", "staff")
        self.assertTrue(ok, msg)

        # Xóa user
        ok, msg = self.user_ctrl.delete_user(uid)
        self.assertTrue(ok, msg)

    def test_02_book_and_category_controller_api(self):
        # Thêm thể loại
        ok, msg = self.cat_ctrl.add_category("Thể Loại GUI Test")
        self.assertTrue(ok, msg)
        cats = self.cat_ctrl.get_categories("Thể Loại GUI Test")
        cat_id = cats[0]["id"]

        # Thêm sách
        ok, msg = self.book_ctrl.add_book("Sách GUI Test", "Tác Giả", "Thể Loại GUI Test", "5")
        self.assertTrue(ok, msg)
        books = self.book_ctrl.get_books("Sách GUI Test")
        b_id = books[0]["id"]

        # Cập nhật sách
        ok, msg = self.book_ctrl.update_book(b_id, "Sách GUI Test Đã Sửa", "Tác Giả", "Thể Loại GUI Test", "8")
        self.assertTrue(ok, msg)

        # Dọn dẹp
        self.book_ctrl.delete_book(b_id)
        self.cat_ctrl.delete_category(cat_id)

    def test_03_member_and_borrow_controller_api(self):
        # Thêm độc giả
        ok, msg = self.member_ctrl.add_member("Độc Giả GUI", "gui_reader@example.com", "0900000000")
        self.assertTrue(ok, msg)
        mems = self.member_ctrl.get_members("gui_reader@example.com")
        m_id = mems[0]["id"]

        # Thêm sách tạm
        self.book_ctrl.add_book("Sách Mượn GUI", "Tác Giả", "Công Nghệ", "4")
        b_id = self.book_ctrl.get_books("Sách Mượn GUI")[0]["id"]

        # Mượn sách
        ok, msg = self.borrow_ctrl.borrow_book(str(m_id), str(b_id), "14 ngày")
        self.assertTrue(ok, msg)

        # Lấy danh sách mượn
        borrows = self.borrow_ctrl.get_borrows(str(m_id))
        self.assertGreater(len(borrows), 0)
        br_id = borrows[0]["id"]

        # Trả sách
        ok, msg = self.borrow_ctrl.return_book(br_id)
        self.assertTrue(ok, msg)

        # Dọn dẹp
        self.book_ctrl.delete_book(b_id)
        self.member_ctrl.delete_member(m_id)

    def test_04_dashboard_and_reports_controller_api(self):
        dash = self.dash_ctrl.get_dashboard_data()
        self.assertIn("books_total", dash)
        self.assertIn("recent_borrows", dash)

        rep = self.report_ctrl.get_report_data()
        self.assertIn("kpis", rep)
        self.assertIn("top_books", rep)

    def test_05_views_exports(self):
        views = [DashboardView, BooksView, CategoriesView, MembersView, BorrowsView, OverdueView, ReportsView, UsersView, LoginView]
        self.assertEqual(len(views), 9)


if __name__ == "__main__":
    unittest.main()
