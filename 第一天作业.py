while True:
 score = (input("输入一个百分制成绩: "))
 if score == "q":
     print("程序已退出")
     break
 else:
     score=int(score)
 if 90 <= score <= 100:
    print('A')
 elif 80 <= score <= 89:
    print('B')
 elif 70 <= score <= 79:
    print('C')
 elif 60 <= score <= 69:
    print('D')
 elif 0 <= score <= 59:
    print('E')
 else:
    print("成绩无效")
