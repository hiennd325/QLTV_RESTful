"""
Pydantic Schemas cho RESTful API Thư Viện
"""
from typing import Optional, List
from datetime import date
from pydantic import BaseModel, Field


# ==================== Auth & User ====================
class LoginRequest(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    id: int
    username: str
    full_name: str
    role: str


class UserCreate(BaseModel):
    username: str
    password: str
    full_name: str
    role: str = "staff"


class UserUpdate(BaseModel):
    full_name: str
    role: str
    password: Optional[str] = None


# ==================== Category ====================
class CategoryResponse(BaseModel):
    id: int
    name: str
    book_count: Optional[int] = 0


class CategoryCreate(BaseModel):
    name: str


class CategoryUpdate(BaseModel):
    name: str


# ==================== Book ====================
class BookResponse(BaseModel):
    id: int
    title: str
    author: str
    category: str
    total: int
    available: int
    cover_image: Optional[str] = None


class BookCreate(BaseModel):
    title: str
    author: str = ""
    category: str
    total: int = Field(gt=0)
    cover_image: Optional[str] = None


class BookUpdate(BaseModel):
    title: str
    author: str = ""
    category: str
    total: int = Field(gt=0)
    cover_image: Optional[str] = None


class InventoryStats(BaseModel):
    books_count: int
    books_total: int
    books_available: int
    books_borrowed: int


# ==================== Member ====================
class MemberResponse(BaseModel):
    id: int
    name: str
    email: str
    phone: str
    active_borrows: Optional[int] = 0


class MemberCreate(BaseModel):
    name: str
    email: str
    phone: str = ""


# ==================== Borrow ====================
class BorrowResponse(BaseModel):
    id: int
    book_id: Optional[int] = None
    member_id: Optional[int] = None
    member_name: str
    book_title: str
    borrow_date: str
    due_date: str
    return_date: Optional[str] = None
    status: str
    fine_amount: int = 0
    renew_count: Optional[int] = 0
    display_status: str


class BorrowCreate(BaseModel):
    member_id: int
    book_id: int
    days: int = Field(default=14, gt=0)


class BorrowRenew(BaseModel):
    days: int = Field(default=7, gt=0, le=30, description="Số ngày gia hạn thêm")


class ReturnResponse(BaseModel):
    borrow_id: int
    return_date: str
    overdue_days: int
    fine_amount: int
    message: str


# ==================== Overdue ====================
class OverdueItem(BaseModel):
    id: int
    name: str
    email: str
    title: str
    due_date: str
    overdue_days: int
    fine_amount: int


class OverdueResponse(BaseModel):
    items: List[OverdueItem]
    total_fine: int


class EmailReminderRequest(BaseModel):
    borrow_id: Optional[int] = None
    recipient: str
    name: str
    book_title: str
    due_date: str
    fine: Optional[int] = None


# ==================== Dashboard & Reports ====================
class RecentBorrowItem(BaseModel):
    id: int
    member_name: str
    book_title: str
    borrow_date: str
    due_date: str
    status: str
    display_status: str


class DashboardResponse(BaseModel):
    books_count: int
    books_total: int
    books_available: int
    books_borrowed: int
    members_count: int
    borrows_count: int
    recent_borrows: List[RecentBorrowItem]


class ReportKPIs(BaseModel):
    books_count: int
    members_count: int
    borrows_count: int
    fines_total: int


class TopBookItem(BaseModel):
    title: str
    cnt: int


class TopCategoryItem(BaseModel):
    category: str
    cnt: int


class ReportResponse(BaseModel):
    kpis: ReportKPIs
    top_books: List[TopBookItem]
    top_categories: List[TopCategoryItem]


# ==================== Generic Response ====================
class MessageResponse(BaseModel):
    success: bool
    message: str
    data: Optional[dict] = None
