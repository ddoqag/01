#!/usr/bin/env python3
"""
完整的DZH DeepSeek测试工具
结合API调用和HTML解析
"""

import json
import sys
import requests
import urllib.parse
from pathlib import Path

# 添加当前目录到路径
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from dzh_html_parser import DZHHTMLParser

class DZHDeepSeekComplete:
    """完整的DZH DeepSeek客户端"""

    def __init__(self):
        self.settings_path = current_dir / "settings.local.json"
        self.parser = DZHHTMLParser()
        self.config = None
        self.load_config()

    def load_config(self):
        """加载配置"""
        try:
            with open(self.settings_path, 'r', encoding='utf-8') as f:
                settings = json.load(f)
                self.config = settings.get("deepseek", {})
                return True
        except Exception as e:
            print(f"❌ 配置加载失败: {e}")
            return False

    def ask(self, question: str, scene: str = "gg") -> dict:
        """向DZH DeepSeek提问"""
        if not self.config:
            return {
                "success": False,
                "error": "未找到配置"
            }

        try:
            # 构建请求参数
            params = {
                "tun": self.config.get("tun", "dzhsp846"),
                "token": self.config.get("api_key", ""),
                "version": "1.0",
                "scene": scene,
                "sceneName": "问题咨询",
                "sceneCode": "QUESTION",
                "sceneDesc": urllib.parse.quote(question.encode('utf-8')),
                "question": urllib.parse.quote(question.encode('utf-8'))
            }

            url = f"{self.config.get('base_url')}?{urllib.parse.urlencode(params)}"

            # 准备请求数据
            data = {
                "question": question,
                "timestamp": "2025-11-25T13:55:00",
                "user_agent": "DZH-DeepSeek-Client/1.0"
            }

            headers = {
                'Content-Type': 'application/json',
                'User-Agent': 'DZH-DeepSeek-Client/1.0',
                'Referer': 'https://f.dzh.com.cn/',
                'Origin': 'https://f.dzh.com.cn'
            }

            print(f"🤖 向DZH DeepSeek提问...")
            print(f"📝 问题: {question}")

            # 发送请求
            response = requests.post(url, json=data, headers=headers, timeout=30)

            print(f"📊 响应状态: {response.status_code}")

            if response.status_code == 200:
                # 解析HTML响应
                result = self.parser.parse_response(response.text)

                if result["success"]:
                    print(f"✅ AI回复获取成功!")
                    print(f"🎯 置信度: {result['confidence']}")
                    print(f"🔧 解析方法: {result['method']}")
                    print(f"🤖 回答: {result['response'][:100]}{'...' if len(result['response']) > 100 else ''}")

                    return {
                        "success": True,
                        "question": question,
                        "response": result["response"],
                        "confidence": result["confidence"],
                        "method": result["method"],
                        "raw_status": response.status_code
                    }
                else:
                    print(f"❌ 解析失败: {result.get('error', '未知错误')}")
                    return {
                        "success": False,
                        "error": result.get("error", "HTML解析失败"),
                        "question": question,
                        "raw_status": response.status_code
                    }
            else:
                print(f"❌ 请求失败: {response.status_code}")
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}",
                    "question": question,
                    "raw_status": response.status_code
                }

        except Exception as e:
            print(f"❌ 请求异常: {e}")
            return {
                "success": False,
                "error": str(e),
                "question": question
            }

    def test_scenarios(self):
        """测试不同场景"""
        scenarios = [
            ("你好，请简单介绍一下自己", "gg"),
            ("分析一下今天的股市走势", "market"),
            ("000001这只股票怎么样？", "stock"),
            ("有什么投资建议吗？", "advice")
        ]

        print("🧪 开始场景测试...")
        print("=" * 60)

        results = []
        for question, scene in scenarios:
            print(f"\n🎯 场景: {scene}")
            print(f"❓ 问题: {question}")
            print("-" * 40)

            result = self.ask(question, scene)
            results.append(result)

            if result["success"]:
                print(f"✅ 测试通过")
            else:
                print(f"❌ 测试失败: {result.get('error', '未知错误')}")

        return results

def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("""
🚀 DZH DeepSeek 完整测试工具

用法:
  python dzh_deepseek_complete.py <command> [arguments]

命令:
  ask "问题"                 - 单次提问
  test                       - 测试多个场景
  status                     - 显示配置状态
  parser-test               - 测试HTML解析器

示例:
  python dzh_deepseek_complete.py ask "什么是人工智能？"
  python dzh_deepseek_complete.py test
        """)
        return

    command = sys.argv[1]
    client = DZHDeepSeekComplete()

    if command == "ask":
        if len(sys.argv) < 3:
            print("❌ 请提供问题")
            return
        question = " ".join(sys.argv[2:])
        result = client.ask(question)
        print(f"\n📋 结果: {json.dumps(result, indent=2, ensure_ascii=False)}")

    elif command == "test":
        results = client.test_scenarios()

        # 统计结果
        success_count = sum(1 for r in results if r["success"])
        total_count = len(results)

        print(f"\n📊 测试统计:")
        print(f"   成功: {success_count}/{total_count}")
        print(f"   成功率: {success_count/total_count*100:.1f}%")

    elif command == "status":
        print("📊 配置状态:")
        print(json.dumps(client.config, indent=2, ensure_ascii=False))

    elif command == "parser-test":
        from dzh_html_parser import test_parser
        test_parser()

    else:
        print(f"❌ 未知命令: {command}")

if __name__ == "__main__":
    main()