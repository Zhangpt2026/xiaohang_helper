import sys
sys.path.insert(0, '.')
from ey7 import ask_deepseek, ask_glm, validate_input, check_api_key

def run_tests():
    test_results = []
    
    print("=" * 60)
    print("ey7.py 异常处理测试")
    print("=" * 60)
    
    test_cases = [
        ("测试1: 空输入", lambda: ask_deepseek(""), "错误：输入不能为空"),
        ("测试2: 空白输入", lambda: ask_deepseek("   "), "错误：输入不能为空"),
        ("测试3: DeepSeek Key 失效检测", lambda: ask_deepseek("hello"), "API Key 未配置或无效"),
        ("测试4: GLM API 调用失败检测", lambda: ask_glm("hello"), "GLM 错误"),
        ("测试5: validate_input 空值", lambda: validate_input(""), (False, "错误：输入不能为空")),
        ("测试6: validate_input 空白", lambda: validate_input("   "), (False, "错误：输入不能为空")),
        ("测试7: validate_input 有效", lambda: validate_input("hello"), (True, "")),
        ("测试8: check_api_key 空值", lambda: check_api_key(""), (False, "API Key 未配置或无效")),
        ("测试9: check_api_key 占位符", lambda: check_api_key("你的 DeepSeek API Key 在这里"), (False, "API Key 未配置或无效")),
        ("测试10: check_api_key 空白", lambda: check_api_key("   "), (False, "API Key 未配置或无效")),
        ("测试11: check_api_key 有效", lambda: check_api_key("sk-valid12345"), (True, "")),
        ("测试12: 非占位符Key但API失败", lambda: ask_glm("test"), "GLM 错误"),
    ]
    
    passed = 0
    failed = 0
    
    for i, (test_name, test_func, expected) in enumerate(test_cases, 1):
        print(f"\n测试 {i}: {test_name}")
        try:
            result = test_func()
            if isinstance(result, tuple):
                actual = result
            else:
                actual = result[0] if isinstance(result, tuple) else result
            
            if isinstance(expected, tuple):
                if actual == expected:
                    print(f"  ✓ 通过")
                    passed += 1
                else:
                    print(f"  ✗ 失败 - 期望: {expected}, 实际: {actual}")
                    failed += 1
            else:
                if expected in str(actual):
                    print(f"  ✓ 通过")
                    passed += 1
                else:
                    print(f"  ✗ 失败 - 期望包含: '{expected}', 实际: '{actual}'")
                    failed += 1
            test_results.append((test_name, "通过" if passed > failed else "失败"))
        except Exception as e:
            print(f"  ✗ 异常 - {str(e)}")
            failed += 1
            test_results.append((test_name, "失败"))
    
    print("\n" + "=" * 60)
    print(f"测试结果汇总: 通过 {passed} / 失败 {failed}")
    print("=" * 60)
    
    for name, status in test_results:
        print(f"{name}: {status}")
    
    return passed == len(test_cases)

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)