import requests

API_URL = "https://api.siliconflow.cn/v1/chat/completions"
API_KEY = "sk-eisgfevoxkvnrqgubncjikuobqyohuzafrshvnmamtnobhzh"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

def chat_with_ai(messages):
    """
    调用 API 进行对话
    messages: 包含对话历史的列表
    """
    data = {
        "model": "Qwen/Qwen2.5-14B-Instruct",
        "messages": messages
    }
    response = requests.post(API_URL, headers=headers, json=data)
    result = response.json()
    return result["choices"][0]["message"]["content"]

# 初始化对话历史，包含 system 消息
messages = [
    {
        "role": "system",
        "content": "你是郑州航空工业管理学院的校园信息助手，请简洁回答学生的问题。"
    }
]

print("=" * 50)
print("欢迎使用校园问答助手，输入 quit 退出")
print("=" * 50)
print()

# 多轮对话循环
while True:
    user_input = input("你：")
    
    if user_input.lower() == "quit":
        print("\n感谢使用，再见！")
        break
    
    if user_input.strip() == "":
        continue
    
    # 将用户消息添加到对话历史
    messages.append({
        "role": "user",
        "content": user_input
    })
    
    # 调用 API 获取回答
    try:
        answer = chat_with_ai(messages)
        print(f"助手：{answer}\n")
        
        # 将助手回答添加到对话历史
        messages.append({
            "role": "assistant",
            "content": answer
        })
    except Exception as e:
        print(f"发生错误：{e}\n")

"""
【3轮对话记录】

第1轮：
用户：我叫张三，是人工智能专业的
助手：好的，张三同学！很高兴认识你。作为人工智能专业的学生，如果你有任何关于课程学习、专业发展或校园生活的问题，都可以随时问我。祝你在郑州航空工业管理学院学习顺利！

第2轮：
用户：学校有哪些社团可以参加？
助手：郑州航空工业管理学院有很多学生社团可供选择，主要包括：
- 学术科技类：计算机协会、AI创新实验室、无人机协会等
- 文化体育类：篮球社、足球社、舞蹈社、吉他社等
- 志愿服务类：青年志愿者协会、红十字会等
- 创业实践类：创业俱乐部、模拟联合国等
你可以根据兴趣选择加入，丰富大学生活！

第3轮：
用户：我叫什么名字？什么专业？
助手：您叫张三，是人工智能专业的学生。
"""