#!/usr/bin/env python3
"""
DeepSeek动态Token管理器
无缝集成现有的DZH Token系统
"""

import json
import sys
import os
from pathlib import Path
from datetime import datetime
import subprocess


class DeepSeekTokenManager:
    def __init__(self):
        self.dzh_path = Path("D:/dzh365(64)")  # Windows路径
        self.settings_path = Path(__file__).parent / "settings.local.json"
        self.cache_path = Path(__file__).parent / ".token_cache.json"

    def load_dzh_token(self, token_name="production_api"):
        """从DZH系统加载Token"""
        try:
            # 方法1: 直接读取token_config.json
            token_config_file = self.dzh_path / "token_config.json"
            if token_config_file.exists():
                with open(token_config_file, 'r', encoding='utf-8') as f:
                    token_config = json.load(f)

                if token_name in token_config:
                    token_info = token_config[token_name]
                    if token_info.get("is_active", True):
                        # 检查是否过期
                        expires_at = token_info.get("expires_at", "")
                        if expires_at:
                            expiry_date = datetime.fromisoformat(expires_at.replace('Z', '+00:00'))
                            if datetime.now(expiry_date.tzinfo) < expiry_date:
                                return token_info["token"]

        except Exception as e:
            print(f"从DZH系统读取Token失败: {e}", file=sys.stderr)

        return None

    def load_dzh_token_via_script(self, token_name="production_api"):
        """通过Python脚本获取DZH Token"""
        try:
            python_cmd = [
                sys.executable, "-c",
                f'''
import sys
sys.path.append("{self.dzh_path}")
try:
    from token_config import DZHTokenManager
    tm = DZHTokenManager()
    token = tm.get_token("{token_name}") or tm.get_token("demo_token")
    print(token)
except:
    pass
'''
            ]

            result = subprocess.run(python_cmd, capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                token = result.stdout.strip()
                if token and len(token) > 10:  # 基本验证
                    return token

        except Exception as e:
            print(f"通过脚本获取Token失败: {e}", file=sys.stderr)

        return None

    def get_environment_token(self):
        """从环境变量获取Token"""
        return os.getenv("DEEPSEEK_CURRENT_TOKEN") or os.getenv("DEEPSEEK_API_KEY")

    def get_settings_token(self):
        """从settings.local.json获取Token"""
        try:
            with open(self.settings_path, 'r', encoding='utf-8') as f:
                settings = json.load(f)
                return settings.get("deepseek", {}).get("api_key", "")
        except:
            return ""

    def get_cached_token(self):
        """从缓存获取Token"""
        try:
            with open(self.cache_path, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
                cached_token = cache_data.get("token", "")
                cache_time = cache_data.get("timestamp", 0)

                # 缓存1小时有效
                if time.time() - cache_time < 3600 and cached_token:
                    return cached_token
        except:
            pass
        return None

    def cache_token(self, token):
        """缓存Token"""
        try:
            cache_data = {
                "token": token,
                "timestamp": time.time()
            }
            with open(self.cache_path, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, indent=2)
        except:
            pass

    def get_best_token(self):
        """按优先级获取最佳Token"""
        import time

        # 优先级顺序: DZH系统 > 环境变量 > settings文件 > 缓存
        token_sources = [
            ("DZH系统(直接)", lambda: self.load_dzh_token()),
            ("DZH系统(脚本)", lambda: self.load_dzh_token_via_script()),
            ("环境变量", self.get_environment_token),
            ("配置文件", self.get_settings_token),
            ("缓存", self.get_cached_token)
        ]

        for source_name, get_token in token_sources:
            try:
                token = get_token()
                if token and len(token) > 10:
                    print(f"✅ 使用Token来源: {source_name}", file=sys.stderr)
                    if source_name not in ["缓存", "配置文件"]:
                        self.cache_token(token)
                    return token
            except Exception as e:
                print(f"❌ {source_name}获取失败: {e}", file=sys.stderr)
                continue

        return None

    def update_settings_token(self, token):
        """更新settings.local.json中的Token"""
        try:
            # 读取现有设置
            settings = {}
            if self.settings_path.exists():
                with open(self.settings_path, 'r', encoding='utf-8') as f:
                    settings = json.load(f)

            # 更新deepseek配置
            if "deepseek" not in settings:
                settings["deepseek"] = {}

            settings["deepseek"]["api_key"] = token
            settings["deepseek"]["token_source"] = "dynamic_integration"
            settings["deepseek"]["updated_at"] = datetime.now().isoformat()

            # 写回文件
            with open(self.settings_path, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=2, ensure_ascii=False)

            return True
        except Exception as e:
            print(f"更新设置文件失败: {e}", file=sys.stderr)
            return False

    def auto_configure(self):
        """自动配置最佳Token"""
        print("🔍 正在搜索最佳Token...", file=sys.stderr)

        token = self.get_best_token()
        if token:
            success = self.update_settings_token(token)
            if success:
                print(f"✅ Token自动配置成功!", file=sys.stderr)
                print(f"🔑 Token长度: {len(token)} 字符", file=sys.stderr)
                return True
            else:
                print("❌ Token配置更新失败", file=sys.stderr)
        else:
            print("❌ 未找到有效的Token", file=sys.stderr)
            print("请确保以下条件之一满足:", file=sys.stderr)
            print("1. DZH系统正常运行且有可用Token", file=sys.stderr)
            print("2. 设置了DEEPSEEK_CURRENT_TOKEN环境变量", file=sys.stderr)
            print("3. 在settings.local.json中手动配置api_key", file=sys.stderr)

        return False

    def show_token_status(self):
        """显示Token状态"""
        print("📊 Token状态报告", file=sys.stderr)
        print("=" * 40, file=sys.stderr)

        # 检查各种Token来源
        sources = {
            "DZH系统(直接)": self.load_dzh_token(),
            "DZH系统(脚本)": self.load_dzh_token_via_script(),
            "环境变量": self.get_environment_token(),
            "配置文件": self.get_settings_token(),
            "缓存": self.get_cached_token()
        }

        for source, token in sources.items():
            if token:
                status = "✅ 可用"
                length = f"({len(token)}字符)"
                print(f"{source}: {status} {length}", file=sys.stderr)
            else:
                print(f"{source}: ❌ 不可用", file=sys.stderr)

        # 显示当前最佳Token
        best_token = self.get_best_token()
        if best_token:
            print(f"\n🎯 当前使用: 有效Token ({len(best_token)}字符)", file=sys.stderr)
        else:
            print(f"\n❌ 当前无可用Token", file=sys.stderr)


def main():
    """命令行接口"""
    import argparse

    parser = argparse.ArgumentParser(description="DeepSeek Token管理器")
    parser.add_argument("action", choices=["status", "auto", "get", "update"],
                       help="操作类型")
    parser.add_argument("--token", help="手动指定Token (用于update)")

    args = parser.parse_args()

    tm = DeepSeekTokenManager()

    if args.action == "status":
        tm.show_token_status()
    elif args.action == "auto":
        tm.auto_configure()
    elif args.action == "get":
        token = tm.get_best_token()
        if token:
            print(token)
        else:
            print("无可用Token", file=sys.stderr)
            sys.exit(1)
    elif args.action == "update" and args.token:
        success = tm.update_settings_token(args.token)
        if success:
            print("Token更新成功")
        else:
            print("Token更新失败", file=sys.stderr)
            sys.exit(1)


if __name__ == "__main__":
    main()