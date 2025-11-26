#!/usr/bin/env python3
"""
更新的MCP服务器管理器
包含修复后的DZH DeepSeek集成
"""

import json
import sys
import subprocess
import os
import time
from pathlib import Path

class MCPManager:
    def __init__(self):
        self.config_file = Path(__file__).parent / "settings.local.json"
        self.servers = {
            "context7": {
                "command": "npx",
                "args": ["-y", "@context7/context7-mcp-server"],
                "status": "enabled"
            },
            "web-search-prime": {
                "command": "npx",
                "args": ["-y", "@websearchprime/mcp-server"],
                "status": "enabled"
            },
            "web-reader": {
                "command": "npx",
                "args": ["-y", "@webreader/mcp-server"],
                "status": "enabled"
            },
            "dzh-deepseek": {
                "command": "python",
                "args": ["./python_portable/python.exe", str(Path(__file__).parent / "fixed_dzh_mcp_server_clean.py")],
                "status": "enabled"
            }
        }

    def load_config(self):
        """加载配置"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"❌ 配置文件加载失败: {e}")
        return {"mcpServers": {}}

    def save_config(self, config):
        """保存配置"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"❌ 配置文件保存失败: {e}")
            return False

    def update_dzh_config(self):
        """更新DZH配置到settings.local.json"""
        config = self.load_config()

        # 确保mcpServers节点存在
        if "mcpServers" not in config:
            config["mcpServers"] = {}

        # 添加DZH DeepSeek服务器配置
        dzh_config = {
            "command": "python",
            "args": [
                str(Path(__file__).parent / "python_portable/python.exe"),
                str(Path(__file__).parent / "fixed_dzh_mcp_server_clean.py")
            ],
            "env": {
                "PYTHONPATH": str(Path(__file__).parent),
                "PYTHONIOENCODING": "utf-8"
            }
        }

        config["mcpServers"]["dzh-deepseek"] = dzh_config

        if self.save_config(config):
            print("✅ DZH DeepSeek MCP配置已更新到settings.local.json")
            return True
        return False

    def test_server(self, server_name):
        """测试指定服务器"""
        if server_name not in self.servers:
            print(f"❌ 未知服务器: {server_name}")
            return False

        server = self.servers[server_name]
        print(f"🧪 测试服务器: {server_name}")

        if server_name == "dzh-deepseek":
            # 测试DZH服务器
            test_file = Path(__file__).parent / "test_dzh_mcp_clean.py"
            if test_file.exists():
                cmd = [
                    str(Path(__file__).parent / "python_portable/python.exe"),
                    str(test_file),
                    "debug"
                ]
                try:
                    result = subprocess.run(cmd, capture_output=True, text=True,
                                          encoding='utf-8', timeout=60)
                    if result.returncode == 0:
                        print("✅ DZH DeepSeek服务器测试通过")
                        print(result.stdout)
                        return True
                    else:
                        print("❌ DZH DeepSeek服务器测试失败")
                        print(result.stderr)
                        return False
                except Exception as e:
                    print(f"❌ 测试过程出错: {e}")
                    return False
            else:
                print("❌ 找不到测试文件")
                return False
        else:
            # 其他服务器的简单测试
            try:
                result = subprocess.run([server["command"]] + server["args"] + ["--version"],
                                       capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    print(f"✅ {server_name} 服务器正常")
                    return True
                else:
                    print(f"❌ {server_name} 服务器异常")
                    return False
            except Exception as e:
                print(f"❌ {server_name} 测试失败: {e}")
                return False

    def test_all_servers(self):
        """测试所有服务器"""
        print("🧪 测试所有MCP服务器")
        print("=" * 50)

        results = {}
        for server_name in self.servers:
            print(f"\n🔍 测试 {server_name}...")
            results[server_name] = self.test_server(server_name)
            time.sleep(2)  # 避免同时测试造成冲突

        print("\n📊 测试结果汇总:")
        print("=" * 30)
        for server_name, success in results.items():
            status = "✅ 正常" if success else "❌ 异常"
            print(f"{server_name:15} : {status}")

        total_success = sum(results.values())
        print(f"\n总计: {total_success}/{len(results)} 服务器正常工作")

        return results

    def show_status(self):
        """显示所有服务器状态"""
        config = self.load_config()
        mcp_servers = config.get("mcpServers", {})

        print("📋 MCP服务器状态")
        print("=" * 50)

        print(f"配置文件: {self.config_file}")
        print(f"已配置服务器数: {len(mcp_servers)}")
        print()

        for name, server_config in mcp_servers.items():
            print(f"🔧 {name}")
            print(f"   命令: {server_config.get('command', 'N/A')}")
            args = server_config.get('args', [])
            if args:
                print(f"   参数: {' '.join(str(arg) for arg in args[:2])}{'...' if len(args) > 2 else ''}")
            print(f"   状态: {'✅ 已配置' if self.servers.get(name, {}).get('status') == 'enabled' else '❌ 未启用'}")
            print()

def main():
    """主函数"""
    manager = MCPManager()

    if len(sys.argv) < 2:
        print("🔧 MCP服务器管理器（更新版）")
        print("用法:")
        print("  python mcp_manager_updated.py status          - 显示服务器状态")
        print("  python mcp_manager_updated.py update-dzh      - 更新DZH配置")
        print("  python mcp_manager_updated.py test <server>   - 测试指定服务器")
        print("  python mcp_manager_updated.py test-all        - 测试所有服务器")
        print()
        print("可用服务器:")
        for name in manager.servers.keys():
            print(f"  - {name}")
        return

    command = sys.argv[1]

    if command == "status":
        manager.show_status()
    elif command == "update-dzh":
        manager.update_dzh_config()
    elif command == "test":
        if len(sys.argv) < 3:
            print("❌ 请指定要测试的服务器名称")
            return
        server_name = sys.argv[2]
        manager.test_server(server_name)
    elif command == "test-all":
        manager.test_all_servers()
    else:
        print(f"❌ 未知命令: {command}")

if __name__ == "__main__":
    main()