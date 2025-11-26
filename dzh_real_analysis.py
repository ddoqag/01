#!/usr/bin/env python3
"""
DZH真实AI股票分析工具
集成动态Token和HTML内容提取 - 单文件版本
"""

import json
import sys
import requests
import urllib.parse
from pathlib import Path
from datetime import datetime
import re
import html
from bs4 import BeautifulSoup

class DZHRealAnalysis:
    """DZH真实股票分析工具"""

    def __init__(self):
        self.config_path = Path(__file__).parent / "settings.local.json"
        self.token = self.load_token()

    def load_token(self):
        """加载Token"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                settings = json.load(f)
                return settings.get("deepseek", {}).get("api_key", "")
        except:
            return ""

    def extract_ai_response(self, html_content: str) -> dict:
        """提取AI回复内容"""
        try:
            decoded_content = html.unescape(html_content)
            soup = BeautifulSoup(decoded_content, 'html.parser')

            # 查找JSON数据
            json_patterns = [
                r'window\.INITIAL_STATE\s*=\s*({.*?});',
                r'window\.AI_RESPONSE\s*=\s*({.*?});',
                r'window\.APP_DATA\s*=\s*({.*?});',
            ]

            for pattern in json_patterns:
                matches = re.findall(pattern, decoded_content, re.DOTALL | re.IGNORECASE)
                for match in matches:
                    try:
                        json_str = match.strip().rstrip(';')
                        data = json.loads(json_str)

                        # 查找AI回复
                        ai_text = self._find_ai_text_in_json(data)
                        if ai_text:
                            return {
                                "success": True,
                                "response": ai_text,
                                "method": "json_extraction",
                                "confidence": 0.9
                            }
                    except:
                        continue

            # CSS选择器提取
            selectors = [
                '.ai-response', '.chat-message', '.deepseek-answer', '.ai-answer',
                '#ai-response', '#chat-answer', '[data-response]', '[data-answer]',
                '.response-content', '.answer-content', '.message-content',
                'article', '.content', '.main-content'
            ]

            for selector in selectors:
                elements = soup.select(selector)
                for element in elements:
                    text = self._clean_text(element.get_text())
                    if self._is_ai_response(text):
                        return {
                            "success": True,
                            "response": text,
                            "method": "css_selector",
                            "confidence": 0.8,
                            "selector": selector
                        }

            # 智能文本提取
            candidates = []
            for element in soup.find_all(['div', 'p', 'span', 'article', 'section']):
                text = self._clean_text(element.get_text())
                if len(text) > 50:
                    score = self._calculate_ai_score(text, element)
                    candidates.append({'text': text, 'score': score})

            if candidates:
                best = max(candidates, key=lambda x: x['score'])
                if best['score'] > 0.3:
                    return {
                        "success": True,
                        "response": best['text'],
                        "method": "smart_extraction",
                        "confidence": best['score']
                    }

            return {
                "success": False,
                "error": "无法提取AI回复内容",
                "html_length": len(html_content)
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"解析失败: {str(e)}"
            }

    def _find_ai_text_in_json(self, data, depth=0) -> str:
        """在JSON中查找AI文本"""
        if depth > 5:
            return None

        if isinstance(data, dict):
            ai_keys = ['response', 'answer', 'content', 'message', 'text', 'data']
            for key in ai_keys:
                if key in data:
                    value = data[key]
                    if isinstance(value, str) and self._is_ai_response(value):
                        return value
                    elif isinstance(value, (dict, list)):
                        result = self._find_ai_text_in_json(value, depth + 1)
                        if result:
                            return result

            for value in data.values():
                if isinstance(value, (dict, list)):
                    result = self._find_ai_text_in_json(value, depth + 1)
                    if result:
                        return result

        elif isinstance(data, list):
            for item in data:
                if isinstance(item, str) and self._is_ai_response(item):
                    return item
                elif isinstance(item, (dict, list)):
                    result = self._find_ai_text_in_json(item, depth + 1)
                    if result:
                        return result

        return None

    def _clean_text(self, text: str) -> str:
        """清理文本"""
        if not text:
            return ""
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    def _is_ai_response(self, text: str) -> bool:
        """判断是否是AI回复"""
        if not text or len(text) < 20:
            return False

        ai_keywords = [
            '您好', '你好', '根据', '分析', '建议', '认为', '预测',
            '总的来说', '首先', '其次', '此外', '最后', '投资建议',
            '技术分析', '基本面', '市场趋势', '风险提示', '操作策略',
            '价格', '股票', '走势', '支撑', '阻力', '买入', '卖出'
        ]

        text_lower = text.lower()
        count = sum(1 for keyword in ai_keywords if keyword in text_lower)
        return count >= 3

    def _calculate_ai_score(self, text: str, element) -> float:
        """计算AI文本得分"""
        score = 0.0

        if len(text) > 100:
            score += 0.2
        if len(text) > 300:
            score += 0.2

        text_lower = text.lower()
        ai_keywords = ['您好', '分析', '建议', '预测', '价格', '股票', '技术', '风险']
        keyword_count = sum(1 for keyword in ai_keywords if keyword in text_lower)
        score += min(keyword_count * 0.15, 0.4)

        classes = str(element.get('class', [])).lower()
        element_id = str(element.get('id', '')).lower()
        if any(word in classes for word in ['ai', 'response', 'answer', 'chat']):
            score += 0.3
        if any(word in element_id for word in ['ai', 'response', 'answer', 'chat']):
            score += 0.3

        return min(score, 1.0)

    def analyze_stock(self, stock_code: str, question: str) -> dict:
        """分析股票"""
        if not self.token or len(self.token) < 20:
            return {"success": False, "error": "Token无效"}

        base_url = "https://f.dzh.com.cn/zswd/newask"
        params = {
            "tun": "dzhsp846",
            "token": self.token,
            "version": "1.0",
            "scene": "gg",
            "sceneName": "股票分析",
            "sceneCode": "STOCK_ANALYSIS"
        }

        url = f"{base_url}?{urllib.parse.urlencode(params)}"
        full_question = f"请对股票{stock_code}进行详细分析：{question}"

        data = {
            "question": full_question,
            "timestamp": datetime.now().isoformat(),
            "client": "dzh_real_analysis",
            "stock_code": stock_code
        }

        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'DZH-DeepSeek-Analysis/2.0.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Referer': 'https://f.dzh.com.cn/'
        }

        try:
            print(f"🚀 正在请求DZH API分析 {stock_code}...")
            print(f"📝 问题: {question}")
            print(f"🔑 Token: {self.token[:20]}...({len(self.token)}字符)")

            response = requests.post(url, json=data, headers=headers, timeout=30)

            print(f"📊 响应状态: {response.status_code}")

            if response.status_code == 200:
                content = response.text
                print(f"📄 响应长度: {len(content)}字符")

                # 提取AI回复
                extraction_result = self.extract_ai_response(content)

                if extraction_result.get("success"):
                    return {
                        "success": True,
                        "stock_code": stock_code,
                        "question": question,
                        "response": extraction_result["response"],
                        "method": extraction_result["method"],
                        "confidence": extraction_result.get("confidence", 0.5),
                        "timestamp": datetime.now().isoformat()
                    }
                else:
                    return {
                        "success": False,
                        "stock_code": stock_code,
                        "error": f"AI内容提取失败: {extraction_result.get('error', '未知错误')}",
                        "html_length": len(content)
                    }
            else:
                return {
                    "success": False,
                    "error": f"HTTP错误: {response.status_code}"
                }

        except Exception as e:
            return {
                "success": False,
                "error": f"请求失败: {str(e)}"
            }

    def format_analysis_report(self, result: dict) -> str:
        """格式化分析报告"""
        if not result.get("success"):
            return f"❌ 分析失败: {result.get('error', '未知错误')}"

        output = []
        output.append("📈 DZH AI股票分析报告")
        output.append("=" * 60)
        output.append(f"🏢 股票代码: {result['stock_code']}")
        output.append(f"📅 分析时间: {result['timestamp'][:19].replace('T', ' ')}")
        output.append(f"📝 分析问题: {result['question']}")
        output.append(f"🔧 提取方法: {result['method']}")
        output.append(f"🎯 置信度: {result.get('confidence', 0.5):.1%}")
        output.append("")

        # AI分析内容
        output.append("🤖 DZH AI分析:")
        output.append("-" * 50)
        response = result['response']
        display_text = response[:1000] + "..." if len(response) > 1000 else response
        output.append(display_text)
        output.append("")

        # 提取价格信息
        prices = self._extract_prices(result['response'])
        if prices:
            output.append("💰 价格信息:")
            output.append("-" * 30)
            for key, value in prices.items():
                output.append(f"  {key}: {value}")
            output.append("")

        # 投资建议
        suggestions = self._extract_suggestions(result['response'])
        if suggestions:
            output.append("💡 投资建议:")
            output.append("-" * 30)
            for suggestion in suggestions[:5]:
                output.append(f"  • {suggestion}")
            output.append("")

        output.append("⚠️  免责声明: 本分析仅供参考，投资需谨慎")
        output.append("📊 数据来源: DZH DeepSeek AI分析系统")

        return "\n".join(output)

    def _extract_prices(self, text: str) -> dict:
        """提取价格信息"""
        prices = {}
        patterns = [
            (r'当前价.*?(\d+\.?\d*)', '当前价'),
            (r'目标价.*?(\d+\.?\d*)', '目标价'),
            (r'支撑位.*?(\d+\.?\d*)', '支撑位'),
            (r'阻力位.*?(\d+\.?\d*)', '阻力位'),
            (r'预测.*?(\d+\.?\d*)', '预测价'),
        ]

        for pattern, label in patterns:
            matches = re.findall(pattern, text)
            if matches:
                prices[label] = f"¥{matches[0]}"

        return prices

    def _extract_suggestions(self, text: str) -> list:
        """提取投资建议"""
        suggestions = []
        sentences = re.split(r'[。！？]', text)

        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) > 10:
                if any(keyword in sentence for keyword in ['建议', '推荐', '操作', '注意', '风险', '买入', '卖出']):
                    suggestions.append(sentence + '。')

        return suggestions

def main():
    """主函数"""
    if len(sys.argv) < 3:
        print("🔧 DZH真实AI股票分析工具")
        print("用法: python dzh_real_analysis.py <股票代码> <问题>")
        print("示例: python dzh_real_analysis.py 000042 明天价格预测")
        return

    stock_code = sys.argv[1]
    question = " ".join(sys.argv[2:])

    analyzer = DZHRealAnalysis()

    print(f"🔮 DZH AI股票分析 - {stock_code}")
    print("=" * 60)

    # 执行分析
    result = analyzer.analyze_stock(stock_code, question)

    # 生成报告
    report = analyzer.format_analysis_report(result)
    print(report)

if __name__ == "__main__":
    main()