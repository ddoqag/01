#!/usr/bin/env python3
"""
增强版动态Token管理器
支持多种Token格式转换和API适配
"""

import json
import sys
import os
import requests
import hashlib
import base64
from pathlib import Path
from datetime import datetime
import subprocess

class EnhancedTokenManager:
    def __init__(self):
        self.current_dir = Path(__file__).parent
        self.dzh_path = Path("D:/dzh365(64)")
        self.settings_path = self.current_dir / "settings.local.json"
        self.cache_path = self.current_dir / ".enhanced_token_cache.json"

    def get_dzh_tokens(self):
        """获取所有DZH Token"""
        tokens = {}
        try:
            token_config_file = self.dzh_path / "token_config.json"
            if token_config_file.exists():
                with open(token_config_file, 'r', encoding='utf-8') as f:
                    token_config = json.load(f)

                for token_name, token_info in token_config.items():
                    if token_info.get("is_active", False):
                        expires_at = token_info.get("expires_at", "")
                        if expires_at:
                            expiry_date = datetime.fromisoformat(expires_at.replace('Z', '+00:00'))
                            if datetime.now(expiry_date.tzinfo) < expiry_date:
                                tokens[token_name] = {
                                    "token": token_info["token"],
                                    "info": token_info
                                }
        except Exception as e:
            print(f"读取DZH Token失败: {e}")

        return tokens

    def convert_token_format(self, original_token, target_format="deepseek"):
        """尝试转换Token格式"""
        if target_format == "deepseek":
            # 尝试多种DeepSeek格式转换
            conversions = [
                original_token,  # 原始格式
                f"sk-{original_token}",  # sk-前缀
                f"deepseek-{original_token}",  # deepseek-前缀
                self.generate_deepseek_compatible_token(original_token)  # 哈希转换
            ]
            return conversions
        return [original_token]

    def generate_deepseek_compatible_token(self, token):
        """生成DeepSeek兼容的Token格式"""
        # 使用DZH Token生成一个模拟的DeepSeek格式Token
        # 这只是示例，实际的DeepSeek API需要真正的API密钥
        timestamp = str(int(datetime.now().timestamp()))
        combined = f"{token}:{timestamp}"
        hash_obj = hashlib.sha256(combined.encode())

        # 生成一个类似sk-格式的token
        encoded = base64.b64encode(hash_obj.digest()).decode()[:32]
        simulated_key = f"sk-{encoded}"

        return simulated_key

    def test_api_key(self, api_key, key_name="unknown"):
        """测试API密钥是否有效"""
        try:
            headers = {
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json'
            }

            data = {
                "model": "deepseek-chat",
                "messages": [{"role": "user", "content": "测试"}],
                "max_tokens": 5
            }

            response = requests.post("https://api.deepseek.com/v1/chat/completions",
                                   headers=headers, json=data, timeout=10)

            if response.status_code == 200:
                print(f"✅ {key_name}: API密钥有效")
                return api_key
            else:
                error_info = response.json().get('error', {}).get('message', '未知错误')
                print(f"❌ {key_name}: {error_info}")
                return None

        except Exception as e:
            print(f"❌ {key_name}: 测试失败 - {e}")
            return None

    def find_working_token(self):
        """寻找可用的Token"""
        print("🔍 开始寻找可用的DeepSeek Token...")

        # 1. 检查环境变量
        env_key = os.getenv("DEEPSEEK_API_KEY")
        if env_key:
            working_key = self.test_api_key(env_key, "环境变量")
            if working_key:
                return working_key

        # 2. 检查settings文件
        if self.settings_path.exists():
            try:
                with open(self.settings_path, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    stored_key = settings.get("deepseek", {}).get("api_key", "")
                    if stored_key:
                        working_key = self.test_api_key(stored_key, "配置文件")
                        if working_key:
                            return working_key
            except Exception as e:
                print(f"读取配置文件失败: {e}")

        # 3. 尝试DZH Token转换
        print("\n🔄 尝试DZH Token转换...")
        dzh_tokens = self.get_dzh_tokens()

        for token_name, token_data in dzh_tokens.items():
            print(f"\n🔧 测试DZH Token: {token_name}")
            original_token = token_data["token"]

            # 尝试各种格式转换
            converted_tokens = self.convert_token_format(original_token)

            for i, converted_token in enumerate(converted_tokens):
                format_name = ["原始", "sk-前缀", "deepseek-前缀", "哈希转换"][i]
                working_key = self.test_api_key(converted_token, f"{token_name} ({format_name})")
                if working_key:
                    print(f"🎉 找到可用的Token!")
                    return working_key

        # 4. 生成模拟Token（仅用于演示）
        print("\n🔧 生成演示Token...")
        if dzh_tokens:
            first_token = list(dzh_tokens.values())[0]["token"]
            demo_token = self.generate_deepseek_compatible_token(first_token)
            print(f"📝 生成演示Token: {demo_token[:20]}...")
            print("⚠️  注意: 这是演示Token，无法实际访问DeepSeek API")

        return None

    def update_settings(self, api_key, token_source="enhanced_manager"):
        """更新配置文件"""
        try:
            settings = {}
            if self.settings_path.exists():
                with open(self.settings_path, 'r', encoding='utf-8') as f:
                    settings = json.load(f)

            if "deepseek" not in settings:
                settings["deepseek"] = {}

            settings["deepseek"]["api_key"] = api_key
            settings["deepseek"]["base_url"] = "https://api.deepseek.com/v1"
            settings["deepseek"]["model"] = "deepseek-chat"
            settings["deepseek"]["token_source"] = token_source
            settings["deepseek"]["updated_at"] = datetime.now().isoformat()

            with open(self.settings_path, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=2, ensure_ascii=False)

            print(f"✅ 配置已更新: {token_source}")
            return True

        except Exception as e:
            print(f"❌ 更新配置失败: {e}")
            return False

    def auto_find_and_configure(self):
        """自动寻找并配置Token"""
        print("🚀 启动增强版Token自动配置...")
        print("=" * 50)

        working_token = self.find_working_token()

        if working_token:
            if self.update_settings(working_token, "enhanced_auto"):
                print(f"\n🎉 配置成功!")
                print(f"🔑 Token: {working_token[:15]}...{working_token[-8:]}")
                return True
        else:
            print("\n❌ 未找到可用的Token")
            print("\n💡 解决方案:")
            print("1. 访问 https://platform.deepseek.com/ 获取官方API密钥")
            print("2. 检查DZH系统是否支持DeepSeek API")
            print("3. 联系DZH技术支持获取API访问权限")

            return False

def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("""
🔧 增强版动态Token管理器

用法:
  python enhanced_token_manager.py <command>

命令:
  auto          自动寻找并配置Token
  find         仅寻找可用Token
  status        显示Token状态
  convert       显示Token转换选项

示例:
  python enhanced_token_manager.py auto
        """)
        return

    command = sys.argv[1]
    manager = EnhancedTokenManager()

    if command == "auto":
        manager.auto_find_and_configure()
    elif command == "find":
        manager.find_working_token()
    elif command == "status":
        manager.show_status()
    elif command == "convert":
        manager.show_conversion_options()
    else:
        print(f"❌ 未知命令: {command}")

if __name__ == "__main__":
    main()