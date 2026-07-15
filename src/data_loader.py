import os
from config import DATA_DIR, DATA_FILES

def load_school_data():
    content = ""
    missing_files = []
    
    for fname in DATA_FILES:
        path = os.path.join(DATA_DIR, fname)
        try:
            with open(path, "r", encoding="utf-8") as f:
                content += f"\n\n=== {fname} ===\n" + f.read()
        except FileNotFoundError:
            missing_files.append(fname)
            print(f"⚠ 文件不存在：{path}")
        except Exception as e:
            missing_files.append(fname)
            print(f"⚠ 读取文件失败 {path}: {str(e)}")
    
    if missing_files:
        print(f"\n⚠ 警告：以下数据文件缺失，部分功能可能受影响：{', '.join(missing_files)}")
    
    return content, missing_files

def load_phone_directory():
    path = os.path.join(DATA_DIR, "03_电话黄页.md")
    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        return content
    except Exception as e:
        return f"无法加载电话黄页：{str(e)}"

if __name__ == "__main__":
    print("测试数据加载模块...")
    school_data, missing = load_school_data()
    print(f"数据加载完成，长度: {len(school_data)}")
    print(f"缺失文件: {missing}")
    
    phone_dir = load_phone_directory()
    print(f"\n电话黄页前200字符:\n{phone_dir[:200]}...")