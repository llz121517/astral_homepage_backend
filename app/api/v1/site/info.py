# app/api/v1/site/info.py
from app.core import site
from fastapi import Depends, APIRouter
from app.core.auth import admin_required

router = APIRouter(prefix="/api/v1/site", tags=["site", "api_v1"])


@router.get("/info")
async def get_site_info():
    """
    返回用户信息
    """
    return site.get_site_info()

@router.post("/info/update", dependencies=[Depends(admin_required)])
async def update_site_info(data: dict):
    """
    更新站点信息
    """
    return site.update_site_info(data)