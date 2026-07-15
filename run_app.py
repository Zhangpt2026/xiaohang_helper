import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import streamlit as st
import requests

API_URL = "https://api.siliconflow.cn/v1/chat/completions"
API_KEY = "sk-eisgfevoxkvnrqgubncjikuobqyohuzafrshvnmamtnobhzh"
FAST_MODEL = "moonshotai/Kimi-K2.7-Code"

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
【规则】
1. 只能根据【资料】回答，资料里没有的明说"这个我没收录，建议拨打 0371-61911000"
2. 严禁编造电话号码、地址、办公时间、学费金额、人名
3. 涉及金钱/转账，无条件提示"先联系辅导员核实，任何要求转账的都是诈骗"
4. 涉及心理危机（自杀、不想活、活不下去等），立即给：12320-5 + 学校心理咨询中心 + 告诉辅导员
5. 不接入学校系统（教务/一卡通/财务），被问"查我的成绩/课表/卡余额"礼貌拒绝
6. 回答末尾标注 [来源:文件名]
"""

ROLE_PROMPTS = {
    "新生": "你是小航，郑州航院校园助手。用户是大一新生，像热心学长一样详细解答，口语化，多鼓励。",
    "在校生": "你是小航，郑州航院校园助手。用户是老生，简洁回答，重点：地点、电话、材料、时间。",
    "教师": "你是小航，郑州航院校园助手。用户是教师，专业礼貌，重点：政策依据、办事窗口、联系人。"
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
    return f"{role}\n{HARD_RULES}\n{ALIAS_DICT}\n【资料】\n{school_data}"

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
        "model": FAST_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": question.strip()}
        ],
        "temperature": 0.3,
        "max_tokens": 500
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
            return "API Key 失效或未配置"
        elif response.status_code == 403:
            return "API 权限不足"
        elif response.status_code == 429:
            return "请求过于频繁，请稍后再试"
        else:
            return f"请求失败，状态码: {response.status_code}"
    
    except requests.exceptions.Timeout:
        return "请求超时，请稍后重试"
    except requests.exceptions.ConnectionError:
        return "网络连接失败"
    except Exception as e:
        return f"调用失败: {str(e)}"

def main():
    st.set_page_config(
        page_title="小航 · 校园信息查询 AI 助手", 
        page_icon="📚",
        menu_items={
            'Get Help': None,
            'Report a bug': None,
            'About': None
        }
    )
    
    st.markdown("""
        <style>
        .stDeployButton {display: none !important;}
        .css-16huue1 {display: none !important;}
        .css-1y4p8pa {padding-top: 0rem; padding-bottom: 0rem;}
        .st-emotion-cache-1xarl3l {padding-top: 1rem;}
        [data-testid="stToolbar"] {display: none !important;}
        [data-testid="stDecoration"] {display: none !important;}
        .st-emotion-cache-1pbsqtx {display: none !important;}
        .st-emotion-cache-17eq0hr {display: none !important;}
        .st-emotion-cache-1q35k3a {display: none !important;}
        
        .title-gradient {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            font-weight: bold;
        }
        
        .stButton>button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 8px;
            padding: 8px 16px;
            font-weight: 500;
            transition: all 0.3s ease;
        }
        
        .stButton>button:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
        }
        
        .chat-user {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 12px 12px 0 12px;
            padding: 12px;
            margin-bottom: 8px;
        }
        
        .chat-assistant {
            background: #f0f2f6;
            color: #333;
            border-radius: 12px 12px 12px 0;
            padding: 12px;
            margin-bottom: 8px;
        }
        </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<h1 class="title-gradient">🎓 小航 · 校园信息查询 AI 助手</h1>', unsafe_allow_html=True)
    st.subheader("郑州航空工业管理学院专属服务")
    
    school_data, missing_files = load_school_data()
    
    if missing_files:
        st.warning(f"⚠ 以下数据文件缺失：{', '.join(missing_files)}")
    
    tab1, tab2 = st.tabs(["💬 智能问答", "📞 电话黄页"])
    
    with tab1:
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("🎒 新生", key="btn_new"):
                st.session_state.identity = "新生"
        with col2:
            if st.button("📚 在校生", key="btn_student"):
                st.session_state.identity = "在校生"
        with col3:
            if st.button("👨‍🏫 教师", key="btn_teacher"):
                st.session_state.identity = "教师"
        
        if "identity" not in st.session_state:
            st.session_state.identity = "新生"
        
        identity = st.session_state.identity
        st.info(f"当前身份：{identity}")
        
        if "messages" not in st.session_state:
            st.session_state.messages = []
        
        st.write("**✨ 推荐问题：**")
        cols = st.columns(2)
        for i, q in enumerate(RECOMMENDED_QUESTIONS.get(identity, [])):
            with cols[i % 2]:
                if st.button(q, key=f"btn_{q}", use_container_width=True):
                    st.session_state.messages.append({"role": "user", "content": q})
                    answer = ask_xiaohang(identity, q, school_data)
                    st.session_state.messages.append({"role": "assistant", "content": answer})
        
        for message in st.session_state.messages:
            if message["role"] == "user":
                st.markdown(f'<div class="chat-user">你：{message["content"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="chat-assistant">小航：{message["content"]}</div>', unsafe_allow_html=True)
        
        if prompt := st.chat_input("💬 请问有什么可以帮你的？"):
            st.session_state.messages.append({"role": "user", "content": prompt})
            st.markdown(f'<div class="chat-user">你：{prompt}</div>', unsafe_allow_html=True)
            
            answer = ask_xiaohang(identity, prompt, school_data)
            st.markdown(f'<div class="chat-assistant">小航：{answer}</div>', unsafe_allow_html=True)
            st.session_state.messages.append({"role": "assistant", "content": answer})
    
    with tab2:
        st.markdown('<h2 style="color: #667eea;">📞 校园电话黄页</h2>', unsafe_allow_html=True)
        phone_content = load_phone_directory()
        st.markdown(phone_content)

if __name__ == "__main__":
    main()