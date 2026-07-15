import requests

API_KEY = "sk-eisgfevoxkvnrqgubncjikuobqyohuzafrshvnmamtnobhzh"
API_URL = "https://api.siliconflow.cn/v1/models"

headers = {"Authorization": f"Bearer {API_KEY}"}

try:
    response = requests.get(API_URL, headers=headers, timeout=10)
    print(f"状态码: {response.status_code}")
    result = response.json()
    if "data" in result:
        for model in result["data"]:
            print(f"- {model['id']}")
    else:
        print(f"响应: {result}")
except Exception as e:
    print(f"异常: {e}")