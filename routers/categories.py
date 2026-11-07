"""
Categories Router — Quản lý thể loại sách
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from models.category import CategoryModel
from schemas import CategoryResponse, CategoryCreate, CategoryUpdate, MessageResponse
from dependencies import get_category_model, get_current_user

router = APIRouter(prefix="/api/categories", tags=["Categories"])


@router.get("", response_model=List[CategoryResponse])
def get_categories(
    keyword: Optional[str] = Query(None, description="Tìm theo ID hoặc tên thể loại"),
    cat_model: CategoryModel = Depends(get_category_model),
    _: dict = Depends(get_current_user)
):
    return cat_model.get_all(keyword)


@router.get("/names", response_model=List[str])
def get_category_names(
    cat_model: CategoryModel = Depends(get_category_model),
    _: dict = Depends(get_current_user)
):
    return cat_model.get_names()


@router.get("/{cat_id}", response_model=CategoryResponse)
def get_category_by_id(
    cat_id: int,
    cat_model: CategoryModel = Depends(get_category_model),
    _: dict = Depends(get_current_user)
):
    cat = cat_model.get_by_id(cat_id)
    if not cat:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy thể loại.")
    return cat


@router.post("", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
def create_category(
    req: CategoryCreate,
    cat_model: CategoryModel = Depends(get_category_model),
    _: dict = Depends(get_current_user)
):
    name = req.name.strip()
    if not name:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Vui lòng nhập tên thể loại.")

    existing = cat_model.get_by_name(name)
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Thể loại '{name}' đã tồn tại.")

    try:
        new_id = cat_model.add(name)
        return MessageResponse(success=True, message=f"Thêm thể loại '{name}' thành công.", data={"category_id": new_id})
    except Exception as ex:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Lỗi khi thêm thể loại: {ex}")


@router.put("/{cat_id}", response_model=MessageResponse)
def update_category(
    cat_id: int,
    req: CategoryUpdate,
    cat_model: CategoryModel = Depends(get_category_model),
    _: dict = Depends(get_current_user)
):
    clean_name = req.name.strip()
    if not clean_name:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Tên thể loại không được để trống.")

    existing = cat_model.get_by_name(clean_name)
    if existing and existing["id"] != cat_id:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Tên thể loại '{clean_name}' đã được sử dụng.")

    try:
        cat_model.update(cat_id, clean_name)
        return MessageResponse(success=True, message="Cập nhật thể loại thành công.")
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(ve))
    except Exception as ex:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Lỗi khi cập nhật thể loại: {ex}")


@router.delete("/{cat_id}", response_model=MessageResponse)
def delete_category(
    cat_id: int,
    cat_model: CategoryModel = Depends(get_category_model),
    _: dict = Depends(get_current_user)
):
    try:
        cat_model.delete(cat_id)
        return MessageResponse(success=True, message="Xóa thể loại thành công.")
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except Exception as ex:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Lỗi khi xóa thể loại: {ex}")
