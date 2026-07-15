import os

folder_path = r'c:\Users\刘雪晴\PyCharmMiscProject\campus_data'

if not os.path.exists(folder_path):
    print("文件夹不存在，请检查路径")
else:
    for root, dirs, files in os.walk(folder_path):
        for filename in files:
            if filename.endswith('.txt'):
                file_path = os.path.join(root, filename)
                line_count = 0
                with open(file_path, 'r', encoding='utf-8') as file:
                    for line in file:
                        line_count += 1
                print(f"{filename}: {line_count} 行")