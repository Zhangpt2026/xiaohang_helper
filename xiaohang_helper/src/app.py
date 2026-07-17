import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import streamlit as st
import requests
import time
from datetime import datetime

API_URL = "https://api.siliconflow.cn/v1/chat/completions"
API_KEY = "sk-eisgfevoxkvnrqgubncjikuobqyohuzafrshvnmamtnobhzh"
FAST_MODEL = "Qwen/Qwen2.5-7B-Instruct"

DATA_DIR = "data"

RECOMMENDED_QUESTIONS = {
    "新生": {
        "新生指南": [
            "报到那天先去哪?",
            "学费什么时候交?",
            "宿舍是几人间?",
            "军训需要准备什么?"
        ],
        "办事流程": [
            "怎么开在读证明?",
            "校园卡丢了怎么补?",
            "转专业怎么转?",
            "图书馆几点关?"
        ],
        "应急防骗": [
            "有人冒充辅导员要钱怎么办?",
            "遇到诈骗怎么报警?",
            "校园安全热线是多少?",
            "心理咨询怎么预约?"
        ]
    },
    "在校生": {
        "新生指南": [
            "新生报到流程是什么?",
            "宿舍分配原则是什么?",
            "学费缴纳方式有哪些?",
            "军训安排是怎样的?"
        ],
        "办事流程": [
            "怎么开在读证明?",
            "校园卡丢了怎么补?",
            "转专业怎么转?",
            "成绩单怎么打印?"
        ],
        "应急防骗": [
            "遇到诈骗怎么报警?",
            "校园安全热线是多少?",
            "心理咨询怎么预约?",
            "宿舍安全注意事项?"
        ]
    },
    "教师": {
        "新生指南": [
            "新生入学教育安排?",
            "迎新工作流程?",
            "新生军训协调?",
            "新生班级管理?"
        ],
        "办事流程": [
            "差旅怎么报销?",
            "调课怎么申请?",
            "教室设备坏了找谁?",
            "科研项目去哪申报?"
        ],
        "应急防骗": [
            "遇到诈骗怎么报警?",
            "校园安全热线是多少?",
            "实验室安全规范?",
            "紧急事件处理流程?"
        ]
    }
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
1. 只能根据【资料】回答，资料里没有的明说暂时没有查询到该业务的相关信息，请咨询对应行政科室，绝不自行编造地点、电话、办理流程
2. 严禁编造电话号码、地址、办公时间、学费金额、人名
3. 涉及金钱/转账，无条件提示先联系辅导员核实，任何要求转账的都是诈骗
4. 涉及心理危机（自杀、不想活、活不下去等），立即给：12320-5 + 学校心理咨询中心 + 告诉辅导员
5. 不接入学校系统（教务/一卡通/财务），被问查我的成绩/课表/卡余额礼貌拒绝
6. 回答末尾禁止标注来源信息
7. 回答禁止出现任何叠字、重复文字、重复数字，语句通顺无冗余
8. 完整输出文档内全部原始信息：地点、房间、联系电话、办理时间、截止月份，绝对不能省略、隐藏、用星号替代
9. 仅回答用户当前单次提问，完全忽略所有历史对话内容，不读取问答历史记录
10. 允许合理扩充语句篇幅、把信息解释得更通俗详细，但不得新增知识库以外的内容，不杜撰办公房间、联系电话、所需材料
11. 输出内容务必核验：无Markdown标记、无关业务内容、重复语句、乱码符号、残缺文字，关键信息完整准确，回答逻辑严谨，不存在信息漏洞
12. 检索只选用和用户问题业务类别一致的资料，跨业务内容（查设备维修混入宿舍、学费相关内容）一律过滤排除
"""

ROLE_PROMPTS = {
    "新生": "你是小航，郑州航院校园助手。用户是大一新生，像热心学长一样详细解答，口语化，多鼓励。",
    "在校生": "你是小航，郑州航院校园助手。用户是老生，简洁回答，重点：地点、电话、材料、时间。",
    "教师": "你是小航，郑州航院校园助手。用户是教师，专业礼貌，重点：政策依据、办事窗口、联系人。"
}

import re

PHONE_PATTERN = r'0\d{2,3}-\d{4,8}'
ROOM_PATTERN = r'[\u4e00-\u9fa5]+楼\d+室'
TIME_PATTERN = r'\d{1,2}:\d{2}'
AMOUNT_PATTERN = r'\d+元'
TEMP_PLACEHOLDER_PREFIX = '___PROTECT_'
TEMP_PLACEHOLDER_SUFFIX = '___'

def fix_date_order(text):
    pattern = r'(\d+)月(\d+)日[—\-–~至](\d+)月(\d+)日'
    def replace_match(match):
        m1, d1, m2, d2 = int(match.group(1)), int(match.group(2)), int(match.group(3)), int(match.group(4))
        if (m1, d1) > (m2, d2):
            return f"{m2}月{d2}日-{m1}月{d1}日"
        return match.group(0)
    text = re.sub(pattern, replace_match, text)
    
    pattern2 = r'(\d+)月(\d+)日到(\d+)月(\d+)日'
    def replace_match2(match):
        m1, d1, m2, d2 = int(match.group(1)), int(match.group(2)), int(match.group(3)), int(match.group(4))
        if (m1, d1) > (m2, d2):
            return f"{m2}月{d2}日到{m1}月{d1}日"
        return match.group(0)
    text = re.sub(pattern2, replace_match2, text)
    
    return text

def protect_key_info(text):
    protected_map = {}
    patterns = [
        ('phone', PHONE_PATTERN),
        ('room', ROOM_PATTERN),
        ('time', TIME_PATTERN),
        ('amount', AMOUNT_PATTERN)
    ]
    
    for pattern_name, pattern in patterns:
        matches = re.findall(pattern, text)
        for i, match in enumerate(matches):
            placeholder = f"{TEMP_PLACEHOLDER_PREFIX}{pattern_name}_{i}{TEMP_PLACEHOLDER_SUFFIX}"
            protected_map[placeholder] = match
            text = text.replace(match, placeholder)
    
    return text, protected_map

def restore_key_info(text, protected_map):
    for placeholder, original in protected_map.items():
        text = text.replace(placeholder, original)
    return text

def validate_and_fix_phones(text):
    def fix_phone(match):
        phone = match.group(0)
        if not phone.startswith('0'):
            phone = '0' + phone
        return phone
    text = re.sub(r'(?<!\d)\d{2,3}-\d{4,8}(?!\d)', fix_phone, text)
    return text

def clean_raw_text(text):
    text, protected_map = protect_key_info(text)
    
    text = re.sub(r'["\'“”‘’]', "", text)
    
    text = fix_date_order(text)
    
    text = re.sub(r'([\u4e00-\u9fa5])\1{1,}', r'\1', text)
    
    text = re.sub(r'(?<![\d:-\u4e00-\u9fa5])(\d)\1{1,}(?![\d:-\u4e00-\u9fa5])', r'\1', text)
    
    text = re.sub(r'-{2,}', "", text)
    
    text = re.sub(r'\*\*', "", text)
    text = re.sub(r'^#{1,3}\s*', "", text, flags=re.MULTILINE)
    
    text = re.sub(r'====[\w_]+\.md====', "", text)
    
    text = re.sub(r'\n\d+\.\s+', '\n', text)
    text = re.sub(r'\n\s*-\s+', '\n', text)
    
    text = re.sub(r'来源:[^\s]+', "", text)
    
    text = re.sub(r'。{2,}', '。', text)
    text = re.sub(r'，{2,}', '，', text)
    text = re.sub(r'、{2,}', '、', text)
    
    text = re.sub(r'\n\s*\n+', '\n', text)
    text = re.sub(r'\t', "", text)
    
    text = restore_key_info(text, protected_map)
    
    text = validate_and_fix_phones(text)
    
    lines = text.split('\n')
    seen_lines = set()
    unique_lines = []
    for line in lines:
        stripped = line.strip()
        if stripped and stripped not in seen_lines:
            seen_lines.add(stripped)
            unique_lines.append(line)
    text = '\n'.join(unique_lines)
    
    return text

DOCUMENT_MAPPING = {
    "01_新生入学.md": ["报到", "新生", "录取", "军训", "宿舍分配", "入学教育", "注册"],
    "02_办事流程.md": ["在读证明", "成绩单", "转专业", "校园卡", "宿舍调整", "差旅报销", "科研", "调课", "报修", "贷款", "学费", "档案", "政审"],
    "03_电话黄页.md": ["电话", "联系", "号码", "黄页"],
    "04_应急防骗.md": ["防骗", "诈骗", "报警", "应急", "心理咨询"],
}

def load_school_data(target_files=None):
    files = target_files or ["01_新生入学.md", "02_办事流程.md", "03_电话黄页.md", "04_应急防骗.md"]
    data_dir = "data"
    content = ""
    missing_files = []

    for fname in files:
        path = f"{data_dir}/{fname}"
        try:
            with open(path, "r", encoding="utf-8") as f:
                raw_text = f.read()
                clean_text_content = clean_raw_text(raw_text)
                content += f"\n===={fname}====\n" + clean_text_content
        except FileNotFoundError:
            missing_files.append(fname)
            print(f"文件不存在: {path}")
        except Exception as e:
            missing_files.append(fname)
            print(f"读取文件失败 {path}: {str(e)}")

    if missing_files:
        print(f"\n 警告: 以下数据文件缺失，部分功能可能受影响：{', '.join(missing_files)}")
    return content, missing_files

def get_relevant_documents(question):
    relevant = []
    for doc, keywords in DOCUMENT_MAPPING.items():
        if any(keyword in question for keyword in keywords):
            relevant.append(doc)
    if not relevant:
        relevant = ["01_新生入学.md", "02_办事流程.md"]
    return relevant

def load_phone_directory():
    path = os.path.join(DATA_DIR, "03_电话黄页.md")
    try:
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
        except UnicodeDecodeError:
            with open(path, "r", encoding="gbk") as f:
                content = f.read()
        return parse_phone_directory(content)
    except Exception as e:
        return f"无法加载电话黄页：{str(e)}"

def parse_phone_directory(content):
    import re
    
    departments = []
    current_dept = None
    current_section = None
    
    lines = content.split('\n')
    for line in lines:
        line = line.strip()
        
        if line.startswith('# '):
            continue
        
        if line.startswith('## '):
            if current_dept:
                departments.append(current_dept)
            dept_name = line[3:].strip()
            current_dept = {'name': dept_name, 'sections': []}
        
        elif line.startswith('### '):
            if current_dept:
                section_name = line[4:].strip()
                current_section = {'name': section_name, 'info': {}}
                current_dept['sections'].append(current_section)
        
        elif line.startswith('- **'):
            if current_section:
                match = re.match(r'- \*\*(.+?)\*\*：(.+)', line)
                if match:
                    key = match.group(1).strip()
                    value = match.group(2).strip()
                    current_section['info'][key] = value
            elif current_dept:
                match = re.match(r'- \*\*(.+?)\*\*：(.+)', line)
                if match:
                    key = match.group(1).strip()
                    value = match.group(2).strip()
                    if not current_dept['sections']:
                        current_dept['sections'].append({'name': dept_name, 'info': {}})
                    current_dept['sections'][0]['info'][key] = value
    
    if current_dept:
        departments.append(current_dept)
    
    return departments

def get_system_prompt(identity, school_data):
    role = ROLE_PROMPTS.get(identity, "你是小航校园助手。")
    return f"{role}\n{HARD_RULES}\n{ALIAS_DICT}\n【资料】\n{school_data}"

def clean_answer(answer):
    if not answer:
        return ""
    
    answer = answer.strip()
    
    answer, protected_map = protect_key_info(answer)
    
    answer = re.sub(r'["\'“”‘’]', "", answer)
    
    answer = fix_date_order(answer)
    
    answer = re.sub(r'([\u4e00-\u9fa5])\1{1,}', r'\1', answer)
    
    answer = re.sub(r'(?<![\d:-\u4e00-\u9fa5])(\d)\1{1,}(?![\d:-\u4e00-\u9fa5])', r'\1', answer)
    
    answer = re.sub(r'-{2,}', "", answer)
    
    answer = re.sub(r'\*\*', "", answer)
    answer = re.sub(r'^#{1,3}\s*', "", answer, flags=re.MULTILINE)
    
    answer = re.sub(r'====[\w_]+\.md====', "", answer)
    
    answer = re.sub(r'来源:[^\s]+', "", answer)
    
    answer = re.sub(r'\n\s*-\s+', '\n', answer)
    
    answer = re.sub(r'。{2,}', '。', answer)
    answer = re.sub(r'，{2,}', '，', answer)
    answer = re.sub(r'、{2,}', '、', answer)
    
    answer = restore_key_info(answer, protected_map)
    
    answer = validate_and_fix_phones(answer)
    
    answer = re.sub(r'\s+', ' ', answer)
    
    return answer.strip()

def check_hard_rules(question):
    if any(keyword in question for keyword in ["查我的成绩", "查成绩", "我的课表", "课表", "卡余额", "余额"]):
        return "抱歉，我无法帮你查询个人成绩、课表或校园卡余额等个人信息。这些信息需要你登录学校系统自行查询，或者联系相关部门咨询。"
    if any(keyword in question for keyword in ["不想活了", "活不下去", "自杀", "死"]):
        return "同学，别自己扛。现在就打 12320-5（全国心理援助，24小时），或马上联系学校心理咨询中心 0371-61911203（学生活动中心301室），然后立刻找你的辅导员。你不是一个人。[来源:04_应急防骗.md]"
    return None

def ask_xiaohang(identity, question, school_data, history_messages=None):
    if not question or not question.strip():
        return "请输入你的问题，我才能帮你解答哦！", 0
    
    if len(question.strip()) > 500:
        return "你的问题太长了，请精简到 500 字以内，我才能更好地帮你解答！", 0
    
    rule_response = check_hard_rules(question)
    if rule_response:
        return rule_response, 0
    
    relevant_docs = get_relevant_documents(question)
    relevant_data, _ = load_school_data(relevant_docs)
    
    system_prompt = get_system_prompt(identity, relevant_data)
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    messages = [{"role": "system", "content": system_prompt}]
    messages.append({"role": "user", "content": question.strip()})
    
    data = {
        "model": FAST_MODEL,
        "messages": messages,
        "temperature": 0.3,
        "max_tokens": 3000,
        "top_p": 0.9,
        "frequency_penalty": 0.1,
        "presence_penalty": 0.1
    }
    
    start_time = time.time()
    
    try:
        response = requests.post(API_URL, headers=headers, json=data, timeout=60)
        
        elapsed_time = time.time() - start_time
        
        if response.status_code == 200:
            result = response.json()
            if "choices" in result:
                answer = result["choices"][0]["message"]["content"]
                return clean_answer(answer), elapsed_time
            else:
                return "API 返回格式错误", elapsed_time
        elif response.status_code == 401:
            return "API Key 失效或未配置", elapsed_time
        elif response.status_code == 403:
            return "API 权限不足", elapsed_time
        elif response.status_code == 429:
            return "请求过于频繁，请稍后再试", elapsed_time
        else:
            return f"请求失败，状态码: {response.status_code}", elapsed_time
    
    except requests.exceptions.Timeout:
        return "请求超时，请检查网络连接或稍后重试", time.time() - start_time
    except requests.exceptions.ConnectionError:
        return "网络连接失败，请检查网络设置或稍后重试", time.time() - start_time
    except Exception as e:
        return f"调用失败: {str(e)}", time.time() - start_time

def switch_identity(new_identity):
    if st.session_state.get("identity") != new_identity:
        st.session_state.identity = new_identity
        st.session_state.messages = []

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
    
    dark = st.toggle("🌙 深色模式", value=False)
    
    if dark:
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
            
            [data-testid="stAppViewContainer"] {background-color: #1a1a2e !important;}
            [data-testid="stHeader"] {background-color: #16213e !important;}
            .st-emotion-cache-183lzff {background-color: #1a1a2e !important;}
            .st-emotion-cache-901oao {background-color: #1a1a2e !important; color: #e0e0e0 !important;}
            
            .title-gradient {
                background: linear-gradient(135deg, #a78bfa 0%, #c4b5fd 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
                font-weight: bold;
            }
            
            .chat-user {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border-radius: 12px 12px 0 12px;
                padding: 12px 16px;
                margin-bottom: 10px;
                max-width: 80%;
                align-self: flex-end;
            }
            
            .chat-assistant {
                background: #2d2d44;
                color: #e0e0e0;
                border-radius: 12px 12px 12px 0;
                padding: 12px 16px;
                margin-bottom: 10px;
                max-width: 80%;
                align-self: flex-start;
            }
            
            .st-emotion-cache-1cpxqw2 {background-color: #252540 !important;}
            .st-emotion-cache-1d391kg {border-color: #4a4a6a !important;}
            .st-emotion-cache-7ym5gk {background-color: #252540 !important; color: #e0e0e0 !important;}
            
            .loading-dots:after {
                content: '.';
                animation: dots 1.5s steps(5, end) infinite;
            }
            
            @keyframes dots {
                0%, 20% { color: rgba(255,255,255,0); text-shadow: .25em 0 0 rgba(255,255,255,0), .5em 0 0 rgba(255,255,255,0);}
                40% { color: #a78bfa; text-shadow: .25em 0 0 rgba(255,255,255,0), .5em 0 0 rgba(255,255,255,0);}
                60% { text-shadow: .25em 0 0 #a78bfa, .5em 0 0 rgba(255,255,255,0);}
                80%, 100% { text-shadow: .25em 0 0 #a78bfa, .5em 0 0 #a78bfa;}
            }
            </style>
        """, unsafe_allow_html=True)
    else:
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
            
            .chat-user {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border-radius: 12px 12px 0 12px;
                padding: 12px 16px;
                margin-bottom: 10px;
                max-width: 80%;
                align-self: flex-end;
            }
            
            .chat-assistant {
                background: #f0f2f6;
                color: #333;
                border-radius: 12px 12px 12px 0;
                padding: 12px 16px;
                margin-bottom: 10px;
                max-width: 80%;
                align-self: flex-start;
            }
            
            .loading-dots:after {
                content: '.';
                animation: dots 1.5s steps(5, end) infinite;
            }
            
            @keyframes dots {
                0%, 20% { color: rgba(0,0,0,0); text-shadow: .25em 0 0 rgba(0,0,0,0), .5em 0 0 rgba(0,0,0,0);}
                40% { color: #667eea; text-shadow: .25em 0 0 rgba(0,0,0,0), .5em 0 0 rgba(0,0,0,0);}
                60% { text-shadow: .25em 0 0 #667eea, .5em 0 0 rgba(0,0,0,0);}
                80%, 100% { text-shadow: .25em 0 0 #667eea, .5em 0 0 #667eea;}
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
        
        identity_colors = {
            "新生": "#667eea",
            "在校生": "#10b981",
            "教师": "#f59e0b"
        }
        
        with col1:
            if st.button("🎒 新生", key="btn_new", use_container_width=True, 
                       type="primary" if st.session_state.get("identity") == "新生" else "secondary"):
                switch_identity("新生")
                st.rerun()
        
        with col2:
            if st.button("📚 在校生", key="btn_student", use_container_width=True,
                       type="primary" if st.session_state.get("identity") == "在校生" else "secondary"):
                switch_identity("在校生")
                st.rerun()
        
        with col3:
            if st.button("👨‍🏫 教师", key="btn_teacher", use_container_width=True,
                       type="primary" if st.session_state.get("identity") == "教师" else "secondary"):
                switch_identity("教师")
                st.rerun()
        
        if "identity" not in st.session_state:
            st.session_state.identity = "新生"
        
        identity = st.session_state.identity
        
        color = identity_colors.get(identity, "#667eea")
        st.markdown(f"ℹ️ 当前身份：<span style='color:{color};font-weight:bold;'>{identity}</span>", unsafe_allow_html=True)
        
        if "messages" not in st.session_state:
            st.session_state.messages = []
        
        col_new_chat, col_export = st.columns([1, 1])
        with col_new_chat:
            if st.button("🔄 新对话", use_container_width=True):
                st.session_state.messages = []
                st.session_state.history = []
                st.rerun()
        
        with col_export:
            if "history" in st.session_state and st.session_state.history:
                export_text = ""
                for record in reversed(st.session_state.history):
                    export_text += f"[{record['time']}] {record['identity']}\n"
                    export_text += f"提问：{record['question']}\n"
                    export_text += f"回答：{record['answer']}\n"
                    export_text += "=" * 50 + "\n"
                
                filename = f"小航对话记录_{datetime.now().strftime('%Y%m%d')}.txt"
                st.download_button(
                    label="📥 导出对话",
                    data=export_text,
                    file_name=filename,
                    mime="text/plain",
                    use_container_width=True
                )
        
        st.write("**✨ 推荐问题：**")
        
        questions_by_category = RECOMMENDED_QUESTIONS.get(identity, {})
        
        tab_new, tab_process, tab_security = st.tabs(["新生指南", "办事流程", "应急防骗"])
        
        with tab_new:
            cols = st.columns(2)
            for i, q in enumerate(questions_by_category.get("新生指南", [])):
                with cols[i % 2]:
                    if st.button(q, key=f"btn_new_{i}", use_container_width=True):
                        st.session_state.messages = []
                        st.session_state.messages.append({"role": "user", "content": q})
                        with st.spinner("小航正在思考中..."):
                            answer, elapsed_time = ask_xiaohang(identity, q, school_data, None)
                        st.session_state.messages.append({"role": "assistant", "content": answer})
                        if "history" not in st.session_state:
                            st.session_state.history = []
                        st.session_state.history.insert(0, {
                            "time": datetime.now().strftime("%H:%M:%S"),
                            "identity": identity,
                            "question": q,
                            "answer": answer,
                            "time_cost": elapsed_time,
                            "word_count": len(answer)
                        })
                        st.rerun()
        
        with tab_process:
            cols = st.columns(2)
            for i, q in enumerate(questions_by_category.get("办事流程", [])):
                with cols[i % 2]:
                    if st.button(q, key=f"btn_process_{i}", use_container_width=True):
                        st.session_state.messages = []
                        st.session_state.messages.append({"role": "user", "content": q})
                        with st.spinner("小航正在思考中..."):
                            answer, elapsed_time = ask_xiaohang(identity, q, school_data, None)
                        st.session_state.messages.append({"role": "assistant", "content": answer})
                        if "history" not in st.session_state:
                            st.session_state.history = []
                        st.session_state.history.insert(0, {
                            "time": datetime.now().strftime("%H:%M:%S"),
                            "identity": identity,
                            "question": q,
                            "answer": answer,
                            "time_cost": elapsed_time,
                            "word_count": len(answer)
                        })
                        st.rerun()
        
        with tab_security:
            cols = st.columns(2)
            for i, q in enumerate(questions_by_category.get("应急防骗", [])):
                with cols[i % 2]:
                    if st.button(q, key=f"btn_security_{i}", use_container_width=True):
                        st.session_state.messages = []
                        st.session_state.messages.append({"role": "user", "content": q})
                        with st.spinner("小航正在思考中..."):
                            answer, elapsed_time = ask_xiaohang(identity, q, school_data, None)
                        st.session_state.messages.append({"role": "assistant", "content": answer})
                        if "history" not in st.session_state:
                            st.session_state.history = []
                        st.session_state.history.insert(0, {
                            "time": datetime.now().strftime("%H:%M:%S"),
                            "identity": identity,
                            "question": q,
                            "answer": answer,
                            "time_cost": elapsed_time,
                            "word_count": len(answer)
                        })
                        st.rerun()
        
        chat_container = st.container()
        with chat_container:
            for idx, message in enumerate(st.session_state.messages):
                if message["role"] == "user":
                    st.markdown(f'<div class="chat-user">你：{message["content"]}</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="chat-assistant">小航：{message["content"]}</div>', unsafe_allow_html=True)
                    if idx == len(st.session_state.messages) - 1:
                        last_record = st.session_state.get("history", [])[0] if st.session_state.get("history") else None
                        if last_record and last_record.get("question") == st.session_state.messages[-2]["content"]:
                            st.caption(f"回答字数：{last_record.get('word_count', 0)} 字 · 耗时：{last_record.get('time_cost', 0):.1f} 秒")
        
        if prompt := st.chat_input("💬 请问有什么可以帮你的？"):
            st.session_state.messages = []
            
            st.session_state.messages.append({"role": "user", "content": prompt})
            
            with chat_container:
                st.markdown(f'<div class="chat-user">你：{prompt}</div>', unsafe_allow_html=True)
            
            with st.spinner("小航正在思考中..."):
                answer, elapsed_time = ask_xiaohang(identity, prompt, school_data, None)
            
            st.session_state.messages.append({"role": "assistant", "content": answer})
            
            if "history" not in st.session_state:
                st.session_state.history = []
            st.session_state.history.insert(0, {
                "time": datetime.now().strftime("%H:%M:%S"),
                "identity": identity,
                "question": prompt,
                "answer": answer,
                "time_cost": elapsed_time,
                "word_count": len(answer)
            })
            
            st.rerun()
        
        st.divider()
        st.markdown('<h3 style="color: #667eea;">📜 问答历史</h3>', unsafe_allow_html=True)
        
        col_clear, col_count = st.columns([1, 3])
        with col_clear:
            if st.button("🗑️ 清空历史", use_container_width=True):
                if "history" in st.session_state:
                    st.session_state.history = []
                st.rerun()
        
        with col_count:
            history_count = len(st.session_state.get("history", []))
            st.write(f"共 {history_count} 条记录")
        
        if "history" in st.session_state and st.session_state.history:
            for idx, record in enumerate(st.session_state.history):
                st.markdown(f"""
                    <div style="background: #f8f9fa; border-radius: 8px; padding: 12px; margin-bottom: 8px; border-left: 4px solid #667eea;">
                        <div style="font-size: 14px; color: #666; margin-bottom: 4px;">
                            [{record['time']}] <span style="font-weight:bold; color:#667eea;">{record['identity']}</span>
                        </div>
                        <div style="font-size: 15px; color: #333; margin-bottom: 4px;">
                            <strong>提问：</strong>{record['question']}
                        </div>
                        <div style="font-size: 14px; color: #555;">
                            <strong>回答：</strong>{record['answer']}
                        </div>
                    </div>
                """, unsafe_allow_html=True)
        else:
            st.info("暂无历史记录")
    
    with tab2:
        st.markdown('<h2 style="color: #667eea;">📞 校园电话黄页</h2>', unsafe_allow_html=True)
        phone_data = load_phone_directory()
        
        if isinstance(phone_data, str):
            st.markdown(phone_data)
        else:
            for dept in phone_data:
                with st.expander(f"🏢 {dept['name']}", expanded=True):
                    for section in dept['sections']:
                        st.markdown(f"""
                            <div style="background: #f8f9fa; border-radius: 8px; padding: 12px; margin-bottom: 8px; border-left: 4px solid #667eea;">
                                <div style="font-size: 16px; font-weight: bold; color: #667eea; margin-bottom: 8px;">
                                    {section['name']}
                                </div>
                                {''.join([f'<div style="font-size: 14px; margin-bottom: 4px;"><strong style="color: #666;">{k}：</strong><span style="color: #333;">{v}</span></div>' for k, v in section['info'].items()])}
                            </div>
                        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
