#!/usr/bin/env python3
"""
DeepSeek API密钥设置指南
"""

import json
import sys
import os
import webbrowser
from pathlib import Path

# 设置环境变量
os.environ['PYTHONIOENCODING'] = 'utf-8'

def show_guide():
    """显示DeepSeek API密钥获取指南"""
    print("🔑 DeepSeek API密钥获取指南")
    print("=" * 60)
    print()

    print("📋 获取步骤:")
    print("1. 访问 DeepSeek 官方平台: https://platform.deepseek.com/")
    print("2. 注册/登录您的账户")
    print("3. 前往 'API Keys' 页面")
    print("4. 点击 'Create API Key' 生成新的密钥")
    print("5. 复制生成的API密钥 (格式通常为 sk-xxx...)")
    print()

    print("💰 重要信息:")
    print("- 新用户通常有免费额度")
    print("- API调用价格: 输入 1元/百万tokens, 输出 16元/百万tokens")
    print("- 支持上下文缓存，缓存命中时仅0.1元/百万tokens")
    print()

    print("🔐 安全提示:")
    print("- 请妥善保管您的API密钥")
    print("- 不要将密钥提交到代码仓库")
    print("- 定期轮换密钥以确保安全")
    print()

def update_api_key():
    """更新API密钥配置"""
    print("📝 更新DeepSeek API密钥")
    print("=" * 30)
    print()

    # 获取用户输入的API密钥
    api_key = input("请输入您的DeepSeek API密钥 (格式: sk-xxx...): ").strip()

    if not api_key:
        print("❌ API密钥不能为空")
        return False

    if not api_key.startswith("sk-"):
        print("⚠️  警告: DeepSeek API密钥通常以 'sk-' 开头")
        confirm = input("继续使用此密钥吗? (y/N): ").strip().lower()
        if confirm != 'y':
            return False

    # 更新settings.local.json
    settings_path = Path(__file__).parent / "settings.local.json"

    try:
        # 读取现有设置
        settings = {}
        if settings_path.exists():
            with open(settings_path, 'r', encoding='utf-8') as f:
                settings = json.load(f)

        # 更新deepseek配置
        if "deepseek" not in settings:
            settings["deepseek"] = {}

        settings["deepseek"]["api_key"] = api_key
        settings["deepseek"]["base_url"] = "https://api.deepseek.com/v1"
        settings["deepseek"]["model"] = "deepseek-chat"
        settings["deepseek"]["token_source"] = "user_input"
        settings["deepseek"]["updated_at"] = "2025-11-25T05:45:00.000Z"

        # 保存设置
        with open(settings_path, 'w', encoding='utf-8') as f:
            json.dump(settings, f, indent=2, ensure_ascii=False)

        print(f"✅ API密钥已保存到 {settings_path}")

        # 同时设置环境变量
        print(f"✅ 设置环境变量: DEEPSEEK_API_KEY")

        # 创建批处理文件来设置环境变量
        batch_content = f"""@echo off
set DEEPSEEK_API_KEY={api_key}
echo DeepSeek API密钥环境变量已设置
echo 当前密钥: {api_key[:10]}...{api_key[-4:]}
"""
        batch_path = Path(__file__).parent / "set_deepseek_env.bat"
        with open(batch_path, 'w', encoding='utf-8') as f:
            f.write(batch_content)

        print(f"✅ 环境变量设置脚本已创建: {batch_path}")
        print("   请运行此脚本来设置当前会话的环境变量")

        return True

    except Exception as e:
        print(f"❌ 保存API密钥失败: {e}")
        return False

def test_new_api_key(api_key):
    """测试新的API密钥"""
    print("\n🧪 测试新的API密钥...")

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

        response = requests.post("https://api.deepseek.com/v1/chat/completions",
                               headers=headers, json=data, timeout=15)

        if response.status_code == 200:
            result = response.json()
            content = result["choices"][0]["message"]["content"]
            print("✅ API密钥测试成功!")
            print(f"🤖 DeepSeek回复: {content[:100]}...")
            return True
        else:
            error_info = response.json().get('error', {}).get('message', '未知错误')
            print(f"❌ API密钥测试失败: {error_info}")
            return False

    except Exception as e:
        print(f"❌ 测试过程出错: {e}")
        return False

def main():
    """主函数"""
    print("🚀 DeepSeek MCP服务器配置工具")
    print("=" * 50)
    print()

    while True:
        print("请选择操作:")
        print("1. 显示API密钥获取指南")
        print("2. 输入并更新API密钥")
        print("3. 打开DeepSeek官网")
        print("4. 测试现有API密钥")
        print("5. 退出")
        print()

        choice = input("请输入选项 (1-5): ").strip()

        if choice == "1":
            show_guide()
        elif choice == "2":
            if update_api_key():
                # 从文件读取新的API密钥进行测试
                settings_path = Path(__file__).parent / "settings.local.json"
                with open(settings_path, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                new_api_key = settings["deepseek"]["api_key"]
                test_new_api_key(new_api_key)
        elif choice == "3":
            print("🌐 正在打开DeepSeek官网...")
            webbrowser.open("https://platform.deepseek.com/")
        elif choice == "4":
            # 测试现有API密钥
            settings_path = Path(__file__).parent / "settings.local.json"
            if settings_path.exists():
                with open(settings_path, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                current_key = settings.get("deepseek", {}).get("api_key", "")
                if current_key:
                    test_new_api_key(current_key)
                else:
                    print("❌ 未找到现有的API密钥")
            else:
                print("❌ 未找到settings.local.json文件")
        elif choice == "5":
            print("👋 再见!")
            break
        else:
            print("❌ 无效选项，请重新选择")

        print("\n" + "-" * 40 + "\n")

if __name__ == "__main__":
    main()