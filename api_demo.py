import requests
API_URL = "https://api.siliconflow.cn/v1/chat/completions"
API_KEY = "sk-eisgfevoxkvnrqgubncjikuobqyohuzafrshvnmamtnobhzh"
headers = {
"Authorization": f"Bearer {API_KEY}",
"Content-Type": "application/json"
}
data = {
"model": "deepseek-ai/DeepSeek-OCR",
"messages": [
{"role": "user", "content": "请用 3 句话介绍郑州航空工业管理学院"}
]
}
response = requests.post(API_URL, headers=headers, json=data)
result = response.json()
answer = result["choices"][0]["message"]["content"]
print(answer)
print(f"总Token数: {result['usage']['total_tokens']}")