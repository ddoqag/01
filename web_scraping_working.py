#!/usr/bin/env python3
"""
工作的网页抓取MCP服务器
使用便携版Python 3.14
"""

import json
import sys
import requests
from bs4 import BeautifulSoup
import html2text

def web_fetch_test(url):
    """测试网页抓取功能"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()

        # 检测编码
        if response.encoding == 'ISO-8859-1':
            response.encoding = response.apparent_encoding

        soup = BeautifulSoup(response.text, 'html.parser')
        title = soup.find('title')
        title = title.get_text().strip() if title else "无标题"

        # 转换为Markdown
        h = html2text.HTML2Text()
        h.ignore_links = False
        h.ignore_images = False
        h.body_width = 0
        markdown_content = h.handle(response.text)

        return {
            "tool": "web_fetch_test",
            "url": url,
            "title": title,
            "status_code": response.status_code,
            "content_type": response.headers.get('content-type', ''),
            "content_length": len(markdown_content),
            "markdown_preview": markdown_content[:500] + "..." if len(markdown_content) > 500 else markdown_content,
            "success": True,
            "message": "网页抓取测试成功！"
        }

    except Exception as e:
        return {
            "tool": "web_fetch_test",
            "url": url,
            "error": str(e),
            "success": False,
            "message": "网页抓取测试失败"
        }

def main():
    """测试主函数"""
    if len(sys.argv) < 2:
        print(json.dumps({
            "error": "请提供URL参数",
            "usage": "./python_portable/python.exe web_scraping_working.py <url>",
            "example": "./python_portable/python.exe web_scraping_working.py https://httpbin.org/html"
        }, ensure_ascii=False, indent=2))
        return

    url = sys.argv[1]
    result = web_fetch_test(url)
    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()