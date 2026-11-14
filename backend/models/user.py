"""
User Model — Quản lý dữ liệu người dùng và tài khoản trong cơ sở dữ liệu
"""
import hashlib


class UserModel:
    def __init__(self, db):
        self.db = db

    @staticmethod
    def hash_password(password):
        # ponytail: simple sha256 hashing; upgrade to bcrypt/argon2 if handling public auth
        return hashlib.sha256((password or "").encode("utf-8")).hexdigest()

    def get_all(self, keyword=None):
        if keyword:
            raw_kw = keyword.strip()
            kw = f"%{raw_kw}%"
            sql = """
                SELECT id, username, full_name, role
                FROM users
                WHERE CAST(id AS CHAR) = %s OR username LIKE %s OR full_name LIKE %s OR role LIKE %s
                ORDER BY id ASC
            """
            return self.db.query(sql, (raw_kw, kw, kw, kw))
        return self.db.query("SELECT id, username, full_name, role FROM users ORDER BY id ASC")

    def get_by_id(self, user_id):
        rows = self.db.query("SELECT id, username, full_name, role FROM users WHERE id=%s", (user_id,))
        return rows[0] if rows else None

    def get_by_username(self, username):
        rows = self.db.query("SELECT * FROM users WHERE username=%s", (username,))
        return rows[0] if rows else None

    def add(self, username, password, full_name, role="staff"):
        pw_hash = self.hash_password(password)
        sql = "INSERT INTO users (username, password_hash, full_name, role) VALUES (%s, %s, %s, %s)"
        return self.db.execute(sql, (username, pw_hash, full_name, role))

    def update(self, user_id, full_name, role, password=None):
        if password:
            pw_hash = self.hash_password(password)
            sql = "UPDATE users SET full_name=%s, role=%s, password_hash=%s WHERE id=%s"
            return self.db.execute(sql, (full_name, role, pw_hash, user_id))
        sql = "UPDATE users SET full_name=%s, role=%s WHERE id=%s"
        return self.db.execute(sql, (full_name, role, user_id))

    def delete(self, user_id):
        return self.db.execute("DELETE FROM users WHERE id=%s", (user_id,))

    def authenticate(self, username, password):
        user = self.get_by_username(username)
        if not user:
            return None
        if user["password_hash"] == self.hash_password(password):
            return {
                "id": user["id"],
                "username": user["username"],
                "full_name": user["full_name"],
                "role": user["role"]
            }
        return None

    def count(self):
        res = self.db.query("SELECT COUNT(*) as c FROM users")
        return res[0]["c"] if res else 0

    def count_admins(self):
        res = self.db.query("SELECT COUNT(*) as c FROM users WHERE role='admin'")
        return res[0]["c"] if res else 0
