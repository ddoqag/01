#!/usr/bin/env python3
"""
DeepSeek工具本地复制脚本
将所有必要文件复制到本地目录，加快加载速度
"""

import os
import sys
import shutil
import json
from pathlib import Path
from datetime import datetime


class LocalCopier:
    def __init__(self):
        self.source_dir = Path(__file__).parent
        self.local_dirs = [
            Path.home() / "deepseek_local",
            Path("C:/deepseek_tools"),
            Path.home() / "AppData/Local/deepseek_tools",
        ]
        self.choose_best_local_dir()

    def choose_best_local_dir(self):
        """选择最佳本地目录"""
        for local_dir in self.local_dirs:
            try:
                local_dir.mkdir(parents=True, exist_ok=True)
                # 测试写入权限
                test_file = local_dir / ".test"
                test_file.write_text("test")
                test_file.unlink()
                self.local_dir = local_dir
                print(f"✅ 选择本地目录: {local_dir}")
                return
            except Exception as e:
                print(f"❌ 目录不可用 {local_dir}: {e}")
                continue

        # 如果都不可用，使用当前目录
        self.local_dir = self.source_dir / "local_copy"
        self.local_dir.mkdir(exist_ok=True)
        print(f"⚠️  使用备用目录: {self.local_dir}")

    def get_files_to_copy(self):
        """获取需要复制的文件列表"""
        files_to_copy = [
            # 核心文件
            "deepseek_helper.py",
            "deepseek_token_manager.py",
            "settings.local.json",

            # 配置文件
            "DEEPSEEK_DYNAMIC_TOKEN_GUIDE.md",
            "DEEPSEEK_SIMPLE_GUIDE.md",

            # 脚本文件
            "ds.cmd",
            "dt.cmd",
            "setup_deepseek_env.cmd",
        ]

        # 添加完整路径
        files_with_paths = []
        for file_name in files_to_copy:
            source_file = self.source_dir / file_name
            if source_file.exists():
                files_with_paths.append(source_file)
            else:
                print(f"⚠️  文件不存在: {file_name}")

        return files_with_paths

    def copy_files(self):
        """复制文件到本地目录"""
        files_to_copy = self.get_files_to_copy()

        print(f"📁 开始复制文件到: {self.local_dir}")
        print("=" * 50)

        copied_files = []
        for source_file in files_to_copy:
            try:
                target_file = self.local_dir / source_file.name

                # 检查文件是否需要更新
                if target_file.exists():
                    source_mtime = source_file.stat().st_mtime
                    target_mtime = target_file.stat().st_mtime

                    if source_mtime <= target_mtime:
                        print(f"⏭️  跳过 {source_file.name} (已是最新)")
                        copied_files.append(source_file.name)
                        continue

                # 复制文件
                shutil.copy2(source_file, target_file)
                print(f"✅ 复制 {source_file.name}")
                copied_files.append(source_file.name)

            except Exception as e:
                print(f"❌ 复制失败 {source_file.name}: {e}")

        print("=" * 50)
        print(f"📊 复制完成: {len(copied_files)} 个文件")
        return copied_files

    def create_local_config(self):
        """创建本地配置文件"""
        config = {
            "installation_info": {
                "source_directory": str(self.source_dir),
                "local_directory": str(self.local_dir),
                "copy_time": datetime.now().isoformat(),
                "version": "1.0.0"
            },
            "file_paths": {
                "helper": str(self.local_dir / "deepseek_helper.py"),
                "token_manager": str(self.local_dir / "deepseek_token_manager.py"),
                "config": str(self.local_dir / "settings.local.json")
            },
            "commands": {
                "dt": f"{self.local_dir}/dt.cmd",
                "ds": f"{self.local_dir}/ds.cmd",
                "setup": f"{self.local_dir}/setup_deepseek_env.cmd"
            }
        }

        config_file = self.local_dir / "local_config.json"
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)

        print(f"📝 创建配置文件: {config_file}")
        return config_file

    def create_quick_start_scripts(self):
        """创建快速启动脚本"""

        # Windows批处理脚本
        quick_start_bat = self.local_dir / "quick_start.bat"
        with open(quick_start_bat, 'w', encoding='utf-8') as f:
            f.write(f'''@echo off
echo 🚀 DeepSeek工具快速启动
echo ========================

REM 设置本地路径
set DEEPSEEK_LOCAL_PATH={self.local_dir}

REM 添加到PATH
set PATH=%DEEPSEEK_LOCAL_PATH%;%PATH%

echo ✅ 环境设置完成
echo.
echo 🎯 可用命令:
echo   dt auto          - 自动配置Token
echo   ds ask "问题"    - 询问DeepSeek
echo   dt status        - 查看Token状态
echo   dt test          - 测试功能
echo.
echo 💬 直接对话方式:
echo   请用DeepSeek分析一下股票000042
echo.

REM 如果有参数，执行相应命令
if not "%~1"=="" (
    echo 🔄 执行命令: %*
    %*
)

''')

        # PowerShell脚本
        quick_start_ps1 = self.local_dir / "quick_start.ps1"
        with open(quick_start_ps1, 'w', encoding='utf-8') as f:
            f.write(f'''# DeepSeek工具快速启动 (PowerShell)
Write-Host "🚀 DeepSeek工具快速启动" -ForegroundColor Green
Write-Host "========================" -ForegroundColor Green

# 设置本地路径
$env:DEEPSEEK_LOCAL_PATH = "{self.local_dir}"

# 添加到PATH
$env:PATH = "$env:DEEPSEEK_LOCAL_PATH;$env:PATH"

Write-Host "✅ 环境设置完成" -ForegroundColor Green
Write-Host ""
Write-Host "🎯 可用命令:" -ForegroundColor Yellow
Write-Host "   dt auto          - 自动配置Token"
Write-Host "   ds ask '问题'    - 询问DeepSeek"
Write-Host "   dt status        - 查看Token状态"
Write-Host "   dt test          - 测试功能"
Write-Host ""
Write-Host "💬 直接对话方式:" -ForegroundColor Yellow
Write-Host "   请用DeepSeek分析一下股票000042"
Write-Host ""

# 如果有参数，执行相应命令
if ($args.Count -gt 0) {{
    Write-Host "🔄 执行命令: $args" -ForegroundColor Cyan
    & $args[0] $args[1..($args.Length-1)]
}}
''')

        print(f"🚀 创建快速启动脚本:")
        print(f"   📄 {quick_start_bat}")
        print(f"   🔧 {quick_start_ps1}")

        return quick_start_bat, quick_start_ps1

    def update_local_scripts(self):
        """更新本地脚本，使用本地路径"""

        # 更新dt.cmd
        dt_cmd = self.local_dir / "dt.cmd"
        if dt_cmd.exists():
            content = dt_cmd.read_text(encoding='utf-8')
            updated_content = content.replace(
                'python "%~dp0deepseek_token_manager.py"',
                f'python "{self.local_dir}/deepseek_token_manager.py"'
            )
            updated_content = updated_content.replace(
                'python "%~dp0deepseek_helper.py"',
                f'python "{self.local_dir}/deepseek_helper.py"'
            )
            dt_cmd.write_text(updated_content, encoding='utf-8')
            print("✅ 更新 dt.cmd")

        # 更新ds.cmd
        ds_cmd = self.local_dir / "ds.cmd"
        if ds_cmd.exists():
            content = ds_cmd.read_text(encoding='utf-8')
            updated_content = content.replace(
                'python "%~dp0deepseek_helper.py"',
                f'python "{self.local_dir}/deepseek_helper.py"'
            )
            ds_cmd.write_text(updated_content, encoding='utf-8')
            print("✅ 更新 ds.cmd")

    def create_environment_setup(self):
        """创建环境设置脚本"""
        env_setup = self.local_dir / "set_env.bat"
        with open(env_setup, 'w', encoding='utf-8') as f:
            f.write(f'''@echo off
REM DeepSeek本地环境设置脚本

echo 🔧 设置DeepSeek本地环境...

REM 设置本地路径
set DEEPSEEK_LOCAL_PATH={self.local_dir}
set PATH=%DEEPSEEK_LOCAL_PATH%;%PATH%

REM 设置Python路径
set PYTHONPATH=%DEEPSEEK_LOCAL_PATH%;%PYTHONPATH%

echo ✅ 本地环境设置完成
echo 📍 本地目录: %DEEPSEEK_LOCAL_PATH%
echo.

REM 测试命令
echo 🧪 测试命令可用性:
where dt
where ds
echo.

REM 快速测试
echo 🚀 快速测试Token状态:
dt status

''')

        print(f"🔧 创建环境设置脚本: {env_setup}")
        return env_setup

    def run_full_copy(self):
        """执行完整复制流程"""
        print("🚀 开始DeepSeek工具本地复制...")
        print("=" * 60)

        # 1. 复制文件
        copied_files = self.copy_files()

        # 2. 创建本地配置
        config_file = self.create_local_config()

        # 3. 创建快速启动脚本
        quick_start_bat, quick_start_ps1 = self.create_quick_start_scripts()

        # 4. 更新脚本路径
        self.update_local_scripts()

        # 5. 创建环境设置脚本
        env_setup = self.create_environment_setup()

        print("\n" + "=" * 60)
        print("🎉 本地复制完成!")
        print(f"📍 本地目录: {self.local_dir}")

        print(f"\n🚀 快速开始:")
        print(f"   Windows: {quick_start_bat}")
        print(f"   PowerShell: {quick_start_ps1}")
        print(f"   环境设置: {env_setup}")

        print(f"\n💡 下一步:")
        print(f"   1. 运行: {quick_start_bat}")
        print(f"   2. 执行: dt auto")
        print(f"   3. 测试: ds ask 'hello'")

        return {
            "local_dir": self.local_dir,
            "copied_files": copied_files,
            "quick_start_bat": quick_start_bat,
            "quick_start_ps1": quick_start_ps1,
            "config_file": config_file,
            "env_setup": env_setup
        }


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="DeepSeek工具本地复制")
    parser.add_argument("--target", "-t", help="目标目录路径")
    parser.add_argument("--update", "-u", action="store_true", help="仅更新文件")

    args = parser.parse_args()

    copier = LocalCopier()

    # 如果指定了目标目录
    if args.target:
        copier.local_dir = Path(args.target)
        copier.local_dir.mkdir(parents=True, exist_ok=True)

    result = copier.run_full_copy()

    # 保存结果到JSON文件
    result_file = copier.local_dir / "copy_result.json"
    with open(result_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, default=str, ensure_ascii=False)

    print(f"\n📄 结果保存到: {result_file}")


if __name__ == "__main__":
    main()