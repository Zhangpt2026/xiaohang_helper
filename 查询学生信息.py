students=[
    {"姓名":"王振辉","id":137891,"专业":"人工智能"},
    {"姓名":"王五","id":134891,"专业":"土木工程"},
    {"姓名":"王巴","id":137691,"专业":"机械设计制造及其自动化"}
]
keyword=input("请输入姓名：")
for student in students:
    if student["姓名"]==keyword:
     print("查询结果：")
     print("学生姓名:",student["姓名"])
     print("id:",student["id"])
     print("专业：",student["专业"])
