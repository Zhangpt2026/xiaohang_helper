import requests
import time
from .config import API_URL, API_KEY, FAST_MODEL, MAX_TOKENS, TIMEOUT, TEMPERATURE

def ask_ai(messages):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }
    
    data = {
        "model": FAST_MODEL,
        "messages": messages,
        "temperature": TEMPERATURE,
        "max_tokens": MAX_TOKENS,
        "top_p": 0.9,
        "frequency_penalty": 0.1,
        "presence_penalty": 0.1
    }
    
    try:
        start_time = time.time()
        response = requests.post(API_URL, headers=headers, json=data, timeout=TIMEOUT)
        response.raise_for_status()
        
        result = response.json()
        answer = result["choices"][0]["message"]["content"]
        elapsed_time = round(time.time() - start_time, 2)
        
        return answer, elapsed_time, None
        
    except requests.exceptions.Timeout:
        return "", 0, "请求超时，请稍后重试"
    except requests.exceptions.ConnectionError:
        return "", 0, "网络连接失败，请检查网络"
    except requests.exceptions.HTTPError as e:
        if response.status_code == 401:
            return "", 0, "API Key 无效，请检查配置"
        return "", 0, f"请求失败: {str(e)}"
    except Exception as e:
        return "", 0, f"发生错误: {str(e)}"