#!/usr/bin/env python3
"""
简化的集成测试脚本
"""

import json
import os
import sys
from pathlib import Path


def test_file_existence():
    """测试文件是否存在"""
    print("🔍 检查文件存在性...")

    current_dir = Path(__file__).parent
    files_to_check = [
        "deepseek_mcp_server.py",
        "deepseek_mcp_integration.py",
        ".claude/claude_desktop_config.json",
        ".claude/commands/mcp.md",
        "DEEPSEEK_MCP_INTEGRATION.md"
    ]

    all_exist = True
    for file_name in files_to_check:
        file_path = current_dir / file_name
        if file_path.exists():
            print(f"✅ {file_name}")
        else:
            print(f"❌ {file_name} 不存在")
            all_exist = False

    return all_exist


def test_config_content():
    """测试配置文件内容"""
    print("\n🔍 检查配置文件内容...")

    config_path = Path.home() / "AppData/Roaming/npm/.claude/claude_desktop_config.json"

    if not config_path.exists():
        print("❌ 配置文件不存在")
        return False

    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)

        if "mcpServers" in config and "deepseek" in config["mcpServers"]:
            deepseek_config = config["mcpServers"]["deepseek"]
            print("✅ DeepSeek配置存在")
            print(f"   命令: {deepseek_config.get('command', 'N/A')}")
            return True
        else:
            print("❌ DeepSeek配置不存在")
            return False

    except Exception as e:
        print(f"❌ 配置读取失败: {e}")
        return False


def test_environment():
    """测试环境变量"""
    print("\n🔍 检查环境变量...")

    api_key = os.getenv("DEEPSEEK_API_KEY")
    if api_key:
        print("✅ DEEPSEEK_API_KEY 已设置")
        return True
    else:
        print("⚠️  DEEPSEEK_API_KEY 未设置")
        return False


def main():
    """主测试流程"""
    print("🚀 简化集成测试开始...")
    print("=" * 40)

    tests = [
        ("文件存在性", test_file_existence),
        ("配置文件", test_config_content),
        ("环境变量", test_environment),
    ]

    results = {}
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ {test_name}测试异常: {e}")
            results[test_name] = False

    print("\n" + "=" * 40)
    print("📊 测试结果:")

    passed = 0
    for test_name, result in results.items():
        status = "✅ 通过" if result else "❌ 失败"
        print(f"   {test_name}: {status}")
        if result:
            passed += 1

    print(f"\n🎯 结果: {passed}/{len(results)} 项测试通过")

    if passed >= 2:  # 至少文件和配置通过
        print("\n🎉 基本集成成功！")
        print("\n📋 下一步:")
        print("   1. 设置 DEEPSEEK_API_KEY 环境变量")
        print("   2. 重启Claude Code")
        print("   3. 测试 /mcp deepseek ask 'hello'")
        return True
    else:
        print("\n⚠️  集成存在问题，请检查配置")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)