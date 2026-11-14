"""
Reports Router — Báo cáo & Phân tích số liệu thống kê
"""
from typing import Optional
from fastapi import APIRouter, Depends, Query
from backend.models.report import ReportModel
from backend.schemas import ReportResponse, ReportKPIs, TopBookItem, TopCategoryItem
from backend.dependencies import get_report_model, get_current_user

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
