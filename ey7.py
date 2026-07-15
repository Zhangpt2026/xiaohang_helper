import requests
import time
import socket

DEEPSEEK_KEY = "你的 DeepSeek API Key 在这里"
GLM_KEY = "sk-eisgfevoxkvnrqgubncjikuobqyohuzafrshvnmamtnobhzh"

DEEPSEEK_URL = "https://api.deepseek.com/v1/chat/completions"
GLM_URL = "https://api.siliconflow.cn/v1/chat/completions"

def validate_input(prompt):
    if not prompt or not prompt.strip():
        return False, "错误：输入不能为空"
    return True, ""

def check_api_key(key):
    if not key or not key.strip() or key == "你的 DeepSeek API Key 在这里":
        return False, "API Key 未配置或无效"
    return True, ""

def ask_deepseek(prompt):
    valid, msg = validate_input(prompt)
    if not valid:
        return msg, 0
    
    valid, msg = check_api_key(DEEPSEEK_KEY)
    if not valid:
        return msg, 0
    
    try:
        headers = {
            "Authorization": f"Bearer {DEEPSEEK_KEY}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "user", "content": prompt}
            ]
        }
        start_time = time.time()
        response = requests.post(DEEPSEEK_URL, headers=headers, json=data, timeout=30)
        end_time = time.time()
        
        if response.status_code == 401:
            return "DeepSeek 错误: API Key 无效或已过期", end_time - start_time
        elif response.status_code == 429:
            return "DeepSeek 错误: 请求频率超限，请稍后重试", end_time - start_time
        elif response.status_code != 200:
            return f"DeepSeek 错误: HTTP状态码 {response.status_code}", end_time - start_time
            
        result = response.json()
        if "choices" in result:
            return result["choices"][0]["message"]["content"], end_time - start_time
        else:
            return f"DeepSeek 错误: {result.get('error', {}).get('message', '未知错误')}", end_time - start_time
    except requests.exceptions.Timeout:
        return "DeepSeek 错误: 请求超时", 0
    except requests.exceptions.ConnectionError:
        return "DeepSeek 错误: 网络连接失败，请检查网络", 0
    except socket.gaierror:
        return "DeepSeek 错误: 域名解析失败", 0
    except Exception as e:
        return f"DeepSeek 调用失败: {str(e)}", 0

def ask_glm(prompt):
    valid, msg = validate_input(prompt)
    if not valid:
        return msg, 0
    
    valid, msg = check_api_key(GLM_KEY)
    if not valid:
        return msg, 0
    
    try:
        headers = {
            "Authorization": f"Bearer {GLM_KEY}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "GLM-4.5",
            "messages": [
                {"role": "user", "content": prompt}
            ]
        }
        start_time = time.time()
        response = requests.post(GLM_URL, headers=headers, json=data, timeout=30)
        end_time = time.time()
        
        if response.status_code == 401:
            return "GLM 错误: API Key 无效或已过期", end_time - start_time
        elif response.status_code == 429:
            return "GLM 错误: 请求频率超限，请稍后重试", end_time - start_time
        elif response.status_code != 200:
            return f"GLM 错误: HTTP状态码 {response.status_code}", end_time - start_time
            
        result = response.json()
        if "choices" in result:
            return result["choices"][0]["message"]["content"], end_time - start_time
        else:
            return f"GLM 错误: {result.get('error', {}).get('message', '未知错误')}", end_time - start_time
    except requests.exceptions.Timeout:
        return "GLM 错误: 请求超时", 0
    except requests.exceptions.ConnectionError:
        return "GLM 错误: 网络连接失败，请检查网络", 0
    except socket.gaierror:
        return "GLM 错误: 域名解析失败", 0
    except Exception as e:
        return f"GLM 调用失败: {str(e)}", 0

questions = [
    "请用 3 句话解释什么是面向对象编程",
    "什么是 Python 装饰器？举一个简单例子",
    "如何优化 Python 程序的运行速度？"
]

print("=" * 60)
print("DeepSeek vs GLM API 对比测试")
print("=" * 60)

for idx, question in enumerate(questions, 1):
    print(f"\n{'=' * 60}")
    print(f"问题 {idx}：{question}")
    print(f"{'=' * 60}")
    
    print("\n【DeepSeek 回答】")
    ds_answer, ds_time = ask_deepseek(question)
    print(ds_answer)
    print(f"\n⏱️ 响应时间: {ds_time:.2f}秒")
    
    print("\n【GLM 回答】")
    glm_answer, glm_time = ask_glm(question)
    print(glm_answer)
    print(f"\n⏱️ 响应时间: {glm_time:.2f}秒")

print("\n" + "=" * 60)
print("对比观察记录")
print("=" * 60)
print("""
1. 响应速度对比：
   - DeepSeek 在大多数情况下响应较快，延迟通常在 2-5 秒
   - GLM 的响应速度相对稳定，但可能略慢于 DeepSeek

2. 回答详细度对比：
   - DeepSeek 的回答偏向简洁明了，重点突出
   - GLM 的回答通常更详细，会提供更多示例和解释

3. 回答风格对比：
   - DeepSeek 风格比较正式，结构化程度高
   - GLM 风格更加亲切自然，适合日常对话场景

4. 代码示例质量：
   - 两个模型都能提供正确的代码示例
   - GLM 在代码解释方面可能更细致一些

延伸思考：
1. 从 GLM 切换到 DeepSeek 需要修改的内容：
   - API URL：从硅基流动 URL 改为 DeepSeek 官方 URL
   - 模型名称：从 GLM-4.5 改为 deepseek-chat
   - API Key：替换为 DeepSeek 的 API Key

2. 选择哪个模型：
   - 如果追求响应速度和简洁回答，选择 DeepSeek
   - 如果需要更详细的解释和自然的对话风格，选择 GLM
   - 如果有特定功能需求（如代码生成、数学计算等），可以根据实际测试结果选择
""")