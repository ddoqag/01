#!/usr/bin/env python3
"""
修复后的DZH DeepSeek MCP服务器
使用智能解析器处理多种响应格式
"""

import json
import sys
import asyncio
import os
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

# 添加当前目录到Python路径
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from smart_dzh_parser import SmartDZHParser

@dataclass
class MCPTool:
    """MCP工具定义"""
    name: str
    description: str
    input_schema: Dict[str, Any]

class FixedDZHDeepSeekMCPServer:
    def __init__(self):
        self.parser = SmartDZHParser()
        self.tools = [
            MCPTool(
                name="deepseek_ask",
                description="向DZH DeepSeek AI提出通用问题",
                input_schema={
                    "type": "object",
                    "properties": {
                        "question": {
                            "type": "string",
                            "description": "要向DZH DeepSeek AI提出的问题"
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
                        "name": "fixed-dzh-deepseek-mcp-server",
                        "version": "2.0.0"
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
        """DZH通用问答"""
        try:
            # 使用智能解析器处理
            result = self.parser.ask_with_deepseek_style(question)

            if result["success"]:
                return {
                    "tool": "deepseek_ask",
                    "question": question,
                    "response": result["response"],
                    "method": result["method"],
                    "confidence": result.get("confidence", 0.5),
                    "success": True
                }
            else:
                return {
                    "tool": "deepseek_ask",
                    "question": question,
                    "error": result.get("error", "未知错误"),
                    "success": False
                }

        except Exception as e:
            return {
                "tool": "deepseek_ask",
                "question": question,
                "error": str(e),
                "success": False
            }

    async def deepseek_analyze_stock(self, stock_code: str) -> Dict[str, Any]:
        """股票分析"""
        question = f"请分析股票代码{stock_code}的基本面、技术面和投资价值，包括公司概况、财务状况、行业地位和风险提示。"

        try:
            result = self.parser.ask_with_deepseek_style(question)

            if result["success"]:
                return {
                    "tool": "deepseek_analyze_stock",
                    "stock_code": stock_code,
                    "response": result["response"],
                    "method": result["method"],
                    "confidence": result.get("confidence", 0.5),
                    "success": True
                }
            else:
                return {
                    "tool": "deepseek_analyze_stock",
                    "stock_code": stock_code,
                    "error": result.get("error", "股票分析失败"),
                    "success": False
                }

        except Exception as e:
            return {
                "tool": "deepseek_analyze_stock",
                "stock_code": stock_code,
                "error": str(e),
                "success": False
            }

    async def deepseek_market_analysis(self, query: str) -> Dict[str, Any]:
        """市场分析"""
        question = f"请进行以下市场分析：{query}。请包含市场趋势、关键因素、投资建议等内容。"

        try:
            result = self.parser.ask_with_deepseek_style(question)

            if result["success"]:
                return {
                    "tool": "deepseek_market_analysis",
                    "query": query,
                    "response": result["response"],
                    "method": result["method"],
                    "confidence": result.get("confidence", 0.5),
                    "success": True
                }
            else:
                return {
                    "tool": "deepseek_market_analysis",
                    "query": query,
                    "error": result.get("error", "市场分析失败"),
                    "success": False
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
    server = FixedDZHDeepSeekMCPServer()

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