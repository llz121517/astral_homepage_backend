# app/api/v1/report.py
import os
import json
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
import base64
from app.config import ASTRAL_AES_KEY

# 从 state 导入最近设备状态字典
from app.core.state import latest_device_status

router = APIRouter(prefix="/api/v1", tags=["report", "status"])

def decrypt_payload(encrypted_b64: str) -> dict:
    try:
        key_b64 = ASTRAL_AES_KEY
        if not key_b64:
            raise ValueError("环境变量 ASTRAL_AES_KEY 未设置")

        key = base64.b64decode(key_b64)
        if len(key) not in (16, 24, 32):  # 支持 AES-128/192/256
            raise ValueError("ASTRAL_AES_KEY 必须是 16/24/32 字节的 Base64 密钥（对应 AES-128/192/256）")

        encrypted = base64.b64decode(encrypted_b64)
        if len(encrypted) < 16:
            raise ValueError("加密数据太短（缺少 IV）")

        iv = encrypted[:16]
        ciphertext = encrypted[16:]

        cipher = AES.new(key, AES.MODE_CBC, iv)
        plaintext = unpad(cipher.decrypt(ciphertext), AES.block_size).decode('utf-8')
        return json.loads(plaintext)

    except Exception as e:
        raise ValueError(f"解密失败: {e}")

@router.post("/report")
async def receive_status_report(request: Request):
    try:
        body = await request.body()
        encrypted_b64 = body.decode('utf-8').strip()
        if not encrypted_b64:
            raise HTTPException(status_code=400, detail="空请求体")

        data = decrypt_payload(encrypted_b64)

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