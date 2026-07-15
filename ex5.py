def show_all(students):
    print(students)
def find_by_name(students, name):
    if not students:
        return None
    for student in students:
        if student["name"] == name:
         return student
    return None
def get_average(students):
    if not students:
        return 0.0
    total=sum(student["score"] for student in students)
    avg = total/len(students)
    return round(avg,1)
def get_pass_count(students):
    count = 0
    for stu in students:
        if stu['score'] >= 60:
            count += 1
    return count
if __name__ == '__main__':
    students_list = [
        {"name": "张三", "age": 18, "score": 85},
        {"name": "李四", "age": 19, "score": 92},
        {"name": "王五", "age": 18, "score": 47},
        {"name": "赵六", "age": 20, "score": 76}]
    print("全部学生信息：")
    show_all(students_list)
    print("平均分:",get_average(students_list))
    print("及格人数：",get_pass_count(students_list))

