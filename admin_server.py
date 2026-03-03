from http.server import HTTPServer, SimpleHTTPRequestHandler
import urllib.request
import os
import re

ADMIN_DIR = '/path/to/your/down'

class CustomHandler(SimpleHTTPRequestHandler):
    def translate_path(self, path):
        if path == '/' or path == '':
            return os.path.join(ADMIN_DIR, 'index.html')
        elif path == '/admin' or path == '/admin/':
            return os.path.join(ADMIN_DIR, 'admin.html')
        elif path == '/favicon.ico':
            return os.path.join(ADMIN_DIR, 'favicon.ico')
        
        # 其他路径返回不存在的文件，导致404
        return os.path.join(ADMIN_DIR, '404.html')
    
    def do_GET(self):
        if self.path.startswith("/api/"):
            api_url = "http://localhost:8082" + self.path
            try:
                req = urllib.request.Request(api_url, headers=self.headers)
                with urllib.request.urlopen(req) as response:
                    self.send_response(response.getcode())
                    for key, value in response.getheaders():
                        if key not in ["Content-Encoding", "Content-Length"]:
                            self.send_header(key, value)
                    self.end_headers()
                    self.wfile.write(response.read())
                return
            except Exception as e:
                self.send_response(500)
                self.send_header("Content-Type", "text/plain")
                self.end_headers()
                self.wfile.write(str(e).encode())
                return
        
        super().do_GET()
    
    def do_POST(self):
        if self.path.startswith("/api/"):
            api_url = "http://localhost:8082" + self.path
            try:
                content_length = int(self.headers.get("Content-Length", 0))
                post_data = self.rfile.read(content_length)
                req = urllib.request.Request(api_url, data=post_data, headers=self.headers, method="POST")
                with urllib.request.urlopen(req) as response:
                    self.send_response(response.getcode())
                    for key, value in response.getheaders():
                        if key not in ["Content-Encoding", "Content-Length"]:
                            self.send_header(key, value)
                    self.end_headers()
                    self.wfile.write(response.read())
                return
            except Exception as e:
                self.send_response(500)
                self.send_header("Content-Type", "text/plain")
                self.end_headers()
                self.wfile.write(str(e).encode())
                return
        super().do_POST()
    
    def do_PUT(self):
        if self.path.startswith("/api/"):
            api_url = "http://localhost:8082" + self.path
            try:
                content_length = int(self.headers.get("Content-Length", 0))
                post_data = self.rfile.read(content_length)
                req = urllib.request.Request(api_url, data=post_data, headers=self.headers, method="PUT")
                with urllib.request.urlopen(req) as response:
                    self.send_response(response.getcode())
                    for key, value in response.getheaders():
                        if key not in ["Content-Encoding", "Content-Length"]:
                            self.send_header(key, value)
                    self.end_headers()
                    self.wfile.write(response.read())
                return
            except Exception as e:
                self.send_response(500)
                self.send_header("Content-Type", "text/plain")
                self.end_headers()
                self.wfile.write(str(e).encode())
                return
        super().do_PUT()
    
    def do_DELETE(self):
        if self.path.startswith("/api/"):
            api_url = "http://localhost:8082" + self.path
            try:
                req = urllib.request.Request(api_url, headers=self.headers, method="DELETE")
                with urllib.request.urlopen(req) as response:
                    self.send_response(response.getcode())
                    for key, value in response.getheaders():
                        if key not in ["Content-Encoding", "Content-Length"]:
                            self.send_header(key, value)
                    self.end_headers()
                    self.wfile.write(response.read())
                return
            except Exception as e:
                self.send_response(500)
                self.send_header("Content-Type", "text/plain")
                self.end_headers()
                self.wfile.write(str(e).encode())
                return
        super().do_DELETE()
    
    def end_headers(self):
        self.send_header('Cache-Control', 'no-cache')
        super().end_headers()

if __name__ == '__main__':
    server = HTTPServer(('0.0.0.0', 8081), CustomHandler)
    print('Admin Server running on http://your-ip:8081/')
    server.serve_forever()
