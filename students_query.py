import csv
import os

def load_students(filename):
    students = []
    try:
        if not filename or not filename.strip():
            print("错误：文件名为空")
            return students
        
        if not os.path.exists(filename):
            print(f"错误：文件 '{filename}' 不存在")
            return students
        
        if not os.path.isfile(filename):
            print(f"错误：'{filename}' 不是有效的文件")
            return students
        
        file = open(filename, "r", encoding="utf-8")
        reader = csv.DictReader(file)
        
        if reader.fieldnames is None:
            print("错误：文件内容为空或格式不正确")
            file.close()
            return students
        
        for row in reader:
            students.append(row)
        file.close()
        return students
    except FileNotFoundError:
        print(f"错误：未找到文件 '{filename}'")
        return students
    except PermissionError:
        print(f"错误：没有权限读取文件 '{filename}'")
        return students
    except csv.Error as e:
        print(f"错误：CSV 文件格式错误 - {str(e)}")
        return students
    except Exception as e:
        print(f"读取文件失败：{str(e)}")
        return students

def _students(students):