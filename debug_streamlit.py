import streamlit as st
import requests

API_URL = "https://api.siliconflow.cn/v1/chat/completions"
API_KEY = "sk-eisgfevoxkvnrqgubncjikuobqyohuzafrshvnmamtnobhzh"

st.title("API 调试工具")

test_input = st.text_input("测试问题:", "你好")

if st.button("测试 API 调用"):
    st.write("开始调用 API...")
    
    try:
        data = {
            "model": "deepseek-ai/DeepSeek-V4-Flash",
            "messages": [
                {"role": "user", "content": test_input}
            ]
        }
        
        with st.spinner("正在请求..."):
            response = requests.post(
                API_URL, 
                headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}, 
                json=data, 
                timeout=60
            )
        
        st.write(f"状态码: {response.status_code}")
        st.write(f"响应时间: {response.elapsed.total_seconds():.2f} 秒")
        
        if response.status_code == 200:
            result = response.json()
            if "choices" in result:
                st.success("API 调用成功！")
                st.write("回答:", result["choices"][0]["message"]["content"])
            else:
                st.error("返回格式错误")
                st.write(result)
        else:
            st.error(f"请求失败: {response.status_code}")
            st.write(response.text[:500])
            
    except requests.exceptions.Timeout:
        st.error("请求超时！")
    except requests.exceptions.ConnectionError:
        st.error("网络连接失败！")
    except Exception as e:
        st.error(f"异常: {str(e)}")

st.divider()
st.write("系统信息:")
st.write(f"requests 版本: {requests.__version__}")
st.write(f"Streamlit 版本: {st.__version__}")