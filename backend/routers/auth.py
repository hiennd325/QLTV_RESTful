"""
Auth Router — Đăng nhập và lấy thông tin người dùng hiện tại
"""
from fastapi import APIRouter, Depends, HTTPException, status
from backend.models.user import UserModel
from backend.schemas import LoginRequest, UserResponse
from backend.dependencies import get_user_model, get_current_user
from backend.auth_token import create_token

router = APIRouter(prefix="/api/auth", tags=["Auth"])


@router.post("/login")
def login(req: LoginRequest, user_model: UserModel = Depends(get_user_model)):
    u = req.username.strip()
    p = req.password.strip()

    if not u or not p:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Vui lòng nhập đầy đủ tên đăng nhập và mật khẩu."
        )

    user = user_model.authenticate(u, p)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Tên đăng nhập hoặc mật khẩu không chính xác."
        )

    if user.get("is_locked"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tài khoản này đã bị khóa. Vui lòng liên hệ Quản trị viên."
        )

    token = create_token({
        "id": user["id"],
        "username": user["username"],
        "role": user["role"]
    })

    return {
        "access_token": token,
        "token_type": "bearer",
        "user": user
    }


@router.get("/me", response_model=UserResponse)
def get_me(current_user: dict = Depends(get_current_user)):
    return current_user
