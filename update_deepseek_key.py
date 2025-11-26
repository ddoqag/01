#!/usr/bin/env python3
"""
更新DeepSeek API密钥
用法: python update_deepseek_key.py <your-api-key>
"""

import json
import sys
import os
from pathlib import Path

def update_key(new_api_key):
    """更新API密钥"""
    if not new_api_key:
        print("❌ 请提供API密钥")
        print("用法: python update_deepseek_key.py sk-your-api-key-here")
        return False

    # 验证密钥格式
    if not new_api_key.startswith("sk-"):
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

        settings["deepseek"]["api_key"] = new_api_key
        settings["deepseek"]["base_url"] = "https://api.deepseek.com/v1"
        settings["deepseek"]["model"] = "deepseek-chat"
        settings["deepseek"]["token_source"] = "user_update"
        settings["deepseek"]["updated_at"] = "2025-11-25T05:50:00.000Z"

        # 保存设置
        with open(settings_path, 'w', encoding='utf-8') as f:
            json.dump(settings, f, indent=2, ensure_ascii=False)

        print(f"✅ API密钥已更新: {new_api_key[:10]}...{new_api_key[-4:]}")
        print(f"📁 配置文件: {settings_path}")

        return True

    except Exception as e:
        print(f"❌ 更新失败: {e}")
        return False

if __name__ == "__main__":
    api_key = sys.argv[1] if len(sys.argv) > 1 else ""
    update_key(api_key)