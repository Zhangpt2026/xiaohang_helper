import random
while True:
    answer = random.randint(1,100)
    count=7
    for i in range(1,count+1):
        guess=int(input("请输入数字："))
        if answer==guess:
            print(f"恭喜猜对！用了{i}次")
            break
        elif guess>answer:
            print("猜大了")
        else:
            print("猜小了")
        yu=count-i
        if yu>0:
            print(f"还剩下{yu}次机会")
        else:
            print(f"游戏结束，答案是{answer}")
    end=input("再来一局吗？（y/n）:")
    if end !='y':
        print("谢谢游玩，再见")
        break
