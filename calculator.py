num1=float(input("请输入一个数字:"))
operator=input("请输入+ - * /")
num2=float(input("请输入一个数字:"))
if operator=='+':
    print(num1+num2)
elif operator=='-':
    print(num1-num2)
elif operator=='*':
    print(num1*num2)
elif operator=='/':
    if num2==0:
        print("除数不能为0")
    else:
     print(num1/num2)
else:
    print("暂不支持该运算")