# /run.py
import uvicorn
from app.config import (
    SERVER_HOST,
    SERVER_PORT,
    RELOAD,
    WORKERS,
    LOG_LEVEL
)

if __name__ == "__main__":
    uvicorn.run(
        app="app.main:app",
        host=SERVER_HOST,
        port=SERVER_PORT,
        reload=RELOAD,
        workers=WORKERS,
        log_level=LOG_LEVEL
    )