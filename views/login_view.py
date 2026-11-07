"""
Login View — Màn hình Đăng Nhập Hệ Thống
"""
import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk

from theme import THEME, RADIUS


class LoginView(ctk.CTkFrame):
    def __init__(self, parent, app, controller=None):
        super().__init__(parent, fg_color="transparent")
        self.app = app
        self.controller = controller or getattr(app, "controllers", {}).get("user")
        self.setup_ui()

    def setup_ui(self):
        # Card đăng nhập ở giữa màn hình
        card = ctk.CTkFrame(
            self,
            fg_color=THEME["card_bg"],
            corner_radius=RADIUS["card"],
            border_color=THEME["card_border"],
            border_width=1,
            width=460
        )
        card.place(relx=0.5, rely=0.5, anchor="center")

        # Header Logo & Badge
        tag_box = ctk.CTkFrame(card, fg_color=THEME["primary_subtle"], corner_radius=RADIUS["pill"])
        tag_box.pack(pady=(32, 8))
        ctk.CTkLabel(
            tag_box,
            text="LIBMASTER SECURE ACCESS",
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color=THEME["primary_glow"]
        ).pack(padx=14, pady=4)

        ctk.CTkLabel(
            card,
            text="Đăng Nhập Hệ Thống",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=THEME["text_primary"]
        ).pack(pady=(0, 6))

        ctk.CTkLabel(
            card,
            text="Vui lòng nhập tài khoản để truy cập vào hệ thống thư viện",
            font=ctk.CTkFont(size=12),
            text_color=THEME["text_secondary"]
        ).pack(pady=(0, 24))

        # Form Inputs
        form_frame = ctk.CTkFrame(card, fg_color="transparent")
        form_frame.pack(fill="x", padx=36, pady=(0, 32))

        # Tên đăng nhập
        ctk.CTkLabel(
            form_frame,
            text="Tên đăng nhập:",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=THEME["text_secondary"]
        ).pack(anchor="w", pady=(0, 4))

        self.username_var = tk.StringVar()
        self.username_entry = ctk.CTkEntry(
            form_frame,
            textvariable=self.username_var,
            height=40,
            fg_color=THEME["input_bg"],
            border_color=THEME["input_border"],
            border_width=1,
            corner_radius=RADIUS["input"],
            text_color=THEME["text_primary"],
            placeholder_text="Nhập tên đăng nhập..."
        )
        self.username_entry.pack(fill="x", pady=(0, 14))
        self.username_entry.bind("<Return>", lambda _: self.password_entry.focus())

        # Mật khẩu
        ctk.CTkLabel(
            form_frame,
            text="Mật khẩu:",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=THEME["text_secondary"]
        ).pack(anchor="w", pady=(0, 4))

        self.password_var = tk.StringVar()
        self.password_entry = ctk.CTkEntry(
            form_frame,
            textvariable=self.password_var,
            height=40,
            show="*",
            fg_color=THEME["input_bg"],
            border_color=THEME["input_border"],
            border_width=1,
            corner_radius=RADIUS["input"],
            text_color=THEME["text_primary"],
            placeholder_text="Nhập mật khẩu..."
        )
        self.password_entry.pack(fill="x", pady=(0, 20))
        self.password_entry.bind("<Return>", lambda _: self.do_login())

        # Nút đăng nhập
        ctk.CTkButton(
            form_frame,
            text="Đăng Nhập Ngay",
            height=44,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=THEME["primary"],
            hover_color=THEME["primary_hover"],
            corner_radius=RADIUS["pill"],
            command=self.do_login
        ).pack(fill="x")

    def do_login(self):
        if not self.controller:
            self.controller = getattr(self.app, "controllers", {}).get("user")

        username = self.username_var.get()
        password = self.password_var.get()

        user, msg = self.controller.login(username, password)
        if not user:
            messagebox.showerror("Đăng nhập thất bại", msg)
            return

        self.password_var.set("")
        if hasattr(self.app, "on_login_success"):
            self.app.on_login_success(user)

    def load_data(self):
        self.username_var.set("")
        self.password_var.set("")
        self.username_entry.focus()
