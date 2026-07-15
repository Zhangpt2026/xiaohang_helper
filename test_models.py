import requests

API_KEY = "sk-eisgfevoxkvnrqgubncjikuobqyohuzafrshvnmamtnobhzh"
API_URL = "https://api.siliconflow.cn/v1/chat/completions"

models_to_test = [
    "glm-4.5",
    "GLM-4.5",
    "GLM-4",
    "glm-4",
    "deepseek-chat",
    "deepseek-v3",
    "Qwen2-7B-Instruct",
    "Qwen/Qwen2-7B-Instruct",
    "ZhipuAI/glm-4.5",
]

for model_name in models_to_test:
    try:
        headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
        data = {"model": model_name, "messages": [{"role": "user", "content": "hi"}]}
        response = requests.post(API_URL, headers=headers, json=data, timeout=10)
        print(f"{model_name}: 状态码 {response.status_code}")
        if response.status_code == 200:
            print(f"  ✓ 成功!")
            break
        else:
            result = response.json()
            print(f"  ✗ {result.get('message', '未知错误')}")
    except Exception as e:
        print(f"{model_name}: 异常 {e}")