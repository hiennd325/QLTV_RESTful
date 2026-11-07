"""
Auth Router — Đăng nhập và lấy thông tin người dùng hiện tại
"""
from fastapi import APIRouter, Depends, HTTPException, status
from models.user import UserModel
from schemas import LoginRequest, UserResponse
from dependencies import get_user_model, get_current_user
from auth_token import create_token

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
