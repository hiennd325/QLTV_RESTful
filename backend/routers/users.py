"""
Users Router — Quản trị người dùng & phân quyền (Chỉ dành cho Admin)
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from backend.models.user import UserModel
from backend.schemas import UserResponse, UserCreate, UserUpdate, MessageResponse
from backend.dependencies import get_user_model, require_admin

router = APIRouter(prefix="/api/users", tags=["Users"])


@router.get("", response_model=List[UserResponse])
def get_users(
    keyword: Optional[str] = Query(None, description="Tìm theo ID, username, họ tên hoặc vai trò"),
    user_model: UserModel = Depends(get_user_model),
    _: dict = Depends(require_admin)
):
    return user_model.get_all(keyword)


@router.get("/{user_id}", response_model=UserResponse)
def get_user_by_id(
    user_id: int,
    user_model: UserModel = Depends(get_user_model),
    _: dict = Depends(require_admin)
):
    user = user_model.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy người dùng.")
    return user


@router.post("", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
def create_user(
    req: UserCreate,
    user_model: UserModel = Depends(get_user_model),
    _: dict = Depends(require_admin)
):
    u = req.username.strip()
    p = req.password.strip()
    fn = req.full_name.strip()
    r = req.role.strip().lower()

    if not u or not p or not fn:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Vui lòng nhập đầy đủ thông tin: tên đăng nhập, mật khẩu và họ tên.")

    if len(u) < 3:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Tên đăng nhập phải có ít nhất 3 ký tự.")

    if len(p) < 4:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Mật khẩu phải có ít nhất 4 ký tự.")

    if r not in ("admin", "staff"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Vai trò không hợp lệ (chỉ chấp nhận admin hoặc staff).")

    existing = user_model.get_by_username(u)
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Tên đăng nhập '{u}' đã tồn tại.")

    try:
        new_id = user_model.add(u, p, fn, r)
        return MessageResponse(success=True, message="Thêm người dùng thành công.", data={"user_id": new_id})
    except Exception as ex:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Lỗi khi thêm người dùng: {ex}")


@router.put("/{user_id}", response_model=MessageResponse)
def update_user(
    user_id: int,
    req: UserUpdate,
    user_model: UserModel = Depends(get_user_model),
    _: dict = Depends(require_admin)
):
    fn = req.full_name.strip()
    r = req.role.strip().lower()
    p = req.password.strip() if req.password else None

    if not fn:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Họ và tên không được để trống.")

    if r not in ("admin", "staff"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Vai trò không hợp lệ.")

    if p and len(p) < 4:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Mật khẩu mới phải có ít nhất 4 ký tự.")

    user = user_model.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy người dùng.")

    # Bảo vệ: Không hạ quyền admin duy nhất
    if user["role"] == "admin" and r != "admin":
        if user_model.count_admins() <= 1:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Không thể chuyển quyền admin cuối cùng trong hệ thống.")

    try:
        user_model.update(user_id, fn, r, p)
        return MessageResponse(success=True, message="Cập nhật người dùng thành công.")
    except Exception as ex:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Lỗi khi cập nhật người dùng: {ex}")


@router.delete("/{user_id}", response_model=MessageResponse)
def delete_user(
    user_id: int,
    user_model: UserModel = Depends(get_user_model),
    current_user: dict = Depends(require_admin)
):
    if user_id == current_user["id"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Không thể xóa chính tài khoản đang đăng nhập.")

    user = user_model.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy người dùng.")

    if user["role"] == "admin" and user_model.count_admins() <= 1:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Không thể xóa tài khoản admin duy nhất trong hệ thống.")

    try:
        user_model.delete(user_id)
        return MessageResponse(success=True, message="Xóa người dùng thành công.")
    except Exception as ex:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Lỗi khi xóa người dùng: {ex}")
