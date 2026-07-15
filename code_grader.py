import requests
API_KEY = "sk-eisgfevoxkvnrqgubncjikuobqyohuzafrshvnmamtnobhzh"
API_URL = "https://api.siliconflow.cn/v1/chat/completions"
def grade_code(code, requirement):
    prompt = f"""你是一位资深的 Python 编程老师，请根据作业要求对学生代码进行评分。
【作业要求】
{requirement}
【评分标准】
1. 功能完整性（0-40分）：代码是否实现了所有要求的功能？是否能正常运行？
2. 代码可读性（0-30分）：代码结构是否清晰？变量和函数命名是否规范？是否有适当的注释？
3. 异常处理（0-30分）：是否处理了可能的异常情况？错误提示是否友好？
【学生代码】
```python
{code}
```
【输出格式要求】
请按照以下格式输出评分结果：
## 评分结果
功能完整性：X分
代码可读性：X分
异常处理：X分
总分：X分
## 改进建议
1. 第一条改进建议
2. 第二条改进建议
请严格按照上述格式输出，不要有多余的内容。"""
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "deepseek-ai/DeepSeek-V4-Flash",
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.3
    }
    
    try:
        response = requests.post(API_URL, headers=headers, json=data, timeout=60)
        if response.status_code == 200:
            result = response.json()
            if "choices" in result:
                return result["choices"][0]["message"]["content"]
            else:
                return f"API 返回格式错误: {result}"
        else:
            return f"API 请求失败，状态码: {response.status_code}"
    except Exception as e:
        return f"API 调用失败: {str(e)}"

def grade_code_local(code, requirement):
    score_function = 25
    score_readability = 15
    score_exception = 20
    
    if "def " in code and "csv" in code.lower():
        score_function += 10
    if "try" in code.lower() and "except" in code.lower():
        score_exception += 5
    if code.count("\n") > 3:
        score_function += 5
    if "print" in code:
        score_exception += 5
    
    total = score_function + score_readability + score_exception
    
    suggestions = []
    if score_function < 40:
        suggestions.append("代码只实现了读取CSV功能，缺少按姓名查询的功能，建议添加search_student函数")
    if score_readability < 25:
        suggestions.append("代码缩进不一致，建议统一使用4个空格缩进，并添加函数注释")
    if score_exception < 25:
        suggestions.append("异常处理过于宽泛，建议捕获具体异常类型（如FileNotFoundError）")
    if len(suggestions) == 0:
        suggestions = ["代码整体质量不错，可以考虑添加更多注释说明", "可以添加单元测试来验证功能正确性"]
    elif len(suggestions) == 1:
        suggestions.append("可以考虑添加更多注释说明代码逻辑")
    
    result = f"""## 评分结果
功能完整性：{score_function}分
代码可读性：{score_readability}分
异常处理：{score_exception}分
总分：{total}分

## 改进建议
1. {suggestions[0]}
2. {suggestions[1]}"""
    
    return result

student_code = """import csv
def load_students(filename):
 students = []
 try:
  file = open(filename, "r", encoding="utf-8")
  reader = csv.DictReader(file)
  for row in reader:
   students.append(row)
   file.close()
 except:
  print("读取文件失败，请检查文件名和保存位置。")
  return students
 def _students(students):"""

homework_requirement = "从 CSV 读取学生信息并支持按姓名查询"

print("=" * 60)
print("编程作业自评助手")
print("=" * 60)
print(f"\n【作业要求】\n{homework_requirement}")
print(f"\n【学生代码】\n{student_code}")
print("\n" + "=" * 60)
print("【AI 评分结果】")
print("=" * 60)

if API_KEY and API_KEY != "你的 API Key 在这里":
    result = grade_code(student_code, homework_requirement)
else:
    print("注意：API Key 未设置，使用本地模拟评分\n")
    result = grade_code_local(student_code, homework_requirement)

print(result)