# app/api/v1/report.py
from fastapi import APIRouter, Request, HTTPException, Body
from fastapi.responses import JSONResponse
from app.core.crypto import decrypt_aes_cbc_payload
from app.core.db.db_op import update_device_status


router = APIRouter(prefix="/api/v1", tags=["report", "status"])


@router.post("/report")
async def receive_status_report(
    request: Request,
    body: bytes = Body(..., max_length=64 * 1024)  # 限制 64KB
):
    try:
        encrypted_b64 = body.decode('utf-8').strip()
        if not encrypted_b64:
            raise HTTPException(status_code=400, detail="空请求体")

        data = decrypt_aes_cbc_payload(encrypted_b64)

        # 入库
        hostname = data["hostname"]
        if "hostname" not in data:
            raise HTTPException(status_code=400, detail="缺少 hostname 字段")
        update_device_status(hostname, data)

        print("\n>>> 收到设备状态:")
        for k, v in data.items():
            print(f"    {k}: {v}")

        return JSONResponse({"status": "ok"})

    except ValueError as ve:
        print(f"[ERROR] {ve}")
        raise HTTPException(status_code=400, detail="无效的加密数据或格式错误")
    except Exception as e:
        print(f"[ERROR] 服务器错误: {e}")
        raise HTTPException(status_code=500, detail="Internal Error")