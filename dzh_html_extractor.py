#!/usr/bin/env python3
"""
DZH HTML内容提取器
专门提取DZH API返回的HTML中的AI回复内容
"""

import json
import re
import sys
from pathlib import Path
from bs4 import BeautifulSoup
import html

class DZHHTMLExtractor:
    """DZH HTML内容提取器"""

    def __init__(self):
        # 常见的AI回复内容选择器
        self.selectors = [
            # DZH特有的class和id
            {'selector': '.ai-response', 'type': 'css'},
            {'selector': '.chat-message', 'type': 'css'},
            {'selector': '.deepseek-answer', 'type': 'css'},
            {'selector': '.ai-answer', 'type': 'css'},
            {'selector': '#ai-response', 'type': 'css'},
            {'selector': '#chat-answer', 'type': 'css'},

            # 通用选择器
            {'selector': '[data-response]', 'type': 'css'},
            {'selector': '[data-answer]', 'type': 'css'},
            {'selector': '.response-content', 'type': 'css'},
            {'selector': '.answer-content', 'type': 'css'},
            {'selector': '.message-content', 'type': 'css'},

            # 更广泛的选择器
            {'selector': 'article', 'type': 'css'},
            {'selector': '.content', 'type': 'css'},
            {'selector': '.main-content', 'type': 'css'},
        ]

        # 文本模式（用于在script标签中查找JSON数据）
        self.json_patterns = [
            r'window\.INITIAL_STATE\s*=\s*({.*?});',
            r'window\.AI_RESPONSE\s*=\s*({.*?});',
            r'window\.APP_DATA\s*=\s*({.*?});',
            r'__NEXT_DATA__\s*=\s*({.*?})',
            r'var\s+aiResponse\s*=\s*({.*?});',
            r'const\s+response\s*=\s*({.*?});',
            r'let\s+answer\s*=\s*({.*?});',
        ]

        # AI回复识别关键词
        self.ai_keywords = [
            '您好', '你好', '根据', '分析', '建议', '认为', '预测',
            '总的来说', '首先', '其次', '此外', '最后', '投资建议',
            '技术分析', '基本面', '市场趋势', '风险提示', '操作策略'
        ]

    def extract_ai_response(self, html_content: str) -> dict:
        """提取AI回复内容"""
        try:
            # 解码HTML实体
            decoded_content = html.unescape(html_content)

            # 使用BeautifulSoup解析
            soup = BeautifulSoup(decoded_content, 'html.parser')

            # 方法1: 查找JSON数据
            json_result = self._extract_json_data(decoded_content)
            if json_result:
                return json_result

            # 方法2: CSS选择器提取
            css_result = self._extract_with_css(soup)
            if css_result:
                return css_result

            # 方法3: 文本模式匹配
            text_result = self._extract_with_text_patterns(soup)
            if text_result:
                return text_result

            # 方法4: 智能文本提取
            smart_result = self._smart_text_extraction(soup)
            if smart_result:
                return smart_result

            return {
                "success": False,
                "error": "无法提取AI回复内容",
                "html_length": len(html_content),
                "extraction_attempts": len(self.selectors) + len(self.json_patterns) + 2
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"HTML解析失败: {str(e)}",
                "type": "extraction_error"
            }

    def _extract_json_data(self, content: str) -> dict:
        """提取JSON数据"""
        for pattern in self.json_patterns:
            try:
                matches = re.findall(pattern, content, re.DOTALL | re.IGNORECASE)
                for match in matches:
                    try:
                        # 清理和解析JSON
                        json_str = match.strip()
                        if json_str.endswith(';'):
                            json_str = json_str[:-1]

                        data = json.loads(json_str)

                        # 在JSON中查找AI回复
                        ai_response = self._find_ai_text_in_json(data)
                        if ai_response:
                            return {
                                "success": True,
                                "response": ai_response,
                                "method": "json_extraction",
                                "pattern": pattern,
                                "confidence": 0.9
                            }
                    except json.JSONDecodeError:
                        continue
            except Exception:
                continue

        return None

    def _find_ai_text_in_json(self, data, depth=0) -> str:
        """在JSON中递归查找AI文本"""
        if depth > 5:  # 防止过深递归
            return None

        if isinstance(data, dict):
            # 查找可能的键
            ai_keys = ['response', 'answer', 'content', 'message', 'text', 'data', 'result']
            for key in ai_keys:
                if key in data:
                    value = data[key]
                    if isinstance(value, str) and self._is_likely_ai_response(value):
                        return value
                    elif isinstance(value, (dict, list)):
                        nested_result = self._find_ai_text_in_json(value, depth + 1)
                        if nested_result:
                            return nested_result

            # 递归搜索所有值
            for value in data.values():
                if isinstance(value, (dict, list)):
                    result = self._find_ai_text_in_json(value, depth + 1)
                    if result:
                        return result

        elif isinstance(data, list):
            for item in data:
                if isinstance(item, str) and self._is_likely_ai_response(item):
                    return item
                elif isinstance(item, (dict, list)):
                    result = self._find_ai_text_in_json(item, depth + 1)
                    if result:
                        return result

        return None

    def _extract_with_css(self, soup: BeautifulSoup) -> dict:
        """使用CSS选择器提取内容"""
        for selector_info in self.selectors:
            selector = selector_info['selector']
            elements = soup.select(selector)

            for element in elements:
                text = self._clean_element_text(element)
                if self._is_likely_ai_response(text):
                    return {
                        "success": True,
                        "response": text,
                        "method": "css_selector",
                        "selector": selector,
                        "confidence": 0.8,
                        "element_tag": element.name,
                        "element_class": element.get('class', [])
                    }

        return None

    def _extract_with_text_patterns(self, soup: BeautifulSoup) -> dict:
        """使用文本模式提取"""
        # 查找包含大量文本的元素
        for element in soup.find_all(['div', 'p', 'span', 'article', 'section']):
            text = self._clean_element_text(element)

            if self._is_likely_ai_response(text):
                # 检查元素是否有AI相关的class或id
                element_info = {
                    'tag': element.name,
                    'class': element.get('class', []),
                    'id': element.get('id', ''),
                    'data_attrs': {k: v for k, v in element.attrs.items() if k.startswith('data-')}
                }

                confidence = self._calculate_confidence(text, element_info)

                if confidence > 0.5:
                    return {
                        "success": True,
                        "response": text,
                        "method": "text_pattern",
                        "confidence": confidence,
                        "element_info": element_info
                    }

        return None

    def _smart_text_extraction(self, soup: BeautifulSoup) -> dict:
        """智能文本提取"""
        candidates = []

        # 收集所有可能包含AI回复的文本
        for element in soup.find_all(['div', 'p', 'span', 'article', 'section']):
            text = self._clean_element_text(element)
            if len(text) > 50:  # 只考虑较长的文本
                element_info = {
                    'tag': element.name,
                    'class': element.get('class', []),
                    'id': element.get('id', ''),
                    'text_length': len(text),
                    'word_count': len(text.split())
                }

                ai_score = self._calculate_ai_score(text, element_info)
                candidates.append({
                    'text': text,
                    'score': ai_score,
                    'info': element_info
                })

        # 选择得分最高的候选
        if candidates:
            best_candidate = max(candidates, key=lambda x: x['score'])
            if best_candidate['score'] > 0.3:
                return {
                    "success": True,
                    "response": best_candidate['text'],
                    "method": "smart_extraction",
                    "confidence": best_candidate['score'],
                    "candidates_total": len(candidates),
                    "element_info": best_candidate['info']
                }

        return None

    def _clean_element_text(self, element) -> str:
        """清理元素文本"""
        if hasattr(element, 'get_text'):
            text = element.get_text(separator=' ', strip=True)
        else:
            text = str(element)

        # 清理多余空白
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    def _is_likely_ai_response(self, text: str) -> bool:
        """判断是否是AI回复"""
        if not text or len(text) < 20:
            return False

        # 检查是否包含AI关键词
        text_lower = text.lower()
        keyword_count = sum(1 for keyword in self.ai_keywords if keyword in text_lower)

        # 如果包含多个关键词，很可能是AI回复
        return keyword_count >= 2

    def _calculate_confidence(self, text: str, element_info: dict) -> float:
        """计算置信度"""
        confidence = 0.0

        # 基础文本长度分数
        if len(text) > 100:
            confidence += 0.2
        if len(text) > 300:
            confidence += 0.1

        # 关键词分数
        text_lower = text.lower()
        keyword_matches = sum(1 for keyword in self.ai_keywords if keyword in text_lower)
        confidence += min(keyword_matches * 0.15, 0.4)

        # 元素属性分数
        classes = str(element_info.get('class', [])).lower()
        element_id = str(element_info.get('id', '')).lower()

        if any(ai_word in classes for ai_word in ['ai', 'response', 'answer', 'chat']):
            confidence += 0.2
        if any(ai_word in element_id for ai_word in ['ai', 'response', 'answer', 'chat']):
            confidence += 0.2

        # 数据属性分数
        for attr_key, attr_value in element_info.get('data_attrs', {}).items():
            if any(word in str(attr_value).lower() for word in ['response', 'answer', 'ai']):
                confidence += 0.1

        return min(confidence, 1.0)

    def _calculate_ai_score(self, text: str, element_info: dict) -> float:
        """计算AI文本得分"""
        score = 0.0

        # 文本质量分数
        if len(text) > 50:
            score += 0.1
        if len(text) > 200:
            score += 0.2
        if len(text.split()) > 20:
            score += 0.1

        # AI特征分数
        text_lower = text.lower()
        ai_matches = sum(1 for keyword in self.ai_keywords if keyword in text_lower)
        score += min(ai_matches * 0.2, 0.6)

        # 元素特征分数
        classes = str(element_info.get('class', [])).lower()
        element_id = str(element_info.get('id', '')).lower()

        if any(word in classes for word in ['ai', 'chat', 'response', 'answer']):
            score += 0.3
        if any(word in element_id for word in ['ai', 'chat', 'response', 'answer']):
            score += 0.3

        # 结构位置分数（通常AI回复在特定位置）
        if element_info.get('tag') in ['article', 'section']:
            score += 0.1

        return min(score, 1.0)

def test_html_extractor():
    """测试HTML提取器"""
    extractor = DZHHTMLExtractor()

    # 测试HTML示例（基于实际DZH响应）
    test_html = """
    <!DOCTYPE html>
    <html>
    <head><title>DZH DeepSeek</title></head>
    <body>
        <div class="main-content">
            <div class="ai-response">
                <p>您好！根据对000042中纺信的技术分析，该股票目前处于关键支撑位附近。</p>
                <p>从技术指标来看，MACD即将形成金叉，RSI处于超卖区域，具备反弹潜力。</p>
                <p>预计明天价格区间在7.8-9.2元之间，建议投资者密切关注成交量变化。</p>
            </div>
        </div>
    </body>
    </html>
    """

    result = extractor.extract_ai_response(test_html)
    print("HTML提取测试结果:")
    print(json.dumps(result, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    test_html_extractor()