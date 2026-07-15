import streamlit as st
from config import RECOMMENDED_QUESTIONS
from data_loader import load_school_data, load_phone_directory
from prompt import get_system_prompt, check_hard_rules
from api import ask_xiaohang

def main():
    st.set_page_config(page_title="小航 · 校园信息查询 AI 助手", page_icon="📚")
    
    st.title("小航 · 校园信息查询 AI 助手")
    st.subheader("郑州航空工业管理学院专属")
    
    school_data, missing_files = load_school_data()
    
    if missing_files:
        st.warning(f"以下数据文件缺失，部分功能可能受影响：{', '.join(missing_files)}")
    
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
                    answer = ask_xiaohang(identity, prompt, school_data, get_system_prompt, check_hard_rules)
                    st.markdown(answer)
            
            st.session_state.messages.append({"role": "assistant", "content": answer})
    
    with tab2:
        st.header("📞 校园电话黄页")
        phone_content = load_phone_directory()
        st.markdown(phone_content)

if __name__ == "__main__":
    main()