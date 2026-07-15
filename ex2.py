dicts={"title":"python入门","author":"张老师","price":59.0,"stock":10}
print(dicts["title"])
print(dicts["author"])
dicts["price"]=49.0
dicts["pulisher"]="清华大学出版社"
dicts.pop("stock")
print(dicts)
for key,value in dicts.items():
    print(key,value)