# 小航 · 校园信息查询 AI 助手

郑州航空工业管理学院专属 AI 助手，提供校园信息查询服务。

## 功能

- 🎒 新生入学指南
- 📚 在校生办事流程
- 👨‍🏫 教师办公服务
- 📞 电话黄页查询

## 技术栈

- Streamlit - 界面框架
- 硅基流动 API - AI 模型调用
- Python - 后端语言

## 运行方式

```bash
pip install -r requirements.txt
streamlit run src/app.py
```

## 项目结构

```
xiaohang_helper/
├── src/
│   ├── __init__.py
│   ├── app.py          # Streamlit 主程序
│   ├── prompts.py      # Prompt 工程
│   ├── api.py          # API 调用
│   └── config.py       # 配置项
├── data/
│   ├── 01_新生入学.md
│   ├── 02_办事流程.md
│   ├── 03_电话黄页.md
│   └── 04_应急防骗.md
├── tests/
│   └── __init__.py
├── docs/
├── .gitignore
├── requirements.txt
└── README.md
```

## 配置说明

在 `src/config.py` 中配置 API Key：

```python
API_KEY = "your_siliconflow_api_key_here"
```

## 身份分流

- **新生**：热心学长风格，详细解答，多鼓励
- **在校生**：简洁回答，重点：地点、电话、材料、时间
- **教师**：专业礼貌，重点：政策依据、办事窗口、联系人

## 防幻觉规则

1. 只能根据资料回答，资料里没有的明说
2. 严禁编造电话号码、地址、办公时间、学费金额、人名
3. 涉及金钱/转账，无条件提示防骗
4. 涉及心理危机，立即给心理援助电话
5. 不接入学校系统，不查询个人信息
6. 回答末尾标注来源文件名