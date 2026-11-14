"""
Điểm khởi chạy ứng dụng LibMaster (GUI Client / Server / Self-test)
"""
import sys
from config import load_config
from client.api_client import APIClient


def self_test():
    cfg = load_config()
    api = APIClient(cfg.get("api_base_url", "http://127.0.0.1:8080"))
    ok, msg = api.check_health()
    if ok:
        print(f"Self-test: RESTful API server is HEALTHY at {api.base_url}")
    else:
        print(f"Self-test: RESTful API server connection error -> {msg}")


if __name__ == "__main__":
    if "--test" in sys.argv:
        self_test()
    elif "--server" in sys.argv:
        import uvicorn
        uvicorn.run("backend.main:app", host="0.0.0.0", port=8080, reload=True)
    else:
        from client.main import ModernLibraryApp
        app = ModernLibraryApp()
        app.mainloop()

