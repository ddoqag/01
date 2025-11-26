#!/usr/bin/env python3
"""
测试DZH DeepSeek API接口
使用正确的DZH端点和配置
"""

import json
import sys
import requests
import urllib.parse
from pathlib import Path

def test_dzh_deepseek_api():
    """测试DZH DeepSeek API"""
    print("🧪 测试DZH DeepSeek API...")
    print("=" * 50)

    # 从配置文件加载
    settings_path = Path(__file__).parent / "settings.local.json"
    if not settings_path.exists():
        print("❌ 配置文件不存在")
        return False

    with open(settings_path, 'r', encoding='utf-8') as f:
        settings = json.load(f)

    deepseek_config = settings.get("deepseek", {})
    api_key = deepseek_config.get("api_key", "")
    base_url = deepseek_config.get("base_url", "https://f.dzh.com.cn/zswd/newask")
    tun = deepseek_config.get("tun", "dzhsp846")
    scene = deepseek_config.get("scene", "gg")

    if not api_key:
        print("❌ 未找到API密钥")
        return False

    print(f"🔑 API密钥: {api_key[:20]}...")
    print(f"🌐 API端点: {base_url}")
    print(f"🔧 Tun参数: {tun}")
    print(f"📝 场景: {scene}")

    # 构建DZH API URL
    params = {
        "tun": tun,
        "token": api_key,
        "version": "1.0",
        "scene": scene,
        "sceneName": "测试",
        "sceneCode": "TEST",
        "sceneDesc": "API测试"
    }

    url = f"{base_url}?{urllib.parse.urlencode(params)}"
    print(f"📡 完整URL: {url}")

    # DZH API通常使用POST请求，参数在URL中
    try:
        # 准备请求数据（如果有需要）
        data = {
            "question": "你好，请简单介绍一下你自己",
            "timestamp": "2025-11-25T13:55:00"
        }

        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'DZH-DeepSeek-Client/1.0'
        }

        print("📤 发送请求...")
        response = requests.post(url, json=data, headers=headers, timeout=30)

        print(f"📊 响应状态码: {response.status_code}")
        print(f"📋 响应头: {dict(response.headers)}")

        if response.status_code == 200:
            try:
                result = response.json()
                print("✅ DZH DeepSeek API调用成功!")
                print("📄 响应内容:")
                print(json.dumps(result, indent=2, ensure_ascii=False))
                return True
            except json.JSONDecodeError:
                print("✅ API调用成功，但响应不是JSON格式")
                print("📄 响应内容:")
                print(response.text[:500] + "..." if len(response.text) > 500 else response.text)
                return True
        else:
            print(f"❌ API调用失败: {response.status_code}")
            print("📄 错误响应:")
            print(response.text)
            return False

    except Exception as e:
        print(f"❌ 请求异常: {e}")
        return False

def test_dzh_token_format():
    """测试DZH Token格式"""
    print("\n🔑 测试DZH Token格式...")
    print("=" * 30)

    token_file = Path("D:/dzh365(64)/token_config.json")
    if token_file.exists():
        with open(token_file, 'r', encoding='utf-8') as f:
            token_config = json.load(f)

        for name, info in token_config.items():
            if info.get("is_active", False):
                token = info["token"]
                print(f"✅ Token: {name}")
                print(f"   长度: {len(token)}")
                print(f"   格式: {token[:10]}...{token[-10:]}")
                print(f"   过期: {info.get('expires_at', '未知')}")
                print()

    return True

if __name__ == "__main__":
    print("🚀 DZH DeepSeek API测试工具")
    print("=" * 50)

    # 1. 测试Token格式
    test_dzh_token_format()

    # 2. 测试API调用
    success = test_dzh_deepseek_api()

    print("\n" + "=" * 50)
    if success:
        print("🎉 DZH DeepSeek API测试成功!")
        print("✅ 您的DeepSeek MCP服务器现在应该可以正常工作了")
    else:
        print("❌ DZH DeepSeek API需要进一步配置")
        print("\n💡 可能的解决方案:")
        print("1. 检查Token是否有效")
        print("2. 确认网络连接到f.dzh.com.cn")
        print("3. 检查DZH系统是否正常运行")