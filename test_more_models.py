import requests

API_KEY = "sk-eisgfevoxkvnrqgubncjikuobqyohuzafrshvnmamtnobhzh"
API_URL = "https://api.siliconflow.cn/v1/chat/completions"

models_to_test = [
    "qwen2-7b-instruct",
    "qwen-7b-chat",
    "deepseek-chat-v3",
    "llama-3-8b-chat",
    "gemma-2-9b-it",
    "mistral-7b-instruct",
    "zephyr-7b-beta",
    "command-r-plus",
    "phi-3-medium",
    "mixtral-8x7b-instruct",
]

for model_name in models_to_test:
    try:
        headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
        data = {"model": model_name, "messages": [{"role": "user", "content": "hello"}]}
        response = requests.post(API_URL, headers=headers, json=data, timeout=10)
        print(f"{model_name}: 状态码 {response.status_code}")
        if response.status_code == 200:
            print(f"  ✓ 成功!")
            break
        else:
            result = response.json()
            msg = result.get('message', '未知错误')
            print(f"  ✗ {msg}")
    except Exception as e:
        print(f"{model_name}: 异常 {e}")