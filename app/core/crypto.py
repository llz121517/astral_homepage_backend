# app/core/crypto.py
import base64
import json
from typing import Dict, Any
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
from app.config import ASTRAL_AES_KEY


def decrypt_aes_cbc_payload(encrypted_b64: str) -> Dict[str, Any]:
    """
    使用 AES-CBC 模式解密 Base64 编码的负载。
    密钥从环境变量 ASTRAL_AES_KEY 读取（Base64 格式）。
    IV 预期为 ciphertext 前 16 字节。

    :param encrypted_b64: Base64 编码的 (IV + ciphertext)
    :return: 解密后的 JSON 对象（dict）
    :raises ValueError: 解密失败或格式错误
    """
    try:
        key_b64 = ASTRAL_AES_KEY
        if not key_b64:
            raise ValueError("环境变量 ASTRAL_AES_KEY 未设置")

        key = base64.b64decode(key_b64)
        if len(key) not in (16, 24, 32):
            raise ValueError("ASTRAL_AES_KEY 必须是 16/24/32 字节的 Base64 密钥（对应 AES-128/192/256）")

        encrypted = base64.b64decode(encrypted_b64)
        if len(encrypted) < 16:
            raise ValueError("加密数据太短（缺少 IV）")

        iv = encrypted[:16]
        ciphertext = encrypted[16:]

        cipher = AES.new(key, AES.MODE_CBC, iv)
        plaintext = unpad(cipher.decrypt(ciphertext), AES.block_size).decode('utf-8')
        return json.loads(plaintext)

    except (ValueError, KeyError, UnicodeDecodeError, json.JSONDecodeError) as e:
        raise ValueError(f"解密失败: {e}")