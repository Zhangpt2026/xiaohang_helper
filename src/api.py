import requests
from config import API_URL, API_KEY

def ask_xiaohang(identity, question, school_data, get_system_prompt, check_hard_rules):
    if not question or not question.strip():
        return "请输入你的问题，我才能帮你解答哦！"
    
    rule_response = check_hard_rules(question)
    if rule_response:
        return rule_response
    system_prompt = get_system_prompt(identity, school_data)
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "deepseek-ai/DeepSeek-V4-Flash",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": question.strip()}
        ]
    }
    
    try:
        response = requests.post(API_URL, headers=headers, json=data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            if "choices" in result:
                answer = result["choices"][0]["message"]["content"]
                return answer
            else:
                return f"API 返回格式错误"
        elif response.status_code == 401:
            return "API Key 失效或未配置，请联系管理员检查"
        elif response.status_code == 403:
            return "API 权限不足，请检查 Key 是否正确"
        elif response.status_code == 429:
            return "请求过于频繁，请稍后再试"
        else:
            return f"请求失败，状态码: {response.status_code}"
    
    except requests.exceptions.Timeout:
        return "请求超时，请检查网络连接或稍后再试"
    except requests.exceptions.ConnectionError:
        return "网络连接失败，请检查网络设置"
    except requests.exceptions.RequestException as e:
        return f"网络请求异常: {str(e)}"
    except Exception as e:
        return f"调用失败: {str(e)}"

if __name__ == "__main__":
    print("测试 API 模块...")
    
    from src.prompt import get_system_prompt, check_hard_rules
    
    test_identity = "新生"
    test_question = "学费什么时候交"
    test_data = "学费缴纳时间：每年8月20日至9月10日。[来源:01_新生入学.md]"
    
    print(f"测试问题: {test_question}")
    print("正在调用 API...")
    result = ask_xiaohang(test_identity, test_question, test_data, get_system_prompt, check_hard_rules)
    print(f"结果: {result}")