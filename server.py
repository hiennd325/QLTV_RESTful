"""
LibMaster RESTful API Server Runner
"""
import uvicorn
from config import load_config
from main import app

if __name__ == "__main__":
    cfg = load_config()
    # Phân tích port từ api_base_url (mặc định 8080)
    url = cfg.get("api_base_url", "http://127.0.0.1:8080")
    port = 8080
    try:
        parts = url.split(":")
        if len(parts) >= 3:
            port = int(parts[2].split("/")[0])
    except Exception:
        port = 8080

    print(f"Khởi chạy LibMaster RESTful API Server tại cổng {port}...")
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
