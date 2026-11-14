"""
Members Router — Quản lý độc giả / thành viên
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from backend.models.member import MemberModel
from backend.schemas import MemberResponse, MemberCreate, MessageResponse
from backend.dependencies import get_member_model, get_current_user

router = APIRouter(prefix="/api/members", tags=["Members"])


@router.get("", response_model=List[MemberResponse])
def get_members(
    keyword: Optional[str] = Query(None, description="Tìm theo ID, họ tên, điện thoại hoặc email"),
    member_model: MemberModel = Depends(get_member_model),
    _: dict = Depends(get_current_user)
):
    return member_model.get_all_with_active_borrows(keyword)


@router.get("/{member_id}", response_model=MemberResponse)
def get_member_by_id(
    member_id: int,
    member_model: MemberModel = Depends(get_member_model),
    _: dict = Depends(get_current_user)
):
    m = member_model.get_by_id(member_id)
    if not m:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Không tìm thấy độc giả với ID: {member_id}")
    return m


@router.post("", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
def create_member(
    req: MemberCreate,
    member_model: MemberModel = Depends(get_member_model),
    _: dict = Depends(get_current_user)
):
    n = req.name.strip()
    e = req.email.strip()
    p = req.phone.strip()

    if not n or "@" not in e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Vui lòng nhập họ tên và email hợp lệ.")

    try:
        new_id = member_model.add(n, e, p)
        return MessageResponse(success=True, message="Thêm độc giả thành công.", data={"member_id": new_id})
    except Exception as ex:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Lỗi khi thêm độc giả: {ex}")


@router.delete("/{member_id}", response_model=MessageResponse)
def delete_member(
    member_id: int,
    member_model: MemberModel = Depends(get_member_model),
    _: dict = Depends(get_current_user)
):
    m = member_model.get_by_id(member_id)
    if not m:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Không tìm thấy độc giả với ID: {member_id}")

    try:
        member_model.delete(member_id)
        return MessageResponse(success=True, message="Xóa độc giả thành công.")
    except Exception as ex:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Lỗi khi xóa độc giả: {ex}")
