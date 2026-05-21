#!/usr/bin/env python
# /run.py
import os
import uvicorn
from app.config import (
    SERVER_HOST,
    SERVER_PORT,
    RELOAD,
    WORKERS,
    LOG_LEVEL
)

if __name__ == "__main__":
    cmd = ("uvicorn app.main:app"
           f" --host {SERVER_HOST}"
           f" --port {SERVER_PORT}"
           f" --workers {WORKERS}"
           f" --log-level {LOG_LEVEL}"
    )

    if RELOAD:
        cmd += " --reload"
        cmd += " --reload-dir app --reload-dir frontend"
        cmd += " --reload-delay 0"

    os.system(cmd)
    """
    uvicorn.run(
        app="app.main:app",
        host=SERVER_HOST,
        port=SERVER_PORT,
        reload=RELOAD,
        workers=WORKERS,
        log_level=LOG_LEVEL
    )
    """