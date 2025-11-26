#!/usr/bin/env python3
"""
调试DZH响应内容
"""

import json
import sys
import requests
import urllib.parse
from pathlib import Path

def debug_response():
    """调试DZH响应"""
    settings_path = Path(__file__).parent / "settings.local.json"
    with open(settings_path, 'r', encoding='utf-8') as f:
        settings = json.load(f)

    deepseek_config = settings.get("deepseek", {})
    api_key = deepseek_config.get("api_key", "")
    base_url = deepseek_config.get("base_url", "https://f.dzh.com.cn/zswd/newask")
    tun = deepseek_config.get("tun", "dzhsp846")

    # 构建请求
    params = {
        "tun": tun,
        "token": api_key,
        "version": "1.0",
        "scene": "gg",
        "sceneName": "测试",
        "sceneCode": "TEST",
        "sceneDesc": "调试测试"
    }

    url = f"{base_url}?{urllib.parse.urlencode(params)}"
    print(f"请求URL: {url}")

    data = {
        "question": "你好，请简单介绍一下自己",
        "timestamp": "2025-11-25T13:55:00"
    }

    headers = {
        'Content-Type': 'application/json',
        'User-Agent': 'DZH-DeepSeek-Client/1.0'
    }

    response = requests.post(url, json=data, headers=headers, timeout=30)
    print(f"状态码: {response.status_code}")
    print(f"响应头: {dict(response.headers)}")
    print("\n响应内容前500字符:")
    print(response.text[:500])

if __name__ == "__main__":
    debug_response()