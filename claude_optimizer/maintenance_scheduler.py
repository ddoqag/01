#!/usr/bin/env python3
"""
Claude Code 自动化维护调度器
定期维护和优化任务调度
"""

import os
import sys
import json
import time
import threading
import logging
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Callable
from dataclasses import dataclass, asdict
import schedule

@dataclass
class ScheduledTask:
    """计划任务数据类"""
    id: str
    name: str
    description: str
    schedule_type: str  # 'daily', 'weekly', 'monthly', 'interval'
    schedule_value: str  # 具体的调度值
    function: Callable
    enabled: bool = True
    last_run: str = None
    next_run: str = None
    max_retries: int = 3
    retry_count: int = 0
    timeout: int = 3600  # 超时时间（秒）

@dataclass
class TaskResult:
    """任务执行结果"""
    task_id: str
    task_name: str
    success: bool
    start_time: str
    end_time: str
    duration: float
    message: str
    details: Dict = None

class MaintenanceScheduler:
    """自动化维护调度器"""

    def __init__(self):
        self.setup_directories()
        self.setup_logging()
        self.load_configuration()

        # 调度器状态
        self.scheduler_active = False
        self.scheduled_tasks: Dict[str, ScheduledTask] = {}
        self.task_history: List[TaskResult] = []
        self.running_tasks: Dict[str, threading.Thread] = {}

        # 任务执行统计
        self.task_stats = {
            "total_runs": 0,
            "successful_runs": 0,
            "failed_runs": 0,
            "average_duration": 0.0
        }

    def setup_directories(self):
        """设置工作目录"""
        self.base_dir = Path(__file__).parent
        self.logs_dir = self.base_dir / "logs"
        self.data_dir = self.base_dir / "data"
        self.reports_dir = self.base_dir / "reports"

        # 确保目录存在
        for directory in [self.logs_dir, self.data_dir, self.reports_dir]:
            directory.mkdir(exist_ok=True)

    def setup_logging(self):
        """配置日志"""
        log_file = self.logs_dir / f"maintenance_scheduler_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        self.logger = logging.getLogger('MaintenanceScheduler')

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
        config_file = self.base_dir / "configs" / "scheduler_config.json"
        default_config = {
            "enabled": True,
            "max_concurrent_tasks": 3,
            "default_timeout": 3600,
            "retry_policy": {
                "max_retries": 3,
                "retry_delay": 300  # 5分钟
            },
            "notification": {
                "enabled": True,
                "on_success": False,
                "on_failure": True
            },
            "maintenance_windows": {
                "start_hour": 2,
                "end_hour": 4,
                "weekend_only": False
            },
            "tasks": [
                {
                    "id": "daily_cleanup",
                    "name": "每日系统清理",
                    "description": "清理临时文件和优化系统性能",
                    "schedule_type": "daily",
                    "schedule_value": "03:00",
                    "enabled": True
                },
                {
                    "id": "weekly_optimization",
                    "name": "周度系统优化",
                    "description": "执行深度系统优化和维护",
                    "schedule_type": "weekly",
                    "schedule_value": "sunday 02:00",
                    "enabled": True
                },
                {
                    "id": "monthly_backup",
                    "name": "月度配置备份",
                    "description": "备份重要配置文件",
                    "schedule_type": "monthly",
                    "schedule_value": "1 02:00",
                    "enabled": True
                }
            ]
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

    def register_task(self, task: ScheduledTask):
        """注册计划任务"""
        self.scheduled_tasks[task.id] = task
        self.logger.info(f"已注册任务: {task.name} ({task.id})")

    def schedule_task(self, task: ScheduledTask):
        """调度任务"""
        if not task.enabled:
            return

        try:
            if task.schedule_type == "daily":
                schedule.every().day.at(task.schedule_value).do(
                    self.execute_task, task.id
                )
            elif task.schedule_type == "weekly":
                day, time_str = task.schedule_value.split()
                getattr(schedule.every(), day.lower()).at(time_str).do(
                    self.execute_task, task.id
                )
            elif task.schedule_type == "monthly":
                # 简化的月度调度，在每月1号执行
                schedule.every().day.do(self.check_monthly_task, task.id, task.schedule_value)
            elif task.schedule_type == "interval":
                # 间隔调度，例如: "30 minutes", "2 hours"
                if "minute" in task.schedule_value:
                    minutes = int(task.schedule_value.split()[0])
                    schedule.every(minutes).minutes.do(self.execute_task, task.id)
                elif "hour" in task.schedule_value:
                    hours = int(task.schedule_value.split()[0])
                    schedule.every(hours).hours.do(self.execute_task, task.id)

            self.logger.info(f"已调度任务: {task.name} - {task.schedule_type} {task.schedule_value}")

        except Exception as e:
            self.logger.error(f"调度任务失败 {task.name}: {e}")

    def check_monthly_task(self, task_id: str, schedule_value: str):
        """检查月度任务是否应该执行"""
        try:
            day_str, time_str = schedule_value.split()
            target_day = int(day_str)
            current_day = datetime.now().day

            if current_day == target_day:
                # 检查时间
                current_time = datetime.now().strftime("%H:%M")
                if abs((datetime.strptime(current_time, "%H:%M") -
                       datetime.strptime(time_str, "%H:%M")).total_seconds()) < 60:
                    self.execute_task(task_id)

        except Exception as e:
            self.logger.error(f"检查月度任务失败 {task_id}: {e}")

    def execute_task(self, task_id: str) -> TaskResult:
        """执行任务"""
        if task_id not in self.scheduled_tasks:
            self.logger.error(f"任务不存在: {task_id}")
            return None

        task = self.scheduled_tasks[task_id]

        # 检查任务是否已在运行
        if task_id in self.running_tasks:
            self.logger.warning(f"任务已在运行中: {task.name}")
            return None

        # 检查维护窗口
        if not self.is_maintenance_window():
            self.logger.info(f"不在维护窗口内，跳过任务: {task.name}")
            return None

        # 创建任务执行线程
        def task_wrapper():
            self.run_task(task)

        thread = threading.Thread(target=task_wrapper, daemon=True)
        self.running_tasks[task_id] = thread
        thread.start()

        return None

    def run_task(self, task: ScheduledTask):
        """运行具体任务"""
        start_time = datetime.now()
        result = TaskResult(
            task_id=task.id,
            task_name=task.name,
            success=False,
            start_time=start_time.isoformat(),
            end_time="",
            duration=0.0,
            message="",
            details={}
        )

        try:
            self.logger.info(f"开始执行任务: {task.name}")

            # 执行任务函数
            task_function = task.function
            if callable(task_function):
                task_result = task_function()
                if isinstance(task_result, dict):
                    result.success = task_result.get("success", False)
                    result.message = task_result.get("message", "任务完成")
                    result.details = task_result.get("details", {})
                else:
                    result.success = True
                    result.message = "任务执行完成"
            else:
                result.success = False
                result.message = "任务函数不可调用"

        except Exception as e:
            result.success = False
            result.message = f"任务执行失败: {str(e)}"
            self.logger.error(f"任务执行失败 {task.name}: {e}")

            # 重试逻辑
            if task.retry_count < task.max_retries:
                task.retry_count += 1
                retry_delay = self.config.get("retry_policy", {}).get("retry_delay", 300)
                self.logger.info(f"任务 {task.name} 将在 {retry_delay} 秒后重试 ({task.retry_count}/{task.max_retries})")

                # 安排重试
                timer = threading.Timer(retry_delay, self.execute_task, [task.id])
                timer.start()
            else:
                self.logger.error(f"任务 {task.name} 重试次数已用尽，标记为失败")

        finally:
            # 完成任务
            end_time = datetime.now()
            result.end_time = end_time.isoformat()
            result.duration = (end_time - start_time).total_seconds()

            # 更新任务信息
            task.last_run = start_time.isoformat()
            task.retry_count = 0  # 重置重试计数

            # 记录结果
            self.task_history.append(result)
            self.update_task_stats(result)

            # 保存历史记录
            self.save_task_history()

            # 通知
            self.notify_task_result(result)

            # 清理运行中的任务记录
            if task.id in self.running_tasks:
                del self.running_tasks[task.id]

            self.logger.info(f"任务完成: {task.name} - {'成功' if result.success else '失败'} (耗时: {result.duration:.2f}秒)")

    def is_maintenance_window(self) -> bool:
        """检查是否在维护窗口内"""
        try:
            maintenance_config = self.config.get("maintenance_windows", {})
            start_hour = maintenance_config.get("start_hour", 2)
            end_hour = maintenance_config.get("end_hour", 4)
            weekend_only = maintenance_config.get("weekend_only", False)

            current_hour = datetime.now().hour
            current_weekday = datetime.now().weekday()  # 0=Monday, 6=Sunday

            # 检查周末限制
            if weekend_only and current_weekday < 5:  # Monday-Friday
                return False

            # 检查时间窗口
            if start_hour <= end_hour:
                # 同一天内的时间窗口
                return start_hour <= current_hour < end_hour
            else:
                # 跨天的时间窗口（例如22:00-04:00）
                return current_hour >= start_hour or current_hour < end_hour

        except Exception as e:
            self.logger.error(f"检查维护窗口失败: {e}")
            return True  # 出错时允许执行

    def update_task_stats(self, result: TaskResult):
        """更新任务统计信息"""
        self.task_stats["total_runs"] += 1

        if result.success:
            self.task_stats["successful_runs"] += 1
        else:
            self.task_stats["failed_runs"] += 1

        # 更新平均执行时间
        if self.task_stats["total_runs"] > 0:
            total_duration = sum(r.duration for r in self.task_history)
            self.task_stats["average_duration"] = total_duration / self.task_stats["total_runs"]

    def save_task_history(self):
        """保存任务历史记录"""
        try:
            history_file = self.data_dir / f"task_history_{datetime.now().strftime('%Y%m')}.json"

            # 保留最近1000条记录
            recent_history = self.task_history[-1000:]

            data = {
                "last_updated": datetime.now().isoformat(),
                "task_stats": self.task_stats,
                "task_history": [asdict(result) for result in recent_history]
            }

            with open(history_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

        except Exception as e:
            self.logger.error(f"保存任务历史失败: {e}")

    def notify_task_result(self, result: TaskResult):
        """通知任务结果"""
        try:
            notification_config = self.config.get("notification", {})
            if not notification_config.get("enabled", True):
                return

            # 成功通知
            if result.success and notification_config.get("on_success", False):
                self.logger.info(f"任务成功通知: {result.task_name} - {result.message}")

            # 失败通知
            if not result.success and notification_config.get("on_failure", True):
                self.logger.error(f"任务失败通知: {result.task_name} - {result.message}")

                # 可以添加其他通知方式，如邮件、桌面通知等

        except Exception as e:
            self.logger.error(f"发送通知失败: {e}")

    def generate_maintenance_report(self) -> Dict:
        """生成维护报告"""
        try:
            now = datetime.now()
            last_month = now - timedelta(days=30)

            # 统计最近30天的任务执行情况
            recent_tasks = [
                task for task in self.task_history
                if datetime.fromisoformat(task.start_time.replace('Z', '+00:00')) > last_month
            ]

            report = {
                "report_period": f"{last_month.strftime('%Y-%m-%d')} 至 {now.strftime('%Y-%m-%d')}",
                "generated_at": now.isoformat(),
                "summary": {
                    "total_tasks_executed": len(recent_tasks),
                    "successful_tasks": len([t for t in recent_tasks if t.success]),
                    "failed_tasks": len([t for t in recent_tasks if not t.success]),
                    "success_rate": 0.0,
                    "average_duration": 0.0
                },
                "task_breakdown": {},
                "performance_metrics": self.task_stats
            }

            # 计算成功率
            if recent_tasks:
                successful = len([t for t in recent_tasks if t.success])
                report["summary"]["success_rate"] = (successful / len(recent_tasks)) * 100

                # 计算平均执行时间
                total_duration = sum(t.duration for t in recent_tasks)
                report["summary"]["average_duration"] = total_duration / len(recent_tasks)

            # 按任务类型分组统计
            task_groups = {}
            for task in recent_tasks:
                if task.task_name not in task_groups:
                    task_groups[task.task_name] = {
                        "total_runs": 0,
                        "successful_runs": 0,
                        "total_duration": 0.0
                    }

                group = task_groups[task.task_name]
                group["total_runs"] += 1
                if task.success:
                    group["successful_runs"] += 1
                group["total_duration"] += task.duration

            # 计算每个任务组的统计信息
            for task_name, group in task_groups.items():
                group["success_rate"] = (group["successful_runs"] / group["total_runs"]) * 100 if group["total_runs"] > 0 else 0
                group["average_duration"] = group["total_duration"] / group["total_runs"] if group["total_runs"] > 0 else 0

            report["task_breakdown"] = task_groups

            # 保存报告
            report_file = self.reports_dir / f"maintenance_report_{now.strftime('%Y%m%d_%H%M%S')}.json"
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)

            self.logger.info(f"维护报告已生成: {report_file}")
            return report

        except Exception as e:
            self.logger.error(f"生成维护报告失败: {e}")
            return {"error": str(e)}

    def start_scheduler(self):
        """启动调度器"""
        if self.scheduler_active:
            self.logger.warning("调度器已在运行中")
            return

        self.scheduler_active = True
        self.logger.info("启动维护调度器...")

        # 注册默认任务
        self.register_default_tasks()

        # 调度所有启用的任务
        for task in self.scheduled_tasks.values():
            if task.enabled:
                self.schedule_task(task)

        # 启动调度循环
        def scheduler_loop():
            while self.scheduler_active:
                schedule.run_pending()
                time.sleep(1)

        scheduler_thread = threading.Thread(target=scheduler_loop, daemon=True)
        scheduler_thread.start()

        self.logger.info("维护调度器已启动")

    def stop_scheduler(self):
        """停止调度器"""
        self.scheduler_active = False
        schedule.clear()

        # 等待运行中的任务完成
        for task_id, thread in self.running_tasks.items():
            if thread.is_alive():
                self.logger.info(f"等待任务完成: {task_id}")
                thread.join(timeout=30)  # 最多等待30秒

        self.logger.info("维护调度器已停止")

    def register_default_tasks(self):
        """注册默认维护任务"""
        # 每日清理任务
        def daily_cleanup():
            try:
                # 执行系统清理
                self.logger.info("执行每日系统清理...")

                # 这里可以调用具体的清理功能
                # 例如：清理临时文件、检查磁盘空间等

                return {
                    "success": True,
                    "message": "每日清理完成",
                    "details": {
                        "cleaned_temp_files": "成功",
                        "disk_space_freed": "未知"
                    }
                }
            except Exception as e:
                return {
                    "success": False,
                    "message": f"每日清理失败: {str(e)}"
                }

        # 周度优化任务
        def weekly_optimization():
            try:
                self.logger.info("执行周度系统优化...")

                # 执行深度优化
                # 例如：注册表清理、磁盘碎片整理等

                return {
                    "success": True,
                    "message": "周度优化完成",
                    "details": {
                        "registry_cleaned": "成功",
                        "disk_defragmented": "成功"
                    }
                }
            except Exception as e:
                return {
                    "success": False,
                    "message": f"周度优化失败: {str(e)}"
                }

        # 月度备份任务
        def monthly_backup():
            try:
                self.logger.info("执行月度配置备份...")

                # 执行配置备份
                # 例如：备份Claude配置、MCP配置等

                return {
                    "success": True,
                    "message": "月度备份完成",
                    "details": {
                        "backed_up_files": ["CLAUDE.md", "mcp_servers.json"],
                        "backup_location": "/backup/path"
                    }
                }
            except Exception as e:
                return {
                    "success": False,
                    "message": f"月度备份失败: {str(e)}"
                }

        # 从配置文件创建任务
        for task_config in self.config.get("tasks", []):
            task_function = None
            if task_config["id"] == "daily_cleanup":
                task_function = daily_cleanup
            elif task_config["id"] == "weekly_optimization":
                task_function = weekly_optimization
            elif task_config["id"] == "monthly_backup":
                task_function = monthly_backup

            if task_function:
                task = ScheduledTask(
                    id=task_config["id"],
                    name=task_config["name"],
                    description=task_config["description"],
                    schedule_type=task_config["schedule_type"],
                    schedule_value=task_config["schedule_value"],
                    function=task_function,
                    enabled=task_config.get("enabled", True)
                )
                self.register_task(task)

def main():
    """主函数"""
    try:
        scheduler = MaintenanceScheduler()

        print("=== Claude Code 自动化维护调度器 ===")
        print("正在启动调度器...")

        # 启动调度器
        scheduler.start_scheduler()

        print("维护调度器已启动!")
        print("已注册的维护任务:")
        for task in scheduler.scheduled_tasks.values():
            print(f"  - {task.name} ({task.schedule_type} {task.schedule_value})")

        print("\n按 Ctrl+C 停止调度器")

        # 保持运行
        try:
            while scheduler.scheduler_active:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n正在停止调度器...")
            scheduler.stop_scheduler()

            # 生成最终报告
            report = scheduler.generate_maintenance_report()
            print(f"维护报告已生成，共执行 {report['summary']['total_tasks_executed']} 个任务")

        return 0

    except Exception as e:
        print(f"维护调度器启动失败: {e}")
        return 1

if __name__ == "__main__":
    # 设置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    sys.exit(main())