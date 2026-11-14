"""
Users View — Màn hình Quản Lý Người Dùng (Chỉ dành cho Admin)
"""
import tkinter as tk
from tkinter import ttk, messagebox
import customtkinter as ctk

from client.theme import THEME, RADIUS


class UsersView(ctk.CTkFrame):
    def __init__(self, parent, app, controller=None):
        super().__init__(parent, fg_color="transparent")
        self.app = app
        self.controller = controller or getattr(app, "controllers", {}).get("user")
        self.setup_ui()

    def setup_ui(self):
        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", pady=(0, 16))

        title_box = ctk.CTkFrame(header, fg_color="transparent")
        title_box.pack(side="left")
        ctk.CTkLabel(
            title_box,
            text="Quản Lý Người Dùng & Phân Quyền",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color=THEME["text_primary"]
        ).pack(anchor="w")

        # Thanh tìm kiếm dạng viên thuốc
        search_box = ctk.CTkFrame(header, fg_color="transparent")
        search_box.pack(side="right")
        self.u_search_var = tk.StringVar()

        u_search_entry = ctk.CTkEntry(
            search_box,
            placeholder_text="Tìm theo ID, Username, Họ tên...",
            textvariable=self.u_search_var,
            width=260,
            height=38,
            fg_color=THEME["input_bg"],
            border_color=THEME["input_border"],
            border_width=1,
            corner_radius=RADIUS["pill"],
            text_color=THEME["text_primary"],
            placeholder_text_color=THEME["text_muted"]
        )
        u_search_entry.pack(side="left", padx=6)
        u_search_entry.bind("<Return>", lambda _: self.load_data())

        ctk.CTkButton(
            search_box,
            text="Tìm Kiếm",
            width=85,
            height=38,
            fg_color=THEME["primary"],
            hover_color=THEME["primary_hover"],
            font=ctk.CTkFont(size=12, weight="bold"),
            corner_radius=RADIUS["pill"],
            command=self.load_data
        ).pack(side="left", padx=3)

        ctk.CTkButton(
            search_box,
            text="Tất Cả",
            width=70,
            height=38,
            fg_color=THEME["btn_secondary"],
            hover_color=THEME["btn_secondary_hover"],
            text_color=THEME["btn_secondary_text"],
            font=ctk.CTkFont(size=12),
            corner_radius=RADIUS["pill"],
            command=lambda: [self.u_search_var.set(""), self.load_data()]
        ).pack(side="left", padx=3)

        # Form thao tác người dùng
        top = ctk.CTkFrame(
            self,
            fg_color=THEME["card_bg"],
            corner_radius=RADIUS["card"],
            border_color=THEME["card_border"],
            border_width=1
        )
        top.pack(fill="x", pady=(0, 16))

        self.u_id_var = tk.StringVar()
        self.u_username_var = tk.StringVar()
        self.u_password_var = tk.StringVar()
        self.u_fullname_var = tk.StringVar()
        self.u_role_var = tk.StringVar(value="staff")

        # Row 0: Inputs
        ctk.CTkLabel(
            top,
            text="Tên đăng nhập:",
            font=ctk.CTkFont(size=12),
            text_color=THEME["text_secondary"]
        ).grid(row=0, column=0, padx=(16, 6), pady=(12, 6), sticky="e")

        self.entry_username = ctk.CTkEntry(
            top,
            textvariable=self.u_username_var,
            width=160,
            height=36,
            fg_color=THEME["input_bg"],
            border_color=THEME["input_border"],
            border_width=1,
            corner_radius=RADIUS["input"],
            text_color=THEME["text_primary"]
        )
        self.entry_username.grid(row=0, column=1, padx=6, pady=(12, 6), sticky="w")

        ctk.CTkLabel(
            top,
            text="Mật khẩu:",
            font=ctk.CTkFont(size=12),
            text_color=THEME["text_secondary"]
        ).grid(row=0, column=2, padx=(16, 6), pady=(12, 6), sticky="e")

        self.entry_password = ctk.CTkEntry(
            top,
            textvariable=self.u_password_var,
            width=160,
            height=36,
            show="*",
            fg_color=THEME["input_bg"],
            border_color=THEME["input_border"],
            border_width=1,
            corner_radius=RADIUS["input"],
            text_color=THEME["text_primary"],
            placeholder_text="Mật khẩu..."
        )
        self.entry_password.grid(row=0, column=3, padx=6, pady=(12, 6), sticky="w")

        ctk.CTkLabel(
            top,
            text="Họ và tên:",
            font=ctk.CTkFont(size=12),
            text_color=THEME["text_secondary"]
        ).grid(row=0, column=4, padx=(16, 6), pady=(12, 6), sticky="e")

        self.entry_fullname = ctk.CTkEntry(
            top,
            textvariable=self.u_fullname_var,
            width=200,
            height=36,
            fg_color=THEME["input_bg"],
            border_color=THEME["input_border"],
            border_width=1,
            corner_radius=RADIUS["input"],
            text_color=THEME["text_primary"]
        )
        self.entry_fullname.grid(row=0, column=5, padx=6, pady=(12, 6), sticky="w")

        ctk.CTkLabel(
            top,
            text="Quyền hạn:",
            font=ctk.CTkFont(size=12),
            text_color=THEME["text_secondary"]
        ).grid(row=0, column=6, padx=(16, 6), pady=(12, 6), sticky="e")

        self.role_menu = ctk.CTkOptionMenu(
            top,
            values=["Admin (Quản trị)", "Nhân viên"],
            width=160,
            height=36,
            corner_radius=RADIUS["input"],
            fg_color=THEME["input_bg"],
            text_color=THEME["text_primary"],
            button_color=THEME["primary"],
            button_hover_color=THEME["primary_hover"],
            command=self._on_role_change
        )
        self.role_menu.grid(row=0, column=7, padx=(6, 16), pady=(12, 6), sticky="w")
        self.role_menu.set("Nhân viên")

        # Row 1: Action buttons
        btn_box = ctk.CTkFrame(top, fg_color="transparent")
        btn_box.grid(row=1, column=0, columnspan=8, padx=16, pady=(8, 14), sticky="w")

        ctk.CTkButton(
            btn_box,
            text="Thêm Mới",
            width=100,
            height=36,
            fg_color=THEME["primary"],
            hover_color=THEME["primary_hover"],
            font=ctk.CTkFont(size=12, weight="bold"),
            corner_radius=RADIUS["pill"],
            command=self.add_user
        ).pack(side="left", padx=4)

        ctk.CTkButton(
            btn_box,
            text="Cập Nhật",
            width=100,
            height=36,
            fg_color=THEME["accent_orange"],
            hover_color=THEME["accent_orange_hover"],
            text_color=THEME["text_white"],
            font=ctk.CTkFont(size=12, weight="bold"),
            corner_radius=RADIUS["pill"],
            command=self.update_user
        ).pack(side="left", padx=4)

        ctk.CTkButton(
            btn_box,
            text="Xóa",
            width=80,
            height=36,
            fg_color=THEME["accent_red"],
            hover_color=THEME["accent_red_hover"],
            text_color=THEME["text_white"],
            font=ctk.CTkFont(size=12, weight="bold"),
            corner_radius=RADIUS["pill"],
            command=self.delete_user
        ).pack(side="left", padx=4)

        ctk.CTkButton(
            btn_box,
            text="Làm Mới",
            width=90,
            height=36,
            fg_color=THEME["btn_secondary"],
            hover_color=THEME["btn_secondary_hover"],
            text_color=THEME["btn_secondary_text"],
            font=ctk.CTkFont(size=12),
            corner_radius=RADIUS["pill"],
            command=self.clear_form
        ).pack(side="left", padx=4)

        # Bảng dữ liệu người dùng
        tbl_card = ctk.CTkFrame(
            self,
            fg_color=THEME["card_bg"],
            corner_radius=RADIUS["card"],
            border_color=THEME["card_border"],
            border_width=1
        )
        tbl_card.pack(fill="both", expand=True)

        self.tree = ttk.Treeview(tbl_card, columns=("id", "username", "fullname", "role"), show="headings")
        cols = [
            ("id", "Mã", 80),
            ("username", "Tên Đăng Nhập", 200),
            ("fullname", "Họ Và Tên", 320),
            ("role", "Quyền Hạn", 160)
        ]
        for c, h, w in cols:
            self.tree.heading(c, text=h)
            self.tree.column(c, width=w, anchor="center" if c in ("id", "role") else "w")

        self.tree.pack(fill="both", expand=True, padx=14, pady=14)
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

    def _on_role_change(self, val):
        if "Admin" in val:
            self.u_role_var.set("admin")
        else:
            self.u_role_var.set("staff")

    def load_data(self):
        if not self.controller:
            self.controller = getattr(self.app, "controllers", {}).get("user")
        if not self.controller or (hasattr(self.app, "db") and self.app.db.connection_error):
            return

        for item in self.tree.get_children():
            self.tree.delete(item)

        kw = self.u_search_var.get().strip() if hasattr(self, "u_search_var") else None
        users = self.controller.get_users(kw)
        for u in users:
            role_label = "Quản trị viên (Admin)" if u["role"] == "admin" else "Nhân viên"
            self.tree.insert("", "end", values=(u["id"], u["username"], u["full_name"], role_label))

    def on_select(self, _):
        sel = self.tree.selection()
        if not sel:
            return
        v = self.tree.item(sel[0])["values"]
        self.u_id_var.set(v[0])
        self.u_username_var.set(v[1])
        self.entry_username.configure(state="disabled") # Không cho đổi username
        self.u_fullname_var.set(v[2])
        self.u_password_var.set("") # Xóa mật khẩu form
        self.entry_password.configure(placeholder_text="Để trống nếu không đổi")

        if "Admin" in str(v[3]):
            self.role_menu.set("Admin (Quản trị)")
            self.u_role_var.set("admin")
        else:
            self.role_menu.set("Nhân viên")
            self.u_role_var.set("staff")

    def clear_form(self):
        self.u_id_var.set("")
        self.u_username_var.set("")
        self.entry_username.configure(state="normal")
        self.u_password_var.set("")
        self.entry_password.configure(placeholder_text="Mật khẩu...")
        self.u_fullname_var.set("")
        self.role_menu.set("Nhân viên")
        self.u_role_var.set("staff")
        if self.tree.selection():
            self.tree.selection_remove(self.tree.selection())

    def add_user(self):
        if not self.controller:
            self.controller = getattr(self.app, "controllers", {}).get("user")

        ok, msg = self.controller.add_user(
            self.u_username_var.get(),
            self.u_password_var.get(),
            self.u_fullname_var.get(),
            self.u_role_var.get()
        )
        if not ok:
            messagebox.showwarning("Lỗi", msg)
            return

        messagebox.showinfo("Thành công", msg)
        self.clear_form()
        self.load_data()

    def update_user(self):
        if not self.controller:
            self.controller = getattr(self.app, "controllers", {}).get("user")

        uid = self.u_id_var.get()
        if not uid:
            messagebox.showwarning("Chọn mục", "Vui lòng chọn người dùng cần cập nhật từ danh sách.")
            return

        current_user_id = None
        if hasattr(self.app, "current_user") and self.app.current_user:
            current_user_id = self.app.current_user.get("id")

        ok, msg = self.controller.update_user(
            uid,
            self.u_fullname_var.get(),
            self.u_role_var.get(),
            self.u_password_var.get() or None,
            current_user_id=current_user_id
        )
        if not ok:
            messagebox.showwarning("Lỗi", msg)
            return

        messagebox.showinfo("Thành công", msg)
        self.clear_form()
        self.load_data()

    def delete_user(self):
        if not self.controller:
            self.controller = getattr(self.app, "controllers", {}).get("user")

        uid = self.u_id_var.get()
        if not uid:
            messagebox.showwarning("Chọn mục", "Vui lòng chọn người dùng cần xóa từ danh sách.")
            return

        current_user_id = None
        if hasattr(self.app, "current_user") and self.app.current_user:
            current_user_id = self.app.current_user.get("id")

        if not messagebox.askyesno("Xác nhận", "Bạn có chắc chắn muốn xóa người dùng này?"):
            return

        ok, msg = self.controller.delete_user(uid, current_user_id=current_user_id)
        if not ok:
            messagebox.showerror("Không thể xóa", msg)
            return

        messagebox.showinfo("Thành công", msg)
        self.clear_form()
        self.load_data()
