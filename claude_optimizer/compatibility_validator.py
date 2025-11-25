#!/usr/bin/env python3
"""
Claude Code Windows 兼容性验证套件
持续验证Windows兼容性和系统健康状态
"""

import os
import sys
import json
import time
import logging
import subprocess
import platform
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict

@dataclass
class CompatibilityTest:
    """兼容性测试数据类"""
    id: str
    name: str
    description: str
    category: str  # 'system', 'software', 'hardware', 'network'
    severity: str  # 'critical', 'warning', 'info'
    enabled: bool = True
    last_result: Dict = None
    last_run: str = None

@dataclass
class TestResult:
    """测试结果数据类"""
    test_id: str
    test_name: str
    success: bool
    severity: str
    message: str
    details: Dict = None
    timestamp: str = None
    execution_time: float = 0.0

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()

class CompatibilityValidator:
    """兼容性验证器"""

    def __init__(self):
        self.setup_directories()
        self.setup_logging()
        self.load_configuration()

        # 测试套件
        self.compatibility_tests: Dict[str, CompatibilityTest] = {}
        self.test_history: List[TestResult] = []
        self.validation_active = False

        # 系统信息缓存
        self.system_info = {}
        self.last_system_update = None

        # 注册默认测试
        self.register_default_tests()

    def setup_directories(self):
        """设置工作目录"""
        self.base_dir = Path(__file__).parent
        self.logs_dir = self.base_dir / "logs"
        self.reports_dir = self.base_dir / "reports"
        self.data_dir = self.base_dir / "data"

        # 确保目录存在
        for directory in [self.logs_dir, self.reports_dir, self.data_dir]:
            directory.mkdir(exist_ok=True)

    def setup_logging(self):
        """配置日志"""
        log_file = self.logs_dir / f"compatibility_validator_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        self.logger = logging.getLogger('CompatibilityValidator')

        if not self.logger.handlers:
            logging.basicConfig(
                level=logging.INFO,
                format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                handlers=[
                    logging.FileHandler(log_file, encoding='utf-8'),
                    logging.StreamHandler(sys.stdout)
                ]
            )

    def load_configuration(self):
        """加载配置"""
        config_file = self.base_dir / "configs" / "compatibility_config.json"
        default_config = {
            "enabled": True,
            "validation_interval": 3600,  # 1小时
            "auto_repair": True,
            "notification": {
                "enabled": True,
                "critical_only": True
            },
            "test_categories": {
                "system": True,
                "software": True,
                "hardware": True,
                "network": True
            },
            "windows_requirements": {
                "min_version": "10.0",
                "required_services": ["RpcSs", "DcomLaunch", "PlugPlay"],
                "critical_paths": [
                    "C:\\Windows",
                    "C:\\Windows\\System32"
                ]
            },
            "custom_tests": []
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
            self.logger.error(f"加载配置失败: {e}")
            self.config = default_config

    def register_test(self, test: CompatibilityTest):
        """注册兼容性测试"""
        self.compatibility_tests[test.id] = test
        self.logger.info(f"已注册测试: {test.name} ({test.id})")

    def register_default_tests(self):
        """注册默认兼容性测试"""

        # 系统版本测试
        def test_windows_version():
            try:
                version_info = platform.win32_ver()
                build_number = version_info[2] if len(version_info) > 2 else ""

                min_version = self.config.get("windows_requirements", {}).get("min_version", "10.0")
                current_version = platform.version()

                # 简单版本比较
                if current_version >= min_version:
                    return {
                        "success": True,
                        "message": f"Windows版本兼容: {current_version}",
                        "details": {
                            "current_version": current_version,
                            "min_required": min_version,
                            "build_number": build_number
                        }
                    }
                else:
                    return {
                        "success": False,
                        "message": f"Windows版本过低: {current_version} (需要 >= {min_version})",
                        "details": {
                            "current_version": current_version,
                            "min_required": min_version
                        }
                    }
            except Exception as e:
                return {
                    "success": False,
                    "message": f"版本检查失败: {str(e)}"
                }

        # 系统服务测试
        def test_system_services():
            try:
                required_services = self.config.get("windows_requirements", {}).get("required_services", [])
                results = {}

                for service in required_services:
                    try:
                        cmd = f'sc query "{service}"'
                        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

                        if result.returncode == 0 and "RUNNING" in result.stdout:
                            results[service] = {"status": "running", "success": True}
                        else:
                            results[service] = {"status": "stopped", "success": False}
                    except Exception as e:
                        results[service] = {"status": "error", "error": str(e), "success": False}

                failed_services = [s for s, r in results.items() if not r.get("success", False)]

                if not failed_services:
                    return {
                        "success": True,
                        "message": "所有必需服务运行正常",
                        "details": results
                    }
                else:
                    return {
                        "success": False,
                        "message": f"服务异常: {', '.join(failed_services)}",
                        "details": results
                    }

            except Exception as e:
                return {
                    "success": False,
                    "message": f"服务检查失败: {str(e)}"
                }

        # 磁盘空间测试
        def test_disk_space():
            try:
                cmd = 'wmic logicaldisk get DeviceID,FreeSpace,Size /format:csv'
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

                if result.returncode != 0:
                    return {
                        "success": False,
                        "message": "无法获取磁盘信息"
                    }

                lines = result.stdout.strip().split('\n')[1:]  # 跳过头部
                disk_info = {}
                critical_disks = []

                for line in lines:
                    if line.strip():
                        parts = line.split(',')
                        if len(parts) >= 4:
                            drive = parts[0].strip('"')
                            free_space = int(parts[1].strip('"')) if parts[1].strip('"') else 0
                            total_space = int(parts[3].strip('"')) if parts[3].strip('"') else 0

                            if total_space > 0:
                                usage_percent = ((total_space - free_space) / total_space) * 100
                                disk_info[drive] = {
                                    "total_gb": total_space // (1024**3),
                                    "free_gb": free_space // (1024**3),
                                    "usage_percent": round(usage_percent, 2)
                                }

                                if usage_percent > 90:
                                    critical_disks.append(drive)

                if not critical_disks:
                    return {
                        "success": True,
                        "message": "磁盘空间充足",
                        "details": disk_info
                    }
                else:
                    return {
                        "success": False,
                        "message": f"磁盘空间不足: {', '.join(critical_disks)}",
                        "details": disk_info
                    }

            except Exception as e:
                return {
                    "success": False,
                    "message": f"磁盘空间检查失败: {str(e)}"
                }

        # 内存测试
        def test_memory():
            try:
                cmd = 'wmic OS get TotalVisibleMemorySize,FreePhysicalMemory /value'
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

                if result.returncode != 0:
                    return {
                        "success": False,
                        "message": "无法获取内存信息"
                    }

                total_memory = 0
                free_memory = 0

                for line in result.stdout.strip().split('\n'):
                    if 'TotalVisibleMemorySize' in line and '=' in line:
                        total_memory = int(line.split('=')[1].strip())
                    elif 'FreePhysicalMemory' in line and '=' in line:
                        free_memory = int(line.split('=')[1].strip())

                if total_memory > 0:
                    usage_percent = ((total_memory - free_memory) / total_memory) * 100

                    return {
                        "success": usage_percent < 90,
                        "message": f"内存使用率: {usage_percent:.1f}%",
                        "details": {
                            "total_mb": total_memory,
                            "free_mb": free_memory,
                            "usage_percent": round(usage_percent, 2)
                        }
                    }
                else:
                    return {
                        "success": False,
                        "message": "无法解析内存信息"
                    }

            except Exception as e:
                return {
                    "success": False,
                    "message": f"内存检查失败: {str(e)}"
                }

        # 网络连接测试
        def test_network_connectivity():
            try:
                # 测试本地连接
                cmd = 'ping -n 1 127.0.0.1'
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

                if result.returncode != 0:
                    return {
                        "success": False,
                        "message": "本地网络连接失败"
                    }

                # 测试DNS解析
                cmd = 'nslookup google.com'
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

                if result.returncode != 0:
                    return {
                        "success": False,
                        "message": "DNS解析失败"
                    }

                return {
                    "success": True,
                    "message": "网络连接正常",
                    "details": {
                        "local_loopback": "OK",
                        "dns_resolution": "OK"
                    }
                }

            except Exception as e:
                return {
                    "success": False,
                    "message": f"网络测试失败: {str(e)}"
                }

        # 文件权限测试
        def test_file_permissions():
            try:
                critical_paths = self.config.get("windows_requirements", {}).get("critical_paths", [])
                results = {}

                for path in critical_paths:
                    path_obj = Path(path)
                    if path_obj.exists():
                        try:
                            # 测试读取权限
                            if path_obj.is_dir():
                                list(path_obj.iterdir())
                            else:
                                path_obj.read_bytes()
                            results[path] = {"status": "accessible", "success": True}
                        except PermissionError:
                            results[path] = {"status": "permission_denied", "success": False}
                        except Exception as e:
                            results[path] = {"status": "error", "error": str(e), "success": False}
                    else:
                        results[path] = {"status": "not_found", "success": False}

                failed_paths = [p for p, r in results.items() if not r.get("success", False)]

                if not failed_paths:
                    return {
                        "success": True,
                        "message": "所有关键路径可访问",
                        "details": results
                    }
                else:
                    return {
                        "success": False,
                        "message": f"路径访问异常: {', '.join(failed_paths)}",
                        "details": results
                    }

            except Exception as e:
                return {
                    "success": False,
                    "message": f"权限检查失败: {str(e)}"
                }

        # 注册所有测试
        tests = [
            CompatibilityTest("windows_version", "Windows版本检查", "验证Windows版本兼容性", "system", "critical", test_windows_version),
            CompatibilityTest("system_services", "系统服务检查", "验证关键系统服务状态", "system", "critical", test_system_services),
            CompatibilityTest("disk_space", "磁盘空间检查", "验证磁盘空间充足", "hardware", "warning", test_disk_space),
            CompatibilityTest("memory_check", "内存状态检查", "验证内存使用情况", "hardware", "warning", test_memory),
            CompatibilityTest("network_connectivity", "网络连接检查", "验证网络连接状态", "network", "info", test_network_connectivity),
            CompatibilityTest("file_permissions", "文件权限检查", "验证关键路径访问权限", "system", "critical", test_file_permissions)
        ]

        for test in tests:
            self.register_test(test)

    def run_test(self, test_id: str) -> TestResult:
        """运行单个兼容性测试"""
        if test_id not in self.compatibility_tests:
            raise ValueError(f"测试不存在: {test_id}")

        test = self.compatibility_tests[test_id]
        if not test.enabled:
            return None

        start_time = time.time()
        test_result = None

        try:
            self.logger.info(f"开始执行测试: {test.name}")

            # 执行测试函数
            if callable(test.function):
                result_data = test.function()

                test_result = TestResult(
                    test_id=test.id,
                    test_name=test.name,
                    success=result_data.get("success", False),
                    severity=test.severity,
                    message=result_data.get("message", "测试完成"),
                    details=result_data.get("details"),
                    execution_time=(time.time() - start_time) * 1000
                )

                # 更新测试的最后结果
                test.last_result = asdict(test_result)
                test.last_run = test_result.timestamp

            else:
                test_result = TestResult(
                    test_id=test.id,
                    test_name=test.name,
                    success=False,
                    severity="critical",
                    message="测试函数不可调用",
                    execution_time=(time.time() - start_time) * 1000
                )

        except Exception as e:
            test_result = TestResult(
                test_id=test.id,
                test_name=test.name,
                success=False,
                severity=test.severity,
                message=f"测试执行失败: {str(e)}",
                execution_time=(time.time() - start_time) * 1000
            )

        # 记录测试结果
        self.test_history.append(test_result)

        # 记录日志
        if test_result.success:
            self.logger.info(f"测试通过: {test.name} - {test_result.message}")
        else:
            level = "WARNING" if test_result.severity == "warning" else "ERROR"
            self.logger.log(getattr(logging, level), f"测试失败: {test.name} - {test_result.message}")

        return test_result

    def run_all_tests(self, categories: List[str] = None) -> List[TestResult]:
        """运行所有兼容性测试"""
        results = []

        # 确定要运行的测试类别
        if categories is None:
            enabled_categories = [
                cat for cat, enabled in self.config.get("test_categories", {}).items()
                if enabled
            ]
        else:
            enabled_categories = categories

        for test_id, test in self.compatibility_tests.items():
            if test.enabled and (not categories or test.category in enabled_categories):
                try:
                    result = self.run_test(test_id)
                    if result:
                        results.append(result)
                except Exception as e:
                    self.logger.error(f"运行测试失败 {test_id}: {e}")

        # 保存测试结果
        self.save_test_results()

        # 生成报告
        self.generate_compatibility_report(results)

        return results

    def save_test_results(self):
        """保存测试结果"""
        try:
            results_file = self.data_dir / f"compatibility_results_{datetime.now().strftime('%Y%m')}.json"

            # 保留最近1000条记录
            recent_results = self.test_history[-1000:]

            data = {
                "last_updated": datetime.now().isoformat(),
                "test_results": [asdict(result) for result in recent_results],
                "system_info": self.get_system_info()
            }

            with open(results_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

        except Exception as e:
            self.logger.error(f"保存测试结果失败: {e}")

    def get_system_info(self) -> Dict:
        """获取系统信息"""
        try:
            # 缓存系统信息，避免频繁查询
            if (self.last_system_update and
                (datetime.now() - datetime.fromisoformat(self.last_system_update)).seconds < 300):
                return self.system_info

            system_info = {
                "platform": platform.platform(),
                "system": platform.system(),
                "release": platform.release(),
                "version": platform.version(),
                "machine": platform.machine(),
                "processor": platform.processor(),
                "python_version": platform.python_version(),
                "architecture": platform.architecture()[0],
                "timestamp": datetime.now().isoformat()
            }

            # 获取Windows特定信息
            try:
                win_info = platform.win32_ver()
                system_info["windows_info"] = {
                    "version": win_info[0] if len(win_info) > 0 else "",
                    "csd": win_info[1] if len(win_info) > 1 else "",
                    "ptype": win_info[2] if len(win_info) > 2 else "",
                    "build_number": win_info[3] if len(win_info) > 3 else ""
                }
            except:
                pass

            # 获取内存信息
            try:
                cmd = 'wmic computersystem get TotalPhysicalMemory /value'
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                if result.returncode == 0:
                    for line in result.stdout.strip().split('\n'):
                        if 'TotalPhysicalMemory' in line and '=' in line:
                            memory_bytes = int(line.split('=')[1].strip())
                            system_info["total_memory_gb"] = memory_bytes // (1024**3)
            except:
                pass

            self.system_info = system_info
            self.last_system_update = datetime.now().isoformat()

            return system_info

        except Exception as e:
            self.logger.error(f"获取系统信息失败: {e}")
            return {"error": str(e)}

    def generate_compatibility_report(self, test_results: List[TestResult]) -> Dict:
        """生成兼容性报告"""
        try:
            now = datetime.now()

            # 统计测试结果
            total_tests = len(test_results)
            passed_tests = len([r for r in test_results if r.success])
            failed_tests = total_tests - passed_tests

            critical_failures = len([
                r for r in test_results
                if not r.success and r.severity == "critical"
            ])
            warning_failures = len([
                r for r in test_results
                if not r.success and r.severity == "warning"
            ])

            # 按类别分组
            category_results = {}
            for result in test_results:
                test = self.compatibility_tests.get(result.test_id)
                if test:
                    category = test.category
                    if category not in category_results:
                        category_results[category] = {"total": 0, "passed": 0, "failed": 0}

                    category_results[category]["total"] += 1
                    if result.success:
                        category_results[category]["passed"] += 1
                    else:
                        category_results[category]["failed"] += 1

            report = {
                "report_metadata": {
                    "generated_at": now.isoformat(),
                    "total_tests": total_tests,
                    "passed_tests": passed_tests,
                    "failed_tests": failed_tests,
                    "success_rate": (passed_tests / total_tests * 100) if total_tests > 0 else 0,
                    "critical_failures": critical_failures,
                    "warning_failures": warning_failures,
                    "overall_status": "PASS" if critical_failures == 0 else "FAIL"
                },
                "system_info": self.get_system_info(),
                "category_breakdown": category_results,
                "test_results": [asdict(result) for result in test_results],
                "recommendations": self.generate_recommendations(test_results)
            }

            # 保存报告
            report_file = self.reports_dir / f"compatibility_report_{now.strftime('%Y%m%d_%H%M%S')}.json"
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)

            self.logger.info(f"兼容性报告已生成: {report_file}")
            return report

        except Exception as e:
            self.logger.error(f"生成兼容性报告失败: {e}")
            return {"error": str(e)}

    def generate_recommendations(self, test_results: List[TestResult]) -> List[str]:
        """基于测试结果生成建议"""
        recommendations = []

        for result in test_results:
            if not result.success:
                test = self.compatibility_tests.get(result.test_id)
                if test:
                    if test.id == "windows_version":
                        recommendations.append("建议升级Windows版本以满足系统要求")
                    elif test.id == "system_services":
                        recommendations.append("检查并修复系统服务配置")
                    elif test.id == "disk_space":
                        recommendations.append("清理磁盘空间或扩展存储容量")
                    elif test.id == "memory_check":
                        recommendations.append("关闭不必要的程序或增加内存容量")
                    elif test.id == "network_connectivity":
                        recommendations.append("检查网络连接和DNS配置")
                    elif test.id == "file_permissions":
                        recommendations.append("修复文件权限或检查用户账户权限")

        # 通用建议
        failed_critical = len([
            r for r in test_results
            if not r.success and r.severity == "critical"
        ])

        if failed_critical > 0:
            recommendations.append(f"发现 {failed_critical} 个关键问题，建议立即修复以确保系统正常运行")

        if not recommendations:
            recommendations.append("所有兼容性测试通过，系统运行正常")

        return recommendations

    def start_continuous_validation(self):
        """启动持续兼容性验证"""
        if self.validation_active:
            self.logger.warning("兼容性验证已在运行中")
            return

        self.validation_active = True
        self.logger.info("启动持续兼容性验证...")

        def validation_loop():
            while self.validation_active:
                try:
                    # 运行所有测试
                    results = self.run_all_tests()

                    # 检查是否需要通知
                    critical_failures = [
                        r for r in results
                        if not r.success and r.severity == "critical"
                    ]

                    if critical_failures and self.config.get("notification", {}).get("enabled", True):
                        self.logger.error(f"发现 {len(critical_failures)} 个关键兼容性问题")

                    # 等待下次验证
                    interval = self.config.get("validation_interval", 3600)
                    time.sleep(interval)

                except Exception as e:
                    self.logger.error(f"兼容性验证循环错误: {e}")
                    time.sleep(60)  # 出错时等待1分钟重试

        validation_thread = threading.Thread(target=validation_loop, daemon=True)
        validation_thread.start()

        self.logger.info("持续兼容性验证已启动")

    def stop_continuous_validation(self):
        """停止持续兼容性验证"""
        self.validation_active = False
        self.logger.info("持续兼容性验证已停止")

def main():
    """主函数"""
    import threading

    try:
        validator = CompatibilityValidator()

        print("=== Claude Code Windows 兼容性验证套件 ===")
        print("正在执行兼容性检查...")

        # 运行所有兼容性测试
        test_results = validator.run_all_tests()

        # 显示结果摘要
        total_tests = len(test_results)
        passed_tests = len([r for r in test_results if r.success])
        failed_tests = total_tests - passed_tests

        print(f"\n=== 兼容性验证结果 ===")
        print(f"总测试数: {total_tests}")
        print(f"通过: {passed_tests}")
        print(f"失败: {failed_tests}")
        print(f"成功率: {(passed_tests/total_tests*100):.1f}%")

        if failed_tests > 0:
            print("\n失败的测试:")
            for result in test_results:
                if not result.success:
                    print(f"  - {result.test_name} ({result.severity}): {result.message}")

        # 生成并显示报告
        report = validator.generate_compatibility_report(test_results)

        print(f"\n=== 建议和修复措施 ===")
        for i, recommendation in enumerate(report.get("recommendations", []), 1):
            print(f"{i}. {recommendation}")

        # 询问是否启动持续验证
        if failed_tests == 0:
            print("\n✓ 系统兼容性检查通过！")

            response = input("\n是否启动持续兼容性监控? (y/N): ").strip().lower()
            if response in ['y', 'yes']:
                print("启动持续兼容性验证...")
                validator.start_continuous_validation()
                print("持续验证已启动，按 Ctrl+C 停止")

                try:
                    while validator.validation_active:
                        time.sleep(1)
                except KeyboardInterrupt:
                    print("\n正在停止持续验证...")
                    validator.stop_continuous_validation()
        else:
            print("\n✗ 发现兼容性问题，请根据建议进行修复")

        return 0 if failed_tests == 0 else 1

    except Exception as e:
        print(f"兼容性验证失败: {e}")
        return 1

if __name__ == "__main__":
    # 设置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    sys.exit(main())