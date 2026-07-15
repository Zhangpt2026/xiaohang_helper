import streamlit as st
st.title("Streamlit 体验")
st.header("简易计算器")

num1 = st.number_input("第一个数", value=0)
num2 = st.number_input("第二个数", value=0)

operation = st.selectbox("运算", ["加法", "减法", "乘法", "除法"])

if st.button("计算"):
    result = None
    if operation == "加法":
        result = num1 + num2
    elif operation == "减法":
        result = num1 - num2
    elif operation == "乘法":
        result = num1 * num2
    elif operation == "除法":
        if num2 == 0:
            st.error("除数不能为 0")
        else:
            result = num1 / num2

    if result is not None:
        st.success(f"结果：{result}")
        st.session_state["history"].append(f"{num1} {operation} {num2} = {result}")

if "history" not in st.session_state:
    st.session_state["history"] = []

st.divider()

st.header("计算历史")
for item in reversed(st.session_state["history"]):
    st.write(item)

st.divider()

st.header("打招呼")

name = st.text_input("名字")
grade = st.selectbox("年级", ["大一", "大二", "大三", "大四"])

if st.button("打招呼"):
    if name:
        st.write(f"你好，{name}！你是{grade}学生。")
    else:
        st.warning("请输入你的名字")