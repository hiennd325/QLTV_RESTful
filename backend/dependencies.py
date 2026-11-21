"""
FastAPI Dependencies: Database, Models, Authentication & RBAC
"""
from functools import lru_cache
from fastapi import Depends, HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from config import load_config
from backend.database import Database
from backend.models.book import BookModel
from backend.models.category import CategoryModel
from backend.models.member import MemberModel
from backend.models.borrow import BorrowModel
from backend.models.report import ReportModel
from backend.models.user import UserModel
from backend.auth_token import verify_token

security = HTTPBearer(auto_error=False)


@lru_cache()
def get_config():
    return load_config()


_db_instance = None


def get_db():
    global _db_instance
    if _db_instance is None:
        cfg = get_config()
        _db_instance = Database(cfg)
        if _db_instance.connection_error:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Lỗi kết nối CSDL: {_db_instance.connection_error}"
            )
    return _db_instance


def get_user_model(db: Database = Depends(get_db)) -> UserModel:
    return UserModel(db)


def get_book_model(db: Database = Depends(get_db)) -> BookModel:
    return BookModel(db)


def get_category_model(db: Database = Depends(get_db)) -> CategoryModel:
    return CategoryModel(db)


def get_member_model(db: Database = Depends(get_db)) -> MemberModel:
    return MemberModel(db)


def get_borrow_model(
    db: Database = Depends(get_db),
    book_model: BookModel = Depends(get_book_model)
) -> BorrowModel:
    return BorrowModel(db, book_model)


def get_report_model(db: Database = Depends(get_db)) -> ReportModel:
    return ReportModel(db)


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(security),
    user_model: UserModel = Depends(get_user_model)
) -> dict:
    if not credentials or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Yêu cầu đăng nhập (thiếu Bearer token).",
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload = verify_token(credentials.credentials)
    if not payload or "id" not in payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token không hợp lệ hoặc đã hết hạn.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = user_model.get_by_id(payload["id"])
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Người dùng không tồn tại.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if user.get("is_locked"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tài khoản này đã bị khóa. Vui lòng liên hệ Quản trị viên.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


def require_admin(current_user: dict = Depends(get_current_user)) -> dict:
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Chức năng yêu cầu quyền Quản Trị Viên (admin)."
        )
    return current_user
