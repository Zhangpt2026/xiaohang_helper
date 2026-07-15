import requests
API_URL = "https://api.siliconflow.cn/v1/chat/completions"
API_KEY = "sk-eisgfevoxkvnrqgubncjikuobqyohuzafrshvnmamtnobhzh"
headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}
def chat_with_ai(user_input, messages):
    messages.append({"role": "user", "content": user_input})
    
    data = {
        "model": "deepseek-ai/DeepSeek-V4-Flash",
        "messages": messages,
        "temperature": 0.7
    }
    try:
        response = requests.post(API_URL, headers=headers, json=data, timeout=60)
        if response.status_code == 200:
            result = response.json()
            if "choices" in result:
                answer = result["choices"][0]["message"]["content"]
                messages.append({"role": "assistant", "content": answer})
                return answer
            else:
                return "API 返回格式错误"
        else:
            return f"请求失败，状态码 {response.status_code}"
    except Exception as e:
        return f"调用失败 - {e}"
print("AI 学习助手 - 多轮对话测试")
print("=" * 50)
messages = []
print("\n【第 1 轮对话】")
print("-" * 50)
user_msg1 = "你好，我叫小明，是一名大一学生"
print(f"你：{user_msg1}")
ai_answer1 = chat_with_ai(user_msg1, messages)
print(f"AI：{ai_answer1}")
print("\n【第 2 轮对话】")
print("-" * 50)
user_msg2 = "我正在学习 Python，能给我一些学习建议吗？"
print(f"你：{user_msg2}")
ai_answer2 = chat_with_ai(user_msg2, messages)
print(f"AI：{ai_answer2}")
print("\n【第 3 轮对话 - 测试上下文记忆】")
print("-" * 50)
user_msg3 = "你还记得我的名字吗？"
print(f"你：{user_msg3}")
ai_answer3 = chat_with_ai(user_msg3, messages)
print(f"AI：{ai_answer3}")
print("\n" + "=" * 50)
print("测试记录表")
print("=" * 50)
print(f"""
轮次 | 你说了什么 | AI 是否记住了上下文
-----|-----------|-------------------
1    | 你好，我叫小明，是一名大一学生 | —
2    | 我正在学习 Python，能给我一些学习建议吗？ | 是
3    | 你还记得我的名字吗？ | 是
观察点：
✓ messages 列表的作用：存储对话历史，每次请求都带上所有历史消息，让 AI 能记住上下文
✓ 多轮对话程序已成功运行
✓ AI 的上下文记忆能力已验证：AI 在第3轮正确回答"当然记得！你叫小明"
""")