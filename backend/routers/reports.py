"""
Reports Router — Báo cáo & Phân tích số liệu thống kê & Xuất file Excel/PDF
"""
import io
from datetime import date
from typing import Optional
from fastapi import APIRouter, Depends, Query, HTTPException, status
from fastapi.responses import StreamingResponse
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

from backend.models.report import ReportModel
from backend.models.book import BookModel
from backend.models.borrow import BorrowModel
from backend.models.member import MemberModel
from backend.schemas import ReportResponse, ReportKPIs, TopBookItem, TopCategoryItem
from backend.dependencies import get_report_model, get_book_model, get_borrow_model, get_member_model, get_current_user

router = APIRouter(prefix="/api/reports", tags=["Reports"])


@router.get("", response_model=ReportResponse)
def get_reports(
    limit: Optional[int] = Query(10, ge=1, le=50, description="Giới hạn top sách và thể loại"),
    report_model: ReportModel = Depends(get_report_model),
    _: dict = Depends(get_current_user)
):
    kpis_raw = report_model.get_kpis()
    top_books_raw = report_model.get_top_books(limit)
    top_categories_raw = report_model.get_top_categories(limit)

    return ReportResponse(
        kpis=ReportKPIs(**kpis_raw),
        top_books=[TopBookItem(**b) for b in top_books_raw],
        top_categories=[TopCategoryItem(**c) for c in top_categories_raw]
    )


@router.get("/export/excel")
def export_excel(
    report_type: str = Query("all", description="Loại báo cáo: books, borrows, members, all"),
    book_model: BookModel = Depends(get_book_model),
    borrow_model: BorrowModel = Depends(get_borrow_model),
    member_model: MemberModel = Depends(get_member_model),
    _: dict = Depends(get_current_user)
):
    wb = openpyxl.Workbook()
    # Style chuẩn
    header_font = Font(name="Arial", size=11, bold=True, color="FFFFFF")
    header_fill = PatternFill(start_color="4F46E5", end_color="4F46E5", fill_type="solid")
    title_font = Font(name="Arial", size=14, bold=True, color="1E1B4B")
    thin_border = Border(
        left=Side(style='thin', color='E2E8F0'),
        right=Side(style='thin', color='E2E8F0'),
        top=Side(style='thin', color='E2E8F0'),
        bottom=Side(style='thin', color='E2E8F0')
    )

    # 1. Sheet Sách
    if report_type in ("all", "books"):
        ws = wb.active if "Sheet" in wb.sheetnames else wb.create_sheet(title="Kho Sách")
        ws.title = "Kho Sách"
        ws.append(["BÁO CÁO KHO SÁCH — THƯ VIỆN LIBMASTER"])
        ws["A1"].font = title_font
        ws.append([f"Ngày xuất: {date.today().strftime('%d/%m/%Y')}"])
        ws.append([])

        headers = ["ID", "Tên Sách", "Tác Giả", "Thể Loại", "Tổng Số", "Sẵn Có", "Đang Mượn"]
        ws.append(headers)
        h_row = ws.max_row
        for col_idx in range(1, len(headers) + 1):
            cell = ws.cell(row=h_row, column=col_idx)
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = Alignment(horizontal="center", vertical="center")

        books = book_model.get_all()
        for b in books:
            borrowed = b["total"] - b["available"]
            row = [b["id"], b["title"], b["author"], b["category"], b["total"], b["available"], borrowed]
            ws.append(row)
            for c_idx in range(1, len(row) + 1):
                c = ws.cell(row=ws.max_row, column=c_idx)
                c.border = thin_border
                if c_idx in (1, 5, 6, 7):
                    c.alignment = Alignment(horizontal="center")

        # Auto width
        for col in ws.columns:
            max_len = max(len(str(cell.value or '')) for cell in col)
            ws.column_dimensions[col[0].column_letter].width = max(max_len + 3, 10)

    # 2. Sheet Mượn / Trả
    if report_type in ("all", "borrows"):
        ws_b = wb.create_sheet(title="Mượn Trả")
        ws_b.append(["BÁO CÁO GIAO DỊCH MƯỢN TRẢ SÁCH"])
        ws_b["A1"].font = title_font
        ws_b.append([f"Ngày xuất: {date.today().strftime('%d/%m/%Y')}"])
        ws_b.append([])

        b_headers = ["Mã Phiếu", "Độc Giả", "Tên Sách", "Ngày Mượn", "Hạn Trả", "Ngày Trả", "Trạng Thái", "Gia Hạn", "Tiền Phạt (VND)"]
        ws_b.append(b_headers)
        h_row = ws_b.max_row
        for col_idx in range(1, len(b_headers) + 1):
            cell = ws_b.cell(row=h_row, column=col_idx)
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = Alignment(horizontal="center", vertical="center")

        borrows = borrow_model.get_all()
        for r in borrows:
            st = "Quá hạn" if r["status"] == "borrowed" and str(r["due_date"]) < date.today().strftime("%Y-%m-%d") else ("Đang mượn" if r["status"] == "borrowed" else "Đã trả")
            row = [
                r["id"], r["member_name"], r["book_title"],
                str(r["borrow_date"]), str(r["due_date"]), str(r["return_date"] or "-"),
                st, r.get("renew_count") or 0, r.get("fine_amount") or 0
            ]
            ws_b.append(row)
            for c_idx in range(1, len(row) + 1):
                c = ws_b.cell(row=ws_b.max_row, column=c_idx)
                c.border = thin_border
                if c_idx in (1, 4, 5, 6, 7, 8):
                    c.alignment = Alignment(horizontal="center")
                elif c_idx == 9:
                    c.alignment = Alignment(horizontal="right")

        for col in ws_b.columns:
            max_len = max(len(str(cell.value or '')) for cell in col)
            ws_b.column_dimensions[col[0].column_letter].width = max(max_len + 3, 10)

    # 3. Sheet Bạn Đọc
    if report_type in ("all", "members"):
        ws_m = wb.create_sheet(title="Độc Giả")
        ws_m.append(["DANH SÁCH ĐỘC GIẢ THƯ VIỆN"])
        ws_m["A1"].font = title_font
        ws_m.append([f"Ngày xuất: {date.today().strftime('%d/%m/%Y')}"])
        ws_m.append([])

        m_headers = ["Mã Độc Giả", "Họ Và Tên", "Email", "Số Điện Thoại"]
        ws_m.append(m_headers)
        h_row = ws_m.max_row
        for col_idx in range(1, len(m_headers) + 1):
            cell = ws_m.cell(row=h_row, column=col_idx)
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = Alignment(horizontal="center", vertical="center")

        members = member_model.get_all()
        for m in members:
            row = [m["id"], m["name"], m["email"], m["phone"]]
            ws_m.append(row)
            for c_idx in range(1, len(row) + 1):
                c = ws_m.cell(row=ws_m.max_row, column=c_idx)
                c.border = thin_border
                if c_idx in (1, 4):
                    c.alignment = Alignment(horizontal="center")

        for col in ws_m.columns:
            max_len = max(len(str(cell.value or '')) for cell in col)
            ws_m.column_dimensions[col[0].column_letter].width = max(max_len + 3, 10)

    stream = io.BytesIO()
    wb.save(stream)
    stream.seek(0)

    filename = f"LibMaster_Report_{date.today().strftime('%Y%m%d')}.xlsx"
    return StreamingResponse(
        stream,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@router.get("/export/pdf")
def export_pdf(
    report_type: str = Query("books", description="Loại báo cáo: books, borrows, members"),
    book_model: BookModel = Depends(get_book_model),
    borrow_model: BorrowModel = Depends(get_borrow_model),
    member_model: MemberModel = Depends(get_member_model),
    _: dict = Depends(get_current_user)
):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=24, leftMargin=24, topMargin=24, bottomMargin=24)
    styles = getSampleStyleSheet()

    elements = []
    title_style = ParagraphStyle(
        'MainTitle',
        parent=styles['Heading1'],
        fontSize=18,
        leading=22,
        textColor=colors.HexColor("#1E1B4B"),
        spaceAfter=6
    )
    subtitle_style = ParagraphStyle(
        'SubTitle',
        parent=styles['Normal'],
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#64748B"),
        spaceAfter=14
    )

    if report_type == "borrows":
        elements.append(Paragraph("<b>BÁO CÁO GIAO DỊCH MƯỢN TRẢ</b>", title_style))
        elements.append(Paragraph(f"Ngày xuất: {date.today().strftime('%d/%m/%Y')} | Đơn vị: Thư viện LibMaster", subtitle_style))
        data = [["Mã", "Độc Giả", "Tên Sách", "Ngày Mượn", "Hạn Trả", "Trạng Thái", "Phạt"]]
        borrows = borrow_model.get_all()[:40]
        today = date.today().strftime("%Y-%m-%d")
        for b in borrows:
            st = "Quá hạn" if b["status"] == "borrowed" and str(b["due_date"]) < today else ("Đang mượn" if b["status"] == "borrowed" else "Đã trả")
            fine = f"{b.get('fine_amount', 0):,}đ" if b.get('fine_amount') else "-"
            data.append([
                str(b["id"]),
                str(b["member_name"])[:16],
                str(b["book_title"])[:22],
                str(b["borrow_date"]),
                str(b["due_date"]),
                st,
                fine
            ])
        col_widths = [30, 95, 130, 65, 65, 65, 55]
    elif report_type == "members":
        elements.append(Paragraph("<b>DANH SÁCH ĐỘC GIẢ THƯ VIỆN</b>", title_style))
        elements.append(Paragraph(f"Ngày xuất: {date.today().strftime('%d/%m/%Y')} | Đơn vị: Thư viện LibMaster", subtitle_style))
        data = [["ID", "Họ Và Tên", "Email", "Số Điện Thoại"]]
        members = member_model.get_all()[:50]
        for m in members:
            data.append([str(m["id"]), str(m["name"])[:25], str(m["email"])[:30], str(m["phone"])])
        col_widths = [40, 160, 180, 120]
    else: # books
        elements.append(Paragraph("<b>BÁO CÁO DANH MỤC KHO SÁCH</b>", title_style))
        elements.append(Paragraph(f"Ngày xuất: {date.today().strftime('%d/%m/%Y')} | Đơn vị: Thư viện LibMaster", subtitle_style))
        data = [["ID", "Tên Sách", "Tác Giả", "Thể Loại", "Tổng", "Sẵn"]]
        books = book_model.get_all()[:50]
        for b in books:
            data.append([
                str(b["id"]),
                str(b["title"])[:26],
                str(b["author"])[:18],
                str(b["category"])[:16],
                str(b["total"]),
                str(b["available"])
            ])
        col_widths = [35, 175, 125, 105, 35, 35]

    t = Table(data, colWidths=col_widths)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#4F46E5")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
        ('TOPPADDING', (0, 0), (-1, 0), 6),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('ALIGN', (1, 1), (2, -1), 'LEFT'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
    ]))

    elements.append(t)
    doc.build(elements)
    buffer.seek(0)

    filename = f"LibMaster_{report_type}_{date.today().strftime('%Y%m%d')}.pdf"
    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
