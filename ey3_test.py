import requests
API_URL = "https://api.siliconflow.cn/v1/chat/completions"
API_KEY = "sk-eisgfevoxkvnrqgubncjikuobqyohuzafrshvnmamtnobhzh"
headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}
def ask_campus(question):
    data = {
        "model": "Qwen/Qwen2.5-14B-Instruct",
        "messages": [
            {
                "role": "system",
                "content": "你是一位郑州航空工业管理学院校园信息助手，专门回答关于学校的问题。"
            },
            {
                "role": "user",
                "content": question
            }
        ]
    }
    response = requests.post(API_URL, headers=headers, json=data)
    result = response.json()
    return result["choices"][0]["message"]["content"]
print("=" * 50)
print("郑州航空工业管理学院 校园信息问答系统")
print("=" * 50)
print()
test_questions = [
    "学校有哪些食堂？",
    "学校地址在哪？",
    "学校有哪些专业？"
]

for i, question in enumerate(test_questions, 1):
    print(f"\n【问题 {i}】{question}")
    print("-" * 50)
    try:
        answer = ask_campus(question)
        print(f"回答：{answer}")
    except Exception as e:
        print(f"查询失败：{e}")
    print()

print("=" * 50)
print("测试完成！")
print("=" * 50)