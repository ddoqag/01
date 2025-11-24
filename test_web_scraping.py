#!/usr/bin/env python3
"""
测试网页抓取MCP服务器
"""

import json
import sys
import os
from pathlib import Path

# 添加当前目录到Python路径
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

def test_imports():
    """测试模块导入"""
    try:
        import requests
        import bs4
        import html2text
        print("✅ 所有依赖模块都已安装")
        return True
    except ImportError as e:
        print(f"❌ 缺少依赖模块: {e}")
        print("请运行以下命令安装依赖:")
        print("pip install requests beautifulsoup4 html2text")
        return False

def test_server_creation():
    """测试服务器创建"""
    try:
        from web_scraping_mcp_server import WebScrapingMCPServer
        server = WebScrapingMCPServer()
        print("✅ 网页抓取MCP服务器创建成功")

        # 测试工具列表
        tools = server.tools
        print(f"✅ 可用工具数量: {len(tools)}")
        for tool in tools:
            print(f"  - {tool.name}: {tool.description}")

        return True
    except Exception as e:
        print(f"❌ 服务器创建失败: {e}")
        return False

def main():
    print("🔍 测试网页抓取MCP服务器...")
    print()

    # 测试依赖
    if not test_imports():
        return

    print()

    # 测试服务器
    if not test_server_creation():
        return

    print()
    print("🎉 网页抓取MCP服务器测试通过！")
    print()
    print("📋 可用功能:")
    print("1. web_fetch - 获取网页内容并转换为Markdown")
    print("2. web_extract_text - 提取网页中的纯文本内容")
    print("3. web_extract_links - 提取网页中的所有链接")
    print("4. web_page_info - 获取网页基本信息")
    print()
    print("🚀 使用方法:")
    print('/mcp web-scraping fetch "https://example.com"')
    print('/mcp web-scraping extract-text "https://example.com"')
    print('/mcp web-scraping extract-links "https://example.com"')
    print('/mcp web-scraping page-info "https://example.com"')

if __name__ == "__main__":
    main()