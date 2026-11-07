"""
Overdue Router — Cảnh báo sách quá hạn và gửi email nhắc nhở
"""
from datetime import date, datetime
from typing import Optional
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from models.borrow import BorrowModel
from schemas import OverdueResponse, OverdueItem, EmailReminderRequest, MessageResponse
from dependencies import get_borrow_model, get_config, get_current_user
from mailer import send_reminder_email

router = APIRouter(prefix="/api/overdue", tags=["Overdue"])


@router.get("", response_model=OverdueResponse)
def get_overdue(
    borrow_model: BorrowModel = Depends(get_borrow_model),
    cfg: dict = Depends(get_config),
    _: dict = Depends(get_current_user)
):
    today_date = date.today()
    today_str = today_date.strftime("%Y-%m-%d")
    rows = borrow_model.get_overdue_list(today_str)

    total_fine = 0
    rate = cfg.get("fine_per_day", 5000)
    items = []

    for r in rows:
        if isinstance(r["due_date"], str):
            d_date = datetime.strptime(r["due_date"], "%Y-%m-%d").date()
        else:
            d_date = r["due_date"]

        over_days = (today_date - d_date).days
        fine = over_days * rate
        total_fine += fine

        items.append(OverdueItem(
            id=r["id"],
            name=r["name"],
            email=r["email"],
            title=r["title"],
            due_date=str(r["due_date"]),
            overdue_days=over_days,
            fine_amount=fine
        ))

    return OverdueResponse(items=items, total_fine=total_fine)


@router.post("/send-reminder", response_model=MessageResponse)
def send_reminder(
    req: EmailReminderRequest,
    background_tasks: BackgroundTasks,
    cfg: dict = Depends(get_config),
    _: dict = Depends(get_current_user)
):
    fine_str = f"{req.fine:,} VND" if req.fine else None

    # Chạy gửi mail dạng background task để không nghẽn luồng HTTP
    def send_task():
        send_reminder_email(cfg, req.recipient, req.name, req.book_title, req.due_date, fine_str)

    background_tasks.add_task(send_task)
    return MessageResponse(
        success=True,
        message=f"Đã lên lịch gửi email nhắc nhở tới {req.recipient}."
    )


@router.post("/send-bulk", response_model=MessageResponse)
def send_bulk_reminders(
    background_tasks: BackgroundTasks,
    borrow_model: BorrowModel = Depends(get_borrow_model),
    cfg: dict = Depends(get_config),
    _: dict = Depends(get_current_user)
):
    today_str = date.today().strftime("%Y-%m-%d")
    rows = borrow_model.get_due_or_overdue_today(today_str)
    if not rows:
        return MessageResponse(success=True, message="Không có độc giả nào đến hạn hoặc quá hạn hôm nay.")

    def bulk_send_task():
        for r in rows:
            send_reminder_email(cfg, r["email"], r["name"], r["title"], str(r["due_date"]))

    background_tasks.add_task(bulk_send_task)
    return MessageResponse(
        success=True,
        message=f"Đã lên lịch gửi email hàng loạt tới {len(rows)} độc giả.",
        data={"count": len(rows)}
    )
