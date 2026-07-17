mport sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import streamlit as st
import time
import re
from datetime import datetime
from .config import DATA_DIR, API_KEY
from .prompts import get_system_prompt, RECOMMENDED_QUESTIONS, ROLE_PROMPTS, ALIAS_DICT, HARD_RULES
from .api import ask_ai

def clean_markdown_text(text):
    if not text:
        return ""
    
    text = text.strip()
    
    left_quotes = ['"', "'", '“', '‘']
    right_quotes = ['"', "'", '”', '’']
    
    while text:
        modified = False
        for lq, rq in zip(left_quotes, right_quotes):
            if text.startswith(lq) and text.endswith(rq):
                text = text[1:-1].strip()
                modified = True
                break
        if not modified:
            break
    
    text = re.sub(r'"{2,}', '"', text)
    text = re.sub(r"'{2,}", "'", text)
    text = re.sub(r'“{2,}', '“', text)
    text = re.sub(r'”{2,}', '”', text)
    text = re.sub(r'‘{2,}', '‘', text)
    text = re.sub(r'’{2,}', '’', text)
    
    text = text.replace('""""', '')
    text = text.replace('“”“”', '')
    text = text.replace('‘’‘’', '')
    
    text = text.replace('  ', ' ')
    
    return text.strip()

def load_school_data():
    content = ""
    missing_files = []
    import glob
    md_files = sorted(glob.glob(os.path.join(DATA_DIR, "*.md")))
    if not md_files:
        return content, ["data/*.md (空目录)"]
    for filepath in md_files:
        fname = os.path.basename(filepath)
        try:
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    file_content = f.read()
            except UnicodeDecodeError:
                with open(filepath, "r", encoding="gbk") as f:
                    file_content = f.read()
            cleaned_content = clean_markdown_text(file_content)
            content += f"\n\n=== {fname} ===\n" + cleaned_content
        except FileNotFoundError:
            missing_files.append(fname)
        except Exception as e:
            missing_files.append(f"{fname}: {str(e)}")
    return content, missing_files

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
            match = re.match(r'- \*\*(.+?)\*\*：(.+)', line)
            if match:
                key = match.group(1).strip()
                value = match.group(2).strip()
                if current_section:
                    current_section['info'][key] = value
                elif current_dept:
                    if not current_dept['sections']:
                        current_dept['sections'].append({'name': current_dept['name'], 'info': {}})
                    current_dept['sections'][0]['info'][key] = value
    
    if current_dept:
        departments.append(current_dept)
    
    return departments

def clean_answer(answer):
    if not answer:
        return ""
    
    answer = answer.strip()
    
    left_quotes = ['"', "'", '“', '‘', '《', '【', '[', '(', '{']
    right_quotes = ['"', "'", '”', '’', '》', '】', ']', ')', '}']
    
    while answer:
        modified = False
        for lq, rq in zip(left_quotes, right_quotes):
            if answer.startswith(lq) and answer.endswith(rq):
                answer = answer[1:-1].strip()
                modified = True
                break
        if not modified:
            break
    
    for rq in right_quotes:
        while answer.endswith(rq):
            answer = answer[:-1].strip()
    
    answer = answer.replace('""', '"')
    answer = answer.replace("''", "'")
    answer = answer.replace('""""', '')
    answer = answer.replace('“”', '')
    answer = answer.replace('‘’', '')
    
    answer = re.sub(r'"{2,}', '"', answer)
    answer = re.sub(r"'{2,}", "'", answer)
    
    answer = answer.replace('  ', ' ')
    
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
    
    system_prompt = get_system_prompt(identity, school_data)
    
    messages = [{"role": "system", "content": system_prompt}]
    if history_messages:
        messages.extend(history_messages)
    messages.append({"role": "user", "content": question.strip()})
    
    answer, elapsed_time, error = ask_ai(messages)
    
    if error:
        return f"请求失败：{error}", 0
    
    cleaned_answer = clean_answer(answer)
    
    return cleaned_answer, elapsed_time

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
    
    st.markdown('<h1 class="title-gradient" style="text-align: center; font-size: 28px; margin-bottom: 10px;">📚 小航 · 校园信息查询 AI 助手</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; color: #888; font-size: 14px;">郑州航空工业管理学院 · 数据更新日期：2026-07-16</p>', unsafe_allow_html=True)
    
    st.markdown('<div style="background: #f0f4ff; border-radius: 8px; padding: 12px; margin-bottom: 15px; font-size: 13px; color: #555;">'
                '<strong>💡 我能聊：</strong>新生报到、办事流程、电话黄页、应急防骗、交通出行<br>'
                '<strong>🚫 我不能聊：</strong>查个人成绩/课表/卡余额（不接入学校系统）<br>'
                '<strong>📅 数据更新日期：</strong>2026-07-16（如有出入，以官方为准）</div>', 
                unsafe_allow_html=True)
    
    if not API_KEY:
        st.warning("⚠️ API Key 未配置，请在 .env 文件中设置 API_KEY")
        return
    
    school_data, missing_files = load_school_data()
    
    if missing_files:
        st.warning(f"⚠️ 以下数据文件缺失或读取失败：{', '.join(missing_files)}")
    
    if "identity" not in st.session_state:
        st.session_state.identity = "新生"
    
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    
    if "history" not in st.session_state:
        st.session_state.history = []
    
    col_identity, col_clear = st.columns([2, 1])
    
    with col_identity:
        identity_options = ["新生", "在校生", "教师"]
        new_identity = st.selectbox("请选择你的身份", identity_options, 
                                    index=identity_options.index(st.session_state.identity),
                                    key="identity_select")
        if new_identity != st.session_state.identity:
            st.session_state.identity = new_identity
            st.session_state.chat_history = []
            st.rerun()
    
    with col_clear:
        if st.button("🗑️ 清空对话", use_container_width=True):
            st.session_state.chat_history = []
            st.session_state.history = []
            st.rerun()
    
    st.markdown(f'<div style="color: #667eea; font-weight: bold; margin-bottom: 10px;">当前身份：{st.session_state.identity}</div>', 
                unsafe_allow_html=True)
    
    recommended_questions = RECOMMENDED_QUESTIONS.get(st.session_state.identity, [])
    
    st.markdown('<div style="font-size: 14px; color: #666; margin-bottom: 8px;">💡 推荐问题（点击快速提问）：</div>', 
                unsafe_allow_html=True)
    
    cols = st.columns(2)
    for i, question in enumerate(recommended_questions):
        with cols[i % 2]:
            if st.button(question, key=f"recommend_{i}", use_container_width=True):
                st.session_state.user_input = question
                st.rerun()
    
    tab1, tab2 = st.tabs(["💬 智能问答", "📞 电话黄页"])
    
    with tab1:
        if "user_input" not in st.session_state:
            st.session_state.user_input = ""
        
        user_input = st.text_input("请输入你的问题...", key="user_input", 
                                  placeholder="例如：报到那天先去哪？")
        
        col_send, col_export = st.columns([1, 1])
        
        with col_send:
            send_btn = st.button("发送", use_container_width=True)
        
        with col_export:
            if st.button("📤 导出对话", use_container_width=True):
                if st.session_state.history:
                    export_content = ""
                    for i, record in enumerate(st.session_state.history, 1):
                        export_content += f"【{i}】{record['time']} | {record['identity']}\n"
                        export_content += f"提问：{record['question']}\n"
                        export_content += f"回答：{record['answer']}\n"
                        export_content += f"耗时：{record['time_cost']}s | 字数：{record['word_count']}\n\n"
                    
                    st.download_button(
                        label="下载对话记录",
                        data=export_content,
                        file_name=f"小航对话记录_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                        mime="text/plain",
                        use_container_width=True
                    )
        
        if send_btn and user_input.strip():
            with st.spinner("小航正在思考..."):
                history_messages = []
                for msg in st.session_state.chat_history[-5:]:
                    history_messages.append({"role": "user", "content": msg["question"]})
                    history_messages.append({"role": "assistant", "content": msg["answer"]})
                
                answer, elapsed_time = ask_xiaohang(st.session_state.identity, 
                                                    user_input, 
                                                    school_data, 
                                                    history_messages)
                
                st.session_state.chat_history.append({
                    "question": user_input.strip(),
                    "answer": answer
                })
                
                st.session_state.history.insert(0, {
                    "time": datetime.now().strftime("%H:%M:%S"),
                    "identity": st.session_state.identity,
                    "question": user_input.strip(),
                    "answer": answer,
                    "time_cost": elapsed_time,
                    "word_count": len(answer)
                })
                
                st.rerun()
        
        elif send_btn and not user_input.strip():
            st.warning("请输入问题后再发送")
        
        if st.session_state.chat_history:
            st.markdown('<div style="font-size: 14px; color: #666; margin-bottom: 10px;">📜 对话记录：</div>', 
                        unsafe_allow_html=True)
            
            for msg in st.session_state.chat_history:
                st.markdown(f'<div class="chat-user">👤 {msg["question"]}</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="chat-assistant">🤖 {msg["answer"]}</div>', unsafe_allow_html=True)
        
        st.divider()
        st.markdown('<h3 style="color: #667eea;">📜 问答历史</h3>', unsafe_allow_html=True)
        
        col_clear_history, col_count = st.columns([1, 3])
        with col_clear_history:
            if st.button("🗑️ 清空历史", use_container_width=True):
                if "history" in st.session_state:
                    st.session_state.history = []
                st.rerun()
        
        if st.session_state.history:
            for record in st.session_state.history[:10]:
                st.markdown(f"""
                    <div style="background: #fff; border-radius: 8px; padding: 12px; margin-bottom: 8px; border: 1px solid #e0e0e0;">
                        <div style="font-size: 12px; color: #888; margin-bottom: 4px;">
                            [{record['time']}] <span style="font-weight:bold; color:#667eea;">{record['identity']}</span>
                            <span style="float:right; color:#aaa;">{record['time_cost']}s | {record['word_count']}字</span>
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
