#!/usr/bin/env python3
"""
智谱AI MCP服务器 - 基于HTTP API
提供智谱AI GLM模型的对话和分析功能
"""

import json
import sys
import asyncio
import subprocess
import os
import requests
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from urllib.parse import urljoin, urlparse, urlunparse


@dataclass
class MCPTool:
    """MCP工具定义"""
    name: str
    description: str
    input_schema: Dict[str, Any]


class ZhipuMCPServer:
    def __init__(self):
        self.api_key = os.getenv('Z_AI_API_KEY')
        self.base_url = "https://open.bigmodel.cn/api/paas/v4"
        self.mode = os.getenv('Z_AI_MODE', 'ZHIPU')

        if not self.api_key:
            raise ValueError("Z_AI_API_KEY environment variable is required")

        self.tools = [
            MCPTool(
                name="zhipu_chat",
                description="使用智谱AI GLM模型进行对话问答",
                input_schema={
                    "type": "object",
                    "properties": {
                        "message": {
                            "type": "string",
                            "description": "要发送给GLM模型的消息"
                        },
                        "model": {
                            "type": "string",
                            "description": "使用的模型名称 (默认: glm-4.6)",
                            "default": "glm-4.6"
                        },
                        "temperature": {
                            "type": "number",
                            "description": "温度参数 (0.0-1.0，默认: 0.7)",
                            "default": 0.7,
                            "minimum": 0.0,
                            "maximum": 1.0
                        },
                        "max_tokens": {
                            "type": "integer",
                            "description": "最大token数 (默认: 1024)",
                            "default": 1024,
                            "minimum": 1,
                            "maximum": 4096
                        }
                    },
                    "required": ["message"]
                }
            ),
            MCPTool(
                name="zhipu_analyze",
                description="使用智谱AI进行文本分析和总结",
                input_schema={
                    "type": "object",
                    "properties": {
                        "text": {
                            "type": "string",
                            "description": "要分析的文本内容"
                        },
                        "analysis_type": {
                            "type": "string",
                            "description": "分析类型: summary, sentiment, keywords, extract",
                            "default": "summary"
                        },
                        "model": {
                            "type": "string",
                            "description": "使用的模型名称 (默认: glm-4.6)",
                            "default": "glm-4.6"
                        }
                    },
                    "required": ["text"]
                }
            )
        ]

    async def call_zhipu_api(self, messages: List[Dict], model: str = "glm-4.6",
                           temperature: float = 0.7, max_tokens: int = 1024) -> Dict[str, Any]:
        """调用智谱AI API"""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }

            data = {
                "model": model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens
            }

            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=data,
                timeout=30
            )

            if response.status_code == 200:
                return response.json()
            else:
                error_msg = f"API调用失败: {response.status_code} - {response.text}"
                return {"error": error_msg}

        except Exception as e:
            return {"error": str(e)}

    async def handle_tool_call(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """处理工具调用"""
        try:
            if tool_name == "zhipu_chat":
                message = arguments["message"]
                model = arguments.get("model", "glm-4.6")
                temperature = arguments.get("temperature", 0.7)
                max_tokens = arguments.get("max_tokens", 1024)

                messages = [{"role": "user", "content": message}]
                result = await self.call_zhipu_api(messages, model, temperature, max_tokens)

                if "error" in result:
                    return {"error": result["error"]}

                content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
                return {
                    "response": content,
                    "model": model,
                    "usage": result.get("usage", {})
                }

            elif tool_name == "zhipu_analyze":
                text = arguments["text"]
                analysis_type = arguments.get("analysis_type", "summary")
                model = arguments.get("model", "glm-4.6")

                analysis_prompts = {
                    "summary": f"请对以下文本进行简洁的总结：\n\n{text}",
                    "sentiment": f"请分析以下文本的情感倾向（积极/消极/中性）：\n\n{text}",
                    "keywords": f"请从以下文本中提取关键词：\n\n{text}",
                    "extract": f"请从以下文本中提取关键信息：\n\n{text}"
                }

                prompt = analysis_prompts.get(analysis_type, analysis_prompts["summary"])
                messages = [{"role": "user", "content": prompt}]

                result = await self.call_zhipu_api(messages, model)

                if "error" in result:
                    return {"error": result["error"]}

                content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
                return {
                    "analysis": content,
                    "analysis_type": analysis_type,
                    "model": model,
                    "usage": result.get("usage", {})
                }

            else:
                return {"error": f"Unknown tool: {tool_name}"}

        except Exception as e:
            return {"error": str(e)}

    async def run(self):
        """运行MCP服务器"""
        try:
            # 发送初始化信息
            init_message = {
                "jsonrpc": "2.0",
                "id": 1,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {}
                    },
                    "serverInfo": {
                        "name": "zhipu-mcp-server",
                        "version": "1.0.0"
                    }
                }
            }
            print(json.dumps(init_message), flush=True)

            # 主循环
            while True:
                try:
                    line = input()
                    if not line:
                        continue

                    request = json.loads(line)

                    if request.get("method") == "tools/list":
                        tools_list = {
                            "jsonrpc": "2.0",
                            "id": request.get("id"),
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
                        print(json.dumps(tools_list), flush=True)

                    elif request.get("method") == "tools/call":
                        params = request.get("params", {})
                        tool_name = params.get("name")
                        arguments = params.get("arguments", {})

                        result = await self.handle_tool_call(tool_name, arguments)

                        response = {
                            "jsonrpc": "2.0",
                            "id": request.get("id"),
                            "result": {
                                "content": [
                                    {
                                        "type": "text",
                                        "text": json.dumps(result, ensure_ascii=False)
                                    }
                                ]
                            }
                        }
                        print(json.dumps(response, ensure_ascii=False), flush=True)

                except EOFError:
                    break
                except Exception as e:
                    error_response = {
                        "jsonrpc": "2.0",
                        "id": request.get("id") if 'request' in locals() else None,
                        "error": {
                            "code": -1,
                            "message": str(e)
                        }
                    }
                    print(json.dumps(error_response, ensure_ascii=False), flush=True)

        except KeyboardInterrupt:
            pass


async def main():
    try:
        server = ZhipuMCPServer()
        await server.run()
    except Exception as e:
        print(f"Server error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())