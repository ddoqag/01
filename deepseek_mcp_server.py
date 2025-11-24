#!/usr/bin/env python3
"""
DeepSeek MCP服务器
提供三个主要工具：
1. deepseek_ask - 通用提问接口
2. deepseek_analyze_stock - 股票分析
3. deepseek_market_analysis - 市场分析
"""

import json
import sys
import asyncio
import subprocess
import os
from pathlib import Path

# 添加当前目录到Python路径
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

try:
    from typing import Dict, Any, List, Optional
    from dataclasses import dataclass
except ImportError:
    # 如果没有typing模块，使用基本类型
    Dict = dict
    Any = object
    List = list
    Optional = type(None)

    def dataclass(cls):
        return cls


@dataclass
class MCPTool:
    """MCP工具定义"""
    name: str
    description: str
    input_schema: Dict[str, Any]


class DeepSeekMCPServer:
    def __init__(self):
        self.tools = [
            MCPTool(
                name="deepseek_ask",
                description="向DeepSeek AI提出通用问题",
                input_schema={
                    "type": "object",
                    "properties": {
                        "question": {
                            "type": "string",
                            "description": "要向DeepSeek AI提出的问题"
                        }
                    },
                    "required": ["question"]
                }
            ),
            MCPTool(
                name="deepseek_analyze_stock",
                description="分析指定股票代码",
                input_schema={
                    "type": "object",
                    "properties": {
                        "stock_code": {
                            "type": "string",
                            "description": "股票代码（如000042）"
                        }
                    },
                    "required": ["stock_code"]
                }
            ),
            MCPTool(
                name="deepseek_market_analysis",
                description="进行市场分析",
                input_schema={
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "市场分析查询内容"
                        }
                    },
                    "required": ["query"]
                }
            )
        ]

    async def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """处理MCP请求"""
        method = request.get("method")

        if method == "initialize":
            return {
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {}
                    },
                    "serverInfo": {
                        "name": "deepseek-mcp-server",
                        "version": "1.0.0"
                    }
                }
            }

        elif method == "tools/list":
            return {
                "result": {
                    "tools": [
                        {
                            "name": tool.name,
                            "description": tool.description,
                            "inputSchema": tool.input_schema
                        }
                        for tool in self.tools
                    ]
                }
            }

        elif method == "tools/call":
            return await self.handle_tool_call(request.get("params", {}))

        else:
            return {
                "error": {
                    "code": -32601,
                    "message": f"Method not found: {method}"
                }
            }

    async def handle_tool_call(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """处理工具调用"""
        tool_name = params.get("name")
        arguments = params.get("arguments", {})

        try:
            if tool_name == "deepseek_ask":
                result = await self.deepseek_ask(arguments.get("question", ""))
            elif tool_name == "deepseek_analyze_stock":
                result = await self.deepseek_analyze_stock(arguments.get("stock_code", ""))
            elif tool_name == "deepseek_market_analysis":
                result = await self.deepseek_market_analysis(arguments.get("query", ""))
            else:
                return {
                    "error": {
                        "code": -32601,
                        "message": f"Unknown tool: {tool_name}"
                    }
                }

            return {
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps(result, ensure_ascii=False, indent=2)
                        }
                    ]
                }
            }

        except Exception as e:
            return {
                "error": {
                    "code": -32603,
                    "message": str(e)
                }
            }

    async def deepseek_ask(self, question: str) -> Dict[str, Any]:
        """调用DeepSeek通用提问接口"""
        try:
            # 这里调用您现有的deepseek_mcp_integration模块
            from deepseek_mcp_integration import create_efficient_wrapper

            deepseek = create_efficient_wrapper()
            result = deepseek.ask(question)

            return {
                "tool": "deepseek_ask",
                "question": question,
                "result": result,
                "success": True
            }
        except Exception as e:
            return {
                "tool": "deepseek_ask",
                "question": question,
                "error": str(e),
                "success": False
            }

    async def deepseek_analyze_stock(self, stock_code: str) -> Dict[str, Any]:
        """调用DeepSeek股票分析接口"""
        try:
            from deepseek_mcp_integration import create_efficient_wrapper

            deepseek = create_efficient_wrapper()
            result = deepseek.analyze(stock_code)

            return {
                "tool": "deepseek_analyze_stock",
                "stock_code": stock_code,
                "result": result,
                "success": True
            }
        except Exception as e:
            return {
                "tool": "deepseek_analyze_stock",
                "stock_code": stock_code,
                "error": str(e),
                "success": False
            }

    async def deepseek_market_analysis(self, query: str) -> Dict[str, Any]:
        """调用DeepSeek市场分析接口"""
        try:
            from deepseek_mcp_integration import create_efficient_wrapper

            deepseek = create_efficient_wrapper()
            # 假设market_analysis方法是分析市场查询
            result = deepseek.ask(f"市场分析：{query}")

            return {
                "tool": "deepseek_market_analysis",
                "query": query,
                "result": result,
                "success": True
            }
        except Exception as e:
            return {
                "tool": "deepseek_market_analysis",
                "query": query,
                "error": str(e),
                "success": False
            }


async def main():
    """MCP服务器主循环"""
    server = DeepSeekMCPServer()

    try:
        while True:
            # 从stdin读取JSON-RPC请求
            line = sys.stdin.readline()
            if not line:
                break

            try:
                request = json.loads(line.strip())
                response = await server.handle_request(request)

                # 添加JSON-RPC响应ID
                if "id" in request:
                    response["id"] = request["id"]

                # 输出响应到stdout
                print(json.dumps(response, ensure_ascii=False), flush=True)

            except json.JSONDecodeError as e:
                error_response = {
                    "jsonrpc": "2.0",
                    "error": {
                        "code": -32700,
                        "message": f"Parse error: {str(e)}"
                    }
                }
                print(json.dumps(error_response), flush=True)

    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"Server error: {e}", file=sys.stderr)


if __name__ == "__main__":
    asyncio.run(main())