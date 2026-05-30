# app/api/v1/report.py
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse
from app.core.crypto import decrypt_aes_cbc_payload

# 从 state 导入最近设备状态字典
from app.core.state import latest_device_status

router = APIRouter(prefix="/api/v1", tags=["report", "status"])


@router.post("/report")
async def receive_status_report(request: Request):
    try:
        body = await request.body()
        encrypted_b64 = body.decode('utf-8').strip()
        if not encrypted_b64:
            raise HTTPException(status_code=400, detail="空请求体")

        data = decrypt_aes_cbc_payload(encrypted_b64)

        # 更新到变量
        latest_device_status.clear()
        latest_device_status.update(data)

        print("\n>>> 收到设备状态:")
        for k, v in data.items():
            print(f"    {k}: {v}")

        return JSONResponse({"status": "ok"})

    except ValueError as ve:
        print(f"[ERROR] {ve}")
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        print(f"[ERROR] 服务器错误: {e}")
        raise HTTPException(status_code=500, detail="Internal Error")