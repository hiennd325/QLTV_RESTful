"""
Dashboard Router — Tổng quan hoạt động thư viện
"""
from datetime import date
from fastapi import APIRouter, Depends
from backend.models.book import BookModel
from backend.models.member import MemberModel
from backend.models.borrow import BorrowModel
from backend.schemas import DashboardResponse, RecentBorrowItem
from backend.dependencies import get_book_model, get_member_model, get_borrow_model, get_current_user

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])


@router.get("", response_model=DashboardResponse)
def get_dashboard(
    book_model: BookModel = Depends(get_book_model),
    member_model: MemberModel = Depends(get_member_model),
    borrow_model: BorrowModel = Depends(get_borrow_model),
    _: dict = Depends(get_current_user)
):
    inv = book_model.get_inventory_stats()
    b_cnt = inv["c"]
    b_total = inv["tot"]
    b_avail = inv["av"]
    b_borrowed = max(0, b_total - b_avail)

    m_cnt = member_model.count()
    br_cnt = borrow_model.count()

    recent_rows = borrow_model.get_recent(8)
    today = date.today().strftime("%Y-%m-%d")

    recent_borrows = []
    for r in recent_rows:
        d_date_str = str(r["due_date"])
        is_overdue = r["status"] == "borrowed" and d_date_str < today
        display_status = "Quá hạn" if is_overdue else ("Đang mượn" if r["status"] == "borrowed" else "Đã trả")

        recent_borrows.append(RecentBorrowItem(
            id=r["id"],
            member_name=r["member_name"],
            book_title=r["book_title"],
            borrow_date=str(r["borrow_date"]),
            due_date=d_date_str,
            status=r["status"],
            display_status=display_status
        ))

    return DashboardResponse(
        books_count=b_cnt,
        books_total=b_total,
        books_available=b_avail,
        books_borrowed=b_borrowed,
        members_count=m_cnt,
        borrows_count=br_cnt,
        recent_borrows=recent_borrows
    )
