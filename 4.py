numbers=input("请输入一串密码：")
score=0
if len(numbers)>=8:
    score+=1
has_shu=False
has_da=False
has_xiao=False
has_special=False
if numbers.isdigit():
    has_shu=True
elif numbers.isupper():
    has_da=True
elif numbers.islower():
    has_xiao=True
else:
    has_special=True
if has_shu:
    score+=1
if has_da:
    score+=1
if has_xiao:
    score+=1
if has_special:
    score+=1
if 0<=score<=1:
    print("弱")
if 2<=score<=3:
    print("中")
if 4<=score<=5:
    print("强")