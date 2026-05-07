# app/api/v1/status/device.py
from fastapi import APIRouter, HTTPException
from ..report import latest_device_status  # 从 report 模块导入共享状态

router = APIRouter(prefix="/api/v1/status", tags=["status"])


@router.get("/device")
async def get_latest_device_status():
    """
    获取最近一次上报的设备状态
    """
    if not latest_device_status:
        raise HTTPException(status_code=404, detail="暂无设备状态数据")

    return latest_device_status