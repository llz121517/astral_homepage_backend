# app/api/v1/status/device.py
from fastapi import APIRouter, HTTPException
from ..report import latest_device_status  # 从 report 模块导入共享状态
from app.core.state import map_device_status

router = APIRouter(prefix="/api/v1/status", tags=["status"])


@router.get("/device")
async def get_latest_device_status():
    """
    获取最近一次上报的设备状态
    """
    result = await map_device_status(latest_device_status)

    if result is None:
        raise HTTPException(status_code=404, detail="暂无设备状态数据")

    return result