import streamlit as st
import requests

API_URL = "https://api.siliconflow.cn/v1/chat/completions"
API_KEY = "sk-eisgfevoxkvnrqgubncjikuobqyohuzafrshvnmamtnobhzh"

def load_school_data():
    files = ["01_新生入学.md", "02_办事流程.md", "03_电话黄页.md", "04_应急防骗.md"]
    data_dir = "data"
    content = ""
    for fname in files:
        path = f"{data_dir}/{fname}"
        try:
            with open(path, "r", encoding="utf-8") as f:
                content += f"\n\n=== {fname} ===\n" + f.read()
        except FileNotFoundError:
            st.warning(f"文件不存在：{path}")
    return content

def get_system_prompt(identity, school_data):
    alias_dict = """
【别名词典】
- "学校""航院""ZUA""郑航" = 郑州航空工业管理学院
- "新校区""龙湖""新校" = 龙子湖校区
- "卡""饭卡""校卡" = 校园一卡通
- "保安""门卫""校警" = 保卫处
- "迁户口""落户" = 户籍迁入/迁出
- "调宿舍""换宿舍" = 宿舍调整申请
- "证明""在读证明" = 在校学籍证明
"""

    hard_rules = """
【防幻觉硬规则】
1. 只能根据【学校资料】回答，资料里没有的明说"这个我没收录，建议拨打 0371-61911000 总值班室问一下"
2. 严禁编造电话号码、地址、办公时间、学费金额、人名
3. 涉及金钱/转账，无条件提示"先联系辅导员核实，任何要求转账的都是诈骗"
4. 涉及心理危机（自杀、不想活、活不下去等），立即给：12320-5 心理援助 + 学校心理咨询中心 + 告诉辅导员
5. 不接入学校系统（教务/一卡通/财务），被问"查我的成绩/课表/卡余额"礼貌拒绝
6. 回答末尾标注 [来源:文件名]
"""

    if identity == "新生":
        role = """你是"小航"，郑州航空工业管理学院的校园信息查询 AI 助手。
当前用户身份：大一新生。
你像一位热心的大二学长，语气详细、口语化、多给鼓励。
回答重点：把流程拆成具体步骤，涉及金钱/转账无条件提示防骗。"""
    elif identity == "在校生":
        role = """你是"小航"，郑州航空工业管理学院的校园信息查询 AI 助手。
当前用户身份：在校老生。
你像一位办事老司机学长，语气简洁。
回答重点：① 地点 ② 电话 ③ 所需材料 ④ 办结时间。"""
    elif identity == "教师":
        role = """你是"小航"，郑州航空工业管理学院的校园信息查询 AI 助手。
当前用户身份：教师。
语气专业礼貌。
回答重点：① 政策依据 ② 办事窗口 ③ 联系人。"""
    else:
        role = "你是小航校园助手。"

    return f"{role}\n{hard_rules}\n{alias_dict}\n【学校资料】\n{school_data}"

def check_hard_rules(question):
    if any(keyword in question for keyword in ["查我的成绩", "查成绩", "我的课表", "课表", "卡余额", "余额"]):
        return "抱歉，我无法帮你查询个人成绩、课表或校园卡余额等个人信息。这些信息需要你登录学校系统自行查询，或者联系相关部门咨询。"
    if any(keyword in question for keyword in ["不想活了", "活不下去", "自杀", "死"]):
        return "同学，别自己扛。现在就打 12320-5（全国心理援助，24小时），或马上联系学校心理咨询中心 0371-61911203（学生活动中心301室），然后立刻找你的辅导员。你不是一个人。[来源:04_应急防骗.md]"
    return None

def ask_xiaohang(identity, question, school_data):
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
            {"role": "user", "content": question}
        ]
    }
    try:
        response = requests.post(API_URL, headers=headers, json=data, timeout=60)
        if response.status_code == 200:
            result = response.json()
            if "choices" in result:
                answer = result["choices"][0]["message"]["content"]
                return answer
            else:
                return f"API 返回格式错误"
        else:
            return f"请求失败，状态码: {response.status_code}"
    except Exception as e:
        return f"调用失败: {str(e)}"

def main():
    st.set_page_config(page_title="小航 · 校园信息查询 AI 助手", page_icon="📚")
    
    st.title("小航 · 校园信息查询 AI 助手")
    st.subheader("郑州航空工业管理学院专属")
    
    school_data = load_school_data()
    
    identity = st.selectbox("请选择你的身份：", ["新生", "在校生", "教师"])
    
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    if prompt := st.chat_input("请问有什么可以帮你的？"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        with st.chat_message("assistant"):
            with st.spinner("小航正在思考..."):
                answer = ask_xiaohang(identity, prompt, school_data)
                st.markdown(answer)
        
        st.session_state.messages.append({"role": "assistant", "content": answer})

if __name__ == "__main__":
    main()