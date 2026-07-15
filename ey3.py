import requests

API_URL = "https://api.siliconflow.cn/v1/chat/completions"
API_KEY = "sk-eisgfevoxkvnrqgubncjikuobqyohuzafrshvnmamtnobhzh"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

def ask_campus(question):
    """
    封装 API 调用逻辑
    使用 system 角色设定为"郑州航空工业管理学院校园信息助手"
    """
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

# 主程序循环
print("=" * 50)
print("郑州航空工业管理学院 校园信息问答系统")
print("=" * 50)
print("输入 quit 退出系统\n")

while True:
    user_input = input("请输入您的问题：")
    
    if user_input.lower() == "quit":
        print("感谢使用，再见！")
        break
    
    if user_input.strip() == "":
        print("请输入有效的问题！\n")
        continue
    
    print("\n正在查询，请稍候...")
    try:
        answer = ask_campus(user_input)
        print(f"\n回答：{answer}\n")
        print("-" * 50)
    except Exception as e:
        print(f"查询失败：{e}\n")