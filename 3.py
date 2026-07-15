n_str=input("请输入一个正整数：")
sum=0
odd=0
even=0
for char in n_str:
    number=int(char)
    sum=sum+number
    if number%2==0:
        even=even+1
    else:
        odd=odd+1
if n_str==n_str[::-1]:
    flag="是回文数"
else:
    flag="不是回文数"
print("各位数之和为：",sum)
print("奇数个数：",odd,"偶数个数:",even)
print(flag)