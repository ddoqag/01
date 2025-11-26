#!/usr/bin/env python3
"""
MCP客户端测试工具
"""

import json
import sys
import os
import asyncio
from pathlib import Path

# 设置环境变量
os.environ['PYTHONIOENCODING'] = 'utf-8'
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from web_scraping_mcp_server import WebScrapingMCPServer

async def test_mcp_server():
    """测试MCP服务器功能"""
    print("🧪 测试Web Scraping MCP服务器...")

    server = WebScrapingMCPServer()

    # 测试初始化
    print("\n1. 测试服务器初始化...")
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

    response = await server.handle_request(init_request)
    print(f"   初始化响应: {json.dumps(response, indent=2, ensure_ascii=False)}")

    # 测试工具列表
    print("\n2. 测试工具列表...")
    tools_request = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/list"
    }

    response = await server.handle_request(tools_request)
    tools = response.get("result", {}).get("tools", [])
    print(f"   发现 {len(tools)} 个工具:")
    for tool in tools:
        print(f"   - {tool['name']}: {tool['description']}")

    # 测试网页抓取工具
    print("\n3. 测试网页抓取工具...")
    tool_call_request = {
        "jsonrpc": "2.0",
        "id": 3,
        "method": "tools/call",
        "params": {
            "name": "web_fetch",
            "arguments": {
                "url": "https://httpbin.org/html",
                "extract_links": True,
                "extract_images": False
            }
        }
    }

    response = await server.handle_request(tool_call_request)
    if "result" in response:
        result = json.loads(response["result"]["content"][0]["text"])
        print(f"   ✅ 网页抓取成功!")
        print(f"   标题: {result.get('title', '无')}")
        print(f"   状态码: {result.get('status_code', '未知')}")
        print(f"   内容长度: {result.get('content_length', 0)} 字符")
        if result.get('success'):
            print(f"   ✅ 功能正常工作")
        else:
            print(f"   ❌ 抓取失败: {result.get('error', '未知错误')}")
    else:
        print(f"   ❌ 工具调用失败: {response}")

    print("\n🎉 MCP服务器测试完成!")

if __name__ == "__main__":
    import os
    asyncio.run(test_mcp_server())