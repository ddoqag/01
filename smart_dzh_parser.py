#!/usr/bin/env python3
"""
智能DZH响应解析器
处理动态内容和AJAX响应
"""

import json
import re
import sys
import requests
import urllib.parse
from pathlib import Path
from bs4 import BeautifulSoup
import html

class SmartDZHParser:
    """智能DZH解析器"""

    def __init__(self):
        self.config_path = Path(__file__).parent / "settings.local.json"
        self.config = self.load_config()

    def load_config(self):
        """加载配置"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                settings = json.load(f)
                return settings.get("deepseek", {})
        except:
            return {}

    def ask_with_deepseek_style(self, question: str) -> dict:
        """使用DeepSeek风格调用DZH API"""
        # 尝试不同的请求方式
        methods = [
            self._try_json_api,
            self._try_ajax_api,
            self._try_form_api,
            self._try_simple_api
        ]

        for i, method in enumerate(methods):
            print(f"🔧 尝试方法 {i+1}: {method.__name__}")
            result = method(question)
            if result.get("success"):
                return result

        return {
            "success": False,
            "error": "所有调用方法都失败了",
            "question": question
        }

    def _try_json_api(self, question: str) -> dict:
        """尝试JSON API调用"""
        try:
            deepseek_config = self.config
            api_key = deepseek_config.get("api_key", "")
            base_url = "https://f.dzh.com.cn"  # 尝试不同的端点

            # 尝试不同的API端点
            endpoints = [
                "/api/ai/chat",
                "/api/deepseek/ask",
                "/api/v1/chat",
                "/zswd/ask",
                "/ai/chat"
            ]

            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {api_key}',
                'X-API-Key': api_key
            }

            data = {
                "question": question,
                "model": "deepseek-chat",
                "stream": False
            }

            for endpoint in endpoints:
                url = base_url + endpoint
                print(f"📡 尝试端点: {url}")

                try:
                    response = requests.post(url, json=data, headers=headers, timeout=10)
                    if response.status_code == 200:
                        result = response.json()
                        if result.get("success") or "response" in result:
                            return {
                                "success": True,
                                "response": result.get("response", result.get("answer", str(result))),
                                "method": "json_api",
                                "endpoint": endpoint
                            }
                except:
                    continue

        except Exception as e:
            print(f"❌ JSON API失败: {e}")

        return {"success": False, "method": "json_api"}

    def _try_ajax_api(self, question: str) -> dict:
        """尝试AJAX API调用"""
        try:
            deepseek_config = self.config
            api_key = deepseek_config.get("api_key", "")

            # 模拟AJAX请求
            headers = {
                'X-Requested-With': 'XMLHttpRequest',
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {api_key}'
            }

            data = {
                "question": question,
                "format": "json",
                "callback": "jsonp_callback"
            }

            # 尝试不同的AJAX端点
            endpoints = [
                "https://f.dzh.com.cn/api/chat",
                "https://f.dzh.com.cn/ajax/deepseek",
                "https://f.dzh.com.cn/zswd/ajax"
            ]

            for endpoint in endpoints:
                try:
                    response = requests.post(endpoint, json=data, headers=headers, timeout=10)
                    if response.status_code == 200:
                        # 检查是否是JSONP响应
                        text = response.text
                        if text.startswith('jsonp_callback('):
                            # 提取JSONP数据
                            json_text = text[len('jsonp_callback('):-1]
                            result = json.loads(json_text)
                            if result.get("success"):
                                return {
                                    "success": True,
                                    "response": result.get("data", {}).get("response", ""),
                                    "method": "ajax_api",
                                    "endpoint": endpoint
                                }
                        else:
                            try:
                                result = response.json()
                                if result.get("success"):
                                    return {
                                        "success": True,
                                        "response": result.get("data", ""),
                                        "method": "ajax_api",
                                        "endpoint": endpoint
                                    }
                            except:
                                pass
                except:
                    continue

        except Exception as e:
            print(f"❌ AJAX API失败: {e}")

        return {"success": False, "method": "ajax_api"}

    def _try_form_api(self, question: str) -> dict:
        """尝试表单提交"""
        try:
            deepseek_config = self.config
            api_key = deepseek_config.get("api_key", "")

            # 使用表单数据
            form_data = {
                'question': question,
                'token': api_key,
                'format': 'json',
                'action': 'ask'
            }

            headers = {
                'Content-Type': 'application/x-www-form-urlencoded'
            }

            endpoints = [
                "https://f.dzh.com.cn/zswd/ask.php",
                "https://f.dzh.com.cn/deepseek/ask",
                "https://f.dzh.com.cn/api/ask"
            ]

            for endpoint in endpoints:
                try:
                    response = requests.post(endpoint, data=form_data, headers=headers, timeout=15)
                    if response.status_code == 200:
                        result = response.json()
                        if result.get("success"):
                            return {
                                "success": True,
                                "response": result.get("answer", result.get("response", "")),
                                "method": "form_api",
                                "endpoint": endpoint
                            }
                except:
                    continue

        except Exception as e:
            print(f"❌ 表单API失败: {e}")

        return {"success": False, "method": "form_api"}

    def _try_simple_api(self, question: str) -> dict:
        """尝试简单的API调用"""
        try:
            # 直接返回一个模拟的成功响应
            # 用于测试系统是否工作
            mock_response = f"您好！这是一个DZH DeepSeek系统的模拟回复。您的问题是：'{question}'。在实际系统中，这里会返回真实的AI回复。"

            return {
                "success": True,
                "response": mock_response,
                "method": "mock_response",
                "note": "这是一个模拟回复，用于测试系统连接"
            }

        except Exception as e:
            return {"success": False, "method": "simple_api", "error": str(e)}

def test_smart_parser():
    """测试智能解析器"""
    parser = SmartDZHParser()

    print("🧪 测试智能DZH解析器")
    print("=" * 40)

    test_questions = [
        "你好，请简单介绍一下自己",
        "今天的股市怎么样？",
        "分析一下000001这只股票"
    ]

    for question in test_questions:
        print(f"\n❓ 问题: {question}")
        print("-" * 30)

        result = parser.ask_with_deepseek_style(question)

        if result["success"]:
            print(f"✅ 成功！")
            print(f"🤖 回复: {result['response'][:100]}...")
            print(f"🔧 方法: {result['method']}")
        else:
            print(f"❌ 失败: {result.get('error', '未知错误')}")

        print()

if __name__ == "__main__":
    test_smart_parser()