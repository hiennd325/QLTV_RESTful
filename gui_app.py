"""
LibMaster GUI Client — Ứng dụng Desktop (CustomTkinter) kết nối RESTful API
Thiết kế giữ nguyên 100% giao diện gốc theo phong cách Obsidian & Neon Purple Glow
"""
import sys
from tkinter import ttk, messagebox
import customtkinter as ctk

from config import load_config
from theme import THEME, RADIUS
from api_client import (
    APIClient,
    UserAPIController,
    BookAPIController,
    CategoryAPIController,
    MemberAPIController,
    BorrowAPIController,
    OverdueAPIController,
    DashboardAPIController,
    ReportAPIController
)
from views import (
    DashboardView,
    BooksView,
    CategoriesView,
    MembersView,
    BorrowsView,
    OverdueView,
    ReportsView,
    UsersView,
    LoginView
)


class ModernLibraryApp(ctk.CTk):
    def __init__(self, api_url=None):
        super().__init__()
        self.cfg = load_config()
        base_url = api_url or self.cfg.get("api_base_url", "http://127.0.0.1:8080")
        self.api = APIClient(base_url)
        self.current_user = None

        self.title("LibMaster — Hệ Thống Quản Lý Thư Viện (RESTful API Client)")
        self.geometry("1240x760")
        self.minsize(1020, 660)

        # Cài đặt giao diện sáng (Light Mode Only)
        ctk.set_appearance_mode("Light")
        ctk.set_default_color_theme("blue")
        self.configure(fg_color=THEME["bg_window"])

        self.style_tables()
        self.init_controllers()
        self.setup_layout()

        # Kiểm tra kết nối tới RESTful API Server
        ok, err_msg = self.api.check_health()
        if not ok:
            self.show_api_error_screen(err_msg)
        else:
            self.show_login_screen()

    def style_tables(self):
        style = ttk.Style()
        style.theme_use("clam")

        style.configure(
            "Treeview",
            background=THEME["tree_bg"],
            foreground=THEME["tree_fg"],
            fieldbackground=THEME["tree_bg"],
            borderwidth=0,
            rowheight=36,
            font=("Segoe UI", 10)
        )
        style.configure(
            "Treeview.Heading",
            background=THEME["tree_head_bg"],
            foreground=THEME["tree_head_fg"],
            relief="flat",
            borderwidth=0,
            font=("Segoe UI", 10, "bold"),
            padding=8
        )
        style.map(
            "Treeview",
            background=[("selected", THEME["tree_selected_bg"])],
            foreground=[("selected", THEME["tree_selected_fg"])]
        )

    def init_controllers(self):
        self.controllers = {
            "user": UserAPIController(self.api),
            "book": BookAPIController(self.api),
            "category": CategoryAPIController(self.api),
            "member": MemberAPIController(self.api),
            "borrow": BorrowAPIController(self.api),
            "overdue": OverdueAPIController(self.api),
            "dashboard": DashboardAPIController(self.api),
            "report": ReportAPIController(self.api),
        }

    def setup_layout(self):
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # 1. Sidebar bên trái
        self.sidebar = ctk.CTkFrame(
            self,
            width=240,
            corner_radius=0,
            fg_color=THEME["bg_sidebar"],
            border_color=THEME["card_border"],
            border_width=1
        )
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(10, weight=1)

        # Logo & Brand Header
        logo_box = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        logo_box.grid(row=0, column=0, padx=20, pady=(28, 24), sticky="w")

        ctk.CTkLabel(
            logo_box,
            text="LibMaster",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color=THEME["text_primary"]
        ).pack(anchor="w")

        tag_box = ctk.CTkFrame(logo_box, fg_color=THEME["primary_subtle"], corner_radius=8)
        tag_box.pack(anchor="w", pady=(4, 0))
        ctk.CTkLabel(
            tag_box,
            text="RESTFUL API",
            font=ctk.CTkFont(size=9, weight="bold"),
            text_color=THEME["primary_glow"]
        ).pack(padx=8, pady=2)

        # Danh sách các trang điều hướng
        self.nav_buttons = {}
        pages = [
            ("dashboard", "Tổng Quan"),
            ("books", "Quản Lý Sách"),
            ("categories", "Thể Loại Sách"),
            ("members", "Bạn Đọc"),
            ("borrows", "Mượn & Trả Sách"),
            ("overdue", "Cảnh Báo Quá Hạn"),
            ("reports", "Báo Cáo & Thống Kê"),
            ("users", "Người Dùng"),
        ]

        for i, (key, label) in enumerate(pages, start=1):
            btn = ctk.CTkButton(
                self.sidebar,
                text=label,
                anchor="w",
                font=ctk.CTkFont(size=13, weight="bold"),
                height=44,
                corner_radius=RADIUS["pill"],
                fg_color="transparent",
                hover_color=THEME["card_inner"],
                text_color=THEME["text_secondary"],
                command=lambda k=key: self.show_page(k)
            )
            btn.grid(row=i, column=0, padx=14, pady=4, sticky="ew")
            self.nav_buttons[key] = btn

        # Footer Sidebar
        footer = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        footer.grid(row=11, column=0, padx=14, pady=20, sticky="ew")

        # Thẻ thông tin tài khoản hiện tại
        self.user_card = ctk.CTkFrame(
            footer,
            fg_color=THEME["card_inner"],
            corner_radius=RADIUS["card_sm"],
            border_color=THEME["card_border"],
            border_width=1
        )
        self.user_card.pack(fill="x", pady=(0, 10))

        u_top = ctk.CTkFrame(self.user_card, fg_color="transparent")
        u_top.pack(fill="x", padx=10, pady=(8, 2))

        self.user_name_lbl = ctk.CTkLabel(
            u_top,
            text="",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=THEME["text_primary"]
        )
        self.user_name_lbl.pack(side="left")

        self.user_role_badge = ctk.CTkLabel(
            u_top,
            text="",
            font=ctk.CTkFont(size=9, weight="bold")
        )
        self.user_role_badge.pack(side="right")

        self.logout_btn = ctk.CTkButton(
            self.user_card,
            text="Đăng Xuất",
            height=28,
            font=ctk.CTkFont(size=11),
            fg_color="transparent",
            hover_color=THEME["accent_red_subtle"],
            text_color=THEME["accent_red"],
            corner_radius=RADIUS["pill"],
            command=self.logout
        )
        self.logout_btn.pack(fill="x", padx=10, pady=(4, 8))

        # Thẻ trạng thái REST API
        api_card = ctk.CTkFrame(
            footer,
            fg_color=THEME["card_inner"],
            corner_radius=RADIUS["card_sm"],
            border_color=THEME["card_border"],
            border_width=1
        )
        api_card.pack(fill="x")

        self.api_badge = ctk.CTkLabel(
            api_card,
            text=f"API: {self.api.base_url}",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=THEME["accent_cyan"]
        )
        self.api_badge.pack(padx=12, pady=8, anchor="w")

        # 2. Main Container
        self.main_container = ctk.CTkFrame(self, fg_color=THEME["bg_main"], corner_radius=0)
        self.main_container.grid(row=0, column=1, sticky="nsew", padx=0, pady=0)
        self.main_container.grid_rowconfigure(0, weight=1)
        self.main_container.grid_columnconfigure(0, weight=1)

        # Màn hình báo lỗi kết nối API
        self.error_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.build_error_screen()

        # Khởi tạo các Views
        self.views = {
            "login": LoginView(self.main_container, self, self.controllers["user"]),
            "dashboard": DashboardView(self.main_container, self, self.controllers["dashboard"]),
            "books": BooksView(self.main_container, self, self.controllers["book"]),
            "categories": CategoriesView(self.main_container, self, self.controllers["category"]),
            "members": MembersView(self.main_container, self, self.controllers["member"]),
            "borrows": BorrowsView(self.main_container, self, self.controllers["borrow"]),
            "overdue": OverdueView(self.main_container, self, self.controllers["overdue"]),
            "reports": ReportsView(self.main_container, self, self.controllers["report"]),
            "users": UsersView(self.main_container, self, self.controllers["user"]),
        }

    def build_error_screen(self):
        box = ctk.CTkFrame(
            self.error_frame,
            fg_color=THEME["card_bg"],
            corner_radius=RADIUS["card"],
            border_color=THEME["accent_red"],
            border_width=1,
            width=650
        )
        box.place(relx=0.5, rely=0.5, anchor="center")

        err_tag = ctk.CTkFrame(box, fg_color=THEME["accent_red_subtle"], corner_radius=RADIUS["pill"])
        err_tag.pack(pady=(30, 10))
        ctk.CTkLabel(
            err_tag,
            text="API CONNECTION FAILED",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=THEME["accent_red"]
        ).pack(padx=16, pady=5)

        ctk.CTkLabel(
            box,
            text="Không Thể Kết Nối Tới RESTful API",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color=THEME["text_primary"]
        ).pack(pady=(0, 10))

        desc = (
            "Ứng dụng giao diện yêu cầu máy chủ RESTful API đang chạy.\n"
            f"Đang kiểm tra kết nối tới: {self.api.base_url}"
        )
        ctk.CTkLabel(
            box,
            text=desc,
            font=ctk.CTkFont(size=13),
            text_color=THEME["text_secondary"],
            justify="center"
        ).pack(padx=30, pady=(0, 15))

        self.err_detail_box = ctk.CTkTextbox(
            box,
            width=540,
            height=100,
            corner_radius=RADIUS["input"],
            fg_color=THEME["input_bg"],
            text_color=THEME["accent_red"]
        )
        self.err_detail_box.pack(padx=20, pady=10)

        ctk.CTkButton(
            box,
            text="Thử Kết Nối Lại",
            font=ctk.CTkFont(size=13, weight="bold"),
            height=42,
            fg_color=THEME["primary"],
            hover_color=THEME["primary_hover"],
            corner_radius=RADIUS["pill"],
            command=self.retry_connection
        ).pack(pady=(15, 30))

    def show_api_error_screen(self, err_msg=""):
        for v in self.views.values():
            v.grid_remove()
        for b in self.nav_buttons.values():
            b.configure(state="disabled", fg_color="transparent")

        self.err_detail_box.configure(state="normal")
        self.err_detail_box.delete("1.0", "end")
        msg = (
            f"Chi tiết lỗi kết nối:\n{err_msg}\n\n"
            f"Vui lòng chạy máy chủ API bằng lệnh:\n"
            f"  python server.py  (hoặc uvicorn main:app --port 8080)"
        )
        self.err_detail_box.insert("1.0", msg)
        self.err_detail_box.configure(state="disabled")

        self.api_badge.configure(text="API: Ngoại Tuyến", text_color=THEME["accent_red"])
        self.error_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)

    def retry_connection(self):
        self.cfg = load_config()
        self.api = APIClient(self.cfg.get("api_base_url", "http://127.0.0.1:8080"))
        self.init_controllers()

        ok, err_msg = self.api.check_health()
        if not ok:
            self.show_api_error_screen(err_msg)
            messagebox.showerror("Kết nối thất bại", f"Vẫn chưa thể kết nối tới máy chủ API:\n{err_msg}")
        else:
            self.error_frame.grid_remove()
            for b in self.nav_buttons.values():
                b.configure(state="normal")
            self.api_badge.configure(text=f"API: {self.api.base_url}", text_color=THEME["accent_cyan"])

            # Cập nhật controller cho views
            for key, view in self.views.items():
                if key in self.controllers:
                    view.controller = self.controllers[key]
                elif key == "login":
                    view.controller = self.controllers["user"]

            messagebox.showinfo("Thành công", "Đã kết nối thành công tới máy chủ RESTful API.")
            self.show_login_screen()

    def show_login_screen(self):
        for v in self.views.values():
            v.grid_remove()
        for b in self.nav_buttons.values():
            b.configure(fg_color="transparent", text_color=THEME["text_secondary"])

        self.sidebar.grid_remove()
        self.main_container.grid(row=0, column=0, columnspan=2, sticky="nsew")
        if "login" in self.views:
            self.views["login"].grid(row=0, column=0, sticky="nsew")
            self.views["login"].load_data()

    def on_login_success(self, user):
        self.current_user = user
        self.user_name_lbl.configure(text=user.get("full_name") or user.get("username"))
        role = user.get("role", "staff")
        if role == "admin":
            self.user_role_badge.configure(text="ADMIN", text_color=THEME["primary_glow"])
            if "users" in self.nav_buttons:
                self.nav_buttons["users"].grid(row=8, column=0, padx=14, pady=4, sticky="ew")
        else:
            self.user_role_badge.configure(text="NHÂN VIÊN", text_color=THEME["text_secondary"])
            if "users" in self.nav_buttons:
                self.nav_buttons["users"].grid_remove()

        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.main_container.grid(row=0, column=1, sticky="nsew")
        self.show_page("dashboard")
        self.refresh_all()

    def logout(self):
        if messagebox.askyesno("Đăng xuất", "Bạn có chắc chắn muốn đăng xuất khỏi hệ thống?"):
            self.api.clear_token()
            self.current_user = None
            self.show_login_screen()

    def show_page(self, name):
        if name == "users" and (not self.current_user or self.current_user.get("role") != "admin"):
            messagebox.showwarning("Từ chối truy cập", "Chỉ Quản trị viên (Admin) mới có quyền truy cập chức năng này.")
            return

        for k, v in self.views.items():
            v.grid_remove()
            if k in self.nav_buttons:
                self.nav_buttons[k].configure(fg_color="transparent", text_color=THEME["text_secondary"])

        if name in self.views:
            self.views[name].grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
            if name in self.nav_buttons:
                self.nav_buttons[name].configure(fg_color=THEME["primary"], text_color=THEME["text_white"])
            self.views[name].load_data()

    def refresh_stats(self):
        if "dashboard" in self.views:
            self.views["dashboard"].load_data()
        if "reports" in self.views:
            self.views["reports"].load_data()

    def refresh_all(self):
        for v in self.views.values():
            v.load_data()
