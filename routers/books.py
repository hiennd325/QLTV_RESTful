"""
Books Router — Quản lý sách & thống kê tồn kho
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from models.book import BookModel
from schemas import BookResponse, BookCreate, BookUpdate, InventoryStats, MessageResponse
from dependencies import get_book_model, get_current_user

router = APIRouter(prefix="/api/books", tags=["Books"])


@router.get("", response_model=List[BookResponse])
def get_books(
    keyword: Optional[str] = Query(None, description="Tìm theo ID, tên sách, tác giả hoặc thể loại"),
    book_model: BookModel = Depends(get_book_model),
    _: dict = Depends(get_current_user)
):
    return book_model.get_all(keyword)


@router.get("/stats/inventory", response_model=InventoryStats)
def get_inventory_stats(
    book_model: BookModel = Depends(get_book_model),
    _: dict = Depends(get_current_user)
):
    inv = book_model.get_inventory_stats()
    b_total = inv["tot"]
    b_avail = inv["av"]
    b_borrowed = max(0, b_total - b_avail)
    return {
        "books_count": inv["c"],
        "books_total": b_total,
        "books_available": b_avail,
        "books_borrowed": b_borrowed
    }


@router.get("/{book_id}", response_model=BookResponse)
def get_book_by_id(
    book_id: int,
    book_model: BookModel = Depends(get_book_model),
    _: dict = Depends(get_current_user)
):
    book = book_model.get_by_id(book_id)
    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Không tìm thấy sách với ID: {book_id}")
    return book


@router.post("", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
def create_book(
    req: BookCreate,
    book_model: BookModel = Depends(get_book_model),
    _: dict = Depends(get_current_user)
):
    t = req.title.strip()
    a = req.author.strip()
    c = req.category.strip()

    if not c or c == "(Chưa có thể loại)":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Vui lòng chọn thể loại sách.")

    if not t or req.total <= 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Vui lòng nhập tên sách và số lượng hợp lệ (lớn hơn 0).")

    try:
        new_id = book_model.add(t, a, c, req.total)
        return MessageResponse(success=True, message="Thêm sách thành công.", data={"book_id": new_id})
    except Exception as ex:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Lỗi khi thêm sách: {ex}")


@router.put("/{book_id}", response_model=MessageResponse)
def update_book(
    book_id: int,
    req: BookUpdate,
    book_model: BookModel = Depends(get_book_model),
    _: dict = Depends(get_current_user)
):
    t = req.title.strip()
    a = req.author.strip()
    c = req.category.strip()

    if not c or c == "(Chưa có thể loại)":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Vui lòng chọn thể loại sách.")

    if not t or req.total <= 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Vui lòng nhập tên sách và số lượng hợp lệ.")

    try:
        book_model.update(book_id, t, a, c, req.total)
        return MessageResponse(success=True, message="Cập nhật sách thành công.")
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(ve))
    except Exception as ex:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Lỗi khi cập nhật sách: {ex}")


@router.delete("/{book_id}", response_model=MessageResponse)
def delete_book(
    book_id: int,
    book_model: BookModel = Depends(get_book_model),
    _: dict = Depends(get_current_user)
):
    book = book_model.get_by_id(book_id)
    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Không tìm thấy sách với ID: {book_id}")

    try:
        book_model.delete(book_id)
        return MessageResponse(success=True, message="Xóa sách thành công.")
    except Exception as ex:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Lỗi khi xóa sách: {ex}")
