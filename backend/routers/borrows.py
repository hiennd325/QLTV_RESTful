"""
Borrows Router — Nghiệp vụ mượn và trả sách
"""
from datetime import date, timedelta
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from backend.models.book import BookModel
from backend.models.borrow import BorrowModel
from backend.schemas import BorrowResponse, BorrowCreate, ReturnResponse, MessageResponse
from backend.dependencies import get_borrow_model, get_book_model, get_config, get_current_user

router = APIRouter(prefix="/api/borrows", tags=["Borrows"])


@router.get("", response_model=List[BorrowResponse])
def get_borrows(
    keyword: Optional[str] = Query(None, description="Tìm theo ID phiếu, tên độc giả hoặc tên sách"),
    borrow_model: BorrowModel = Depends(get_borrow_model),
    _: dict = Depends(get_current_user)
):
    rows = borrow_model.get_all(keyword)
    today = date.today().strftime("%Y-%m-%d")

    formatted = []
    for r in rows:
        item = dict(r)
        d_date_str = str(item["due_date"])
        is_overdue = item["status"] == "borrowed" and d_date_str < today
        item["display_status"] = "Quá hạn" if is_overdue else ("Đang mượn" if item["status"] == "borrowed" else "Đã trả")
        item["borrow_date"] = str(item["borrow_date"])
        item["due_date"] = d_date_str
        item["return_date"] = str(item["return_date"]) if item["return_date"] else None
        item["fine_amount"] = item["fine_amount"] or 0
        formatted.append(item)

    return formatted


@router.post("", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
def borrow_book(
    req: BorrowCreate,
    borrow_model: BorrowModel = Depends(get_borrow_model),
    book_model: BookModel = Depends(get_book_model),
    _: dict = Depends(get_current_user)
):
    book = book_model.get_by_id(req.book_id)
    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Không tìm thấy sách có mã {req.book_id}.")

    if book["available"] <= 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Sách này hiện đã được mượn hết.")

    b_date = date.today()
    d_date = b_date + timedelta(days=req.days)
    b_date_str = b_date.strftime("%Y-%m-%d")
    d_date_str = d_date.strftime("%Y-%m-%d")

    try:
        new_id = borrow_model.create_borrow(req.book_id, req.member_id, b_date_str, d_date_str)
        return MessageResponse(
            success=True,
            message=f"Đã ghi nhận mượn sách. Hạn trả: {d_date_str}",
            data={
                "borrow_id": new_id,
                "borrow_date": b_date_str,
                "due_date": d_date_str
            }
        )
    except Exception as ex:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Lỗi khi ghi nhận mượn: {ex}")


@router.post("/{borrow_id}/return", response_model=ReturnResponse)
def return_book(
    borrow_id: int,
    borrow_model: BorrowModel = Depends(get_borrow_model),
    cfg: dict = Depends(get_config),
    _: dict = Depends(get_current_user)
):
    try:
        fine_rate = cfg.get("fine_per_day", 5000)
        res = borrow_model.return_borrow(borrow_id, fine_rate)
        ret_date = res["return_date"]
        overdue_days = res["overdue_days"]
        fine = res["fine_amount"]

        msg = f"Đã trả sách ngày {ret_date}."
        if fine > 0:
            msg += f" Quá hạn {overdue_days} ngày. Phí phạt: {fine:,} VND."

        return ReturnResponse(
            borrow_id=borrow_id,
            return_date=ret_date,
            overdue_days=overdue_days,
            fine_amount=fine,
            message=msg
        )
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except Exception as ex:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Lỗi khi trả sách: {ex}")
