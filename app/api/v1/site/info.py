# app/api/v1/site/info.py
from fastapi import APIRouter
from app.core.db.db_op import get_site_config

router = APIRouter(prefix="/api/v1/site", tags=["site", "api_v1"])


@router.get("/info")
async def get_site_info():
    """
    返回站点基础信息
    """
    return get_site_config()