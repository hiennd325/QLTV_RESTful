"""
API Client & API Controllers — Cầu nối HTTP giữa Giao diện CustomTkinter và RESTful API
"""
import threading
import httpx


class APIClient:
    def __init__(self, base_url="http://127.0.0.1:8080"):
        self.base_url = base_url.rstrip("/")
        self.token = None
        self.client = httpx.Client(base_url=self.base_url, timeout=10.0)

    def set_token(self, token):
        self.token = token

    def clear_token(self):
        self.token = None

    def get_headers(self):
        headers = {"Accept": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    def check_health(self) -> tuple[bool, str]:
        try:
            r = self.client.get("/health", headers=self.get_headers())
            if r.status_code == 200:
                data = r.json()
                if data.get("status") == "healthy":
                    return True, "API kết nối bình thường."
                return False, f"CSDL chưa sẵn sàng: {data.get('database_error')}"
            return False, f"Mã phản hồi từ máy chủ API: {r.status_code}"
        except Exception as e:
            return False, f"Không thể kết nối máy chủ RESTful API tại {self.base_url}: {e}"

    def request(self, method, endpoint, **kwargs):
        headers = self.get_headers()
        if "headers" in kwargs:
            headers.update(kwargs.pop("headers"))
        return self.client.request(method, endpoint, headers=headers, **kwargs)


# ==============================================================================
# 1. User API Controller
# ==============================================================================
class UserAPIController:
    def __init__(self, api: APIClient):
        self.api = api

    def login(self, username, password):
        u = (username or "").strip()
        p = (password or "").strip()
        if not u or not p:
            return None, "Vui lòng nhập đầy đủ tên đăng nhập và mật khẩu."

        try:
            r = self.api.request("POST", "/api/auth/login", json={"username": u, "password": p})
            if r.status_code == 200:
                data = r.json()
                self.api.set_token(data.get("access_token"))
                return data.get("user"), "Đăng nhập thành công."
            err = r.json().get("detail", "Đăng nhập thất bại.")
            return None, err
        except Exception as e:
            return None, f"Lỗi kết nối API: {e}"

    def get_users(self, keyword=None):
        try:
            params = {"keyword": keyword} if keyword else {}
            r = self.api.request("GET", "/api/users", params=params)
            if r.status_code == 200:
                return r.json()
            return []
        except Exception:
            return []

    def add_user(self, username, password, full_name, role="staff"):
        try:
            payload = {
                "username": username,
                "password": password,
                "full_name": full_name,
                "role": role
            }
            r = self.api.request("POST", "/api/users", json=payload)
            if r.status_code in (200, 201):
                return True, r.json().get("message", "Thêm người dùng thành công.")
            return False, r.json().get("detail", "Lỗi khi thêm người dùng.")
        except Exception as e:
            return False, f"Lỗi kết nối API: {e}"

    def update_user(self, user_id, full_name, role, password=None, current_user_id=None):
        try:
            payload = {
                "full_name": full_name,
                "role": role
            }
            if password:
                payload["password"] = password
            r = self.api.request("PUT", f"/api/users/{user_id}", json=payload)
            if r.status_code == 200:
                return True, r.json().get("message", "Cập nhật người dùng thành công.")
            return False, r.json().get("detail", "Lỗi khi cập nhật người dùng.")
        except Exception as e:
            return False, f"Lỗi kết nối API: {e}"

    def delete_user(self, user_id, current_user_id=None):
        try:
            r = self.api.request("DELETE", f"/api/users/{user_id}")
            if r.status_code == 200:
                return True, r.json().get("message", "Xóa người dùng thành công.")
            return False, r.json().get("detail", "Lỗi khi xóa người dùng.")
        except Exception as e:
            return False, f"Lỗi kết nối API: {e}"


# ==============================================================================
# 2. Book API Controller
# ==============================================================================
class BookAPIController:
    def __init__(self, api: APIClient):
        self.api = api

    def get_books(self, keyword=None):
        try:
            params = {"keyword": keyword} if keyword else {}
            r = self.api.request("GET", "/api/books", params=params)
            if r.status_code == 200:
                return r.json()
            return []
        except Exception:
            return []

    def add_book(self, title, author, category, total_str, cover_image=None):
        try:
            total = int(total_str)
        except (ValueError, TypeError):
            return False, "Vui lòng nhập tên sách và số lượng hợp lệ (lớn hơn 0)."

        try:
            payload = {
                "title": (title or "").strip(),
                "author": (author or "").strip(),
                "category": (category or "").strip(),
                "total": total
            }
            if cover_image:
                payload["cover_image"] = cover_image
            r = self.api.request("POST", "/api/books", json=payload)
            if r.status_code in (200, 201):
                return True, r.json().get("message", "Thêm sách thành công.")
            return False, r.json().get("detail", "Lỗi khi thêm sách.")
        except Exception as e:
            return False, f"Lỗi kết nối API: {e}"

    def update_book(self, book_id, title, author, category, total_str, cover_image=None):
        if not book_id:
            return False, "Hãy chọn sách cần cập nhật."
        try:
            total = int(total_str)
        except (ValueError, TypeError):
            return False, "Vui lòng nhập tên sách và số lượng hợp lệ."

        try:
            payload = {
                "title": (title or "").strip(),
                "author": (author or "").strip(),
                "category": (category or "").strip(),
                "total": total
            }
            if cover_image is not None:
                payload["cover_image"] = cover_image
            r = self.api.request("PUT", f"/api/books/{book_id}", json=payload)
            if r.status_code == 200:
                return True, r.json().get("message", "Cập nhật sách thành công.")
            return False, r.json().get("detail", "Lỗi khi cập nhật sách.")
        except Exception as e:
            return False, f"Lỗi kết nối API: {e}"

    def upload_cover(self, file_source, filename="cover.jpg", book_id=None):
        import os
        try:
            if isinstance(file_source, str):
                filename = os.path.basename(file_source)
                with open(file_source, "rb") as f:
                    content = f.read()
            elif hasattr(file_source, "read"):
                content = file_source.read()
            else:
                content = file_source

            files = {"file": (filename, content)}
            endpoint = f"/api/books/{book_id}/cover" if book_id else "/api/books/upload-cover"
            r = self.api.request("POST", endpoint, files=files)
            if r.status_code in (200, 201):
                data = r.json()
                cover_url = data.get("data", {}).get("cover_image") or data.get("cover_image")
                return True, cover_url, data.get("message", "Tải ảnh thành công.")
            err = r.json().get("detail", "Lỗi khi tải ảnh bìa.")
            return False, None, err
        except Exception as e:
            return False, None, f"Lỗi kết nối upload ảnh: {e}"

    def delete_book(self, book_id):
        if not book_id:
            return False, "Hãy chọn sách cần xóa."
        try:
            r = self.api.request("DELETE", f"/api/books/{book_id}")
            if r.status_code == 200:
                return True, r.json().get("message", "Xóa sách thành công.")
            return False, r.json().get("detail", "Lỗi khi xóa sách.")
        except Exception as e:
            return False, f"Lỗi kết nối API: {e}"


# ==============================================================================
# 3. Category API Controller
# ==============================================================================
class CategoryAPIController:
    def __init__(self, api: APIClient):
        self.api = api

    def get_categories(self, keyword=None):
        try:
            params = {"keyword": keyword} if keyword else {}
            r = self.api.request("GET", "/api/categories", params=params)
            if r.status_code == 200:
                return r.json()
            return []
        except Exception:
            return []

    def get_category_names(self):
        try:
            r = self.api.request("GET", "/api/categories/names")
            if r.status_code == 200:
                return r.json()
            return []
        except Exception:
            return []

    def add_category(self, name):
        try:
            payload = {"name": (name or "").strip()}
            r = self.api.request("POST", "/api/categories", json=payload)
            if r.status_code in (200, 201):
                return True, r.json().get("message", "Thêm thể loại thành công.")
            return False, r.json().get("detail", "Lỗi khi thêm thể loại.")
        except Exception as e:
            return False, f"Lỗi kết nối API: {e}"

    def update_category(self, cat_id, new_name):
        try:
            payload = {"name": (new_name or "").strip()}
            r = self.api.request("PUT", f"/api/categories/{cat_id}", json=payload)
            if r.status_code == 200:
                return True, r.json().get("message", "Cập nhật thể loại thành công.")
            return False, r.json().get("detail", "Lỗi khi cập nhật thể loại.")
        except Exception as e:
            return False, f"Lỗi kết nối API: {e}"

    def delete_category(self, cat_id):
        try:
            r = self.api.request("DELETE", f"/api/categories/{cat_id}")
            if r.status_code == 200:
                return True, r.json().get("message", "Xóa thể loại thành công.")
            return False, r.json().get("detail", "Lỗi khi xóa thể loại.")
        except Exception as e:
            return False, f"Lỗi kết nối API: {e}"


# ==============================================================================
# 4. Member API Controller
# ==============================================================================
class MemberAPIController:
    def __init__(self, api: APIClient):
        self.api = api

    def get_members(self, keyword=None):
        try:
            params = {"keyword": keyword} if keyword else {}
            r = self.api.request("GET", "/api/members", params=params)
            if r.status_code == 200:
                return r.json()
            return []
        except Exception:
            return []

    def add_member(self, name, email, phone):
        try:
            payload = {
                "name": (name or "").strip(),
                "email": (email or "").strip(),
                "phone": (phone or "").strip()
            }
            r = self.api.request("POST", "/api/members", json=payload)
            if r.status_code in (200, 201):
                return True, r.json().get("message", "Thêm độc giả thành công.")
            return False, r.json().get("detail", "Lỗi khi thêm độc giả.")
        except Exception as e:
            return False, f"Lỗi kết nối API: {e}"

    def delete_member(self, member_id):
        try:
            r = self.api.request("DELETE", f"/api/members/{member_id}")
            if r.status_code == 200:
                return True, r.json().get("message", "Xóa độc giả thành công.")
            return False, r.json().get("detail", "Lỗi khi xóa độc giả.")
        except Exception as e:
            return False, f"Lỗi kết nối API: {e}"


# ==============================================================================
# 5. Borrow API Controller
# ==============================================================================
class BorrowAPIController:
    def __init__(self, api: APIClient):
        self.api = api

    def get_borrows(self, keyword=None):
        try:
            params = {"keyword": keyword} if keyword else {}
            r = self.api.request("GET", "/api/borrows", params=params)
            if r.status_code == 200:
                return r.json()
            return []
        except Exception:
            return []

    def get_borrows_by_book(self, book_id):
        try:
            r = self.api.request("GET", f"/api/borrows/book/{book_id}")
            if r.status_code == 200:
                return r.json()
            return []
        except Exception:
            return []

    def get_borrows_by_member(self, member_id):
        try:
            r = self.api.request("GET", f"/api/borrows/member/{member_id}")
            if r.status_code == 200:
                return r.json()
            return []
        except Exception:
            return []

    def renew_book(self, borrow_id, days=7):
        try:
            payload = {"days": days}
            r = self.api.request("POST", f"/api/borrows/{borrow_id}/renew", json=payload)
            if r.status_code == 200:
                return True, r.json().get("message", "Gia hạn mượn sách thành công.")
            return False, r.json().get("detail", "Lỗi khi gia hạn mượn sách.")
        except Exception as e:
            return False, f"Lỗi kết nối API: {e}"

    def borrow_book(self, member_id_str, book_id_str, days_str):
        try:
            m_id = int(str(member_id_str).strip())
            b_id = int(str(book_id_str).strip())
            days = int(str(days_str).strip().split()[0])
        except (ValueError, IndexError, AttributeError):
            return False, "Vui lòng nhập đúng ID độc giả và ID sách (dạng số)."

        try:
            payload = {"member_id": m_id, "book_id": b_id, "days": days}
            r = self.api.request("POST", "/api/borrows", json=payload)
            if r.status_code in (200, 201):
                return True, r.json().get("message", "Đã ghi nhận mượn sách.")
            return False, r.json().get("detail", "Lỗi khi ghi nhận mượn.")
        except Exception as e:
            return False, f"Lỗi kết nối API: {e}"

    def return_book(self, borrow_id):
        try:
            r = self.api.request("POST", f"/api/borrows/{borrow_id}/return")
            if r.status_code == 200:
                return True, r.json().get("message", "Đã trả sách thành công.")
            return False, r.json().get("detail", "Lỗi khi trả sách.")
        except Exception as e:
            return False, f"Lỗi kết nối API: {e}"


# ==============================================================================
# 6. Overdue API Controller
# ==============================================================================
class OverdueAPIController:
    def __init__(self, api: APIClient):
        self.api = api

    def get_overdue_data(self):
        try:
            r = self.api.request("GET", "/api/overdue")
            if r.status_code == 200:
                data = r.json()
                return data.get("items", []), data.get("total_fine", 0)
            return [], 0
        except Exception:
            return [], 0

    def send_single_reminder_async(self, recipient, name, book_title, due_date, fine_str, callback):
        def worker():
            try:
                # Trích xuất số tiền phạt nếu có dạng '15,000 VND'
                fine_num = None
                if fine_str:
                    digits = "".join(ch for ch in str(fine_str) if ch.isdigit())
                    if digits:
                        fine_num = int(digits)

                payload = {
                    "recipient": recipient,
                    "name": name,
                    "book_title": book_title,
                    "due_date": str(due_date),
                    "fine": fine_num
                }
                r = self.api.request("POST", "/api/overdue/send-reminder", json=payload)
                ok = (r.status_code == 200)
            except Exception:
                ok = False
            if callback:
                callback(ok, recipient)

        threading.Thread(target=worker, daemon=True).start()

    def send_bulk_reminders_async(self, callback):
        def worker():
            try:
                r = self.api.request("POST", "/api/overdue/send-bulk")
                if r.status_code == 200:
                    cnt = r.json().get("data", {}).get("count", 0)
                    if callback:
                        callback(cnt, cnt)
                    return
            except Exception:
                pass
            if callback:
                callback(0, 0)

        threading.Thread(target=worker, daemon=True).start()


# ==============================================================================
# 7. Dashboard API Controller
# ==============================================================================
class DashboardAPIController:
    def __init__(self, api: APIClient):
        self.api = api

    def get_dashboard_data(self):
        try:
            r = self.api.request("GET", "/api/dashboard")
            if r.status_code == 200:
                return r.json()
            return {
                "books_count": 0, "books_total": 0, "books_available": 0, "books_borrowed": 0,
                "members_count": 0, "borrows_count": 0, "recent_borrows": []
            }
        except Exception:
            return {
                "books_count": 0, "books_total": 0, "books_available": 0, "books_borrowed": 0,
                "members_count": 0, "borrows_count": 0, "recent_borrows": []
            }


# ==============================================================================
# 8. Report API Controller
# ==============================================================================
class ReportAPIController:
    def __init__(self, api: APIClient):
        self.api = api

    def get_report_data(self):
        try:
            r = self.api.request("GET", "/api/reports")
            if r.status_code == 200:
                return r.json()
            return {
                "kpis": {"books_count": 0, "members_count": 0, "borrows_count": 0, "fines_total": 0},
                "top_books": [], "top_categories": []
            }
        except Exception:
            return {
                "kpis": {"books_count": 0, "members_count": 0, "borrows_count": 0, "fines_total": 0},
                "top_books": [], "top_categories": []
            }

    def export_excel(self, save_path, report_type="all"):
        try:
            r = self.api.request("GET", "/api/reports/export/excel", params={"report_type": report_type})
            if r.status_code == 200:
                with open(save_path, "wb") as f:
                    f.write(r.content)
                return True, "Xuất file Excel thành công!"
            return False, f"Lỗi từ máy chủ: {r.status_code}"
        except Exception as e:
            return False, f"Lỗi khi lưu file: {e}"

    def export_pdf(self, save_path, report_type="books"):
        try:
            r = self.api.request("GET", "/api/reports/export/pdf", params={"report_type": report_type})
            if r.status_code == 200:
                with open(save_path, "wb") as f:
                    f.write(r.content)
                return True, "Xuất file PDF thành công!"
            return False, f"Lỗi từ máy chủ: {r.status_code}"
        except Exception as e:
            return False, f"Lỗi khi lưu file: {e}"
