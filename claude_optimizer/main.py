#!/usr/bin/env python3
"""
Claude Code Windows 系统优化工具
一键系统修复和优化主脚本
"""

import os
import sys
import json
import time
import logging
import subprocess
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict

@dataclass
class OptimizationResult:
    """优化结果数据类"""
    module: str
    success: bool
    message: str
    details: Dict = None
    timestamp: str = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()

class ClaudeOptimizer:
    """Claude Code Windows 系统优化器主类"""

    def __init__(self):
        self.setup_directories()
        self.setup_logging()
        self.load_configuration()
        self.results: List[OptimizationResult] = []

    def setup_directories(self):
        """设置工作目录"""
        self.base_dir = Path(__file__).parent
        self.config_dir = self.base_dir / "configs"
        self.logs_dir = self.base_dir / "logs"
        self.backup_dir = self.base_dir / "backups"
        self.tools_dir = self.base_dir / "tools"

        # 确保目录存在
        for directory in [self.config_dir, self.logs_dir, self.backup_dir, self.tools_dir]:
            directory.mkdir(exist_ok=True)

    def setup_logging(self):
        """配置日志系统"""
        log_file = self.logs_dir / f"optimization_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger('ClaudeOptimizer')

    def load_configuration(self):
        """加载配置文件"""
        config_file = self.config_dir / "optimizer_config.json"
        default_config = {
            "backup_enabled": True,
            "auto_rollback": True,
            "optimization_modules": [
                "registry_cleaner",
                "service_manager",
                "disk_optimizer",
                "network_optimizer",
                "security_enhancer"
            ],
            "performance_monitoring": True,
            "log_level": "INFO"
        }

        try:
            if config_file.exists():
                with open(config_file, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
            else:
                self.config = default_config
                with open(config_file, 'w', encoding='utf-8') as f:
                    json.dump(self.config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.logger.error(f"加载配置文件失败: {e}")
            self.config = default_config

    def create_backup(self) -> bool:
        """创建系统备份"""
        if not self.config.get("backup_enabled", True):
            return True

        backup_name = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        backup_path = self.backup_dir / backup_name

        try:
            self.logger.info("开始创建系统备份...")
            backup_path.mkdir(exist_ok=True)

            # 备份注册表
            reg_backup = backup_path / "registry"
            reg_backup.mkdir(exist_ok=True)

            # 备份关键注册表项
            reg_keys = [
                "HKEY_LOCAL_MACHINE\\SYSTEM\\CurrentControlSet\\Services",
                "HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Run",
                "HKEY_CURRENT_USER\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Run"
            ]

            for key in reg_keys:
                try:
                    output_file = reg_backup / f"{key.replace('\\\\', '_')}.reg"
                    cmd = f'reg export "{key}" "{output_file}" /y'
                    subprocess.run(cmd, shell=True, check=True, capture_output=True)
                    self.logger.info(f"已备份注册表项: {key}")
                except subprocess.CalledProcessError as e:
                    self.logger.warning(f"备份注册表项失败 {key}: {e}")

            # 创建备份信息文件
            backup_info = {
                "created_at": datetime.now().isoformat(),
                "backup_path": str(backup_path),
                "optimization_modules": self.config.get("optimization_modules", [])
            }

            with open(backup_path / "backup_info.json", 'w', encoding='utf-8') as f:
                json.dump(backup_info, f, indent=2, ensure_ascii=False)

            self.logger.info(f"系统备份完成: {backup_path}")
            self.current_backup = backup_path
            return True

        except Exception as e:
            self.logger.error(f"创建系统备份失败: {e}")
            return False

    def run_optimization_module(self, module_name: str) -> OptimizationResult:
        """运行单个优化模块"""
        self.logger.info(f"开始执行优化模块: {module_name}")

        try:
            module_file = self.tools_dir / f"{module_name}.py"
            if not module_file.exists():
                return OptimizationResult(
                    module=module_name,
                    success=False,
                    message=f"模块文件不存在: {module_file}"
                )

            # 动态导入并执行模块
            spec = __import__(f"tools.{module_name}", fromlist=['main'])
            if hasattr(spec, 'main'):
                result = spec.main()
                if isinstance(result, dict):
                    return OptimizationResult(
                        module=module_name,
                        success=result.get('success', False),
                        message=result.get('message', ''),
                        details=result.get('details', {})
                    )
                else:
                    return OptimizationResult(
                        module=module_name,
                        success=True,
                        message="模块执行完成"
                    )
            else:
                return OptimizationResult(
                    module=module_name,
                    success=False,
                    message="模块缺少main函数"
                )

        except Exception as e:
            self.logger.error(f"执行优化模块 {module_name} 失败: {e}")
            return OptimizationResult(
                module=module_name,
                success=False,
                message=f"执行失败: {str(e)}"
            )

    def rollback_changes(self) -> bool:
        """回滚优化更改"""
        if not hasattr(self, 'current_backup') or not self.current_backup.exists():
            self.logger.error("没有可用的备份文件")
            return False

        try:
            self.logger.info("开始回滚系统更改...")

            # 恢复注册表
            reg_backup = self.current_backup / "registry"
            if reg_backup.exists():
                for reg_file in reg_backup.glob("*.reg"):
                    try:
                        cmd = f'reg import "{reg_file}"'
                        subprocess.run(cmd, shell=True, check=True, capture_output=True)
                        self.logger.info(f"已恢复注册表项: {reg_file.name}")
                    except subprocess.CalledProcessError as e:
                        self.logger.warning(f"恢复注册表项失败 {reg_file}: {e}")

            self.logger.info("系统回滚完成")
            return True

        except Exception as e:
            self.logger.error(f"回滚失败: {e}")
            return False

    def generate_report(self) -> str:
        """生成优化报告"""
        report_file = self.logs_dir / f"optimization_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"

        success_count = sum(1 for r in self.results if r.success)
        total_count = len(self.results)

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Claude Code 系统优化报告</title>
            <style>
                body {{ font-family: 'Microsoft YaHei', Arial, sans-serif; margin: 20px; }}
                .header {{ background-color: #2c3e50; color: white; padding: 20px; border-radius: 5px; }}
                .summary {{ background-color: #ecf0f1; padding: 15px; margin: 20px 0; border-radius: 5px; }}
                .result {{ margin: 10px 0; padding: 10px; border-left: 4px solid #ddd; }}
                .success {{ border-left-color: #27ae60; background-color: #d5f4e6; }}
                .failure {{ border-left-color: #e74c3c; background-color: #fadbd8; }}
                .details {{ margin-top: 10px; font-size: 0.9em; color: #555; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Claude Code Windows 系统优化报告</h1>
                <p>生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>

            <div class="summary">
                <h2>优化摘要</h2>
                <p>总计执行模块: {total_count}</p>
                <p>成功: {success_count} | 失败: {total_count - success_count}</p>
                <p>成功率: {(success_count/total_count*100):.1f}%</p>
            </div>

            <div class="results">
                <h2>详细结果</h2>
        """

        for result in self.results:
            css_class = "success" if result.success else "failure"
            status = "✓ 成功" if result.success else "✗ 失败"

            html_content += f"""
                <div class="result {css_class}">
                    <h3>{result.module} - {status}</h3>
                    <p><strong>消息:</strong> {result.message}</p>
                    <p><strong>时间:</strong> {result.timestamp}</p>
            """

            if result.details:
                html_content += f"""
                    <div class="details">
                        <strong>详细信息:</strong>
                        <pre>{json.dumps(result.details, indent=2, ensure_ascii=False)}</pre>
                    </div>
                """

            html_content += "</div>"

        html_content += """
            </div>
        </body>
        </html>
        """

        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(html_content)

        self.logger.info(f"优化报告已生成: {report_file}")
        return str(report_file)

    def run_optimization(self) -> bool:
        """运行完整的优化流程"""
        self.logger.info("开始Claude Code Windows系统优化...")

        # 创建备份
        if not self.create_backup():
            self.logger.error("备份创建失败，终止优化流程")
            return False

        # 执行优化模块
        modules = self.config.get("optimization_modules", [])
        for module in modules:
            result = self.run_optimization_module(module)
            self.results.append(result)

            # 如果关键模块失败且启用自动回滚
            if not result.success and self.config.get("auto_rollback", True):
                self.logger.warning(f"关键模块 {module} 失败，执行自动回滚")
                self.rollback_changes()
                return False

        # 生成报告
        report_path = self.generate_report()

        # 显示摘要
        success_count = sum(1 for r in self.results if r.success)
        total_count = len(self.results)

        self.logger.info(f"优化完成! 成功率: {success_count}/{total_count}")
        self.logger.info(f"详细报告: {report_path}")

        return success_count > 0

def main():
    """主函数"""
    print("=== Claude Code Windows 系统优化工具 ===")
    print("正在初始化优化器...")

    optimizer = ClaudeOptimizer()

    try:
        success = optimizer.run_optimization()

        if success:
            print("\n✓ 系统优化完成!")
            print("请查看生成的详细报告了解具体优化结果。")
        else:
            print("\n✗ 系统优化失败!")
            print("请检查日志文件了解详细错误信息。")

        return 0 if success else 1

    except KeyboardInterrupt:
        print("\n用户取消优化操作")
        if hasattr(optimizer, 'current_backup'):
            optimizer.rollback_changes()
        return 1
    except Exception as e:
        print(f"\n优化过程中发生未预期的错误: {e}")
        if hasattr(optimizer, 'current_backup'):
            optimizer.rollback_changes()
        return 1

if __name__ == "__main__":
    sys.exit(main())