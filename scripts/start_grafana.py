from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

def main() -> int:
    print("=" * 60)
    print("🚀 DAY 13 AI OBSERVABILITY - GRAFANA STACK LAUNCHER")
    print("=" * 60)
    print("Stack bao gồm: Grafana + Loki + Promtail")
    print("File log theo dõi: data/logs.jsonl")
    print("Giao diện Grafana: http://localhost:3000 (User: admin / Pass: admin)")
    print("=" * 60)
    
    compose_file = REPO_ROOT / "docker-compose.yml"
    if not compose_file.exists():
        print(f"❌ Không tìm thấy docker-compose.yml tại {compose_file}")
        return 1
        
    try:
        print("\n⏳ Đang khởi chạy Docker Compose...")
        cmd = ["docker", "compose", "up", "-d"]
        res = subprocess.run(cmd, cwd=REPO_ROOT, check=False)
        if res.returncode == 0:
            print("\n✅ Grafana Stack đã được khởi chạy thành công!")
            print("👉 Mở trình duyệt và truy cập: http://localhost:3000")
            print("👉 Chọn Dashboard 'Day 13 AI Observability Dashboard'")
            return 0
        else:
            print("\n⚠️ Docker Compose gặp lỗi khi khởi chạy. Vui lòng kiểm tra Docker Desktop.")
            return res.returncode
    except Exception as exc:
        print(f"\n❌ Lỗi khi thực thi docker compose: {exc}")
        print("Vui lòng đảm bảo Docker Desktop đã được cài đặt và đang chạy.")
        return 1

if __name__ == "__main__":
    raise SystemExit(main())
