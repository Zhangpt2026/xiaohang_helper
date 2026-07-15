def choices():
    print("1.摄氏转华氏")
    print("2.华氏转摄氏")
    print("3.退出")
def celsius_to_fahrenheit(c):
    f=((c*9/5)+32)
    return f
def fahrenheit_to_celsius(f):
    c=(f-32)*5/9
    return round(c,1)
while True:
    choices()
    choice=input("请选择：")
    if choice=="1":
        try:
            celsius = float(input("请输入摄氏温度："))
            result = celsius_to_fahrenheit(celsius)
            print("华氏温度：", result)
        except ValueError:
            print("请输入有效的数字。")
    elif choice=="2":
        try:
            fahrenheit = float(input("请输入华氏温度："))
            result = fahrenheit_to_celsius(fahrenheit)
            print("摄氏温度：", result)
        except ValueError:
            print("请输入有效的数字。")
    elif choice == "3":
            print("程序结束")
            break
    else:
            print("无效的选择，请重新输入。")

