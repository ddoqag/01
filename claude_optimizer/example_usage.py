#!/usr/bin/env python3
"""
Claude Code Windows 系统优化工具使用示例
演示如何使用各个功能模块
"""

import sys
import time
from pathlib import Path

# 添加当前目录到路径
sys.path.insert(0, str(Path(__file__).parent))

def example_system_optimization():
    """示例：系统优化"""
    print("\n" + "="*50)
    print("示例1: 系统优化")
    print("="*50)

    from main import ClaudeOptimizer

    # 创建优化器实例
    optimizer = ClaudeOptimizer()

    # 运行优化
    print("开始系统优化...")
    success = optimizer.run_optimization()

    if success:
        print("✅ 系统优化完成!")
        print("📊 优化报告已生成在 logs/ 目录")
    else:
        print("❌ 系统优化失败，请查看日志")

def example_config_management():
    """示例：配置管理"""
    print("\n" + "="*50)
    print("示例2: 配置管理")
    print("="*50)

    from config_manager import IntelligentConfigManager

    # 创建配置管理器实例
    manager = IntelligentConfigManager()

    # 获取配置状态
    print("获取配置状态...")
    status = manager.get_config_status()
    print(f"总配置数: {status['total_configs']}")
    print(f"现有配置: {status['existing_configs']}")
    print(f"备份数量: {status['backup_count']}")

    # 创建备份
    print("\n创建配置备份...")
    backup_success = manager.create_config_backup("claude_settings", "示例备份")
    print(f"备份结果: {'成功' if backup_success else '失败'}")

    # 优化配置
    print("\n优化Claude配置...")
    optimization_results = manager.auto_optimize_claude_config()
    print(f"优化了 {len(optimization_results['optimized_files'])} 个配置文件")

def example_performance_monitoring():
    """示例：性能监控"""
    print("\n" + "="*50)
    print("示例3: 性能监控（运行10秒）")
    print("="*50)

    from monitoring.performance_dashboard import PerformanceMonitor

    # 创建性能监控器
    monitor = PerformanceMonitor()

    # 开始监控
    print("开始性能监控...")
    monitor.start_monitoring()

    # 运行10秒
    print("监控运行中... (10秒)")
    for i in range(10):
        time.sleep(1)
        print(f"  {i+1}/10 秒")

    # 停止监控
    print("停止性能监控...")
    monitor.stop_monitoring()

    # 显示结果
    if monitor.metrics_history:
        latest = monitor.metrics_history[-1]
        print(f"\n最新性能数据:")
        print(f"  CPU使用率: {latest.cpu_usage:.1f}%")
        print(f"  内存使用率: {latest.memory_usage:.1f}%")
        print(f"  进程数量: {latest.process_count}")
    else:
        print("未收集到性能数据")

def example_maintenance_scheduler():
    """示例：维护调度器"""
    print("\n" + "="*50)
    print("示例4: 维护调度器")
    print("="*50)

    from maintenance_scheduler import MaintenanceScheduler

    # 创建调度器实例
    scheduler = MaintenanceScheduler()

    # 显示已注册的任务
    print("已注册的维护任务:")
    for task_id, task in scheduler.scheduled_tasks.items():
        print(f"  - {task.name} ({task.schedule_type} {task.schedule_value})")

    # 生成维护报告
    print("\n生成维护报告...")
    report = scheduler.generate_maintenance_report()

    if "error" not in report:
        print(f"报告期间: {report['report_period']}")
        print(f"总任务执行数: {report['summary']['total_tasks_executed']}")
        print(f"成功率: {report['summary']['success_rate']:.1f}%")
    else:
        print("报告生成失败:", report["error"])

def example_compatibility_validation():
    """示例：兼容性验证"""
    print("\n" + "="*50)
    print("示例5: 兼容性验证")
    print("="*50)

    from compatibility_validator import CompatibilityValidator

    # 创建验证器实例
    validator = CompatibilityValidator()

    # 显示已注册的测试
    print("已注册的兼容性测试:")
    for test_id, test in validator.compatibility_tests.items():
        print(f"  - {test.name} ({test.category}, {test.severity})")

    # 运行快速验证（仅系统测试）
    print("\n运行系统兼容性测试...")
    results = validator.run_all_tests(categories=["system"])

    # 显示结果
    total_tests = len(results)
    passed_tests = len([r for r in results if r.success])

    print(f"\n测试结果:")
    print(f"  总测试数: {total_tests}")
    print(f"  通过: {passed_tests}")
    print(f"  失败: {total_tests - passed_tests}")

    if total_tests - passed_tests > 0:
        print("\n失败的测试:")
        for result in results:
            if not result.success:
                print(f"  - {result.test_name}: {result.message}")

def main():
    """主函数"""
    print("🚀 Claude Code Windows 系统优化工具 - 使用示例")
    print("=" * 60)

    examples = [
        ("系统优化", example_system_optimization),
        ("配置管理", example_config_management),
        ("性能监控", example_performance_monitoring),
        ("维护调度器", example_maintenance_scheduler),
        ("兼容性验证", example_compatibility_validation)
    ]

    try:
        for i, (name, func) in enumerate(examples, 1):
            print(f"\n运行示例 {i}: {name}")
            response = input("是否继续? (y/N): ").strip().lower()

            if response in ['y', 'yes']:
                try:
                    func()
                except Exception as e:
                    print(f"❌ 示例执行失败: {e}")
            else:
                print("跳过此示例")

        print("\n" + "="*60)
        print("🎉 所有示例运行完成!")
        print("\n💡 提示:")
        print("1. 实际使用时请以管理员身份运行")
        print("2. 首次运行建议使用兼容性验证检查系统")
        print("3. 重要数据请在优化前进行备份")
        print("4. 查看完整文档: README.md")

    except KeyboardInterrupt:
        print("\n\n⏹️ 用户取消操作")
    except Exception as e:
        print(f"\n❌ 示例运行失败: {e}")

if __name__ == "__main__":
    main()