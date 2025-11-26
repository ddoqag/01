#!/usr/bin/env python3
"""
MCP服务器管理器
提供统一的MCP服务器管理和交互接口
"""

import json
import sys
import os
import subprocess
import asyncio
from pathlib import Path

# 设置环境变量
os.environ['PYTHONIOENCODING'] = 'utf-8'

class MCPManager:
    def __init__(self):
        self.config_path = Path(__file__).parent / "mcp_config.json"
        self.current_dir = Path(__file__).parent
        self.load_config()

    def load_config(self):
        """加载MCP配置"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
        except FileNotFoundError:
            self.config = {"mcpServers": {}}

    def save_config(self):
        """保存MCP配置"""
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=2, ensure_ascii=False)

    def list_servers(self):
        """列出所有MCP服务器"""
        print("\n📋 可用的MCP服务器:")
        print("=" * 60)

        for name, server in self.config.get("mcpServers", {}).items():
            status = server.get("status", "❓ 未知")
            description = server.get("description", "无描述")
            tools = server.get("tools", [])

            print(f"\n🔧 {name}")
            print(f"   状态: {status}")
            print(f"   描述: {description}")
            print(f"   工具: {', '.join(tools)}")

            usage = server.get("usage", "")
            if usage:
                print(f"   用法: {usage}")

    def test_server(self, server_name):
        """测试指定MCP服务器"""
        if server_name not in self.config.get("mcpServers", {}):
            print(f"❌ 服务器 '{server_name}' 不存在")
            return False

        server = self.config["mcpServers"][server_name]
        print(f"\n🧪 测试MCP服务器: {server_name}")
        print("=" * 40)

        if server_name == "web-scraping":
            return self.test_web_scraping_server()
        elif server_name == "context7":
            return self.test_context7_server()
        elif server_name == "deepseek":
            return self.test_deepseek_server()
        else:
            print(f"❌ 不支持测试服务器类型: {server_name}")
            return False

    def test_web_scraping_server(self):
        """测试Web Scraping服务器"""
        try:
            cmd = [
                str(self.current_dir / "python_portable" / "python.exe"),
                "test_mcp_client.py"
            ]

            result = subprocess.run(cmd, capture_output=True, text=True,
                                  cwd=self.current_dir, timeout=60)

            if result.returncode == 0:
                print("✅ Web Scraping MCP服务器测试成功")
                print("📊 测试结果:")
                # 解析输出中的关键信息
                output_lines = result.stdout.split('\n')
                for line in output_lines:
                    if '✅' in line or '发现' in line or '工具' in line:
                        print(f"   {line}")
                return True
            else:
                print(f"❌ Web Scraping MCP服务器测试失败")
                print(f"   错误: {result.stderr}")
                return False

        except Exception as e:
            print(f"❌ 测试过程出错: {e}")
            return False

    def test_context7_server(self):
        """测试Context7服务器"""
        try:
            # 尝试调用Context7工具
            from mcp__context7 import resolve_library_id

            result = resolve_library_id("python")
            print("✅ Context7 MCP服务器测试成功")
            print(f"   Python库查询结果: 找到 {len(result.get('available_libraries', []))} 个相关库")
            return True

        except Exception as e:
            print(f"❌ Context7 MCP服务器测试失败: {e}")
            return False

    def test_deepseek_server(self):
        """测试DeepSeek服务器"""
        try:
            # 检查API密钥
            api_key = os.getenv("DEEPSEEK_API_KEY")
            if not api_key:
                print("❌ DeepSeek服务器测试失败: 未设置DEEPSEEK_API_KEY环境变量")
                return False

            import requests

            headers = {
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json'
            }

            data = {
                "model": "deepseek-chat",
                "messages": [{"role": "user", "content": "测试"}],
                "max_tokens": 10
            }

            response = requests.post("https://api.deepseek.com/v1/chat/completions",
                                   headers=headers, json=data, timeout=10)

            if response.status_code == 200:
                print("✅ DeepSeek MCP服务器测试成功")
                return True
            else:
                print(f"❌ DeepSeek MCP服务器测试失败: API密钥无效")
                return False

        except Exception as e:
            print(f"❌ DeepSeek服务器测试失败: {e}")
            return False

    def get_status(self):
        """获取所有服务器状态"""
        print("\n📊 MCP服务器状态总览:")
        print("=" * 60)

        working = 0
        total = len(self.config.get("mcpServers", {}))

        for name, server in self.config.get("mcpServers", {}).items():
            status = server.get("status", "❓ 未知")
            print(f"   {name}: {status}")
            if "✅" in status:
                working += 1

        print(f"\n📈 总计: {working}/{total} 个服务器正常工作")

def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("""
🔧 MCP服务器管理器

用法:
  python mcp_manager.py <command> [arguments]

命令:
  list                    列出所有MCP服务器
  status                  显示服务器状态总览
  test <server_name>      测试指定服务器
  test-all                测试所有服务器

示例:
  python mcp_manager.py list
  python mcp_manager.py test web-scraping
  python mcp_manager.py status
        """)
        return

    manager = MCPManager()
    command = sys.argv[1]

    if command == "list":
        manager.list_servers()
    elif command == "status":
        manager.get_status()
    elif command == "test":
        if len(sys.argv) < 3:
            print("❌ 请指定要测试的服务器名称")
            return
        server_name = sys.argv[2]
        manager.test_server(server_name)
    elif command == "test-all":
        print("\n🔄 测试所有MCP服务器...")
        for server_name in manager.config.get("mcpServers", {}):
            manager.test_server(server_name)
            print()
    else:
        print(f"❌ 未知命令: {command}")

if __name__ == "__main__":
    main()