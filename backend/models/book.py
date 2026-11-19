"""
Book Model — Quản lý dữ liệu sách trong cơ sở dữ liệu
"""


class BookModel:
    def __init__(self, db):
        self.db = db

    def get_all(self, keyword=None):
        if keyword:
            raw_kw = keyword.strip()
            kw = f"%{raw_kw}%"
            sql = "SELECT * FROM books WHERE CAST(id AS CHAR) = %s OR title LIKE %s OR author LIKE %s OR category LIKE %s ORDER BY id DESC"
            return self.db.query(sql, (raw_kw, kw, kw, kw))
        return self.db.query("SELECT * FROM books ORDER BY id DESC")

    def get_by_id(self, book_id):
        rows = self.db.query("SELECT * FROM books WHERE id=%s", (book_id,))
        return rows[0] if rows else None

    def add(self, title, author, category, total, cover_image=None):
        sql = "INSERT INTO books (title, author, category, total, available, cover_image) VALUES (%s, %s, %s, %s, %s, %s)"
        return self.db.execute(sql, (title, author, category, total, total, cover_image))

    def update(self, book_id, title, author, category, total, cover_image=None):
        old = self.get_by_id(book_id)
        if not old:
            raise ValueError(f"Không tìm thấy sách với ID: {book_id}")
        new_avail = max(0, old["available"] + (total - old["total"]))
        new_cover = cover_image if cover_image is not None else old.get("cover_image")
        sql = "UPDATE books SET title=%s, author=%s, category=%s, total=%s, available=%s, cover_image=%s WHERE id=%s"
        return self.db.execute(sql, (title, author, category, total, new_avail, new_cover, book_id))

    def update_cover(self, book_id, cover_image):
        old = self.get_by_id(book_id)
        if not old:
            raise ValueError(f"Không tìm thấy sách với ID: {book_id}")
        sql = "UPDATE books SET cover_image=%s WHERE id=%s"
        return self.db.execute(sql, (cover_image, book_id))

    def delete(self, book_id):
        return self.db.execute("DELETE FROM books WHERE id=%s", (book_id,))

    def get_inventory_stats(self):
        sql = "SELECT COUNT(*) as c, COALESCE(SUM(total), 0) as tot, COALESCE(SUM(available), 0) as av FROM books"
        res = self.db.query(sql)
        if res:
            return res[0]
        return {"c": 0, "tot": 0, "av": 0}

    def adjust_available(self, book_id, delta):
        sql = "UPDATE books SET available = available + %s WHERE id=%s"
        return self.db.execute(sql, (delta, book_id))
