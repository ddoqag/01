#!/usr/bin/env python3
"""
测试DZH DeepSeek接口
"""

import json
import sys
import os
from pathlib import Path

# 设置路径
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

def test_dzh_token():
    """测试DZH Token"""
    try:
        token_file = Path("D:/dzh365(64)/token_config.json")
        if token_file.exists():
            with open(token_file, 'r', encoding='utf-8') as f:
                token_config = json.load(f)

            for name, info in token_config.items():
                if info.get("is_active", False):
                    print(f"✅ 找到活跃Token: {name}")
                    print(f"   Token: {info['token'][:20]}...")
                    print(f"   过期时间: {info.get('expires_at', '未知')}")
                    return info['token']
        else:
            print("❌ DZH token配置文件不存在")
    except Exception as e:
        print(f"❌ 读取DZH Token失败: {e}")

    return None

def test_deepseek_call():
    """测试DeepSeek调用"""
    print("🧪 测试DZH DeepSeek接口...")

    # 尝试使用当前配置的API密钥
    settings_path = current_dir / "settings.local.json"
    api_key = None
    base_url = "https://api.deepseek.com/v1"

    if settings_path.exists():
        with open(settings_path, 'r', encoding='utf-8') as f:
            settings = json.load(f)
            deepseek_config = settings.get("deepseek", {})
            api_key = deepseek_config.get("api_key", "")
            base_url = deepseek_config.get("base_url", "https://api.deepseek.com/v1")

    if not api_key:
        # 尝试从DZH获取
        api_key = test_dzh_token()

    if not api_key:
        print("❌ 未找到API密钥")
        return False

    print(f"🔑 使用API密钥: {api_key[:15]}...")
    print(f"🌐 API端点: {base_url}")

    # 尝试调用
    try:
        import requests

        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }

        data = {
            "model": "deepseek-chat",
            "messages": [{"role": "user", "content": "你好，请简单介绍一下自己"}],
            "max_tokens": 50
        }

        print(f"📡 发送请求到: {base_url}/chat/completions")
        response = requests.post(f"{base_url}/chat/completions",
                               headers=headers, json=data, timeout=15)

        print(f"📊 响应状态码: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            answer = result["choices"][0]["message"]["content"]
            print("✅ DeepSeek接口调用成功!")
            print(f"🤖 回答: {answer}")
            return True
        else:
            try:
                error_info = response.json().get('error', {})
                print(f"❌ API调用失败: {error_info}")
            except:
                print(f"❌ API调用失败: {response.text}")
            return False

    except Exception as e:
        print(f"❌ 请求异常: {e}")
        return False

def check_dzh_deepseek_integration():
    """检查DZH DeepSeek集成"""
    print("🔍 检查DZH DeepSeek集成配置...")

    # 检查是否有DZH专用的DeepSeek配置
    possible_configs = [
        "D:/dzh365(64)/deepseek_config.json",
        "D:/dzh365(64)/config/deepseek.json",
        "D:/dzh365(64)/api_config.json"
    ]

    for config_path in possible_configs:
        path = Path(config_path)
        if path.exists():
            print(f"✅ 找到配置文件: {config_path}")
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    print(f"   配置内容: {json.dumps(config, indent=2, ensure_ascii=False)}")
            except Exception as e:
                print(f"   读取失败: {e}")
        else:
            print(f"❌ 配置文件不存在: {config_path}")

if __name__ == "__main__":
    print("🚀 DZH DeepSeek接口测试")
    print("=" * 40)

    # 1. 检查DZH DeepSeek集成
    check_dzh_deepseek_integration()
    print()

    # 2. 测试Token
    test_dzh_token()
    print()

    # 3. 测试API调用
    success = test_deepseek_call()

    print()
    if success:
        print("🎉 DZH DeepSeek接口正常工作!")
    else:
        print("❌ DZH DeepSeek接口需要配置")
        print("\n💡 建议检查:")
        print("1. DZH系统中的DeepSeek配置")
        print("2. API端点URL是否正确")
        print("3. Token是否有效")