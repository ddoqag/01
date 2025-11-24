#!/usr/bin/env python3
"""
简洁的DeepSeek助手 - 直接对话方式使用
无需复杂的MCP配置，直接调用DeepSeek API
"""

import json
import sys
import os
from pathlib import Path


def load_config():
    """加载配置 - 集成动态Token管理"""
    # 首先尝试动态Token管理
    try:
        from deepseek_token_manager import DeepSeekTokenManager
        tm = DeepSeekTokenManager()

        # 自动获取最佳Token
        token = tm.get_best_token()
        if token:
            # 确保settings文件中有最新的Token
            tm.update_settings_token(token)
            print("✅ 使用动态Token", file=sys.stderr)
        else:
            print("⚠️  未找到可用Token，尝试静态配置", file=sys.stderr)
    except Exception as e:
        print(f"⚠️  动态Token管理失败: {e}", file=sys.stderr)

    # 加载配置文件
    config_file = Path(__file__).parent / "settings.local.json"
    try:
        if config_file.exists():
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
        else:
            config = {}
    except:
        config = {}

    # 确保有deepseek配置
    if "deepseek" not in config:
        config["deepseek"] = {}

    # 设置默认值
    deepseek_config = config["deepseek"]
    deepseek_config.setdefault("base_url", "https://api.deepseek.com/v1")
    deepseek_config.setdefault("model", "deepseek-chat")
    deepseek_config.setdefault("api_key", "")

    return config


def simple_api_call(question, config=None):
    """简单的API调用 - 集成动态Token"""
    if config is None:
        config = load_config()

    # 多重Token获取策略
    api_key = config.get("deepseek", {}).get("api_key", "")

    # 如果配置中没有Token，再次尝试动态获取
    if not api_key:
        try:
            from deepseek_token_manager import DeepSeekTokenManager
            tm = DeepSeekTokenManager()
            api_key = tm.get_best_token()
            if api_key:
                print("🔄 实时获取到Token", file=sys.stderr)
        except Exception as e:
            print(f"❌ 实时Token获取失败: {e}", file=sys.stderr)

    if not api_key:
        return {
            "success": False,
            "error": "未找到有效的API Token",
            "answer": "请运行以下命令配置Token:\npython deepseek_token_manager.py auto\n或手动设置DEEPSEEK_CURRENT_TOKEN环境变量"
        }

    # 简单的curl命令调用（避免复杂的Python依赖）
    import subprocess

    curl_command = [
        "curl", "-s", "-X", "POST",
        f"{config['deepseek']['base_url']}/chat/completions",
        "-H", "Authorization: Bearer " + api_key,
        "-H", "Content-Type: application/json",
        "-d", json.dumps({
            "model": config['deepseek']['model'],
            "messages": [{"role": "user", "content": question}],
            "max_tokens": 2000,
            "temperature": 0.7
        })
    ]

    try:
        result = subprocess.run(curl_command, capture_output=True, text=True)
        if result.returncode == 0:
            response = json.loads(result.stdout)
            answer = response["choices"][0]["message"]["content"]
            return {
                "success": True,
                "answer": answer,
                "usage": response.get("usage", {})
            }
        else:
            return {
                "success": False,
                "error": result.stderr,
                "answer": f"API调用失败: {result.stderr}"
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "answer": f"调用出错: {str(e)}"
        }


def ask_deepseek(question):
    """向DeepSeek提问 - 最简洁的接口"""
    result = simple_api_call(question)
    return result


def analyze_stock(stock_code):
    """分析股票"""
    question = f"请分析股票代码{stock_code}的基本面、技术面和投资价值，包括公司概况、财务状况、行业地位和风险提示。请用中文回答，结构清晰。"
    result = simple_api_call(question)

    if result.get("success"):
        result["analysis_type"] = "股票分析"
        result["stock_code"] = stock_code

    return result


def market_analysis(query):
    """市场分析"""
    question = f"请进行市场分析：{query}。请包含市场趋势、关键因素、投资建议等内容，用中文回答。"
    result = simple_api_call(question)

    if result.get("success"):
        result["analysis_type"] = "市场分析"
        result["market_query"] = query

    return result


# 简化的命令行接口
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("使用方法:")
        print("  python deepseek_helper.py ask '你的问题'")
        print("  python deepseek_helper.py analyze 000042")
        print("  python deepseek_helper.py market '市场分析内容'")
        sys.exit(1)

    command = sys.argv[1].lower()

    if command == "ask" and len(sys.argv) >= 3:
        question = " ".join(sys.argv[2:])
        result = ask_deepseek(question)
    elif command == "analyze" and len(sys.argv) >= 3:
        stock_code = sys.argv[2]
        result = analyze_stock(stock_code)
    elif command == "market" and len(sys.argv) >= 3:
        query = " ".join(sys.argv[2:])
        result = market_analysis(query)
    else:
        print("参数错误，请检查使用方法")
        sys.exit(1)

    print(f"✅ {'成功' if result.get('success') else '失败'}")
    print(f"📝 答案:\n{result.get('answer', '无答案')}")

    if not result.get("success"):
        print(f"❌ 错误: {result.get('error', '未知错误')}")