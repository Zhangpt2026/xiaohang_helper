

def show_menu():
    print("1. 根据姓名查询学生")
    print("2. 根据学号查询学生")
    print("0. 退出系统")
def show_student(student):
    print("学号：", student["id"])
    print("姓名：", student["姓名"])
    print("专业：", student["专业"])
def find_student(students, keyword, search_type):
    for stu in students:
        if search_type == 1 and stu["姓名"] == keyword:
            return stu
        elif search_type == 2 and str(stu["id"]) == keyword:
            return stu
    return None
students = [
    {"姓名": "王振辉", "id": 137891, "专业": "人工智能"},
    {"姓名": "王五", "id": 134891, "专业": "土木工程"},
    {"姓名": "王巴", "id": 137691, "专业": "机械设计制造及其自动化"}
]
while True:
    try:
        show_menu()
        choice = int(input("请输入操作序号："))
        if choice == 0:
            print("已退出查询系统，再见！")
            break
        elif choice == 1:
            name = input("请输入要查询的学生姓名：")
            res = find_student(students, name, 1)
            if res is not None:
                show_student("res")
            else:
                print(f"未找到姓名为【{name}】的学生\n")
        elif choice == 2:
            sid = input("请输入要查询的学生学号：")
            res = find_student(students, sid, 2)
            if res is not None:
                show_student("res")
            else:
                print(f"未找到学号为【{sid}】的学生\n")
        else:
            print("输入序号无效，请选择 0/1/2\n")
    except ValueError:
        print("输入错误！请输入数字序号 0、1、2\n")