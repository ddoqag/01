#!/usr/bin/env python3
"""
DZH DeepSeek HTML响应解析器
解析DZH API返回的HTML格式响应，提取AI对话内容
"""

import json
import re
import sys
from pathlib import Path
from bs4 import BeautifulSoup
import html
from typing import Dict, Any, Optional

class DZHHTMLParser:
    """DZH HTML响应解析器"""

    def __init__(self):
        # DZH响应中常见的AI回复模式
        self.ai_patterns = [
            # JSON格式的回复
            r'window\.INITIAL_STATE\s*=\s*({[^}]+});',
            r'window\.AI_RESPONSE\s*=\s*({[^}]+});',
            r'__NEXT_DATA__\s*=\s*({[^}]+})',

            # HTML中的特定class或id
            r'<[^>]*class=["\'][^"\']*ai-response[^"\']*["\'][^>]*>(.*?)</[^>]*>',
            r'<[^>]*id=["\'][^"\']*ai-answer[^"\']*["\'][^>]*>(.*?)</[^>]*>',
            r'<div[^>]*class=["\'][^"\']*chat-message[^"\']*["\'][^>]*>(.*?)</div>',

            # 预定义的数据属性
            r'<[^>]*data-response=["\']([^"\']*)["\']',
            r'<[^>]*data-answer=["\']([^"\']*)["\']',

            # 文本模式匹配AI回复
            r'(?:AI回复|回答|Response)[:：]\s*(.+?)(?:\n\n|$)',
            r'(?:Assistant|助手)[:：]\s*(.+?)(?:\n\n|$)',
            r'(?:DeepSeek|深度求索)[:：]\s*(.+?)(?:\n\n|$))',
        ]

        # 需要清理的HTML标签
        self.cleanup_patterns = [
            r'<script[^>]*>.*?</script>',
            r'<style[^>]*>.*?</style>',
            r'<[^>]*class=["\'][^"\']*loading[^"\']*["\'][^>]*>.*?</[^>]*>',
            r'<[^>]*class=["\'][^"\']*spinner[^"\']*["\'][^>]*>.*?</[^>]*>',
            r'<!--.*?-->',
        ]

    def parse_response(self, html_content: str) -> Dict[str, Any]:
        """解析DZH HTML响应"""
        try:
            # 解码HTML实体
            decoded_content = html.unescape(html_content)

            # 使用BeautifulSoup解析HTML
            soup = BeautifulSoup(decoded_content, 'html.parser')

            result = {
                "success": False,
                "response": "",
                "confidence": 0,
                "method": "",
                "raw_content": html_content
            }

            # 方法1: 查找JSON数据
            json_result = self._extract_json_data(decoded_content)
            if json_result:
                result.update(json_result)
                result["method"] = "json_extraction"
                return result

            # 方法2: 查找特定HTML元素
            html_result = self._extract_from_html(soup)
            if html_result:
                result.update(html_result)
                result["method"] = "html_extraction"
                return result

            # 方法3: 文本模式匹配
            text_result = self._extract_from_text(decoded_content)
            if text_result:
                result.update(text_result)
                result["method"] = "text_pattern"
                return result

            # 方法4: 通用文本提取
            generic_result = self._extract_generic_text(soup)
            if generic_result:
                result.update(generic_result)
                result["method"] = "generic_extraction"
                return result

            result["error"] = "无法解析AI回复内容"
            return result

        except Exception as e:
            return {
                "success": False,
                "error": f"HTML解析失败: {str(e)}",
                "method": "error"
            }

    def _extract_json_data(self, content: str) -> Optional[Dict[str, Any]]:
        """提取JSON数据"""
        for pattern in self.ai_patterns[:4]:  # 前四个是JSON模式
            matches = re.findall(pattern, content, re.DOTALL | re.IGNORECASE)
            for match in matches:
                try:
                    # 清理可能的JavaScript代码
                    json_str = re.sub(r'^\s*window\.\w+\s*=\s*', '', match.strip())
                    json_str = re.sub(r';\s*$', '', json_str)

                    data = json.loads(json_str)

                    # 查找AI回复字段
                    ai_response = self._find_ai_response_in_json(data)
                    if ai_response:
                        return {
                            "success": True,
                            "response": ai_response,
                            "confidence": 0.9,
                            "json_data": data
                        }
                except json.JSONDecodeError:
                    continue

        return None

    def _find_ai_response_in_json(self, data: Any, path: str = "") -> Optional[str]:
        """在JSON数据中递归查找AI回复"""
        if isinstance(data, dict):
            # 查找可能的AI回复字段
            ai_keys = ['response', 'answer', 'content', 'message', 'text', 'data', 'result']
            for key in ai_keys:
                if key in data:
                    value = data[key]
                    if isinstance(value, str) and len(value.strip()) > 10:
                        return value.strip()
                    elif isinstance(value, dict) or isinstance(value, list):
                        nested_result = self._find_ai_response_in_json(value, f"{path}.{key}")
                        if nested_result:
                            return nested_result

            # 递归搜索所有字段
            for key, value in data.items():
                if isinstance(value, (dict, list)):
                    nested_result = self._find_ai_response_in_json(value, f"{path}.{key}")
                    if nested_result:
                        return nested_result

        elif isinstance(data, list):
            for i, item in enumerate(data):
                if isinstance(item, (dict, list)):
                    nested_result = self._find_ai_response_in_json(item, f"{path}[{i}]")
                    if nested_result:
                        return nested_result
                elif isinstance(item, str) and len(item.strip()) > 20:
                    return item.strip()

        return None

    def _extract_from_html(self, soup: BeautifulSoup) -> Optional[Dict[str, Any]]:
        """从HTML元素中提取AI回复"""
        # 查找可能的AI回复元素
        selectors = [
            {'name': 'class', 'value': 'ai-response'},
            {'name': 'class', 'value': 'chat-response'},
            {'name': 'class', 'value': 'ai-answer'},
            {'name': 'id', 'value': 'ai-response'},
            {'name': 'id', 'value': 'chat-answer'},
            {'name': 'data-response', 'value': 'true'},
            {'name': 'data-answer', 'value': 'true'},
        ]

        for selector in selectors:
            if selector['name'] == 'class':
                elements = soup.find_all(class_=selector['value'])
            else:
                elements = soup.find_all(attrs={selector['name']: selector['value']})

            for element in elements:
                text = self._clean_text(element.get_text())
                if text and len(text.strip()) > 10:
                    # 检查是否像AI回复
                    if self._is_likely_ai_response(text):
                        return {
                            "success": True,
                            "response": text,
                            "confidence": 0.8,
                            "element": element.name,
                            "selector": f"{selector['name']}={selector['value']}"
                        }

        return None

    def _extract_from_text(self, content: str) -> Optional[Dict[str, Any]]:
        """使用文本模式匹配AI回复"""
        for pattern in self.ai_patterns[4:]:  # 文本模式
            matches = re.findall(pattern, content, re.MULTILINE | re.DOTALL | re.IGNORECASE)
            for match in matches:
                text = match.strip()
                if text and len(text) > 10 and self._is_likely_ai_response(text):
                    return {
                        "success": True,
                        "response": text,
                        "confidence": 0.7,
                        "pattern": pattern
                    }

        return None

    def _extract_generic_text(self, soup: BeautifulSoup) -> Optional[Dict[str, Any]]:
        """通用文本提取"""
        # 查找可能包含长文本的元素
        text_elements = []

        # 查找段落、div等块级元素
        for element in soup.find_all(['p', 'div', 'span', 'article', 'section']):
            text = self._clean_text(element.get_text())
            if text and len(text) > 50:  # 较长的文本更可能是AI回复
                # 检查文本质量
                if self._is_likely_ai_response(text):
                    text_elements.append({
                        'text': text,
                        'element': element.name,
                        'class': element.get('class', []),
                        'id': element.get('id', '')
                    })

        # 选择最佳候选
        if text_elements:
            # 优先选择带有AI相关class的元素
            for item in text_elements:
                classes = item['class'] if isinstance(item['class'], list) else [item['class']]
                for cls in classes:
                    if any(ai_keyword in str(cls).lower() for ai_keyword in ['ai', 'chat', 'response', 'answer']):
                        return {
                            "success": True,
                            "response": item['text'],
                            "confidence": 0.6,
                            "element": item['element'],
                            "class": item['class']
                        }

            # 选择最长的文本
            best_item = max(text_elements, key=lambda x: len(x['text']))
            return {
                "success": True,
                "response": best_item['text'],
                "confidence": 0.5,
                "element": best_item['element'],
                "length": len(best_item['text'])
            }

        return None

    def _clean_text(self, text: str) -> str:
        """清理文本"""
        if not text:
            return ""

        # 清理HTML标签
        text = re.sub(r'<[^>]+>', '', text)

        # 清理多余空白
        text = re.sub(r'\s+', ' ', text)

        # 清理特殊字符
        text = text.strip()

        return text

    def _is_likely_ai_response(self, text: str) -> bool:
        """判断文本是否可能是AI回复"""
        if len(text) < 10:
            return False

        # AI回复的常见特征
        ai_indicators = [
            '您好', '你好', '关于', '根据', '我认为', '建议',
            '总的来说', '首先', '其次', '此外', '最后',
            '你好，我是', '我是', '可以帮助', '有什么可以帮助',
            '您的问题', '您的问题是', '您想了解',
            '分析', '预测', '建议', '看法', '观点'
        ]

        text_lower = text.lower()

        # 检查是否包含AI回复特征
        for indicator in ai_indicators:
            if indicator in text_lower:
                return True

        # 检查是否是完整句子（包含主谓宾结构）
        if len(text) > 50 and ('。' in text or '！' in text or '？' in text):
            return True

        return False

def test_parser():
    """测试HTML解析器"""
    parser = DZHHTMLParser()

    # 测试HTML示例
    test_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>DZH DeepSeek</title>
        <script>window.AI_RESPONSE = {"response": "您好，我是DZH DeepSeek助手，很高兴为您服务。请问您有什么问题需要帮助？"};</script>
    </head>
    <body>
        <div class="ai-response">
            <p>这是另一个可能的AI回复内容。</p>
        </div>
        <p>普通文本内容，不是AI回复。</p>
    </body>
    </html>
    """

    result = parser.parse_response(test_html)
    print("HTML解析测试结果:")
    print(json.dumps(result, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    test_parser()