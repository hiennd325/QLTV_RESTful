"""
Routers Package
"""
from backend.routers.auth import router as auth_router
from backend.routers.users import router as users_router
from backend.routers.books import router as books_router
from backend.routers.categories import router as categories_router
from backend.routers.members import router as members_router
from backend.routers.borrows import router as borrows_router
from backend.routers.overdue import router as overdue_router
from backend.routers.dashboard import router as dashboard_router
from backend.routers.reports import router as reports_router

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
