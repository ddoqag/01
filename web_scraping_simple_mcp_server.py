#!/usr/bin/env python3
"""
简化版网页抓取MCP服务器
提供基本的网页内容提取功能（不依赖外部包）
"""

import json
import sys
import asyncio
import subprocess
import os
import re
from pathlib import Path
from urllib.parse import urljoin, urlparse, urlunparse
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

# 添加当前目录到Python路径
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))


@dataclass
class MCPTool:
    """MCP工具定义"""
    name: str
    description: str
    input_schema: Dict[str, Any]


class SimpleWebScrapingMCPServer:
    def __init__(self):
        self.tools = [
            MCPTool(
                name="web_check",
                description="检查网页可访问性和基本信息",
                input_schema={
                    "type": "object",
                    "properties": {
                        "url": {
                            "type": "string",
                            "description": "要检查的网页URL"
                        }
                    },
                    "required": ["url"]
                }
            ),
            MCPTool(
                name="web_simple_fetch",
                description="获取网页原始HTML内容",
                input_schema={
                    "type": "object",
                    "properties": {
                        "url": {
                            "type": "string",
                            "description": "要获取的网页URL"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "返回内容的字符数限制",
                            "default": 5000
                        }
                    },
                    "required": ["url"]
                }
            ),
            MCPTool(
                name="web_extract_urls",
                description="从HTML内容中提取所有URL链接",
                input_schema={
                    "type": "object",
                    "properties": {
                        "url": {
                            "type": "string",
                            "description": "要分析的网页URL"
                        }
                    },
                    "required": ["url"]
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
                        "name": "simple-web-scraping-mcp-server",
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
            if tool_name == "web_check":
                result = await self.web_check(arguments)
            elif tool_name == "web_simple_fetch":
                result = await self.web_simple_fetch(arguments)
            elif tool_name == "web_extract_urls":
                result = await self.web_extract_urls(arguments)
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

    async def web_check(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """检查网页可访问性"""
        url = args["url"]

        try:
            # 使用curl命令获取网页
            curl_cmd = [
                "curl", "-s", "-L",
                "-A", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "--connect-timeout", "10",
                "--max-time", "30",
                url
            ]

            result = subprocess.run(
                curl_cmd,
                capture_output=True,
                text=True,
                timeout=35
            )

            if result.returncode == 0:
                content = result.stdout

                # 使用正则表达式提取基本信息
                title_match = re.search(r'<title[^>]*>(.*?)</title>', content, re.IGNORECASE | re.DOTALL)
                title = title_match.group(1).strip() if title_match else "未找到标题"

                # 提取meta描述
                desc_match = re.search(r'<meta[^>]*name=["\']description["\'][^>]*content=["\']([^"\']*)["\']', content, re.IGNORECASE)
                description = desc_match.group(1).strip() if desc_match else "未找到描述"

                return {
                    "tool": "web_check",
                    "url": url,
                    "accessible": True,
                    "title": title,
                    "description": description,
                    "content_length": len(content),
                    "success": True
                }
            else:
                return {
                    "tool": "web_check",
                    "url": url,
                    "accessible": False,
                    "error": f"curl返回错误: {result.returncode}",
                    "stderr": result.stderr,
                    "success": False
                }

        except subprocess.TimeoutExpired:
            return {
                "tool": "web_check",
                "url": url,
                "accessible": False,
                "error": "请求超时",
                "success": False
            }
        except Exception as e:
            return {
                "tool": "web_check",
                "url": url,
                "accessible": False,
                "error": str(e),
                "success": False
            }

    async def web_simple_fetch(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """获取网页原始HTML内容"""
        url = args["url"]
        limit = args.get("limit", 5000)

        try:
            # 使用curl命令获取网页
            curl_cmd = [
                "curl", "-s", "-L",
                "-A", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "--connect-timeout", "10",
                "--max-time", "30",
                url
            ]

            result = subprocess.run(
                curl_cmd,
                capture_output=True,
                text=True,
                timeout=35
            )

            if result.returncode == 0:
                content = result.stdout

                # 限制内容长度
                if len(content) > limit:
                    content = content[:limit] + "\n\n... [内容已截断]"

                # 提取标题
                title_match = re.search(r'<title[^>]*>(.*?)</title>', content, re.IGNORECASE | re.DOTALL)
                title = title_match.group(1).strip() if title_match else "未找到标题"

                return {
                    "tool": "web_simple_fetch",
                    "url": url,
                    "title": title,
                    "content": content,
                    "original_length": len(result.stdout),
                    "success": True
                }
            else:
                return {
                    "tool": "web_simple_fetch",
                    "url": url,
                    "error": f"curl返回错误: {result.returncode}",
                    "stderr": result.stderr,
                    "success": False
                }

        except Exception as e:
            return {
                "tool": "web_simple_fetch",
                "url": url,
                "error": str(e),
                "success": False
            }

    async def web_extract_urls(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """从HTML内容中提取URL链接"""
        url = args["url"]

        try:
            # 使用curl命令获取网页
            curl_cmd = [
                "curl", "-s", "-L",
                "-A", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "--connect-timeout", "10",
                "--max-time", "30",
                url
            ]

            result = subprocess.run(
                curl_cmd,
                capture_output=True,
                text=True,
                timeout=35
            )

            if result.returncode == 0:
                content = result.stdout

                # 使用正则表达式提取链接
                url_pattern = r'<a[^>]*href=["\']([^"\']+)["\'][^>]*>(.*?)</a>'
                matches = re.findall(url_pattern, content, re.IGNORECASE | re.DOTALL)

                links = []
                for href, text in matches:
                    # 转换为绝对URL
                    absolute_url = urljoin(url, href)
                    text = re.sub(r'<[^>]+>', '', text).strip()  # 移除HTML标签

                    if absolute_url.startswith(('http://', 'https://')):
                        links.append({
                            "url": absolute_url,
                            "text": text[:100],  # 限制文本长度
                            "domain": urlparse(absolute_url).netloc
                        })

                # 去重并限制数量
                seen_urls = set()
                unique_links = []
                for link in links:
                    if link["url"] not in seen_urls:
                        seen_urls.add(link["url"])
                        unique_links.append(link)
                        if len(unique_links) >= 50:  # 限制链接数量
                            break

                return {
                    "tool": "web_extract_urls",
                    "url": url,
                    "total_links_found": len(matches),
                    "unique_links": len(unique_links),
                    "links": unique_links,
                    "success": True
                }
            else:
                return {
                    "tool": "web_extract_urls",
                    "url": url,
                    "error": f"curl返回错误: {result.returncode}",
                    "success": False
                }

        except Exception as e:
            return {
                "tool": "web_extract_urls",
                "url": url,
                "error": str(e),
                "success": False
            }


async def main():
    """MCP服务器主循环"""
    server = SimpleWebScrapingMCPServer()

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