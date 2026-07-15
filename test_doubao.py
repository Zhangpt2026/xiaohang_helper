import requests

API_KEY = "sk-eisgfevoxkvnrqgubncjikuobqyohuzafrshvnmamtnobhzh"
API_URL = "https://api.doubao.com/v1/chat/completions"

try:
    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
    data = {"model": "Doubao-7B-Instruct", "messages": [{"role": "user", "content": "hi"}]}
    response = requests.post(API_URL, headers=headers, json=data, timeout=10)
    print(f"状态码: {response.status_code}")
    print(f"响应: {response.text[:1000]}")
except Exception as e:
    print(f"异常: {e}")