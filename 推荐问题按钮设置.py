from typing import Optional


class CampusQA:
    UNIFORM_RULES = """
    【6条防幻觉强制硬规则】
    1. 无校园官方文件、通知支撑的信息一律不得编造，不确定内容直接告知用户暂无相关政策并指引咨询对应办公室；
    2. 涉及金钱缴费、转账、校外收费时，必须附带校园反诈提示，提醒仅走学校官方渠道；
    3. 用户流露抑郁、焦虑、轻生、学业崩溃等心理危机表述，立刻推送校内心理咨询中心联系方式与值班时间，不做心理诊断；
    4. 不虚构校内办公室、辅导员、教师私人电话，所有联系方式仅输出官方电话黄页内登记号码；
    5. 跨身份问题需主动分流，新生咨询转专业、教师咨询新生报到时，提示切换对应身份获取精准答复；
    6. 所有流程、时间、费用标准严格依照校内MD资料原文作答，禁止主观修改、估算政策条款。
    """
    QUESTIONS = {
        "大一新生": [
            {"id": "F1", "text": "报到那天先去哪？", "trigger_rule": None},
            {"id": "F2", "text": "学费什么时候交？", "trigger_rule": "finance_anti_fraud"},
            {"id": "F3", "text": "宿舍是4人间还是6人间？", "trigger_rule": None},
            {"id": "F4", "text": "有人冒充辅导员要钱怎么办？", "trigger_rule": "anti_fraud"}
        ],
        "在校老生": [
            {"id": "S1", "text": "怎么开在读证明？", "trigger_rule": None},
            {"id": "S2", "text": "校园卡丢了怎么补？", "trigger_rule": None},
            {"id": "S3", "text": "转专业怎么转？", "trigger_rule": None},
            {"id": "S4", "text": "感觉学业压力大想找人倾诉该找谁？", "trigger_rule": "mental_crisis"}
        ],
        "教师": [
            {"id": "T1", "text": "差旅怎么报销？", "trigger_rule": "finance_anti_fraud"},
            {"id": "T2", "text": "调课怎么申请？", "trigger_rule": None},
            {"id": "T3", "text": "教室设备坏了找谁？", "trigger_rule": None},
            {"id": "T4", "text": "科研项目去哪申报？", "trigger_rule": None}
        ]
    }
    DICT_MAP = {
        "大一新生": {
            "报到点": "新生报到处/各学院迎新摊位",
            "校园卡": "新生一卡通",
            "宿舍费": "住宿费",
            "辅导员": "迎新带班辅导员",
            "迎新群": "学院官方新生微信群",
            "缴费平台": "校园统一缴费小程序"
        },
        "在校老生": {
            "在读证明": "学籍在校证明",
            "校园卡": "学生一卡通",
            "教务系统": "选课成绩系统",
            "心理中心": "校内心理咨询室",
            "转专业申请": "学籍变更申报",
            "自习室": "图书馆阅览自习区域"
        },
        "教师": {
            "差旅报销": "教职工出差经费申报",
            "调课申请": "教学课时变更报备",
            "教室设备": "多媒体教学仪器",
            "科研项目": "校级/省级科研课题",
            "教务办": "教学管理办公室",
            "财务处": "经费报销审核科室"
        }
    }

    def __init__(self) -> None:
        self.current_user_type: Optional[str] = None
        self.prompt_cache: dict[str, str] = {}

    def build_prompt(self, user_type: str) -> str:
        if user_type in self.prompt_cache:
            return self.prompt_cache[user_type]
        if user_type == "大一新生":
            position = "你当前服务对象为【大一新生】，所有回答围绕新生入学、报到、住宿、缴费、校园入门生活展开，优先响应新生4个推荐问题，输出简洁易懂的入学指引。"
            limit = "应答约束：优先解读新生推荐按钮问题，回答侧重入门操作，篇幅简短，关键信息加粗标注，主动提醒报到、缴费、住宿相关反诈注意事项。"
        elif user_type == "在校老生":
            position = "你当前服务对象为【在校老生（大二至大四）】，所有回答围绕学籍办理、校园日常服务、转专业、图书馆、学业压力疏导、校内证明开具展开，优先响应老生4个推荐问题。"
            limit = "应答约束：老生咨询学籍、办事类问题输出完整办理步骤，用户倾诉学业压力时主动触发心理干预规则，复杂流程分点罗列，可同步推送对应科室官方咨询电话。"
        else:
            position = "你当前服务对象为【校内任课教师、行政教职工】，所有回答围绕差旅报销、调课申请、教室设备报修、科研项目申报、教学教务办公事务展开，优先响应教师4个推荐问题。"
            limit = "应答约束：教职工财务、教学、科研类问题精准匹配对应部门政策，报销、申报类内容明确材料清单，设备故障直接推送后勤维修官方对接渠道。"
        dict_text = "【专属别名词典】\n"
        for k, v in self.DICT_MAP[user_type].items():
            dict_text += f"{k} = {v}\n"
        full_prompt = f"""
        ======校园身份分流Prompt-{user_type}======
        {position}
        {dict_text}
        {self.UNIFORM_RULES}
        {limit}
        ==========================================
        """
        self.prompt_cache[user_type] = full_prompt
        return full_prompt

    def switch_user_type(self, user_type: str) -> bool:
        if user_type not in self.QUESTIONS:
            print("身份不存在！可选：大一新生 / 在校老生 / 教师")
            return False
        self.current_user_type = user_type
        self.build_prompt(user_type)
        print(f"\n✅ 已切换身份：{user_type}，加载专属Prompt完成")
        print(self.prompt_cache[user_type])
        return True

    def show_quick_questions(self) -> None:
        if not self.current_user_type:
            print("⚠️ 请先选择用户身份！")
            return
        print(f"\n=====【{self.current_user_type} 快捷提问按钮】=====")
        q_list = self.QUESTIONS[self.current_user_type]
        for idx, item in enumerate(q_list, 1):
            print(f"{idx}. {item['text']} （编号：{item['id']}）")
        print("0. 手动输入自定义问题")

    def click_question(self, select_num: int) -> None:
        if not self.current_user_type:
            print("⚠️ 请先选择用户身份！")
            return
        q_list = self.QUESTIONS[self.current_user_type]
        if select_num == 0:
            user_input = input("请输入你的问题：")
            self.simulate_ai_reply(user_input, trigger_rule=None)
            return
        if select_num < 1 or select_num > 4:
            print("输入数字错误，请输入0-4之间数字")
            return

        target_q = q_list[select_num - 1]
        print(f"\n👉 点击快捷问题：{target_q['text']}")
        self.simulate_ai_reply(target_q["text"], target_q["trigger_rule"])

    def simulate_ai_reply(self, question: str, trigger_rule: Optional[str]) -> None:
        print(f"\n🤖 AI调用当前身份Prompt作答，问题：{question}")
        if trigger_rule == "anti_fraud":
            print("【触发反诈硬规则强制输出】：凡是辅导员、老师私下索要学费、住宿费、资料费均为诈骗，所有缴费仅走学校官方缴费平台，切勿私转微信支付宝！")
        elif trigger_rule == "mental_crisis":
            print("【触发心理危机硬规则强制输出】：校内心理咨询中心位于图书馆302室，工作日8:30-17:00免费咨询，心理热线：0XX-XXXX8899，有情绪困扰可随时前往。")
        elif trigger_rule == "finance_anti_fraud":
            print("【触发财务反诈硬规则强制输出】：所有经费缴费、报销仅通过校内财务系统办理，陌生链接、私人转账一律不要相信。")
        print(f"基础问答回复：已根据校内MD资料、{self.current_user_type}专属政策解答该问题，严格遵循6条防幻觉规则，无编造信息。\n")


if __name__ == "__main__":
    qa_system = CampusQA()
    print("========校园身份分流快捷问答系统========")
    print("操作指引：")
    print("1. 输入身份名称切换身份：大一新生 / 在校老生 / 教师")
    print("2. show 展示当前身份4个快捷提问按钮")
    print("3. 直接输入数字 0-4 选择快捷问题（0=手动输入）")
    print("4. exit 退出系统\n")
    while True:
        cmd = input("请输入操作指令：").strip()
        if cmd == "exit":
            print("系统退出，程序结束")
            break
        elif cmd in ["大一新生", "在校老生", "教师"]:
            qa_system.switch_user_type(cmd)
        elif cmd == "show":
            qa_system.show_quick_questions()
        elif cmd in ("0", "1", "2", "3", "4"):
            qa_system.click_question(int(cmd))
        elif cmd.startswith("click"):
            try:
                num = int(cmd.split()[1])
                qa_system.click_question(num)
            except (ValueError, IndexError):
                print("指令格式错误，示例：click 1 或直接输入数字 1")
        else:
            print("无效指令，重新输入！")