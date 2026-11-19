"""
Reports View — Màn hình Báo Cáo & Phân Tích Thống Kê
"""
from tkinter import ttk, filedialog, messagebox
import customtkinter as ctk

from client.theme import THEME, RADIUS


class ReportsView(ctk.CTkScrollableFrame):
    """
    Màn hình Báo Cáo & Phân Tích Thống Kê cao cấp:
    - 4 Thẻ KPI bo góc thiết kế tối giản, thanh lịch
    - Phân tích Top Sách & Top Thể Loại
    - Xuất Báo Cáo ra file Excel & PDF
    """
    def __init__(self, parent, app, controller=None):
        super().__init__(parent, fg_color="transparent")
        self.app = app
        self.controller = controller or getattr(app, "controllers", {}).get("report")
        self.setup_ui()

    def setup_ui(self):
        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", pady=(0, 16))

        title_box = ctk.CTkFrame(header, fg_color="transparent")
        title_box.pack(side="left")
        ctk.CTkLabel(
            title_box,
            text="Báo Cáo & Phân Tích Thống Kê",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color=THEME["text_primary"]
        ).pack(anchor="w")

        # Cụm nút Xuất Báo Cáo
        export_box = ctk.CTkFrame(header, fg_color="transparent")
        export_box.pack(side="right")

        ctk.CTkButton(
            export_box,
            text="📊 Xuất Excel",
            width=110,
            height=36,
            fg_color="#10B981",
            hover_color="#059669",
            font=ctk.CTkFont(size=12, weight="bold"),
            corner_radius=RADIUS["pill"],
            command=self.do_export_excel
        ).pack(side="left", padx=4)

        ctk.CTkButton(
            export_box,
            text="📄 Xuất PDF",
            width=110,
            height=36,
            fg_color=THEME["accent_red"],
            hover_color=THEME["accent_red_hover"],
            font=ctk.CTkFont(size=12, weight="bold"),
            corner_radius=RADIUS["pill"],
            command=self.do_export_pdf
        ).pack(side="left", padx=4)

        # 4 Thẻ KPI bo góc chuẩn phong cách phẳng
        cards_grid = ctk.CTkFrame(self, fg_color="transparent")
        cards_grid.pack(fill="x", pady=(0, 16))
        cards_grid.grid_columnconfigure((0, 1, 2, 3), weight=1)

        self.kpi_widgets = {}
        kpi_defs = [
            ("books", "Tổng Đầu Sách", THEME["primary"]),
            ("members", "Tổng Bạn Đọc", THEME["accent_cyan"]),
            ("borrows", "Tổng Lượt Mượn", THEME["primary_glow"]),
            ("fines", "Tiền Phạt Thu Về", THEME["accent_orange"])
        ]
        for idx, (k, title, color) in enumerate(kpi_defs):
            card = ctk.CTkFrame(
                cards_grid,
                fg_color=THEME["card_bg"],
                corner_radius=RADIUS["card"],
                border_color=THEME["card_border"],
                border_width=1
            )
            card.grid(row=0, column=idx, padx=6, sticky="ew")

            top_row = ctk.CTkFrame(card, fg_color="transparent")
            top_row.pack(fill="x", padx=16, pady=(16, 4))

            ctk.CTkLabel(
                top_row,
                text=title,
                font=ctk.CTkFont(size=12),
                text_color=THEME["text_secondary"]
            ).pack(side="left")

            val_lbl = ctk.CTkLabel(
                card,
                text="0",
                font=ctk.CTkFont(size=24, weight="bold"),
                text_color=color
            )
            val_lbl.pack(anchor="w", padx=16, pady=(0, 16))
            self.kpi_widgets[k] = val_lbl

        # Bảng Top Sách & Top Thể Loại
        grid_frame = ctk.CTkFrame(self, fg_color="transparent")
        grid_frame.pack(fill="both", expand=True)
        grid_frame.grid_columnconfigure((0, 1), weight=1)

        c1 = ctk.CTkFrame(
            grid_frame,
            fg_color=THEME["card_bg"],
            corner_radius=RADIUS["card"],
            border_color=THEME["card_border"],
            border_width=1
        )
        c1.grid(row=0, column=0, padx=6, sticky="nsew")

        ctk.CTkLabel(
            c1,
            text="Top Sách Được Mượn Nhiều Nhất",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=THEME["text_primary"]
        ).pack(anchor="w", padx=16, pady=(14, 8))

        self.top_books_tree = ttk.Treeview(c1, columns=("title", "count"), show="headings", height=8)
        self.top_books_tree.heading("title", text="Tên Sách")
        self.top_books_tree.heading("count", text="Lượt Mượn")
        self.top_books_tree.column("title", width=280)
        self.top_books_tree.column("count", width=80, anchor="center")
        self.top_books_tree.pack(fill="both", expand=True, padx=14, pady=(0, 14))

        c2 = ctk.CTkFrame(
            grid_frame,
            fg_color=THEME["card_bg"],
            corner_radius=RADIUS["card"],
            border_color=THEME["card_border"],
            border_width=1
        )
        c2.grid(row=0, column=1, padx=6, sticky="nsew")

        ctk.CTkLabel(
            c2,
            text="Thể Loại Sách Phổ Biến Nhất",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=THEME["text_primary"]
        ).pack(anchor="w", padx=16, pady=(14, 8))

        self.top_cats_tree = ttk.Treeview(c2, columns=("cat", "count"), show="headings", height=8)
        self.top_cats_tree.heading("cat", text="Thể Loại")
        self.top_cats_tree.heading("count", text="Tổng Mượn")
        self.top_cats_tree.column("cat", width=220)
        self.top_cats_tree.column("count", width=80, anchor="center")
        self.top_cats_tree.pack(fill="both", expand=True, padx=14, pady=(0, 14))

    def load_data(self):
        if not self.controller:
            self.controller = getattr(self.app, "controllers", {}).get("report")
        if not self.controller or (hasattr(self.app, "db") and self.app.db.connection_error):
            return

        data = self.controller.get_report_data()
        kpis = data["kpis"]

        self.kpi_widgets["books"].configure(text=str(kpis["books_count"]))
        self.kpi_widgets["members"].configure(text=str(kpis["members_count"]))
        self.kpi_widgets["borrows"].configure(text=str(kpis["borrows_count"]))
        self.kpi_widgets["fines"].configure(text=f"{kpis['fines_total']:,}đ")

        for item in self.top_books_tree.get_children():
            self.top_books_tree.delete(item)
        for r in data["top_books"]:
            self.top_books_tree.insert("", "end", values=(r["title"], r["cnt"]))

        for item in self.top_cats_tree.get_children():
            self.top_cats_tree.delete(item)
        for r in data["top_categories"]:
            self.top_cats_tree.insert("", "end", values=(r["category"], r["cnt"]))

    def do_export_excel(self):
        if not self.controller:
            self.controller = getattr(self.app, "controllers", {}).get("report")
        file_path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel Files", "*.xlsx")],
            initialfile="LibMaster_BaoCao.xlsx",
            title="Lưu file Báo Cáo Excel"
        )
        if not file_path:
            return

        ok, msg = self.controller.export_excel(file_path, report_type="all")
        if ok:
            messagebox.showinfo("Thành công", f"{msg}\nĐã lưu tại: {file_path}")
        else:
            messagebox.showerror("Lỗi xuất Excel", msg)

    def do_export_pdf(self):
        if not self.controller:
            self.controller = getattr(self.app, "controllers", {}).get("report")
        file_path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF Files", "*.pdf")],
            initialfile="LibMaster_BaoCao_KhoSach.pdf",
            title="Lưu file Báo Cáo PDF"
        )
        if not file_path:
            return

        ok, msg = self.controller.export_pdf(file_path, report_type="books")
        if ok:
            messagebox.showinfo("Thành công", f"{msg}\nĐã lưu tại: {file_path}")
        else:
            messagebox.showerror("Lỗi xuất PDF", msg)
