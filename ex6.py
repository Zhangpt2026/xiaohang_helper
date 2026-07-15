def load_scores(filename):
    students = []
    try:
        with open(filename, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                name, score_str = line.split(",")
                score = int(score_str)
                student_dict = {"name": name, "score": score}
                students.append(student_dict)
        return students
    except FileNotFoundError:
        print(f"错误：文件 {filename} 不存在！")
        return None
def get_stats(students):
    if not students:
        return None, None, 0.0
    score_list = [s["score"] for s in students]
    max_score = max(score_list)
    max_student = next(s for s in students if s["score"] == max_score)
    max_choice = (max_score, max_student["name"])
    min_score = min(score_list)
    min_student = next(s for s in students if s["score"] == min_score)
    min_info = (min_score, min_student["name"])
    average_score = sum(score_list) / len(score_list)
    return max_choice, min_info, average_score
if __name__ == "__main__":
    file_name = "scores.txt"
    student_data = load_scores(file_name)
    if student_data is not None:
        print(f"加载成功，共{len(student_data)}人")
        max_result, min_result, average_result = get_stats(student_data)
        print(f"最高分：{max_result[0]}（{max_result[1]}）")
        print(f"最低分：{min_result[0]}（{min_result[1]})")
        print(f"平均分：{average_result}")