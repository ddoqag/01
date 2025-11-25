#!/usr/bin/env python3
"""
Windows 注册表清理和优化模块
"""

import os
import sys
import subprocess
import json
import logging
from pathlib import Path
from typing import Dict, List, Tuple

class RegistryCleaner:
    """Windows 注册表清理器"""

    def __init__(self):
        self.logger = logging.getLogger('RegistryCleaner')

        # 要清理的注册表路径
        self.cleanup_paths = [
            "HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Explorer\\RunMRU",
            "HKEY_CURRENT_USER\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\RunMRU",
            "HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Explorer\\RecentDocs",
            "HKEY_CURRENT_USER\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\RecentDocs",
            "HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Explorer\\TypedPaths",
            "HKEY_CURRENT_USER\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\TypedPaths"
        ]

        # 要优化的注册表设置
        self.optimization_settings = {
            # 内存管理优化
            "HKEY_LOCAL_MACHINE\\SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Memory Management": {
                "ClearPageFileAtShutdown": 0,
                "LargeSystemCache": 1,
                "DisablePagingExecutive": 1
            },

            # 网络优化
            "HKEY_LOCAL_MACHINE\\SYSTEM\\CurrentControlSet\\Services\\Tcpip\\Parameters": {
                "TcpWindowSize": 65535,
                "Tcp1323Opts": 1,
                "DefaultTTL": 64,
                "EnablePMTUDiscovery": 1,
                "SackOpts": 1,
                "MaxFreeTcbs": 65535
            },

            # 文件系统优化
            "HKEY_LOCAL_MACHINE\\SYSTEM\\CurrentControlSet\\Control\\FileSystem": {
                "NtfsDisableLastAccessUpdate": 1,
                "NtfsMemoryUsage": 2
            },

            # UI响应优化
            "HKEY_CURRENT_USER\\Control Panel\\Desktop": {
                "MenuShowDelay": 200,
                "WaitToKillAppTimeout": 20000,
                "HungAppTimeout": 5000,
                "AutoEndTasks": 1
            }
        }

    def backup_registry_key(self, key_path: str, backup_dir: Path) -> bool:
        """备份注册表键"""
        try:
            backup_file = backup_dir / f"{key_path.replace('\\\\', '_')}.reg"
            cmd = f'reg export "{key_path}" "{backup_file}" /y'

            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                self.logger.info(f"已备份注册表键: {key_path}")
                return True
            else:
                self.logger.error(f"备份注册表键失败 {key_path}: {result.stderr}")
                return False

        except Exception as e:
            self.logger.error(f"备份注册表键时发生错误 {key_path}: {e}")
            return False

    def cleanup_registry_key(self, key_path: str) -> bool:
        """清理指定的注册表键"""
        try:
            # 先检查键是否存在
            cmd = f'reg query "{key_path}"'
            result = subprocess.run(cmd, shell=True, capture_output=True)

            if result.returncode != 0:
                self.logger.info(f"注册表键不存在，跳过: {key_path}")
                return True

            # 删除键值
            cmd = f'reg delete "{key_path}" /f'
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

            if result.returncode == 0:
                self.logger.info(f"已清理注册表键: {key_path}")
                return True
            else:
                self.logger.error(f"清理注册表键失败 {key_path}: {result.stderr}")
                return False

        except Exception as e:
            self.logger.error(f"清理注册表键时发生错误 {key_path}: {e}")
            return False

    def set_registry_value(self, key_path: str, value_name: str, value_data: str, value_type: str = "REG_DWORD") -> bool:
        """设置注册表值"""
        try:
            # 确保键存在
            cmd = f'reg add "{key_path}" /f'
            subprocess.run(cmd, shell=True, capture_output=True)

            # 设置值
            cmd = f'reg add "{key_path}" /v "{value_name}" /t {value_type} /d "{value_data}" /f'
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

            if result.returncode == 0:
                self.logger.info(f"已设置注册表值: {key_path}\\{value_name} = {value_data}")
                return True
            else:
                self.logger.error(f"设置注册表值失败 {key_path}\\{value_name}: {result.stderr}")
                return False

        except Exception as e:
            self.logger.error(f"设置注册表值时发生错误 {key_path}\\{value_name}: {e}")
            return False

    def optimize_registry_settings(self) -> Dict:
        """优化注册表设置"""
        results = {
            "optimized_keys": 0,
            "failed_keys": 0,
            "details": []
        }

        for key_path, settings in self.optimization_settings.items():
            try:
                success_count = 0
                for value_name, value_data in settings.items():
                    if self.set_registry_value(key_path, value_name, str(value_data)):
                        success_count += 1

                results["details"].append({
                    "key": key_path,
                    "total_values": len(settings),
                    "success_count": success_count,
                    "success_rate": success_count / len(settings) * 100
                })

                if success_count == len(settings):
                    results["optimized_keys"] += 1
                else:
                    results["failed_keys"] += 1

            except Exception as e:
                self.logger.error(f"优化注册表设置时发生错误 {key_path}: {e}")
                results["failed_keys"] += 1

        return results

    def run_cleanup(self, backup_dir: Path = None) -> Dict:
        """运行注册表清理"""
        results = {
            "cleaned_keys": 0,
            "skipped_keys": 0,
            "failed_keys": 0,
            "details": []
        }

        for key_path in self.cleanup_paths:
            try:
                # 备份
                if backup_dir:
                    self.backup_registry_key(key_path, backup_dir)

                # 清理
                if self.cleanup_registry_key(key_path):
                    results["cleaned_keys"] += 1
                    results["details"].append({
                        "key": key_path,
                        "status": "success",
                        "message": "清理成功"
                    })
                else:
                    results["failed_keys"] += 1
                    results["details"].append({
                        "key": key_path,
                        "status": "failed",
                        "message": "清理失败"
                    })

            except Exception as e:
                self.logger.error(f"处理注册表键时发生错误 {key_path}: {e}")
                results["failed_keys"] += 1
                results["details"].append({
                    "key": key_path,
                    "status": "error",
                    "message": f"处理错误: {str(e)}"
                })

        return results

def main():
    """主函数"""
    import tempfile

    try:
        cleaner = RegistryCleaner()

        # 创建临时备份目录
        backup_dir = Path(tempfile.mkdtemp(prefix="reg_backup_"))

        # 执行清理
        cleanup_results = cleaner.run_cleanup(backup_dir)

        # 执行优化
        optimization_results = cleaner.optimize_registry_settings()

        # 合并结果
        combined_results = {
            "success": True,
            "message": "注册表清理和优化完成",
            "details": {
                "cleanup": cleanup_results,
                "optimization": optimization_results
            }
        }

        # 记录摘要
        logger = logging.getLogger('RegistryCleaner')
        logger.info(f"注册表清理完成: 清理了 {cleanup_results['cleaned_keys']} 个键")
        logger.info(f"注册表优化完成: 优化了 {optimization_results['optimized_keys']} 个键")

        return combined_results

    except Exception as e:
        logger = logging.getLogger('RegistryCleaner')
        logger.error(f"注册表清理器执行失败: {e}")

        return {
            "success": False,
            "message": f"注册表清理失败: {str(e)}",
            "details": None
        }

if __name__ == "__main__":
    # 设置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    result = main()
    print(json.dumps(result, indent=2, ensure_ascii=False))