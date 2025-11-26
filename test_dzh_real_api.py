#!/usr/bin/env python3
"""
测试DZH真实API - 集成动态Token
"""

import json
import sys
import requests
import urllib.parse
from pathlib import Path
from datetime import datetime
import re

def load_token():
    """加载DZH Token"""
    config_path = Path(__file__).parent / "settings.local.json"
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            settings = json.load(f)
            return settings.get("deepseek", {}).get("api_key", "")
    except:
        return ""

def test_dzh_api_with_token(question, stock_code=None):
    """使用动态Token测试DZH API"""
    token = load_token()

    if not token or len(token) < 20:
        print("❌ Token无效或过短")
        return None

    print(f"🔑 使用Token: {token[:20]}...({len(token)}字符)")

    # DZH官方API配置
    base_url = "https://f.dzh.com.cn/zswd/newask"
    tun = "dzhsp846"
    version = "1.0"
    scene = "gg"

    # 构建请求参数
    params = {
        "tun": tun,
        "token": token,
        "version": version,
        "scene": scene,
        "sceneName": "股票分析",
        "sceneCode": "STOCK_ANALYSIS",
        "sceneDesc": "AI智能股票分析"
    }

    url = f"{base_url}?{urllib.parse.urlencode(params)}"
    print(f"📡 请求URL: {url}")

    # 构建请求问题
    if stock_code:
        full_question = f"请对股票{stock_code}进行详细分析，{question}"
    else:
        full_question = question

    data = {
        "question": full_question,
        "timestamp": datetime.now().isoformat(),
        "client": "dzh_mcp_client",
        "version": "2.0.0",
        "stock_code": stock_code
    }

    headers = {
        'Content-Type': 'application/json',
        'User-Agent': 'DZH-DeepSeek-MCP/2.0.0',
        'Accept': 'application/json, text/html, */*',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Referer': 'https://f.dzh.com.cn/',
        'Origin': 'https://f.dzh.com.cn'
    }

    try:
        print(f"🚀 发送请求: {full_question[:50]}...")
        response = requests.post(url, json=data, headers=headers, timeout=30)

        print(f"📊 响应状态: {response.status_code}")
        print(f"📋 响应头: {dict(response.headers)}")

        if response.status_code == 200:
            content = response.text.strip()
            print(f"📄 响应长度: {len(content)}字符")
            print(f"🔍 响应预览: {content[:200]}...")

            # 尝试解析响应
            return parse_dzh_response(content, token)
        else:
            print(f"❌ HTTP错误: {response.status_code}")
            print(f"错误内容: {response.text}")
            return None

    except Exception as e:
        print(f"❌ 请求失败: {e}")
        return None

def parse_dzh_response(content, token):
    """解析DZH响应"""
    try:
        # 方法1: 直接JSON解析
        if content.startswith('{'):
            result = json.loads(content)
            if result.get("success") or "response" in result or "answer" in result:
                response_text = result.get("response", result.get("answer", str(result)))
                return {
                    "success": True,
                    "response": response_text,
                    "method": "direct_json",
                    "token_used": token[:20] + "...",
                    "full_response": result
                }

        # 方法2: 提取JSON数据
        json_match = re.search(r'(\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\})', content)
        if json_match:
            try:
                json_data = json.loads(json_match.group(1))
                if "response" in json_data or "answer" in json_data:
                    response_text = json_data.get("response", json_data.get("answer", ""))
                    return {
                        "success": True,
                        "response": response_text,
                        "method": "extracted_json",
                        "token_used": token[:20] + "...",
                        "extracted_data": json_data
                    }
            except:
                pass

        # 方法3: HTML解析
        if '<html' in content.lower() or '<!DOCTYPE' in content.upper():
            # 尝试提取AI回复
            ai_patterns = [
                r'window\.AI_RESPONSE\s*=\s*({[^}]+})',
                r'window\.INITIAL_STATE\s*=\s*({[^}]+})',
                r'<[^>]*class=["\'][^"\']*ai-response[^"\']*["\'][^>]*>(.*?)</[^>]*>',
                r'<[^>]*class=["\'][^"\']*chat-message[^"\']*["\'][^>]*>(.*?)</[^>]*>',
            ]

            for pattern in ai_patterns:
                match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
                if match:
                    response_text = match.group(1) if len(match.groups()) > 0 else match.group(0)
                    # 清理HTML标签
                    response_text = re.sub(r'<[^>]+>', '', response_text).strip()

                    if len(response_text) > 20:
                        return {
                            "success": True,
                            "response": response_text,
                            "method": "html_pattern",
                            "token_used": token[:20] + "...",
                            "pattern": pattern
                        }

        # 方法4: 直接文本提取
        if len(content) > 50 and not content.startswith('<'):
            return {
                "success": True,
                "response": content,
                "method": "direct_text",
                "token_used": token[:20] + "..."
            }

        # 无法解析
        return {
            "success": False,
            "error": "无法解析响应内容",
            "content_preview": content[:100],
            "token_used": token[:20] + "..."
        }

    except Exception as e:
        return {
            "success": False,
            "error": f"解析失败: {str(e)}",
            "content_preview": content[:100] if content else "空响应",
            "token_used": token[:20] + "..."
        }

def test_stock_prediction():
    """测试股票预测"""
    print("🔮 测试DZH股票预测API")
    print("=" * 60)

    # 测试000042股票预测
    questions = [
        "预测明天的价格走势",
        "技术分析当前价格位置",
        "给出具体的买入卖出建议"
    ]

    for i, question in enumerate(questions, 1):
        print(f"\n📈 测试 {i}: {question}")
        print("-" * 50)

        result = test_dzh_api_with_token(question, "000042")

        if result and result.get("success"):
            print("✅ 调用成功!")
            print(f"🔧 解析方法: {result['method']}")
            print(f"🤖 AI回复:")
            print("-" * 30)
            print(result['response'][:500])
            if len(result['response']) > 500:
                print("...(截断)")
            print("-" * 30)
        else:
            print("❌ 调用失败")
            if result:
                print(f"错误: {result.get('error', '未知错误')}")

if __name__ == "__main__":
    test_stock_prediction()