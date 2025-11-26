#!/usr/bin/env python3
"""
启动Web Scraping MCP服务器
"""

import sys
import os
from pathlib import Path

# 设置环境变量
os.environ['PYTHONIOENCODING'] = 'utf-8'

# 添加当前目录到Python路径
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# 导入并启动MCP服务器
if __name__ == "__main__":
    print("🚀 启动Web Scraping MCP服务器...", file=sys.stderr)

    # 使用便携版Python
    portable_python = current_dir / "python_portable" / "python.exe"
    if portable_python.exists():
        # 切换到便携版Python并启动服务器
        import subprocess
        cmd = [str(portable_python), "web_scraping_mcp_server.py"]
        subprocess.run(cmd)
    else:
        # 使用当前Python
        from web_scraping_mcp_server import main
        import asyncio
        asyncio.run(main())