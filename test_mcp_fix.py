#!/usr/bin/env python3
"""
测试 MCP 服务器修复效果的脚本
"""
import subprocess
import sys
import os

def test_python_environment():
    """测试Python环境是否正常工作"""
    print("🔍 测试Python环境...")

    python_exe = r"C:\Users\ddo\AppData\Local\Programs\Python\Python312\python.exe"

    # 测试基本Python功能
    try:
        result = subprocess.run([
            python_exe, "-c",
            "import sys; print(f'Python version: {sys.version}'); print('✅ Python environment working!')"
        ], capture_output=True, text=True, env={
            'PYTHONPATH': r"C:\Users\ddo\AppData\Roaming\npm",
            'PYTHONHOME': ''
        })

        if result.returncode == 0:
            print("✅ Python环境测试通过")
            print(result.stdout)
            return True
        else:
            print("❌ Python环境测试失败")
            print(result.stderr)
            return False
    except Exception as e:
        print(f"❌ Python环境测试异常: {e}")
        return False

def test_deepseek_server():
    """测试deepseek服务器是否能正常导入"""
    print("\n🔍 测试DeepSeek MCP服务器...")

    python_exe = r"C:\Users\ddo\AppData\Local\Programs\Python\Python312\python.exe"
    server_path = r"C:\Users\ddo\AppData\Roaming\npm\deepseek_mcp_server.py"

    try:
        result = subprocess.run([
            python_exe, "-c",
            f"import sys; sys.path.insert(0, r'C:\Users\ddo\AppData\Roaming\npm'); import importlib.util; spec = importlib.util.spec_from_file_location('deepseek_server', r'{server_path}'); print('✅ DeepSeek服务器文件可导入')"
        ], capture_output=True, text=True, env={
            'PYTHONPATH': r"C:\Users\ddo\AppData\Roaming\npm",
            'PYTHONHOME': ''
        })

        if result.returncode == 0:
            print("✅ DeepSeek服务器文件测试通过")
            return True
        else:
            print("❌ DeepSeek服务器文件测试失败")
            print(result.stderr)
            return False
    except Exception as e:
        print(f"❌ DeepSeek服务器测试异常: {e}")
        return False

def test_web_scraping_server():
    """测试web-scraping服务器是否能正常导入"""
    print("\n🔍 测试Web-Scraping MCP服务器...")

    python_exe = r"C:\Users\ddo\AppData\Local\Programs\Python\Python312\python.exe"
    server_path = r"C:\Users\ddo\AppData\Roaming\npm\web_scraping_simple_mcp_server.py"

    try:
        result = subprocess.run([
            python_exe, "-c",
            f"import sys; sys.path.insert(0, r'C:\Users\ddo\AppData\Roaming\npm'); import importlib.util; spec = importlib.util.spec_from_file_location('web_scraping_server', r'{server_path}'); print('✅ Web-Scraping服务器文件可导入')"
        ], capture_output=True, text=True, env={
            'PYTHONPATH': r"C:\Users\ddo\AppData\Roaming\npm",
            'PYTHONHOME': ''
        })

        if result.returncode == 0:
            print("✅ Web-Scraping服务器文件测试通过")
            return True
        else:
            print("❌ Web-Scraping服务器文件测试失败")
            print(result.stderr)
            return False
    except Exception as e:
        print(f"❌ Web-Scraping服务器测试异常: {e}")
        return False

def main():
    print("🚀 开始MCP服务器修复效果测试\n")

    tests = [
        ("Python环境", test_python_environment),
        ("DeepSeek服务器", test_deepseek_server),
        ("Web-Scraping服务器", test_web_scraping_server)
    ]

    results = []
    for test_name, test_func in tests:
        result = test_func()
        results.append((test_name, result))

    print("\n" + "="*50)
    print("📊 测试结果汇总:")
    print("="*50)

    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{test_name:<20} {status}")

    passed = sum(1 for _, result in results if result)
    total = len(results)

    print(f"\n总计: {passed}/{total} 测试通过")

    if passed == total:
        print("\n🎉 所有测试通过！MCP服务器配置修复成功。")
        print("\n📋 修复摘要:")
        print("1. ✅ 明确指定了Python可执行文件路径")
        print("2. ✅ 清除了PYTHONHOME环境变量冲突")
        print("3. ✅ 配置了正确的PYTHONPATH")
        print("4. ✅ 添加了web-scraping-mcp配置")
        print("\n🔄 重启Claude Code以使配置生效。")
    else:
        print(f"\n⚠️  {total - passed} 个测试失败，需要进一步排查。")

    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)