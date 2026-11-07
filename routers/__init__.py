"""
Routers Package
"""
from routers.auth import router as auth_router
from routers.users import router as users_router
from routers.books import router as books_router
from routers.categories import router as categories_router
from routers.members import router as members_router
from routers.borrows import router as borrows_router
from routers.overdue import router as overdue_router
from routers.dashboard import router as dashboard_router
from routers.reports import router as reports_router

__all__ = [
    "auth_router",
    "users_router",
    "books_router",
    "categories_router",
    "members_router",
    "borrows_router",
    "overdue_router",
    "dashboard_router",
    "reports_router"
]
