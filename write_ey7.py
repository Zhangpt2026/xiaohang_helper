import base64,os
b = input()
H = base64.b64decode(b).decode("utf-8")
p = os.path.join(os.path.expanduser("~"), "PyCharmMiscProject", "ey7.py")
open(p, "w", encoding="utf-8").write(H)
print("Done")
