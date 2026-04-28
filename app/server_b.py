from __future__ import annotations

import sys
from pathlib import Path

import uvicorn

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.core.config import Settings
from app.main import create_app


settings = Settings.from_env()
settings.node_id = "node-b"
settings.peer_urls = ("http://127.0.0.1:8000", "http://127.0.0.1:8002")

app = create_app(settings)


if __name__ == "__main__":
    uvicorn.run("app.server_b:app", host="127.0.0.1", port=8001, reload=False)
