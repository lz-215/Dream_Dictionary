from http.server import BaseHTTPRequestHandler
import json

def get_model_status():
    """获取模型状态"""
    return {
        "model_available": True,
        "model_type": "Vercel Serverless Basic Analyzer",
        "features": [
            "Basic keyword matching",
            "Limited symbol dictionary",
            "Fast global response"
        ]
    }

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # 设置响应头
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        
        # 获取模型状态
        status = get_model_status()
        
        # 返回结果
        self.wfile.write(json.dumps(status).encode())
    
    def do_OPTIONS(self):
        # 处理预检请求
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
