import requests
import os

API_URL = "https://api.siliconflow.cn/v1/chat/completions"
API_KEY = "sk-eisgfevoxkvnrqgubncjikuobqyohuzafrshvnmamtnobhzh"

DATA_DIR = "data"
DATA_FILES = ["01_新生入学.md", "02_办事流程.md", "03_电话黄页.md", "04_应急防骗.md"]

def load_school_data():
    content = ""
    for fname in DATA_FILES:
        path = os.path.join(DATA_DIR, fname)
        with open(path, "r", encoding="utf-8") as f:
            content += f"\n\n=== {fname} ===\n" + f.read()
    return content

school_data = load_school_data()
print(f"学校资料大小: {len(school_data)} 字符")

system_prompt = f"""你是"小航"，郑州航空工业管理学院的校园信息查询 AI 助手。
当前用户身份：大一新生。
你像一位热心的大二学长，语气详细、口语化、多给鼓励。
回答重点：把流程拆成具体步骤，涉及金钱/转账无条件提示防骗。

【防幻觉硬规则】
1. 只能根据【学校资料】回答，资料里没有的明说"这个我没收录，建议拨打 0371-61911000 总值班室问一下"
2. 严禁编造电话号码、地址、办公时间、学费金额、人名
3. 涉及金钱/转账，无条件提示"先联系辅导员核实，任何要求转账的都是诈骗"
4. 涉及心理危机（自杀、不想活、活不下去等），立即给：12320-5 心理援助 + 学校心理咨询中心 + 告诉辅导员
5. 不接入学校系统（教务/一卡通/财务），被问"查我的成绩/课表/卡余额"礼貌拒绝
6. 回答末尾标注 [来源:文件名]

【别名词典】
- "学校""航院""ZUA""郑航" = 郑州航空工业管理学院
- "新校区""龙湖""新校" = 龙子湖校区
- "卡""饭卡""校卡" = 校园一卡通
- "保安""门卫""校警" = 保卫处
- "迁户口""落户" = 户籍迁入/迁出
- "调宿舍""换宿舍" = 宿舍调整申请
- "证明""在读证明" = 在校学籍证明

【学校资料】
{school_data}"""

print(f"系统提示词总大小: {len(system_prompt)} 字符")

data = {
    "model": "deepseek-ai/DeepSeek-V4-Flash",
    "messages": [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": "学费什么时候交"}
    ]
}

print("\n开始调用 API...")
try:
    response = requests.post(API_URL, headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}, json=data, timeout=60)
    print(f"状态码: {response.status_code}")
    result = response.json()
    if "choices" in result:
        print("回答:", result["choices"][0]["message"]["content"])
    else:
        print("错误:", result)
except Exception as e:
    print(f"异常: {str(e)}")