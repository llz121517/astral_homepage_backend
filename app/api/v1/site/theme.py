# app/api/v1/site/theme.py
import json

from fastapi import APIRouter, Query
from app.core.db.db_op import get_theme_by_id

router = APIRouter(prefix="/api/v1/site", tags=["site", "api_v1"])


@router.get("/theme")
async def get_site_theme(theme_id: int = Query(0, description="0=全量列表；大于0=单条")):
    if theme_id < 0:
        return {"code": 0, "msg": "参数错误"}

    data = get_theme_by_id(theme_id)
    if not data:
        msg = "暂无主题数据" if theme_id == 0 else "主题不存在"
        return {"code": 0, "msg": msg}

    return {"code": 1, "msg": "success", "data": data}