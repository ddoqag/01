#!/usr/bin/env python3
"""
Claude Code Windows 系统优化工具启动脚本
"""

import os
import sys
import argparse
import json
import logging
from pathlib import Path
from datetime import datetime

# 添加当前目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from main import ClaudeOptimizer
from config_manager import IntelligentConfigManager
from monitoring.performance_dashboard import PerformanceMonitor
from maintenance_scheduler import MaintenanceScheduler
from compatibility_validator import CompatibilityValidator

def setup_logging():
    """设置日志"""
    base_dir = Path(__file__).parent
    logs_dir = base_dir / "logs"
    logs_dir.mkdir(exist_ok=True)

    log_file = logs_dir / f"optimizer_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )

def run_system_optimization():
    """运行系统优化"""
    print("🔧 启动Claude Code Windows系统优化...")
    optimizer = ClaudeOptimizer()
    success = optimizer.run_optimization()

    if success:
        print("✅ 系统优化完成!")
        print("📊 请查看生成的报告了解详细优化结果。")
    else:
        print("❌ 系统优化失败!")
        print("📋 请查看日志文件了解详细错误信息。")

    return success

def run_config_management():
    """运行配置管理"""
    print("⚙️ 启动智能配置管理...")
    manager = IntelligentConfigManager()

    # 创建备份
    print("📦 创建配置备份...")
    manager.create_config_backup("claude_settings", "手动备份")

    # 优化配置
    print("🔍 优化Claude配置...")
    optimization_results = manager.auto_optimize_claude_config()

    # 同步配置
    print("🔄 同步配置文件...")
    sync_results = manager.sync_configurations()

    # 获取状态
    print("📈 获取配置状态...")
    status = manager.get_config_status()

    print("✅ 配置管理完成!")
    return True

def run_performance_monitor():
    """运行性能监控"""
    print("📊 启动性能监控仪表板...")
    monitor = PerformanceMonitor()
    monitor.start_monitoring()

    try:
        print("🌐 监控仪表板运行中...")
        print("📝 访问 http://localhost:8080 查看实时性能监控")
        print("⏹️ 按 Ctrl+C 停止监控")

        while monitor.monitoring_active:
            import time
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 正在停止性能监控...")
        monitor.stop_monitoring()
        print("✅ 性能监控已停止")

    return True

def run_maintenance_scheduler():
    """运行维护调度器"""
    print("⏰ 启动自动化维护调度器...")
    scheduler = MaintenanceScheduler()
    scheduler.start_scheduler()

    try:
        print("🔄 维护调度器运行中...")
        print("📋 已注册的维护任务将按计划自动执行")
        print("⏹️ 按 Ctrl+C 停止调度器")

        while scheduler.scheduler_active:
            import time
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 正在停止维护调度器...")
        scheduler.stop_scheduler()

        # 生成报告
        print("📊 生成维护报告...")
        report = scheduler.generate_maintenance_report()
        print(f"📈 维护报告已生成，共执行 {report['summary']['total_tasks_executed']} 个任务")

        print("✅ 维护调度器已停止")

    return True

def run_compatibility_validation():
    """运行兼容性验证"""
    print("🔍 启动Windows兼容性验证...")
    validator = CompatibilityValidator()

    # 运行所有测试
    print("🧪 执行兼容性测试...")
    test_results = validator.run_all_tests()

    # 显示结果
    total_tests = len(test_results)
    passed_tests = len([r for r in test_results if r.success])
    failed_tests = total_tests - passed_tests

    print(f"\n📊 兼容性验证结果:")
    print(f"   总测试数: {total_tests}")
    print(f"   ✅ 通过: {passed_tests}")
    print(f"   ❌ 失败: {failed_tests}")
    print(f"   📈 成功率: {(passed_tests/total_tests*100):.1f}%")

    if failed_tests > 0:
        print("\n⚠️ 失败的测试:")
        for result in test_results:
            if not result.success:
                print(f"   - {result.test_name} ({result.severity}): {result.message}")

    # 生成报告
    print("\n📋 生成兼容性报告...")
    report = validator.generate_compatibility_report(test_results)

    print("\n💡 建议和修复措施:")
    for i, recommendation in enumerate(report.get("recommendations", []), 1):
        print(f"   {i}. {recommendation}")

    if failed_tests == 0:
        print("\n✅ 系统兼容性检查通过!")

        response = input("\n🔄 是否启动持续兼容性监控? (y/N): ").strip().lower()
        if response in ['y', 'yes']:
            print("🚀 启动持续兼容性验证...")
            validator.start_continuous_validation()
            print("🔍 持续验证已启动，按 Ctrl+C 停止")

            try:
                while validator.validation_active:
                    import time
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\n🛑 正在停止持续验证...")
                validator.stop_continuous_validation()
                print("✅ 持续验证已停止")
    else:
        print("\n❌ 发现兼容性问题，请根据建议进行修复")

    return failed_tests == 0

def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="Claude Code Windows 系统优化工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  python run_optimizer.py --mode optimize          # 运行系统优化
  python run_optimizer.py --mode config           # 运行配置管理
  python run_optimizer.py --mode monitor          # 启动性能监控
  python run_optimizer.py --mode scheduler        # 启动维护调度器
  python run_optimizer.py --mode validate         # 运行兼容性验证
  python run_optimizer.py --mode all              # 运行所有功能
        """
    )

    parser.add_argument(
        '--mode',
        choices=['optimize', 'config', 'monitor', 'scheduler', 'validate', 'all'],
        default='optimize',
        help='选择运行模式'
    )

    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='启用详细日志输出'
    )

    args = parser.parse_args()

    # 设置日志
    setup_logging()
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # 显示启动信息
    print("=" * 60)
    print("🚀 Claude Code Windows 系统优化工具")
    print("=" * 60)
    print(f"📅 运行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"💻 操作系统: {sys.platform}")
    print(f"🐍 Python版本: {sys.version}")
    print("=" * 60)

    results = {}

    try:
        if args.mode == 'optimize':
            results['optimize'] = run_system_optimization()

        elif args.mode == 'config':
            results['config'] = run_config_management()

        elif args.mode == 'monitor':
            results['monitor'] = run_performance_monitor()

        elif args.mode == 'scheduler':
            results['scheduler'] = run_maintenance_scheduler()

        elif args.mode == 'validate':
            results['validate'] = run_compatibility_validation()

        elif args.mode == 'all':
            print("🔄 运行完整优化流程...\n")

            # 按顺序执行所有功能
            print("\n1️⃣ 兼容性验证")
            results['validate'] = run_compatibility_validation()

            print("\n2️⃣ 系统优化")
            results['optimize'] = run_system_optimization()

            print("\n3️⃣ 配置管理")
            results['config'] = run_config_management()

            print("\n4️⃣ 性能监控")
            results['monitor'] = run_performance_monitor()

    except KeyboardInterrupt:
        print("\n⏹️ 用户取消操作")
        return 1
    except Exception as e:
        print(f"\n❌ 运行过程中发生错误: {e}")
        logging.error(f"主程序错误: {e}", exc_info=True)
        return 1

    # 显示最终结果
    print("\n" + "=" * 60)
    print("📊 运行结果摘要")
    print("=" * 60)

    success_count = 0
    total_count = len(results)

    for mode, success in results.items():
        status = "✅ 成功" if success else "❌ 失败"
        mode_names = {
            'optimize': '系统优化',
            'config': '配置管理',
            'monitor': '性能监控',
            'scheduler': '维护调度器',
            'validate': '兼容性验证'
        }
        print(f"{mode_names.get(mode, mode)}: {status}")
        if success:
            success_count += 1

    if total_count > 0:
        print(f"\n📈 总体成功率: {success_count}/{total_count} ({success_count/total_count*100:.1f}%)")

    if success_count == total_count:
        print("\n🎉 所有任务执行完成!")
        return 0
    else:
        print(f"\n⚠️ {total_count - success_count} 个任务执行失败")
        return 1

if __name__ == "__main__":
    sys.exit(main())