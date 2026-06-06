# app/api/v1/status/device.py
from fastapi import APIRouter, HTTPException
from app.core.db.db_op import get_device_status
from app.core.state import map_device_status

router = APIRouter(prefix="/api/v1/status", tags=["status", "api_v1"])


@router.get("/device")
async def get_latest_device_status():
    """
    获取最近一次上报的设备状态
    """
    try:
        res = get_device_status()
    except RuntimeError:
        raise HTTPException(status_code=404, detail="暂无设备状态数据")
    result = map_device_status(res["status"])

    if result is None:
        raise HTTPException(status_code=404, detail="暂无设备状态数据")
    print(result)
    return result