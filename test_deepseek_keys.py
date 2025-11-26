#!/usr/bin/env python3
"""
测试不同DeepSeek API密钥格式
"""

import json
import sys
import requests
import os
from pathlib import Path

# 设置环境变量
os.environ['PYTHONIOENCODING'] = 'utf-8'

def test_api_key(api_key, key_name="unknown"):
    """测试API密钥是否有效"""
    try:
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }

        data = {
            "model": "deepseek-chat",
            "messages": [{"role": "user", "content": "测试连接"}],
            "max_tokens": 5
        }

        response = requests.post("https://api.deepseek.com/v1/chat/completions",
                               headers=headers, json=data, timeout=10)

        if response.status_code == 200:
            print(f"✅ {key_name}: API密钥有效")
            return True
        else:
            error_info = response.json().get('error', {}).get('message', '未知错误')
            print(f"❌ {key_name}: {error_info}")
            return False

    except Exception as e:
        print(f"❌ {key_name}: 测试失败 - {e}")
        return False

def main():
    """测试所有可用的API密钥"""
    print("🔑 测试DeepSeek API密钥...")
    print("=" * 50)

    # 1. 测试环境变量中的密钥
    env_key = os.getenv("DEEPSEEK_API_KEY")
    if env_key:
        test_api_key(env_key, "环境变量 DEEPSEEK_API_KEY")
    else:
        print("❌ 环境变量 DEEPSEEK_API_KEY 未设置")

    # 2. 测试settings.local.json中的密钥
    settings_path = Path(__file__).parent / "settings.local.json"
    if settings_path.exists():
        try:
            with open(settings_path, 'r', encoding='utf-8') as f:
                settings = json.load(f)
                deepseek_config = settings.get("deepseek", {})
                api_key = deepseek_config.get("api_key", "")
                if api_key:
                    test_api_key(api_key, "settings.local.json中的密钥")
                else:
                    print("❌ settings.local.json中未找到deepseek.api_key")
        except Exception as e:
            print(f"❌ 读取settings.local.json失败: {e}")

    # 3. 测试DZH系统中的Token
    dzh_token_path = Path("D:/dzh365(64)/token_config.json")
    if dzh_token_path.exists():
        try:
            with open(dzh_token_path, 'r', encoding='utf-8') as f:
                token_config = json.load(f)

            print("\n🔍 测试DZH系统Token...")
            for token_name, token_info in token_config.items():
                if token_info.get("is_active", False):
                    token = token_info.get("token", "")
                    if token:
                        # 尝试直接作为DeepSeek API密钥
                        test_api_key(token, f"DZH Token: {token_name}")

                        # 尝试可能的格式转换
                        if not token.startswith("sk-"):
                            # 可能需要添加sk-前缀
                            test_api_key(f"sk-{token}", f"DZH Token (sk-前缀): {token_name}")
        except Exception as e:
            print(f"❌ 读取DZH Token配置失败: {e}")

    print("\n💡 建议:")
    print("1. 如果没有有效密钥，请访问 https://platform.deepseek.com/ 获取")
    print("2. 将有效密钥设置到环境变量或settings.local.json中")
    print("3. DZH Token可能不是为DeepSeek API设计的，需要专用的DeepSeek API密钥")

if __name__ == "__main__":
    main()