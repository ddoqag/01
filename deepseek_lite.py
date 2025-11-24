#!/usr/bin/env python3
"""
DeepSeek轻量级版本 - 快速加载和执行
专为本地优化，减少依赖和启动时间
"""

import json
import sys
import os
import subprocess
import time
from pathlib import Path


class DeepSeekLite:
    def __init__(self):
        # 缓存配置，避免重复读取
        self._config_cache = None
        self._token_cache = None
        self._token_cache_time = 0

        # 本地文件路径优化
        self.script_dir = Path(__file__).parent
        self.cache_timeout = 300  # 5分钟缓存

    def fast_load_config(self):
        """快速加载配置 - 带缓存"""
        if self._config_cache is not None:
            return self._config_cache

        config_files = [
            self.script_dir / "settings.local.json",
            self.script_dir / ".deepseek_config.json",
            Path.home() / "AppData/Local/deepseek_tools/settings.local.json"
        ]

        for config_file in config_files:
            try:
                if config_file.exists():
                    with open(config_file, 'r', encoding='utf-8') as f:
                        self._config_cache = json.load(f)
                        return self._config_cache
            except:
                continue

        # 默认配置
        self._config_cache = {
            "deepseek": {
                "base_url": "https://api.deepseek.com/v1",
                "model": "deepseek-chat",
                "api_key": ""
            }
        }
        return self._config_cache

    def fast_get_token(self):
        """快速获取Token - 带缓存"""
        current_time = time.time()

        # 检查缓存
        if (self._token_cache is not None and
            current_time - self._token_cache_time < self.cache_timeout):
            return self._token_cache

        # 优先级获取Token
        token_sources = [
            # 1. 环境变量（最快）
            lambda: os.getenv("DEEPSEEK_CURRENT_TOKEN") or os.getenv("DEEPSEEK_API_KEY"),

            # 2. 配置文件
            lambda: self.fast_load_config().get("deepseek", {}).get("api_key", ""),

            # 3. 缓存文件
            self._load_cached_token,

            # 4. 轻量级Token管理（仅在必要时）
            self._lightweight_token_manager
        ]

        for get_token in token_sources:
            try:
                token = get_token()
                if token and len(token) > 10:
                    self._token_cache = token
                    self._token_cache_time = current_time
                    return token
            except:
                continue

        return None

    def _load_cached_token(self):
        """从缓存文件加载Token"""
        cache_files = [
            self.script_dir / ".token_cache.json",
            Path.home() / "AppData/Local/deepseek_tools/.token_cache.json"
        ]

        for cache_file in cache_files:
            try:
                if cache_file.exists():
                    with open(cache_file, 'r') as f:
                        cache_data = json.load(f)
                        if time.time() - cache_data.get("timestamp", 0) < 3600:
                            return cache_data.get("token", "")
            except:
                continue
        return ""

    def _lightweight_token_manager(self):
        """轻量级Token获取 - 仅在必要时导入"""
        try:
            # 避免重复导入，提高性能
            if not hasattr(self, '_token_manager'):
                sys.path.insert(0, str(self.script_dir))
                from deepseek_token_manager import DeepSeekTokenManager
                self._token_manager = DeepSeekTokenManager()

            return self._token_manager.get_best_token()
        except:
            return ""

    def fast_api_call(self, question):
        """快速API调用 - 优化版本"""
        token = self.fast_get_token()

        if not token:
            return {
                "success": False,
                "error": "需要配置Token",
                "answer": "运行: python copy_to_local.py 然后 dt auto"
            }

        # 优化的curl调用
        config = self.fast_load_config()
        api_config = config.get("deepseek", {})

        curl_cmd = [
            "curl", "-s", "-X", "POST",
            f"{api_config.get('base_url', 'https://api.deepseek.com/v1')}/chat/completions",
            "-H", f"Authorization: Bearer {token}",
            "-H", "Content-Type: application/json",
            "-d", json.dumps({
                "model": api_config.get('model', 'deepseek-chat'),
                "messages": [{"role": "user", "content": question}],
                "max_tokens": 2000,
                "temperature": 0.7
            }, separators=(',', ':'))  # 紧凑JSON，减少传输大小
        ]

        try:
            # 使用subprocess的优化参数
            result = subprocess.run(
                curl_cmd,
                capture_output=True,
                text=True,
                timeout=30,  # 30秒超时
                check=False
            )

            if result.returncode == 0:
                response = json.loads(result.stdout)
                if "choices" in response and response["choices"]:
                    answer = response["choices"][0]["message"]["content"]
                    return {
                        "success": True,
                        "answer": answer,
                        "usage": response.get("usage", {}),
                        "cached": self._token_cache is not None
                    }
                else:
                    return {
                        "success": False,
                        "error": "API响应异常",
                        "answer": "API调用成功但返回格式异常"
                    }
            else:
                return {
                    "success": False,
                    "error": f"API调用失败 (代码: {result.returncode})",
                    "answer": f"API错误: {result.stderr[:200]}" if result.stderr else "未知API错误"
                }

        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "请求超时",
                "answer": "API请求超时，请稍后重试"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "answer": f"调用出错: {str(e)}"
            }

    def quick_ask(self, question):
        """快速提问 - 最简接口"""
        return self.fast_api_call(question)

    def quick_analyze_stock(self, stock_code):
        """快速股票分析"""
        question = f"请分析股票代码{stock_code}的基本面、技术面和投资价值，用中文简洁回答。"
        result = self.fast_api_call(question)

        if result.get("success"):
            result["analysis_type"] = "股票分析"
            result["stock_code"] = stock_code

        return result

    def quick_market_analysis(self, query):
        """快速市场分析"""
        question = f"市场分析: {query}，请用中文简洁分析关键要点。"
        result = self.fast_api_call(question)

        if result.get("success"):
            result["analysis_type"] = "市场分析"
            result["market_query"] = query

        return result

    def show_status(self):
        """显示快速状态"""
        print("📊 DeepSeek Lite状态", file=sys.stderr)
        print("=" * 30, file=sys.stderr)

        token = self.fast_get_token()
        if token:
            print(f"✅ Token: 可用 ({len(token)}字符)", file=sys.stderr)
            print(f"🚀 缓存: {'启用' if self._token_cache else '未启用'}", file=sys.stderr)
        else:
            print("❌ Token: 不可用", file=sys.stderr)
            print("💡 解决: 运行 dt auto", file=sys.stderr)


def main():
    """命令行接口"""
    if len(sys.argv) < 2:
        print("DeepSeek Lite - 轻量级快速版本")
        print("使用方法:")
        print("  python deepseek_lite.py ask '问题'")
        print("  python deepseek_lite.py analyze 000042")
        print("  python deepseek_lite.py market '分析内容'")
        print("  python deepseek_lite.py status")
        return

    lite = DeepSeekLite()
    command = sys.argv[1].lower()

    if command == "status":
        lite.show_status()
    elif command == "ask" and len(sys.argv) >= 3:
        question = " ".join(sys.argv[2:])
        result = lite.quick_ask(question)
        print(result.get("answer", "无回答"))
    elif command == "analyze" and len(sys.argv) >= 3:
        stock_code = sys.argv[2]
        result = lite.quick_analyze_stock(stock_code)
        print(result.get("answer", "分析失败"))
    elif command == "market" and len(sys.argv) >= 3:
        query = " ".join(sys.argv[2:])
        result = lite.quick_market_analysis(query)
        print(result.get("answer", "分析失败"))
    else:
        print("参数错误，请检查使用方法")


if __name__ == "__main__":
    main()