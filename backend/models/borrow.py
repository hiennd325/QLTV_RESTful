"""
Borrow Model — Quản lý các giao dịch mượn/trả sách trong cơ sở dữ liệu
"""
from datetime import datetime, date


class BorrowModel:
    def __init__(self, db, book_model=None):
        self.db = db
        self.book_model = book_model

    def get_all(self, keyword=None):
        if keyword:
            raw_kw = keyword.strip()
            kw = f"%{raw_kw}%"
            sql = """
                SELECT b.id, b.book_id, b.member_id, m.name as member_name, bk.title as book_title,
                       b.borrow_date, b.due_date, b.return_date, b.status, b.fine_amount,
                       COALESCE(b.renew_count, 0) as renew_count
                FROM borrows b
                JOIN members m ON b.member_id = m.id
                JOIN books bk ON b.book_id = bk.id
                WHERE CAST(b.id AS CHAR) = %s
                   OR m.name LIKE %s
                   OR bk.title LIKE %s
                   OR CAST(m.id AS CHAR) = %s
                   OR CAST(bk.id AS CHAR) = %s
                ORDER BY b.id DESC
            """
            return self.db.query(sql, (raw_kw, kw, kw, raw_kw, raw_kw))

        sql = """
            SELECT b.id, b.book_id, b.member_id, m.name as member_name, bk.title as book_title,
                   b.borrow_date, b.due_date, b.return_date, b.status, b.fine_amount,
                   COALESCE(b.renew_count, 0) as renew_count
            FROM borrows b
            JOIN members m ON b.member_id = m.id
            JOIN books bk ON b.book_id = bk.id
            ORDER BY b.id DESC
        """
        return self.db.query(sql)

    def get_by_book_id(self, book_id):
        """Lấy lịch sử mượn/trả chi tiết theo từng cuốn sách"""
        sql = """
            SELECT b.id, b.book_id, b.member_id, m.name as member_name, bk.title as book_title,
                   b.borrow_date, b.due_date, b.return_date, b.status, b.fine_amount,
                   COALESCE(b.renew_count, 0) as renew_count
            FROM borrows b
            JOIN members m ON b.member_id = m.id
            JOIN books bk ON b.book_id = bk.id
            WHERE b.book_id = %s
            ORDER BY b.id DESC
        """
        return self.db.query(sql, (book_id,))

    def get_by_member_id(self, member_id):
        """Lấy lịch sử mượn/trả chi tiết theo từng độc giả"""
        sql = """
            SELECT b.id, b.book_id, b.member_id, m.name as member_name, bk.title as book_title,
                   b.borrow_date, b.due_date, b.return_date, b.status, b.fine_amount,
                   COALESCE(b.renew_count, 0) as renew_count
            FROM borrows b
            JOIN members m ON b.member_id = m.id
            JOIN books bk ON b.book_id = bk.id
            WHERE b.member_id = %s
            ORDER BY b.id DESC
        """
        return self.db.query(sql, (member_id,))

    def get_recent(self, limit=8):
        sql = """
            SELECT b.id, m.name as member_name, bk.title as book_title,
                   b.borrow_date, b.due_date, b.status
            FROM borrows b
            JOIN members m ON b.member_id = m.id
            JOIN books bk ON b.book_id = bk.id
            ORDER BY b.id DESC LIMIT %s
        """
        return self.db.query(sql, (limit,))

    def get_by_id(self, borrow_id):
        rows = self.db.query("SELECT * FROM borrows WHERE id=%s", (borrow_id,))
        return rows[0] if rows else None

    def create_borrow(self, book_id, member_id, borrow_date_str, due_date_str):
        # Trừ số lượng sẵn có của sách
        sql_borrow = """
            INSERT INTO borrows (book_id, member_id, borrow_date, due_date, status, renew_count)
            VALUES (%s, %s, %s, %s, 'borrowed', 0)
        """
        borrow_id = self.db.execute(sql_borrow, (book_id, member_id, borrow_date_str, due_date_str))
        self.db.execute("UPDATE books SET available = available - 1 WHERE id=%s", (book_id,))
        return borrow_id

    def renew_borrow(self, borrow_id, extend_days=7, max_renews=2):
        """Gia hạn mượn sách thêm số ngày nhất định"""
        borrow = self.get_by_id(borrow_id)
        if not borrow:
            raise ValueError(f"Không tìm thấy phiếu mượn ID: {borrow_id}")
        if borrow["status"] == "returned":
            raise ValueError("Phiếu mượn này đã được trả sách, không thể gia hạn.")

        # Kiểm tra số lần đã gia hạn
        current_renews = borrow.get("renew_count") or 0
        if current_renews >= max_renews:
            raise ValueError(f"Phiếu mượn này đã đạt giới hạn gia hạn tối đa ({max_renews} lần).")

        # Kiểm tra xem có đang quá hạn không
        from datetime import date, timedelta
        today = date.today()
        due_val = borrow["due_date"]
        if isinstance(due_val, str):
            due_date = datetime.strptime(due_val, "%Y-%m-%d").date()
        else:
            due_date = due_val

        if due_date < today:
            raise ValueError("Phiếu mượn đã quá hạn, không thể gia hạn. Vui lòng thanh toán phạt và hoàn trả sách.")

        new_due_date = due_date + timedelta(days=extend_days)
        new_due_str = new_due_date.strftime("%Y-%m-%d")

        sql = "UPDATE borrows SET due_date=%s, renew_count=COALESCE(renew_count, 0) + 1 WHERE id=%s"
        self.db.execute(sql, (new_due_str, borrow_id))

        return {
            "borrow_id": borrow_id,
            "old_due_date": str(due_date),
            "new_due_date": new_due_str,
            "renew_count": current_renews + 1,
            "extended_days": extend_days
        }

    def return_borrow(self, borrow_id, fine_per_day=5000):
        borrow = self.get_by_id(borrow_id)
        if not borrow:
            raise ValueError(f"Không tìm thấy phiếu mượn ID: {borrow_id}")
        if borrow["status"] == "returned":
            raise ValueError("Sách này đã được trả trước đó.")

        ret_date = date.today()
        # Chuyển due_date thành date object nếu là string hoặc date
        if isinstance(borrow["due_date"], str):
            due_date = datetime.strptime(borrow["due_date"], "%Y-%m-%d").date()
        else:
            due_date = borrow["due_date"]

        overdue_days = max(0, (ret_date - due_date).days)
        fine = overdue_days * fine_per_day

        ret_date_str = ret_date.strftime("%Y-%m-%d")
        sql = "UPDATE borrows SET return_date=%s, fine_amount=%s, status='returned' WHERE id=%s"
        self.db.execute(sql, (ret_date_str, fine, borrow_id))
        self.db.execute("UPDATE books SET available = available + 1 WHERE id=%s", (borrow["book_id"],))

        return {
            "borrow_id": borrow_id,
            "return_date": ret_date_str,
            "overdue_days": overdue_days,
            "fine_amount": fine
        }

    def get_overdue_list(self, today_str=None):
        if not today_str:
            today_str = date.today().strftime("%Y-%m-%d")
        sql = """
            SELECT b.id, m.name, m.email, bk.title, b.due_date
            FROM borrows b
            JOIN members m ON b.member_id = m.id
            JOIN books bk ON b.book_id = bk.id
            WHERE b.status = 'borrowed' AND b.due_date < %s
            ORDER BY b.due_date ASC
        """
        return self.db.query(sql, (today_str,))

    def get_due_or_overdue_today(self, today_str=None):
        if not today_str:
            today_str = date.today().strftime("%Y-%m-%d")
        sql = """
            SELECT m.name, m.email, bk.title, b.due_date
            FROM borrows b
            JOIN members m ON b.member_id = m.id
            JOIN books bk ON b.book_id = bk.id
            WHERE b.status = 'borrowed' AND b.due_date <= %s
        """
        return self.db.query(sql, (today_str,))

    def count(self):
        res = self.db.query("SELECT COUNT(*) as c FROM borrows")
        return res[0]["c"] if res else 0

    def get_total_fines(self):
        res = self.db.query("SELECT SUM(fine_amount) as s FROM borrows")
        val = res[0]["s"] if res else 0
        return val or 0
