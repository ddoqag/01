#!/usr/bin/env python3
"""
网页抓取MCP服务器
提供网页内容提取、解析和分析功能
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

# 使用便携版Python的依赖包
try:
    import requests
    from bs4 import BeautifulSoup
    import html2text
    HAS_DEPS = True
    print("✅ Web Scraping MCP服务器依赖包加载成功", file=sys.stderr)
except ImportError as e:
    HAS_DEPS = False
    print(f"❌ 依赖包导入失败: {e}", file=sys.stderr)


@dataclass
class MCPTool:
    """MCP工具定义"""
    name: str
    description: str
    input_schema: Dict[str, Any]


class WebScrapingMCPServer:
    def __init__(self):
        self.session = None
        self.html_converter = html2text.HTML2Text() if HAS_DEPS else None
        if self.html_converter:
            self.html_converter.ignore_links = False
            self.html_converter.ignore_images = False
            self.html_converter.body_width = 0  # 不限制行宽

        self.tools = [
            MCPTool(
                name="web_fetch",
                description="获取网页内容并转换为Markdown格式",
                input_schema={
                    "type": "object",
                    "properties": {
                        "url": {
                            "type": "string",
                            "description": "要抓取的网页URL"
                        },
                        "extract_links": {
                            "type": "boolean",
                            "description": "是否提取页面中的链接",
                            "default": True
                        },
                        "extract_images": {
                            "type": "boolean",
                            "description": "是否提取页面中的图片",
                            "default": False
                        }
                    },
                    "required": ["url"]
                }
            ),
            MCPTool(
                name="web_extract_text",
                description="提取网页中的纯文本内容",
                input_schema={
                    "type": "object",
                    "properties": {
                        "url": {
                            "type": "string",
                            "description": "要提取文本的网页URL"
                        },
                        "selector": {
                            "type": "string",
                            "description": "CSS选择器，用于提取特定元素的内容（可选）"
                        },
                        "remove_tags": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "要移除的HTML标签列表",
                            "default": ["script", "style", "nav", "footer", "header"]
                        }
                    },
                    "required": ["url"]
                }
            ),
            MCPTool(
                name="web_extract_links",
                description="提取网页中的所有链接",
                input_schema={
                    "type": "object",
                    "properties": {
                        "url": {
                            "type": "string",
                            "description": "要提取链接的网页URL"
                        },
                        "filter_domain": {
                            "type": "string",
                            "description": "过滤特定域名的链接（可选）"
                        },
                        "link_type": {
                            "type": "string",
                            "enum": ["all", "internal", "external"],
                            "description": "链接类型：all(全部), internal(内部链接), external(外部链接)",
                            "default": "all"
                        }
                    },
                    "required": ["url"]
                }
            ),
            MCPTool(
                name="web_page_info",
                description="获取网页基本信息（标题、描述、关键词等）",
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
                        "name": "web-scraping-mcp-server",
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

        if not HAS_DEPS:
            return {
                "error": {
                    "code": -32603,
                    "message": "缺少依赖包，请安装: pip install requests beautifulsoup4 html2text"
                }
            }

        try:
            if tool_name == "web_fetch":
                result = await self.web_fetch(arguments)
            elif tool_name == "web_extract_text":
                result = await self.web_extract_text(arguments)
            elif tool_name == "web_extract_links":
                result = await self.web_extract_links(arguments)
            elif tool_name == "web_page_info":
                result = await self.web_page_info(arguments)
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

    def get_session(self):
        """获取HTTP会话"""
        if self.session is None:
            self.session = requests.Session()
            self.session.headers.update({
                'User-Agent': (
                    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                    'AppleWebKit/537.36 (KHTML, like Gecko) '
                    'Chrome/91.0.4472.124 Safari/537.36'
                )
            })
        return self.session

    async def web_fetch(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """获取网页内容并转换为Markdown"""
        url = args["url"]
        extract_links = args.get("extract_links", True)
        extract_images = args.get("extract_images", False)

        try:
            session = self.get_session()
            response = session.get(url, timeout=30)
            response.raise_for_status()

            # 检测编码
            if response.encoding == 'ISO-8859-1':
                response.encoding = response.apparent_encoding

            soup = BeautifulSoup(response.text, 'html.parser')

            # 提取基本信息
            title = soup.find('title')
            title = title.get_text().strip() if title else "无标题"

            # 转换为Markdown
            markdown_content = self.html_converter.handle(response.text)

            result = {
                "tool": "web_fetch",
                "url": url,
                "title": title,
                "status_code": response.status_code,
                "content_type": response.headers.get('content-type', ''),
                "markdown": markdown_content,
                "success": True
            }

            # 提取链接
            if extract_links:
                links = self._extract_links(soup, url)
                result["links"] = links[:20]  # 限制链接数量

            # 提取图片
            if extract_images:
                images = self._extract_images(soup, url)
                result["images"] = images[:10]  # 限制图片数量

            return result

        except Exception as e:
            return {
                "tool": "web_fetch",
                "url": url,
                "error": str(e),
                "success": False
            }

    async def web_extract_text(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """提取网页中的纯文本内容"""
        url = args["url"]
        selector = args.get("selector")
        remove_tags = args.get("remove_tags", ["script", "style", "nav", "footer", "header"])

        try:
            session = self.get_session()
            response = session.get(url, timeout=30)
            response.raise_for_status()

            if response.encoding == 'ISO-8859-1':
                response.encoding = response.apparent_encoding

            soup = BeautifulSoup(response.text, 'html.parser')

            # 移除指定标签
            for tag in remove_tags:
                for element in soup.find_all(tag):
                    element.decompose()

            # 如果指定了选择器，只提取匹配的元素
            if selector:
                elements = soup.select(selector)
                text_content = '\n'.join([elem.get_text().strip() for elem in elements])
            else:
                text_content = soup.get_text()

            # 清理文本
            text_content = re.sub(r'\n\s*\n', '\n\n', text_content)
            text_content = text_content.strip()

            return {
                "tool": "web_extract_text",
                "url": url,
                "selector": selector,
                "text": text_content,
                "char_count": len(text_content),
                "success": True
            }

        except Exception as e:
            return {
                "tool": "web_extract_text",
                "url": url,
                "error": str(e),
                "success": False
            }

    async def web_extract_links(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """提取网页中的所有链接"""
        url = args["url"]
        filter_domain = args.get("filter_domain")
        link_type = args.get("link_type", "all")

        try:
            session = self.get_session()
            response = session.get(url, timeout=30)
            response.raise_for_status()

            if response.encoding == 'ISO-8859-1':
                response.encoding = response.apparent_encoding

            soup = BeautifulSoup(response.text, 'html.parser')

            links = self._extract_links(soup, url, filter_domain, link_type)

            return {
                "tool": "web_extract_links",
                "url": url,
                "filter_domain": filter_domain,
                "link_type": link_type,
                "links": links,
                "total_links": len(links),
                "success": True
            }

        except Exception as e:
            return {
                "tool": "web_extract_links",
                "url": url,
                "error": str(e),
                "success": False
            }

    async def web_page_info(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """获取网页基本信息"""
        url = args["url"]

        try:
            session = self.get_session()
            response = session.get(url, timeout=30)
            response.raise_for_status()

            if response.encoding == 'ISO-8859-1':
                response.encoding = response.apparent_encoding

            soup = BeautifulSoup(response.text, 'html.parser')

            # 提取基本信息
            title = soup.find('title')
            title = title.get_text().strip() if title else ""

            # 提取meta信息
            description = soup.find('meta', attrs={'name': 'description'})
            description = description.get('content', '') if description else ""

            keywords = soup.find('meta', attrs={'name': 'keywords'})
            keywords = keywords.get('content', '') if keywords else ""

            author = soup.find('meta', attrs={'name': 'author'})
            author = author.get('content', '') if author else ""

            # 提取Open Graph信息
            og_title = soup.find('meta', attrs={'property': 'og:title'})
            og_title = og_title.get('content', '') if og_title else ""

            og_description = soup.find('meta', attrs={'property': 'og:description'})
            og_description = og_description.get('content', '') if og_description else ""

            og_image = soup.find('meta', attrs={'property': 'og:image'})
            og_image = og_image.get('content', '') if og_image else ""

            # 统计信息
            text_content = soup.get_text()
            word_count = len(text_content.split())
            char_count = len(text_content)

            return {
                "tool": "web_page_info",
                "url": url,
                "title": title,
                "meta": {
                    "description": description,
                    "keywords": keywords,
                    "author": author
                },
                "open_graph": {
                    "title": og_title,
                    "description": og_description,
                    "image": og_image
                },
                "stats": {
                    "word_count": word_count,
                    "char_count": char_count,
                    "status_code": response.status_code,
                    "content_type": response.headers.get('content-type', '')
                },
                "success": True
            }

        except Exception as e:
            return {
                "tool": "web_page_info",
                "url": url,
                "error": str(e),
                "success": False
            }

    def _extract_links(self, soup, base_url, filter_domain=None, link_type="all"):
        """提取链接"""
        links = []
        base_domain = urlparse(base_url).netloc

        for link in soup.find_all('a', href=True):
            href = link['href']
            text = link.get_text().strip()

            # 转换为绝对URL
            absolute_url = urljoin(base_url, href)

            # 验证URL格式
            parsed = urlparse(absolute_url)
            if not parsed.scheme or not parsed.netloc:
                continue

            link_domain = parsed.netloc

            # 过滤链接类型
            if link_type == "internal" and link_domain != base_domain:
                continue
            elif link_type == "external" and link_domain == base_domain:
                continue

            # 过滤域名
            if filter_domain and filter_domain not in link_domain:
                continue

            links.append({
                "url": absolute_url,
                "text": text,
                "domain": link_domain,
                "type": "internal" if link_domain == base_domain else "external"
            })

        return links

    def _extract_images(self, soup, base_url):
        """提取图片"""
        images = []

        for img in soup.find_all('img', src=True):
            src = img['src']
            alt = img.get('alt', '')

            # 转换为绝对URL
            absolute_url = urljoin(base_url, src)

            images.append({
                "url": absolute_url,
                "alt": alt
            })

        return images


async def main():
    """MCP服务器主循环"""
    server = WebScrapingMCPServer()

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