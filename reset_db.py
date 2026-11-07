"""
Script Reset Database — Xóa trắng toàn bộ dữ liệu và đặt lại ID về 1
"""
import sys
from config import load_config
from database import Database


def reset_database():
    cfg = load_config()
    db = Database(cfg)
    if db.connection_error:
        print(f"Lỗi kết nối MySQL: {db.connection_error}")
        sys.exit(1)

    print(f"Đang reset database: {cfg['db_name']}...")
    conn = db.get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SET FOREIGN_KEY_CHECKS = 0;")
            cur.execute("TRUNCATE TABLE borrows;")
            cur.execute("TRUNCATE TABLE members;")
            cur.execute("TRUNCATE TABLE books;")
            cur.execute("TRUNCATE TABLE categories;")
            cur.execute("TRUNCATE TABLE users;")
            cur.execute("SET FOREIGN_KEY_CHECKS = 1;")
            admin_pw = "240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9"
            staff_pw = "10176e7b7b24d317acfcf8d2064cfd2f24e154f7b5a96603077d5ef813d6a6b6"
            cur.execute(
                "INSERT INTO users (username, password_hash, full_name, role) VALUES (%s, %s, %s, %s), (%s, %s, %s, %s)",
                ("admin", admin_pw, "Quản Trị Viên", "admin", "staff", staff_pw, "Nhân Viên Thư Viện", "staff")
            )
        print("Reset thành công: Đã dọn sạch bảng và tạo tài khoản admin, staff mặc định.")
    except Exception as e:
        print(f"Lỗi khi reset: {e}")
        sys.exit(1)
    finally:
        conn.close()


if __name__ == "__main__":
    reset_database()
