#!/usr/bin/env python3
"""
简化版网页抓取测试
不依赖外部库，使用Python标准库
"""

import json
import sys
import urllib.request
import urllib.error
import urllib.parse
from pathlib import Path

def simple_fetch(url):
    """简单网页抓取功能"""
    try:
        # 模拟浏览器头
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=30) as response:
            content = response.read().decode('utf-8', errors='ignore')

            return {
                "tool": "simple_fetch",
                "url": url,
                "status_code": response.getcode(),
                "content_type": response.headers.get('content-type', ''),
                "content_length": len(content),
                "success": True,
                "message": "网页抓取成功（标准库版本）"
            }

    except Exception as e:
        return {
            "tool": "simple_fetch",
            "url": url,
            "error": str(e),
            "success": False,
            "message": "网页抓取失败"
        }

def main():
    """测试功能"""
    if len(sys.argv) < 2:
        print(json.dumps({
            "error": "请提供URL参数",
            "usage": "python web_scraping_simple_test.py <url>",
            "example": "python web_scraping_simple_test.py https://httpbin.org/html"
        }, ensure_ascii=False, indent=2))
        return

    url = sys.argv[1]
    result = simple_fetch(url)
    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()