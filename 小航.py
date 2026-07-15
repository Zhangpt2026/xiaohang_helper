import requests

API_URL = "https://api.siliconflow.cn/v1/chat/completions"
API_KEY = "sk-eisgfevoxkvnrqgubncjikuobqyohuzafrshvnmamtnobhzh"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

user_types = {
    "1": {
        "name": "大一新生",
        "scenarios": ["新生入学适应", "校园生活入门", "学业基础开启", "校园服务初识"],
        "questions": [
            "新生入学报到流程和需要准备的材料有哪些？",
            "宿舍入住规则、设施维修和熄灯时间是怎样的？",
            "校园卡充值、挂失和食堂/超市使用的相关问题？",
            "一年学费多少，餐厅在哪？"
        ],
        "functions": ["校园问答", "推荐问题"],
        "priority": "高"
    },
    "2": {
        "name": "在校老生",
        "scenarios": ["日常学业进阶", "校园生活服务", "学业事务办理", "校园功能深度使用"],
        "questions": [
            "课程退改选、成绩查询和绩点计算的相关规则？",
            "校园网连接、带宽升级和故障报修的方式？",
            "图书馆借阅、续借、馆藏查询和自习室预约？",
            "校园内各类证明（在读、成绩）的办理流程？"
        ],
        "functions": ["校园问答", "电话黄页"],
        "priority": "中"
    },
    "3": {
        "name": "教师",
        "scenarios": ["教学办公管理", "师生服务对接", "校园行政办事", "科研服务支持"],
        "questions": [
            "教室预约、多媒体设备使用和故障报修的流程？",
            "学生成绩录入、教学任务安排和课表查询？",
            "校园办公系统登录、公文流转和行政事务办理？",
            "科研项目申报、经费报销和学术资源获取？"
        ],
        "functions": ["校园问答", "电话黄页"],
        "priority": "中"
    }
}

role_prompts = {
    "1": "你是一名热情友好的高校新生辅导员，专门帮助大一新生适应大学生活。你的语气亲切温暖，回答简洁明了，避免使用专业术语。",
    "2": "你是一名资深的在校学生，熟悉校园各项事务和规章制度。你的语气沉稳专业，提供的信息准确可靠，包含具体的操作步骤。",
    "3": "你是一名高校行政助理，熟悉教学管理和行政办公流程。你的语气正式严谨，提供的信息规范权威，符合学校官方表述。"
}

def chat_with_ai(messages, user_role):
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

def select_user_type():
    print("=" * 50)
    print("欢迎使用校园智能问答助手 - 小航")
    print("=" * 50)
    print("\n请选择你的身份：")
    print("1. 大一新生")
    print("2. 在校老生")
    print("3. 教师")
    
    while True:
        choice = input("\n请输入选项（1/2/3）：")
        if choice in user_types:
            return choice
        print("无效选项，请重新输入！")

def main():
    user_choice = select_user_type()
    user_info = user_types[user_choice]
    
    print(f"\n你好！{user_info['name']}")
    print("=" * 50)
    print(f"使用场景：{'、'.join(user_info['scenarios'])}")
    print(f"对应功能：{'、'.join(user_info['functions'])}")
    print(f"优先级：{user_info['priority']}")
    
    print("\n推荐问题：")
    for i, q in enumerate(user_info['questions'], 1):
        print(f"{i}. {q}")
    
    messages = []
    messages.append({"role": "system", "content": role_prompts[user_choice]})
    
    print("\n" + "=" * 50)
    print("开始提问吧（输入 quit 退出）")
    print("=" * 50)
    
    while True:
        user_input = input("\n你：")
        if user_input.lower() == "quit":
            print("再见！")
            break
        
        messages.append({"role": "user", "content": user_input})
        answer = chat_with_ai(messages, user_choice)
        print(f"\n小航：{answer}")

if __name__ == "__main__":
    main()