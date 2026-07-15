import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import streamlit as st
import requests
API_URL = "https://api.siliconflow.cn/v1/chat/completions"
API_KEY = "sk-eisgfevoxkvnrqgubncjikuobqyohuzafrshvnmamtnobhzh"

DATA_DIR = "data"
DATA_FILES = ["01_新生入学.md", "02_办事流程.md", "03_电话黄页.md", "04_应急防骗.md"]

RECOMMENDED_QUESTIONS = {
    "新生": [
        "新生入学报到流程和需要准备的材料有哪些？",
        "宿舍入住规则、设施维修和熄灯时间是怎样的？",
        "校园卡充值、挂失和食堂/超市使用的相关问题？",
        "一年学费多少，餐厅在哪？"
    ],
    "在校生": [
        "课程退改选、成绩查询和绩点计算的相关规则？",
        "校园网连接、带宽升级和故障报修的方式？",
        "图书馆借阅、续借、馆藏查询和自习室预约？",
        "校园内各类证明（在读、成绩）的办理流程？"
    ],
    "教师": [
        "教室预约、多媒体设备使用和故障报修的流程？",
        "学生成绩录入、教学任务安排和课表查询？",
        "校园办公系统登录、公文流转和行政事务办理？",
        "科研项目申报、经费报销和学术资源获取？"
    ]
}

ALIAS_DICT = """
【别名词典】
- "学校""航院""ZUA""郑航" = 郑州航空工业管理学院
- "新校区""龙湖""新校" = 龙子湖校区
- "卡""饭卡""校卡" = 校园一卡通
- "保安""门卫""校警" = 保卫处
- "迁户口""落户" = 户籍迁入/迁出
- "调宿舍""换宿舍" = 宿舍调整申请
- "证明""在读证明" = 在校学籍证明
"""

HARD_RULES = """
【防幻觉硬规则】
1. 只能根据【学校资料】回答，资料里没有的明说"这个我没收录，建议拨打 0371-61911000 总值班室问一下"
2. 严禁编造电话号码、地址、办公时间、学费金额、人名
3. 涉及金钱/转账，无条件提示"先联系辅导员核实，任何要求转账的都是诈骗"
4. 涉及心理危机（自杀、不想活、活不下去等），立即给：12320-5 心理援助 + 学校心理咨询中心 + 告诉辅导员
5. 不接入学校系统（教务/一卡通/财务），被问"查我的成绩/课表/卡余额"礼貌拒绝
6. 回答末尾标注 [来源:文件名]
"""

ROLE_PROMPTS = {
    "新生": """你是"小航"，郑州航空工业管理学院的校园信息查询 AI 助手。
当前用户身份：大一新生。
你像一位热心的大二学长，语气详细、口语化、多给鼓励。
回答重点：把流程拆成具体步骤，涉及金钱/转账无条件提示防骗。""",

    "在校生": """你是"小航"，郑州航空工业管理学院的校园信息查询 AI 助手。
当前用户身份：在校老生。
你像一位办事老司机学长，语气简洁。
回答重点：① 地点 ② 电话 ③ 所需材料 ④ 办结时间。""",

    "教师": """你是"小航"，郑州航空工业管理学院的校园信息查询 AI 助手。
当前用户身份：教师。
语气专业礼貌。
回答重点：① 政策依据 ② 办事窗口 ③ 联系人。"""
}


def load_school_data():
    content = ""
    missing_files = []
    for fname in DATA_FILES:
        path = os.path.join(DATA_DIR, fname)
        try:
            with open(path, "r", encoding="utf-8") as f:
                content += f"\n\n=== {fname} ===\n" + f.read()
        except FileNotFoundError:
            missing_files.append(fname)
    return content, missing_files


def load_phone_directory():
    path = os.path.join(DATA_DIR, "03_电话黄页.md")
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"无法加载电话黄页：{str(e)}"


def get_system_prompt(identity, school_data):
    role = ROLE_PROMPTS.get(identity, "你是小航校园助手。")
    return f"{role}\n{HARD_RULES}\n{ALIAS_DICT}\n【学校资料】\n{school_data}"


def check_hard_rules(question):
    if any(keyword in question for keyword in ["查我的成绩", "查成绩", "我的课表", "课表", "卡余额", "余额"]):
        return "抱歉，我无法帮你查询个人成绩、课表或校园卡余额等个人信息。这些信息需要你登录学校系统自行查询，或者联系相关部门咨询。"
    if any(keyword in question for keyword in ["不想活了", "活不下去", "自杀", "死"]):
        return "同学，别自己扛。现在就打 12320-5（全国心理援助，24小时），或马上联系学校心理咨询中心 0371-61911203（学生活动中心301室），然后立刻找你的辅导员。你不是一个人。[来源:04_应急防骗.md]"
    return None


def ask_xiaohang(identity, question, school_data):
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
                return result["choices"][0]["message"]["content"]
            else:
                return "API 返回格式错误"
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
    except Exception as e:
        return f"调用失败: {str(e)}"


def main():
    st.set_page_config(page_title="小航 · 校园信息查询 AI 助手", page_icon="📚")

    st.title("小航 · 校园信息查询 AI 助手")
    st.subheader("郑州航空工业管理学院专属")

    school_data, missing_files = load_school_data()

    if missing_files:
        st.warning(f"以下数据文件缺失：{', '.join(missing_files)}")

    tab1, tab2 = st.tabs(["智能问答", "电话黄页"])

    with tab1:
        identity = st.selectbox("请选择你的身份：", ["新生", "在校生", "教师"])

        if "messages" not in st.session_state:
            st.session_state.messages = []

        st.write("**推荐问题：**")
        for q in RECOMMENDED_QUESTIONS.get(identity, []):
            if st.button(q, key=f"btn_{q}"):
                st.session_state.messages.append({"role": "user", "content": q})

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

    with tab2:
        st.header("📞 校园电话黄页")
        phone_content = load_phone_directory()
        st.markdown(phone_content)


if __name__ == "__main__":
    main()