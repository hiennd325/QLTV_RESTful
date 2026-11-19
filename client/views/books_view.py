"""
Books View — Màn hình Quản Lý Sách
"""
import io
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import customtkinter as ctk
from PIL import Image

from client.theme import THEME, RADIUS


class BooksView(ctk.CTkFrame):
    def __init__(self, parent, app, controller=None):
        super().__init__(parent, fg_color="transparent")
        self.app = app
        self.controller = controller or getattr(app, "controllers", {}).get("book")
        self.books_cache = {}
        self.current_cover_url = None
        self.selected_local_image = None
        self._current_ctk_image = None
        self._cover_cache = {}
        self.setup_ui()

    def setup_ui(self):
        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", pady=(0, 16))

        title_box = ctk.CTkFrame(header, fg_color="transparent")
        title_box.pack(side="left")
        ctk.CTkLabel(
            title_box,
            text="Quản Lý Kho Sách",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color=THEME["text_primary"]
        ).pack(anchor="w")

        # Thanh tìm kiếm dạng viên thuốc
        search_box = ctk.CTkFrame(header, fg_color="transparent")
        search_box.pack(side="right")
        self.b_search_var = tk.StringVar()

        b_search_entry = ctk.CTkEntry(
            search_box,
            placeholder_text="Tìm theo ID, Tên sách, Tác giả...",
            textvariable=self.b_search_var,
            width=270,
            height=38,
            fg_color=THEME["input_bg"],
            border_color=THEME["input_border"],
            border_width=1,
            corner_radius=RADIUS["pill"],
            text_color=THEME["text_primary"],
            placeholder_text_color=THEME["text_muted"]
        )
        b_search_entry.pack(side="left", padx=6)
        b_search_entry.bind("<Return>", lambda _: self.load_data())

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
            command=lambda: [self.b_search_var.set(""), self.load_data()]
        ).pack(side="left", padx=3)

        # Thẻ Bảng Dữ Liệu
        tbl_card = ctk.CTkFrame(
            self,
            fg_color=THEME["card_bg"],
            corner_radius=RADIUS["card"],
            border_color=THEME["card_border"],
            border_width=1
        )
        tbl_card.pack(fill="both", expand=True, pady=(0, 16))

        self.tree = ttk.Treeview(tbl_card, columns=("id", "title", "author", "cat", "total", "avail", "cover"), show="headings")
        cols = [
            ("id", "ID", 50),
            ("title", "Tên Sách", 320),
            ("author", "Tác Giả", 180),
            ("cat", "Thể Loại", 130),
            ("total", "Tổng Số", 70),
            ("avail", "Sẵn Có", 70),
            ("cover", "Ảnh Bìa", 70)
        ]
        for c, h, w in cols:
            self.tree.heading(c, text=h)
            self.tree.column(c, width=w, anchor="center" if c in ("id", "total", "avail", "cover") else "w")

        self.tree.pack(fill="both", expand=True, padx=14, pady=14)
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

        # Thẻ Form Thêm / Sửa
        form = ctk.CTkFrame(
            self,
            fg_color=THEME["card_bg"],
            corner_radius=RADIUS["card"],
            border_color=THEME["card_border"],
            border_width=1
        )
        form.pack(fill="x")

        self.b_id_var, self.b_title_var = tk.StringVar(), tk.StringVar()
        self.b_author_var, self.b_cat_var, self.b_total_var = tk.StringVar(), tk.StringVar(), tk.StringVar(value="1")

        # Tên sách:
        ctk.CTkLabel(
            form,
            text="Tên sách:",
            font=ctk.CTkFont(size=12),
            text_color=THEME["text_secondary"]
        ).grid(row=0, column=0, padx=14, pady=10, sticky="e")

        ctk.CTkEntry(
            form,
            textvariable=self.b_title_var,
            width=260,
            height=34,
            fg_color=THEME["input_bg"],
            border_color=THEME["input_border"],
            border_width=1,
            corner_radius=RADIUS["input"],
            text_color=THEME["text_primary"]
        ).grid(row=0, column=1, padx=6, pady=10, sticky="w")

        # Tác giả:
        ctk.CTkLabel(
            form,
            text="Tác giả:",
            font=ctk.CTkFont(size=12),
            text_color=THEME["text_secondary"]
        ).grid(row=0, column=2, padx=14, pady=10, sticky="e")

        ctk.CTkEntry(
            form,
            textvariable=self.b_author_var,
            width=200,
            height=34,
            fg_color=THEME["input_bg"],
            border_color=THEME["input_border"],
            border_width=1,
            corner_radius=RADIUS["input"],
            text_color=THEME["text_primary"]
        ).grid(row=0, column=3, padx=6, pady=10, sticky="w")

        # Thể loại (chọn từ danh sách đã thêm, không nhập tự do)
        ctk.CTkLabel(
            form,
            text="Thể loại:",
            font=ctk.CTkFont(size=12),
            text_color=THEME["text_secondary"]
        ).grid(row=1, column=0, padx=14, pady=10, sticky="e")

        self.b_cat_combo = ctk.CTkComboBox(
            form,
            variable=self.b_cat_var,
            values=["(Chưa có thể loại)"],
            width=260,
            height=34,
            state="readonly",
            fg_color=THEME["input_bg"],
            border_color=THEME["input_border"],
            border_width=1,
            corner_radius=RADIUS["input"],
            text_color=THEME["text_primary"],
            button_color=THEME["primary"],
            button_hover_color=THEME["primary_hover"]
        )
        self.b_cat_combo.grid(row=1, column=1, padx=6, pady=10, sticky="w")

        # Số lượng:
        ctk.CTkLabel(
            form,
            text="Số lượng:",
            font=ctk.CTkFont(size=12),
            text_color=THEME["text_secondary"]
        ).grid(row=1, column=2, padx=14, pady=10, sticky="e")

        ctk.CTkEntry(
            form,
            textvariable=self.b_total_var,
            width=200,
            height=34,
            fg_color=THEME["input_bg"],
            border_color=THEME["input_border"],
            border_width=1,
            corner_radius=RADIUS["input"],
            text_color=THEME["text_primary"]
        ).grid(row=1, column=3, padx=6, pady=10, sticky="w")

        # Khung tải ảnh bìa sách
        cover_card = ctk.CTkFrame(form, fg_color="transparent")
        cover_card.grid(row=0, column=4, rowspan=2, padx=(10, 6), pady=8)

        self.cover_label = ctk.CTkLabel(
            cover_card,
            text="Chưa có\nảnh bìa",
            width=70,
            height=80,
            fg_color=THEME["input_bg"],
            corner_radius=RADIUS["input"],
            text_color=THEME["text_muted"],
            font=ctk.CTkFont(size=11)
        )
        self.cover_label.pack(side="left", padx=(0, 8))

        cover_btn_box = ctk.CTkFrame(cover_card, fg_color="transparent")
        cover_btn_box.pack(side="left")

        ctk.CTkButton(
            cover_btn_box,
            text="Chọn Ảnh",
            width=80,
            height=32,
            fg_color=THEME["primary"],
            hover_color=THEME["primary_hover"],
            font=ctk.CTkFont(size=11, weight="bold"),
            corner_radius=RADIUS["pill"],
            command=self.choose_cover_image
        ).pack(pady=(0, 4))

        ctk.CTkButton(
            cover_btn_box,
            text="Bỏ Ảnh",
            width=80,
            height=32,
            fg_color=THEME["btn_secondary"],
            hover_color=THEME["btn_secondary_hover"],
            text_color=THEME["btn_secondary_text"],
            font=ctk.CTkFont(size=11),
            corner_radius=RADIUS["pill"],
            command=self.remove_cover_image
        ).pack()

        # Các nút bấm thao tác dạng viên thuốc
        btn_box = ctk.CTkFrame(form, fg_color="transparent")
        btn_box.grid(row=0, column=5, rowspan=2, padx=(10, 16), pady=10)

        ctk.CTkButton(
            btn_box,
            text="Thêm Mới",
            width=100,
            height=34,
            fg_color=THEME["primary"],
            hover_color=THEME["primary_hover"],
            font=ctk.CTkFont(size=12, weight="bold"),
            corner_radius=RADIUS["pill"],
            command=self.add_book
        ).grid(row=0, column=0, padx=4, pady=4)

        ctk.CTkButton(
            btn_box,
            text="Cập Nhật",
            width=100,
            height=34,
            fg_color=THEME["accent_orange"],
            hover_color=THEME["accent_orange_hover"],
            text_color=THEME["text_white"],
            font=ctk.CTkFont(size=12, weight="bold"),
            corner_radius=RADIUS["pill"],
            command=self.update_book
        ).grid(row=0, column=1, padx=4, pady=4)

        ctk.CTkButton(
            btn_box,
            text="Xóa",
            width=100,
            height=34,
            fg_color=THEME["accent_red"],
            hover_color=THEME["accent_red_hover"],
            text_color=THEME["text_white"],
            font=ctk.CTkFont(size=12, weight="bold"),
            corner_radius=RADIUS["pill"],
            command=self.delete_book
        ).grid(row=1, column=0, padx=4, pady=4)

        ctk.CTkButton(
            btn_box,
            text="Làm Mới",
            width=100,
            height=34,
            fg_color=THEME["btn_secondary"],
            hover_color=THEME["btn_secondary_hover"],
            text_color=THEME["btn_secondary_text"],
            font=ctk.CTkFont(size=12),
            corner_radius=RADIUS["pill"],
            command=self.clear_form
        ).grid(row=1, column=1, padx=4, pady=4)

    def choose_cover_image(self):
        filetypes = [("Hình ảnh", "*.png *.jpg *.jpeg *.webp *.gif"), ("Tất cả", "*.*")]
        fpath = filedialog.askopenfilename(title="Chọn ảnh bìa sách", filetypes=filetypes)
        if fpath:
            self.selected_local_image = fpath
            self.display_cover_image(fpath, is_local=True)

    def remove_cover_image(self):
        self.selected_local_image = None
        self.current_cover_url = ""
        self.display_cover_image(None)

    def display_cover_image(self, img_source, is_local=False):
        if not img_source:
            self.cover_label.configure(image=None, text="Chưa có\nảnh bìa")
            self._current_ctk_image = None
            return

        if not is_local and img_source in self._cover_cache:
            self._current_ctk_image = self._cover_cache[img_source]
            self.cover_label.configure(image=self._current_ctk_image, text="")
            return

        try:
            if is_local:
                pil_img = Image.open(img_source)
            else:
                endpoint = img_source if img_source.startswith("/") else f"/{img_source}"
                r = self.app.api.request("GET", endpoint)
                if r.status_code == 200:
                    pil_img = Image.open(io.BytesIO(r.content))
                else:
                    self.cover_label.configure(image=None, text="Chưa có\nảnh bìa")
                    return

            pil_img.thumbnail((70, 80), Image.Resampling.LANCZOS)
            ctk_img = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(pil_img.width, pil_img.height))
            self._current_ctk_image = ctk_img
            if not is_local:
                self._cover_cache[img_source] = ctk_img
            self.cover_label.configure(image=ctk_img, text="")
        except Exception:
            self.cover_label.configure(image=None, text="Lỗi ảnh")

    def refresh_categories(self):
        cat_ctrl = getattr(self.app, "controllers", {}).get("category")
        cats = cat_ctrl.get_category_names() if cat_ctrl else []
        if cats:
            self.b_cat_combo.configure(values=cats)
            cur = self.b_cat_var.get().strip()
            if cur in cats:
                self.b_cat_combo.set(cur)
            else:
                self.b_cat_combo.set(cats[0])
                self.b_cat_var.set(cats[0])
        else:
            self.b_cat_combo.configure(values=["(Chưa có thể loại)"])
            self.b_cat_combo.set("(Chưa có thể loại)")
            self.b_cat_var.set("")

    def load_data(self):
        self.refresh_categories()
        if not self.controller:
            self.controller = getattr(self.app, "controllers", {}).get("book")
        if not self.controller or (hasattr(self.app, "db") and self.app.db.connection_error):
            return

        for item in self.tree.get_children():
            self.tree.delete(item)

        self.books_cache = {}
        kw = self.b_search_var.get().strip()
        rows = self.controller.get_books(kw)
        for r in rows:
            self.books_cache[r["id"]] = r
            has_cov = "Có" if r.get("cover_image") else "-"
            self.tree.insert("", "end", values=(r["id"], r["title"], r["author"], r["category"], r["total"], r["available"], has_cov))

    def on_select(self, _):
        sel = self.tree.selection()
        if not sel:
            return
        v = self.tree.item(sel[0])["values"]
        b_id = int(v[0])
        self.b_id_var.set(str(b_id))
        self.b_title_var.set(v[1])
        self.b_author_var.set(v[2])
        cat_val = str(v[3])
        self.b_cat_var.set(cat_val)
        self.b_cat_combo.set(cat_val)
        self.b_total_var.set(v[4])

        self.selected_local_image = None
        book = self.books_cache.get(b_id, {})
        self.current_cover_url = book.get("cover_image")
        self.display_cover_image(self.current_cover_url)

    def clear_form(self):
        self.b_id_var.set("")
        self.b_title_var.set("")
        self.b_author_var.set("")
        self.b_total_var.set("1")
        self.selected_local_image = None
        self.current_cover_url = None
        self.display_cover_image(None)
        if self.tree.selection():
            self.tree.selection_remove(self.tree.selection())
        self.refresh_categories()

    def add_book(self):
        if not self.controller:
            self.controller = getattr(self.app, "controllers", {}).get("book")

        cat_val = self.b_cat_combo.get().strip()
        if not cat_val or cat_val == "(Chưa có thể loại)":
            messagebox.showwarning("Lỗi", "Vui lòng chọn thể loại sách hợp lệ hoặc thêm thể loại tại mục Thể Loại Sách.")
            return

        cover_url = None
        if self.selected_local_image:
            ok_up, uploaded_url, up_msg = self.controller.upload_cover(self.selected_local_image)
            if not ok_up:
                messagebox.showwarning("Lỗi", f"Tải ảnh bìa thất bại: {up_msg}")
                return
            cover_url = uploaded_url

        ok, msg = self.controller.add_book(
            self.b_title_var.get(),
            self.b_author_var.get(),
            cat_val,
            self.b_total_var.get(),
            cover_image=cover_url
        )
        if not ok:
            messagebox.showwarning("Lỗi", msg)
            return

        self.clear_form()
        self.load_data()
        self.app.refresh_stats()

    def update_book(self):
        if not self.controller:
            self.controller = getattr(self.app, "controllers", {}).get("book")

        b_id = self.b_id_var.get()
        cat_val = self.b_cat_combo.get().strip()
        if not cat_val or cat_val == "(Chưa có thể loại)":
            messagebox.showwarning("Lỗi", "Vui lòng chọn thể loại sách hợp lệ.")
            return

        cover_url = self.current_cover_url
        if self.selected_local_image:
            ok_up, uploaded_url, up_msg = self.controller.upload_cover(self.selected_local_image, book_id=b_id)
            if not ok_up:
                messagebox.showwarning("Lỗi", f"Tải ảnh bìa thất bại: {up_msg}")
                return
            cover_url = uploaded_url

        ok, msg = self.controller.update_book(
            b_id,
            self.b_title_var.get(),
            self.b_author_var.get(),
            cat_val,
            self.b_total_var.get(),
            cover_image=cover_url
        )
        if not ok:
            messagebox.showwarning("Lỗi", msg)
            return

        self.clear_form()
        self.load_data()
        self.app.refresh_stats()

    def delete_book(self):
        if not self.controller:
            self.controller = getattr(self.app, "controllers", {}).get("book")

        b_id = self.b_id_var.get()
        if not b_id:
            messagebox.showwarning("Lỗi", "Hãy chọn sách cần xóa.")
            return

        if not messagebox.askyesno("Xác nhận", "Xóa sách này khỏi kho?"):
            return

        ok, msg = self.controller.delete_book(b_id)
        if not ok:
            messagebox.showerror("Lỗi", msg)
            return

        self.clear_form()
        self.load_data()
        self.app.refresh_stats()
