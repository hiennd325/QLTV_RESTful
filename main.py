"""
LibMaster RESTful API Server — Điểm khởi chạy ứng dụng
"""
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import load_config
from database import Database
from routers import (
    auth_router,
    users_router,
    books_router,
    categories_router,
    members_router,
    borrows_router,
    overdue_router,
    dashboard_router,
    reports_router
)

cfg = load_config()

app = FastAPI(
    title="LibMaster RESTful API",
    description="Hệ thống quản lý thư viện hiện đại cung cấp đầy đủ RESTful API cho Sách, Thể loại, Độc giả, Mượn/Trả, Cảnh báo quá hạn, Người dùng và Báo cáo.",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Cấu hình CORS cho phép các ứng dụng Frontend kết nối linh hoạt
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Đăng ký các Router nghiệp vụ
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(books_router)
app.include_router(categories_router)
app.include_router(members_router)
app.include_router(borrows_router)
app.include_router(overdue_router)
app.include_router(dashboard_router)
app.include_router(reports_router)


@app.get("/", tags=["General"])
def root():
    return {
        "app": "LibMaster RESTful API",
        "version": "2.0.0",
        "docs": "/docs",
        "redoc": "/redoc",
        "status": "running"
    }


@app.get("/health", tags=["General"])
def health_check():
    db = Database(cfg)
    if db.connection_error:
        return {"status": "unhealthy", "database_error": db.connection_error}
    return {"status": "healthy", "database": "connected"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
