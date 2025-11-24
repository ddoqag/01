#!/usr/bin/env python3
"""
更新 Claude 全局配置文件，添加 MCP 服务器配置
"""

import json
import os
from pathlib import Path

def update_claude_config():
    # 配置文件路径
    config_path = Path("/c/Users/ddo/.claude.json")

    # 读取现有配置
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)

    # 定义 MCP 服务器配置
    mcp_servers = {
        "deepseek-mcp": {
            "command": "python",
            "args": ["C:\\Users\\ddo\\AppData\\Roaming\\npm\\deepseek_mcp_server.py"],
            "description": "DeepSeek AI 集成服务器 - 提供通用提问、股票分析和市场分析功能"
        },
        "sugar-mcp": {
            "command": "node",
            "args": ["C:\\Users\\ddo\\AppData\\Roaming\\npm\\mcp-tools\\sugar-mcp.js"],
            "description": "Sugar DevOps MCP 服务器 - 提供 DevOps 相关工具"
        },
        "cloudbase": {
            "command": "npx",
            "args": ["@cloudbase/cloudbase-mcp"],
            "description": "CloudBase MCP 服务器 - 腾讯云云开发工具"
        }
    }

    # 更新项目配置
    project_path = "C:\\Users\\ddo\\AppData\\Roaming\\npm"
    if project_path in config["projects"]:
        config["projects"][project_path]["mcpServers"] = mcp_servers
        config["projects"][project_path]["enabledMcpjsonServers"] = ["deepseek-mcp", "sugar-mcp"]
        config["projects"][project_path]["disabledMcpjsonServers"] = []

    # 备份原配置
    backup_path = config_path.with_suffix('.json.backup_updated')
    with open(backup_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)

    # 写入更新后的配置
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)

    print(f"✅ Claude 配置已更新")
    print(f"📁 配置文件: {config_path}")
    print(f"💾 备份文件: {backup_path}")
    print(f"🔧 已添加 {len(mcp_servers)} 个 MCP 服务器:")
    for name, server_config in mcp_servers.items():
        print(f"  - {name}: {server_config['description']}")

if __name__ == "__main__":
    update_claude_config()