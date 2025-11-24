#!/usr/bin/env python3
"""
DeepSeek MCP集成模块
提供与DeepSeek API交互的封装函数
"""

import json
import sys
import os
from pathlib import Path

# 添加当前目录到Python路径
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

try:
    from typing import Dict, Any, Optional
    from dataclasses import dataclass
    import requests
except ImportError as e:
    print(f"导入错误: {e}", file=sys.stderr)
    # 如果没有某些模块，使用基本类型
    Dict = dict
    Any = object
    Optional = type(None)

    def dataclass(cls):
        return cls

    # 如果没有requests，定义一个简单的替代
    class MockRequests:
        class Session:
            def __init__(self):
                self.headers = {}

            def update(self, headers):
                self.headers.update(headers)

            def post(self, url, json=None):
                class MockResponse:
                    def raise_for_status(self):
                        pass

                    def json(self):
                        return {"error": "requests模块未安装"}

                return MockResponse()

        def Session(self):
            return self.Session()

    requests = MockRequests()


@dataclass
class DeepSeekConfig:
    """DeepSeek配置"""
    api_key: str
    base_url: str = "https://api.deepseek.com/v1"
    model: str = "deepseek-chat"
    max_tokens: int = 2000
    temperature: float = 0.7


class DeepSeekMCPClient:
    """DeepSeek MCP客户端"""

    def __init__(self, config: Optional[DeepSeekConfig] = None):
        if config is None:
            api_key = os.getenv("DEEPSEEK_API_KEY")
            if not api_key:
                raise ValueError("DEEPSEEK_API_KEY环境变量未设置")
            config = DeepSeekConfig(api_key=api_key)

        self.config = config
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {config.api_key}",
            "Content-Type": "application/json"
        })

    def ask(self, question: str) -> Dict[str, Any]:
        """通用问题回答"""
        try:
            payload = {
                "model": self.config.model,
                "messages": [
                    {"role": "user", "content": question}
                ],
                "max_tokens": self.config.max_tokens,
                "temperature": self.config.temperature
            }

            response = self.session.post(
                f"{self.config.base_url}/chat/completions",
                json=payload
            )
            response.raise_for_status()

            data = response.json()

            return {
                "success": True,
                "content_type": "text",
                "answer": data["choices"][0]["message"]["content"],
                "usage": data.get("usage", {}),
                "extracted_info": {
                    "has_answer": True,
                    "question": question,
                    "model": self.config.model
                }
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "extracted_info": {
                    "has_answer": False,
                    "question": question,
                    "error": str(e)
                }
            }

    def analyze(self, stock_code: str) -> Dict[str, Any]:
        """股票分析"""
        question = f"请分析股票代码{stock_code}的基本面、技术面和投资价值，包括公司概况、财务状况、行业地位和风险提示。"

        result = self.ask(question)

        # 添加股票特定信息
        if result.get("success"):
            result["extracted_info"]["stock_code"] = stock_code
            result["extracted_info"]["analysis_type"] = "股票分析"

        return result

    def market_analysis(self, query: str) -> Dict[str, Any]:
        """市场分析"""
        question = f"请进行以下市场分析：{query}。请包含市场趋势、关键因素、投资建议等内容。"

        result = self.ask(question)

        # 添加市场分析特定信息
        if result.get("success"):
            result["extracted_info"]["analysis_type"] = "市场分析"
            result["extracted_info"]["market_query"] = query

        return result


class DeepSeekMCPServer:
    """DeepSeek MCP服务器（简化版，用于测试）"""

    def __init__(self):
        try:
            self.client = DeepSeekMCPClient()
        except ValueError as e:
            print(f"警告: {e}", file=sys.stderr)
            self.client = None

    def get_available_tools(self) -> list:
        """获取可用工具列表"""
        return [
            {
                "name": "deepseek_ask",
                "description": "向DeepSeek AI提出通用问题",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "question": {
                            "type": "string",
                            "description": "要向DeepSeek AI提出的问题"
                        }
                    },
                    "required": ["question"]
                }
            },
            {
                "name": "deepseek_analyze_stock",
                "description": "分析指定股票代码",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "stock_code": {
                            "type": "string",
                            "description": "股票代码（如000042）"
                        }
                    },
                    "required": ["stock_code"]
                }
            },
            {
                "name": "deepseek_market_analysis",
                "description": "进行市场分析",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "市场分析查询内容"
                        }
                    },
                    "required": ["query"]
                }
            }
        ]

    def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """调用工具"""
        if not self.client:
            return {
                "success": False,
                "error": "DeepSeek客户端未正确初始化，请检查API密钥配置"
            }

        try:
            if tool_name == "deepseek_ask":
                return self.client.ask(arguments.get("question", ""))
            elif tool_name == "deepseek_analyze_stock":
                return self.client.analyze(arguments.get("stock_code", ""))
            elif tool_name == "deepseek_market_analysis":
                return self.client.market_analysis(arguments.get("query", ""))
            else:
                return {
                    "success": False,
                    "error": f"未知工具: {tool_name}"
                }
        except Exception as e:
            return {
                "success": False,
                "error": f"工具调用失败: {str(e)}"
            }


def create_efficient_wrapper() -> DeepSeekMCPServer:
    """创建高效的包装器"""
    return DeepSeekMCPServer()


# 兼容性函数
def create_mcp_client() -> DeepSeekMCPClient:
    """创建MCP客户端"""
    return DeepSeekMCPClient()


def create_mcp_server() -> DeepSeekMCPServer:
    """创建MCP服务器"""
    return DeepSeekMCPServer()


# 测试代码
if __name__ == "__main__":
    # 测试工具列表
    server = create_mcp_server()
    tools = server.get_available_tools()
    print("可用工具:")
    for tool in tools:
        print(f"- {tool['name']}: {tool['description']}")

    # 测试工具调用（如果有API密钥）
    if os.getenv("DEEPSEEK_API_KEY"):
        print("\n测试工具调用:")
        result = server.call_tool("deepseek_ask", {"question": "什么是MCP？"})
        print(f"结果: {json.dumps(result, ensure_ascii=False, indent=2)}")
    else:
        print("\n未设置DEEPSEEK_API_KEY，跳过工具调用测试")