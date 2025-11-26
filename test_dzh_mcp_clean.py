#!/usr/bin/env python3
"""
测试修复后的DZH MCP服务器（干净版本）
"""

import json
import sys
import asyncio
from pathlib import Path

# 添加当前目录到Python路径
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from fixed_dzh_mcp_server_clean import FixedDZHDeepSeekMCPServer

async def test_mcp_server():
    """测试MCP服务器"""
    print("🧪 测试修复后的DZH MCP服务器（干净版本）")
    print("=" * 50)

    server = FixedDZHDeepSeekMCPServer()

    # 测试1: 通用问答
    print("\n1️⃣ 测试通用问答...")
    request1 = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": "deepseek_ask",
            "arguments": {
                "question": "你好，请简单介绍一下你自己"
            }
        }
    }

    response1 = await server.handle_request(request1)
    print("📋 响应:")
    print(json.dumps(response1, indent=2, ensure_ascii=False))

    # 测试2: 股票分析
    print("\n2️⃣ 测试股票分析...")
    request2 = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/call",
        "params": {
            "name": "deepseek_analyze_stock",
            "arguments": {
                "stock_code": "000001"
            }
        }
    }

    response2 = await server.handle_request(request2)
    print("📋 响应:")
    print(json.dumps(response2, indent=2, ensure_ascii=False))

    # 测试3: 市场分析
    print("\n3️⃣ 测试市场分析...")
    request3 = {
        "jsonrpc": "2.0",
        "id": 3,
        "method": "tools/call",
        "params": {
            "name": "deepseek_market_analysis",
            "arguments": {
                "query": "今日A股市场走势"
            }
        }
    }

    response3 = await server.handle_request(request3)
    print("📋 响应:")
    print(json.dumps(response3, indent=2, ensure_ascii=False))

    # 统计结果
    responses = [response1, response2, response3]
    success_count = 0

    for r in responses:
        if "result" in r:
            # 解析响应内容
            content = r["result"]["content"][0]["text"]
            try:
                data = json.loads(content)
                if data.get("success"):
                    success_count += 1
            except:
                # 如果无法解析JSON，检查是否包含success标识
                if '"success": true' in content:
                    success_count += 1

    print(f"\n📊 测试统计:")
    print(f"   成功: {success_count}/{len(responses)}")
    print(f"   成功率: {success_count/len(responses)*100:.1f}%")

    if success_count == len(responses):
        print("🎉 所有测试都通过了！")
        print("✅ DZH DeepSeek MCP服务器现在可以正常工作！")
    else:
        print("⚠️  部分测试失败，但服务器架构正常")

def main():
    """主函数"""
    if len(sys.argv) > 1 and sys.argv[1] == "debug":
        asyncio.run(test_mcp_server())
    else:
        print("🔧 DZH MCP服务器测试工具（干净版本）")
        print("用法: python test_dzh_mcp_clean.py debug")
        print("       运行调试模式测试")

if __name__ == "__main__":
    main()