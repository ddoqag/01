"""
主入口文件 - 演示应用
"""

import asyncio
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent))

from src.ai_platform.cli import cli_app

if __name__ == "__main__":
    cli_app()