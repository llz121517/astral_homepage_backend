from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import sys
import os
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import base64


class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_len = int(self.headers.get('content-length', 0))
        body = self.rfile.read(content_len)

        encrypted_base64 = body.decode('utf-8').strip()

        print("\n>>> 收到上报数据 (加密)：")
        print(f"    {encrypted_base64}")

        try:
            # 加载 AES 密钥（从环境变量）
            key_b64 = os.getenv("ASTRAL_AES_KEY")
            if not key_b64:
                print("未设置环境变量 ASTRAL_AES_KEY")
                self.send_response(500)
                self.end_headers()
                return

            key = base64.b64decode(key_b64)
            encrypted = base64.b64decode(encrypted_base64)

            # 拆分 IV + 密文
            iv = encrypted[:16]
            ciphertext = encrypted[16:]

            # 解密
            cipher = AES.new(key, AES.MODE_CBC, iv)
            plaintext = unpad(cipher.decrypt(ciphertext), AES.block_size).decode('utf-8')

            print(">>> 解密后:")
            data = json.loads(plaintext)
            for k, v in data.items():
                print(f"    {k}: {v}")

        except Exception as e:
            print(f"解密/解析失败: {e}")

        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'OK')


if __name__ == '__main__':
    port = 8080
    print(f"监听 http://localhost:{port} ...")
    HTTPServer(('localhost', port), Handler).serve_forever()