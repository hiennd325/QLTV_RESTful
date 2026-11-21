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
                SELECT id, username, full_name, role, is_locked
                FROM users
                WHERE CAST(id AS CHAR) = %s OR username LIKE %s OR full_name LIKE %s OR role LIKE %s
                ORDER BY id ASC
            """
            return self.db.query(sql, (raw_kw, kw, kw, kw))
        return self.db.query("SELECT id, username, full_name, role, is_locked FROM users ORDER BY id ASC")

    def get_by_id(self, user_id):
        rows = self.db.query("SELECT id, username, full_name, role, is_locked FROM users WHERE id=%s", (user_id,))
        return rows[0] if rows else None

    def get_by_username(self, username):
        rows = self.db.query("SELECT * FROM users WHERE username=%s", (username,))
        return rows[0] if rows else None

    def add(self, username, password, full_name, role="staff", is_locked=False):
        pw_hash = self.hash_password(password)
        sql = "INSERT INTO users (username, password_hash, full_name, role, is_locked) VALUES (%s, %s, %s, %s, %s)"
        return self.db.execute(sql, (username, pw_hash, full_name, role, 1 if is_locked else 0))

    def update(self, user_id, full_name, role, password=None, is_locked=None):
        params = [full_name, role]
        fields = ["full_name=%s", "role=%s"]
        if password:
            fields.append("password_hash=%s")
            params.append(self.hash_password(password))
        if is_locked is not None:
            fields.append("is_locked=%s")
            params.append(1 if is_locked else 0)
        params.append(user_id)
        sql = f"UPDATE users SET {', '.join(fields)} WHERE id=%s"
        return self.db.execute(sql, tuple(params))

    def set_lock_status(self, user_id, is_locked: bool):
        return self.db.execute("UPDATE users SET is_locked=%s WHERE id=%s", (1 if is_locked else 0, user_id))

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
                "role": user["role"],
                "is_locked": bool(user.get("is_locked", 0))
            }
        return None

    def count(self):
        res = self.db.query("SELECT COUNT(*) as c FROM users")
        return res[0]["c"] if res else 0

    def count_admins(self):
        res = self.db.query("SELECT COUNT(*) as c FROM users WHERE role='admin'")
        return res[0]["c"] if res else 0

    def count_active_admins(self):
        res = self.db.query("SELECT COUNT(*) as c FROM users WHERE role='admin' AND is_locked=0")
        return res[0]["c"] if res else 0
