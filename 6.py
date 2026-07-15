names, scores = [], []
while (n:=input("请输入学生姓名(输入done结束)："))!="done":
    grade=int(input("请输入成绩："))
    names.append(n);scores.append(grade)
if not names:
    print("无学生数据")
else:
    s=len(scores)
    average=sum(scores)/s
    high=max(scores);high_n=names[scores.index(high)]
    low=min(scores);low_n=names[scores.index(low)]
    pass_number=sum(1 for x in scores if x>=60)
    print("---")
    print(f"参与人数：{s}")
    print(f"平均分：{average:.1f}")
    print(f"最高分：{high}（{high_n}）")
    print(f"最低分：{low}（{low_n}）")
    print(f"及格：{pass_number}人  不及格：{s-pass_number}人")