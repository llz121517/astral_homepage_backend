from http.server import HTTPServer, BaseHTTPRequestHandler
import json, sys

class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_len = int(self.headers.get('content-length', 0))
        body = self.rfile.read(content_len)
        print("\n>>> 收到上报数据:")
        try:
            data = json.loads(body)
            for k, v in data.items():
                print(f"    {k}: {v}")
        except:
            print(body.decode('utf-8', errors='replace'))
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'OK')

if __name__ == '__main__':
    port = 8080
    print(f"监听 http://localhost:{port} ...")
    HTTPServer(('localhost', port), Handler).serve_forever()