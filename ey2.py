import requests

API_URL = "https://api.siliconflow.cn/v1/chat/completions"
API_KEY = "sk-eisgfevoxkvnrqgubncjikuobqyohuzafrshvnmamtnobhzh"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

def ask_ai(prompt):
    data = {
        "model": "Qwen/Qwen2.5-14B-Instruct",
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }
    response = requests.post(API_URL, headers=headers, json=data)
    result = response.json()
    return result["choices"][0]["message"]["content"]
ordinary_prompt = "什么是函数"
structured_prompt = """你是一位经验丰富的编程教师。
【背景】用户是编程初学者，对技术概念理解有限。
【任务】请解释什么是函数。
【要求】
- 使用通俗易懂的语言
- 给出生活中的实际例子
- 不超过 5 句话"""
print("=" * 50)
print("【普通 Prompt】")
print("=" * 50)
print(ordinary_prompt)
print("\n回答：")
answer1 = ask_ai(ordinary_prompt)
print(answer1)
print("\n" + "=" * 50)
print("【结构化 Prompt】")
print("=" * 50)
print(structured_prompt)
print("\n回答：")
answer2 = ask_ai(structured_prompt)
print(answer2)
print("\n" + "=" * 50)
print("【对比观察记录】")
print("=" * 50)
print("""
1. 回答详细程度：结构化 Prompt 的回答更完整、更有条理，
   普通 Prompt 的回答通常较为简洁，可能缺乏背景铺垫。

2. 实用性强弱：结构化 Prompt 明确要求"给出生活例子"，
   因此回答中会包含具体的类比（如"把函数看作自动售货机"），
   而普通 Prompt 可能只给出抽象定义。

3. 内容针对性：结构化 Prompt 指定了"初学者"这一背景，
   AI 会相应调整解释的深度和用语，确保易于理解；
   普通 Prompt 没有明确受众，回答可能过于专业或笼统。
""")