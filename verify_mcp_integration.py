#!/usr/bin/env python3
"""
DeepSeek MCP集成验证脚本
验证MCP服务器配置和功能是否正常工作
"""

import json
import subprocess
import sys
import os
from pathlib import Path


def test_mcp_server_config():
    """测试MCP服务器配置"""
    print("🔍 检查MCP服务器配置...")

    config_path = Path.home() / "AppData/Roaming/npm/.claude/claude_desktop_config.json"

    if not config_path.exists():
        print("❌ 配置文件不存在")
        return False

    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)

        if "mcpServers" not in config:
            print("❌ 配置文件中未找到mcpServers")
            return False

        if "deepseek" not in config["mcpServers"]:
            print("❌ 配置文件中未找到deepseek服务器")
            return False

        deepseek_config = config["mcpServers"]["deepseek"]
        print("✅ DeepSeek MCP服务器配置存在")
        print(f"   命令: {deepseek_config.get('command', 'N/A')}")
        print(f"   参数: {deepseek_config.get('args', 'N/A')}")

        return True

    except Exception as e:
        print(f"❌ 配置文件读取错误: {e}")
        return False


def test_deepseek_module():
    """测试DeepSeek模块导入"""
    print("\n🔍 测试DeepSeek模块导入...")

    try:
        # 添加当前目录到Python路径
        current_dir = Path(__file__).parent
        sys.path.insert(0, str(current_dir))

        from deepseek_mcp_integration import create_efficient_wrapper
        wrapper = create_efficient_wrapper()

        print("✅ DeepSeek模块导入成功")

        # 测试工具列表
        tools = wrapper.get_available_tools()
        print(f"✅ 可用工具数量: {len(tools)}")
        for tool in tools:
            print(f"   - {tool['name']}: {tool['description']}")

        return True

    except ImportError as e:
        print(f"❌ 模块导入失败: {e}")
        return False
    except Exception as e:
        print(f"❌ 模块测试失败: {e}")
        return False


def test_environment_variables():
    """测试环境变量"""
    print("\n🔍 检查环境变量...")

    api_key = os.getenv("DEEPSEEK_API_KEY")

    if api_key:
        print("✅ DEEPSEEK_API_KEY 已设置")
        print(f"   密钥长度: {len(api_key)} 字符")
        return True
    else:
        print("⚠️  DEEPSEEK_API_KEY 未设置")
        print("   提示: 请设置环境变量以使用完整功能")
        return False


def test_mcp_server_process():
    """测试MCP服务器进程启动"""
    print("\n🔍 测试MCP服务器启动...")

    server_script = Path(__file__).parent / "deepseek_mcp_server.py"

    if not server_script.exists():
        print("❌ MCP服务器脚本不存在")
        return False

    try:
        # 尝试启动服务器进程（超时测试）
        process = subprocess.Popen(
            [sys.executable, str(server_script)],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        # 发送初始化请求
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {
                    "name": "test-client",
                    "version": "1.0.0"
                }
            }
        }

        process.stdin.write(json.dumps(init_request) + "\n")
        process.stdin.flush()

        # 读取响应（简短超时）
        try:
            response_line = process.stdout.readline()
            if response_line:
                response = json.loads(response_line.strip())
                if "result" in response:
                    print("✅ MCP服务器响应正常")
                    print(f"   服务器信息: {response['result'].get('serverInfo', {})}")
                    success = True
                else:
                    print("❌ MCP服务器响应异常")
                    print(f"   响应: {response}")
                    success = False
            else:
                print("❌ MCP服务器无响应")
                success = False
        except json.JSONDecodeError as e:
            print(f"❌ MCP服务器响应解析失败: {e}")
            success = False
        finally:
            process.terminate()
            process.wait(timeout=5)

        return success

    except Exception as e:
        print(f"❌ MCP服务器启动测试失败: {e}")
        return False


def test_slash_command_exists():
    """测试Slash命令文件是否存在"""
    print("\n🔍 检查Slash命令...")

    command_file = Path(__file__).parent / ".claude/commands/mcp.md"

    if command_file.exists():
        print("✅ /mcp Slash命令文件存在")
        return True
    else:
        print("❌ /mcp Slash命令文件不存在")
        return False


def main():
    """主验证流程"""
    print("🚀 DeepSeek MCP集成验证开始...")
    print("=" * 50)

    tests = [
        ("MCP服务器配置", test_mcp_server_config),
        ("DeepSeek模块", test_deepseek_module),
        ("环境变量", test_environment_variables),
        ("MCP服务器进程", test_mcp_server_process),
        ("Slash命令", test_slash_command_exists),
    ]

    results = {}

    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ {test_name}测试出现异常: {e}")
            results[test_name] = False

    print("\n" + "=" * 50)
    print("📊 验证结果汇总:")

    passed = 0
    total = len(results)

    for test_name, result in results.items():
        status = "✅ 通过" if result else "❌ 失败"
        print(f"   {test_name}: {status}")
        if result:
            passed += 1

    print(f"\n🎯 总体结果: {passed}/{total} 项测试通过")

    if passed == total:
        print("🎉 所有验证项目都通过了！")
        print("\n📋 使用方法:")
        print("   1. 重启Claude Code以加载MCP服务器")
        print("   2. 使用 /mcp deepseek ask '你的问题' 进行测试")
        print("   3. 使用 /mcp deepseek analyze 000042 进行股票分析")
    else:
        print("⚠️  部分验证未通过，请检查相关配置")
        print("\n🔧 故障排除:")
        if not results.get("环境变量"):
            print("   - 设置 DEEPSEEK_API_KEY 环境变量")
        if not results.get("MCP服务器配置"):
            print("   - 检查 claude_desktop_config.json 配置")
        if not results.get("DeepSeek模块"):
            print("   - 确保 deepseek_mcp_integration.py 文件存在且可导入")

    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)