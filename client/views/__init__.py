"""
Views Package
"""
from client.views.dashboard_view import DashboardView
from client.views.books_view import BooksView
from client.views.categories_view import CategoriesView
from client.views.members_view import MembersView
from client.views.borrows_view import BorrowsView
from client.views.overdue_view import OverdueView
from client.views.reports_view import ReportsView
from client.views.users_view import UsersView
from client.views.login_view import LoginView

__all__ = [
    "DashboardView",
    "BooksView",
    "CategoriesView",
    "MembersView",
    "BorrowsView",
    "OverdueView",
    "ReportsView",
    "UsersView",
    "LoginView"
]
