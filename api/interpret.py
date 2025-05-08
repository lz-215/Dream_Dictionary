from http.server import BaseHTTPRequestHandler
import json
import re
from datetime import datetime

# 简化版的梦境解析逻辑
dream_symbols = {
    "water": "Water often represents emotions, the unconscious, or a state of transition.",
    "flying": "Flying can symbolize freedom, escape, or a desire to rise above a situation.",
    "falling": "Falling may indicate insecurity, loss of control, or fear of failure.",
    "teeth": "Dreams about teeth can relate to anxiety, appearance, or communication issues.",
    "house": "A house typically represents the self, with different rooms symbolizing different aspects of your personality.",
    "car": "Cars often represent your direction in life, personal drive, or how you present yourself to others.",
    "death": "Death in dreams usually symbolizes transformation, endings, or change rather than literal death.",
    "snake": "Snakes can represent wisdom, transformation, healing, or hidden fears.",
    "baby": "Babies often symbolize new beginnings, innocence, or aspects of yourself that are vulnerable.",
    "money": "Money can represent self-worth, power, or how you value yourself and others."
}

def analyze_dream(dream_text):
    """分析梦境文本并返回解释"""
    dream_lower = dream_text.lower()
    results = []
    
    # 检查梦境文本中是否包含已知的符号
    for symbol, interpretation in dream_symbols.items():
        if symbol in dream_lower:
            results.append({
                "keyword": symbol.capitalize(),
                "interpretation": interpretation
            })
    
    # 如果没有找到任何符号，提供一个通用的回应
    if not results:
        results.append({
            "keyword": "General",
            "interpretation": "Your dream contains elements that may represent your subconscious thoughts. Dreams are highly personal, and you might want to consider what these symbols mean specifically to you."
        })
    
    # 生成简单的摘要
    dream_summary = "Your dream appears to involve "
    if len(results) > 1:
        keywords = [r["keyword"].lower() for r in results]
        dream_summary += ", ".join(keywords[:-1]) + " and " + keywords[-1] + "."
    else:
        dream_summary += results[0]["keyword"].lower() + "."
    
    # 生成心理学视角
    psych_perspective = "From a psychological perspective, this dream may reflect your current emotional state or recent experiences. Consider how the symbols in your dream might connect to your waking life and what emotions they evoke."
    
    return {
        "dream_summary": dream_summary,
        "interpretations": results,
        "psychological_perspective": psych_perspective,
        "model_used": "vercel_serverless",
        "processing_time": "0.05s"
    }

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        # 设置响应头
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        
        # 获取请求体长度
        content_length = int(self.headers['Content-Length'])
        # 读取请求体
        post_data = self.rfile.read(content_length)
        # 解析JSON
        data = json.loads(post_data.decode('utf-8'))
        
        # 获取梦境文本
        dream_text = data.get('dream_text', '')
        
        if not dream_text:
            self.wfile.write(json.dumps({"error": "Dream description cannot be empty"}).encode())
            return
        
        # 分析梦境
        result = analyze_dream(dream_text)
        
        # 返回结果
        self.wfile.write(json.dumps(result).encode())
    
    def do_OPTIONS(self):
        # 处理预检请求
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
