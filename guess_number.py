import random
answer=random.randint(1,100)
count=0
print('欢迎开始猜数字游戏')
while count<7:
    num=int(input('你要输入的数字:'))
    count+=1
    if num==answer:
        if count==7:
            print('恭喜你猜对了')
        else:
            print('恭喜你猜对了')
            break
    elif num>answer:
        if count==7:
            print('很遗憾你没有猜对')
            break
        print('猜大了')

    else :
        if count==7:
            print('很遗憾你没有猜对')
            break
        print('猜小了')