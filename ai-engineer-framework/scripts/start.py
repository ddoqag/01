#!/usr/bin/env python3
"""
AI Engineer Framework 启动脚本

提供便捷的服务启动、管理和维护功能
"""

import asyncio
import argparse
import sys
import os
from pathlib import Path

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from utils.config import load_config, validate_config
from utils.logging import setup_logging
from services.factory import ServiceFactory
from services.monitoring_service import init_monitoring
from services.cost_optimizer import init_cost_optimizer
from main import create_app


async def start_server(host: str = "0.0.0.0", port: int = 8000, workers: int = 1):
    """启动服务器"""
    print(f"🚀 启动 AI Engineer Framework...")
    print(f"📍 地址: http://{host}:{port}")
    print(f"📚 API文档: http://{host}:{port}/docs")
    print(f"📊 监控面板: http://{host}:{port}/metrics")

    # 加载配置
    config = load_config()
    setup_logging(config.get("app", {}).get("log_level", "INFO"))

    # 验证配置
    if not validate_config(config):
        print("❌ 配置验证失败，请检查配置文件")
        sys.exit(1)

    # 创建应用
    app = create_app()

    # 启动服务
    import uvicorn
    config_dict = {
        "app": app,
        "host": host,
        "port": port,
        "log_level": config.get("app", {}).get("log_level", "info").lower(),
        "access_log": True,
    }

    if workers > 1:
        config_dict["workers"] = workers

    uvicorn.run(**config_dict)


async def run_health_check():
    """运行健康检查"""
    print("🔍 运行健康检查...")

    try:
        from services.factory import get_service_registry
        from services.monitoring_service import get_monitoring_service
        from services.cost_optimizer import get_cost_optimizer

        # 检查服务注册表
        registry = get_service_registry()
        services = registry.list_services()
        print(f"✅ 已注册服务: {len(services)}")
        for name, service_type in services.items():
            print(f"  - {name}: {service_type}")

        # 检查监控服务
        try:
            monitoring = get_monitoring_service()
            health = await monitoring.health_check()
            print(f"✅ 监控服务: {'健康' if health else '异常'}")
        except Exception as e:
            print(f"❌ 监控服务异常: {e}")

        # 检查成本优化器
        try:
            cost_optimizer = get_cost_optimizer()
            summary = cost_optimizer.get_cost_summary()
            print(f"✅ 成本优化器: 正常")
            print(f"  - 总成本: ${summary.get('total_cost', 0):.4f}")
            print(f"  - 总请求: {summary.get('total_requests', 0)}")
        except Exception as e:
            print(f"❌ 成本优化器异常: {e}")

        print("✅ 健康检查完成")

    except Exception as e:
        print(f"❌ 健康检查失败: {e}")


async def init_services():
    """初始化所有服务"""
    print("🔧 初始化服务...")

    try:
        config = load_config()

        # 初始化监控服务
        monitoring_config = config.get("monitoring", {})
        await init_monitoring(monitoring_config)
        print("✅ 监控服务初始化完成")

        # 初始化成本优化器
        cost_config = config.get("cost_optimization", {})
        await init_cost_optimizer(cost_config)
        print("✅ 成本优化器初始化完成")

        print("✅ 所有服务初始化完成")

    except Exception as e:
        print(f"❌ 服务初始化失败: {e}")
        sys.exit(1)


async def show_status():
    """显示系统状态"""
    print("📊 系统状态报告")
    print("=" * 50)

    try:
        from services.monitoring_service import get_monitoring_service
        from services.cost_optimizer import get_cost_optimizer
        from services.factory import get_service_registry

        # 获取服务状态
        registry = get_service_registry()
        health_status = await registry.health_check()

        print("\n🏥 服务健康状态:")
        for service_name, is_healthy in health_status.items():
            status = "✅ 健康" if is_healthy else "❌ 异常"
            print(f"  - {service_name}: {status}")

        # 获取监控统计
        try:
            monitoring = get_monitoring_service()
            monitoring_summary = monitoring.get_monitoring_summary()
            print(f"\n📈 监控统计:")
            print(f"  - 活跃告警: {monitoring_summary['alerts']['active']}")
            print(f"  - 总告警数: {monitoring_summary['alerts']['total']}")
        except:
            print("\n📈 监控统计: 不可用")

        # 获取成本统计
        try:
            cost_optimizer = get_cost_optimizer()
            cost_summary = cost_optimizer.get_cost_summary()
            budget_status = cost_summary.get('budget_status', {})

            print(f"\n💰 成本统计:")
            print(f"  - 总成本: ${cost_summary.get('total_cost', 0):.4f}")
            print(f"  - 总Token: {cost_summary.get('total_tokens', 0):,}")
            print(f"  - 总请求: {cost_summary.get('total_requests', 0):,}")
            print(f"  - 日预算使用: {budget_status.get('daily_usage_ratio', 0):.1%}")
            print(f"  - 月预算使用: {budget_status.get('monthly_usage_ratio', 0):.1%}")
        except:
            print("\n💰 成本统计: 不可用")

    except Exception as e:
        print(f"❌ 获取状态失败: {e}")


def run_tests():
    """运行测试"""
    print("🧪 运行测试套件...")
    os.system("pytest tests/ -v --cov=src --cov-report=term-missing")


def setup_environment():
    """设置开发环境"""
    print("⚙️ 设置开发环境...")

    # 检查Python版本
    if sys.version_info < (3, 12):
        print("❌ 需要Python 3.12或更高版本")
        sys.exit(1)

    # 安装依赖
    print("📦 安装依赖...")
    os.system("pip install -r requirements/base.txt")
    os.system("pip install -r requirements/development.txt")

    # 创建必要目录
    directories = [
        "data",
        "data/chromadb",
        "logs",
        "temp",
        "uploads"
    ]

    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)

    # 复制环境配置
    if not Path(".env").exists():
        os.system("cp .env.example .env")
        print("📝 已创建 .env 文件，请填入你的配置")

    print("✅ 开发环境设置完成")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="AI Engineer Framework 管理工具")
    subparsers = parser.add_subparsers(dest="command", help="可用命令")

    # 启动命令
    start_parser = subparsers.add_parser("start", help="启动服务")
    start_parser.add_argument("--host", default="0.0.0.0", help="服务器地址")
    start_parser.add_argument("--port", type=int, default=8000, help="服务器端口")
    start_parser.add_argument("--workers", type=int, default=1, help="工作进程数")

    # 健康检查命令
    subparsers.add_parser("health", help="运行健康检查")

    # 初始化命令
    subparsers.add_parser("init", help="初始化服务")

    # 状态命令
    subparsers.add_parser("status", help="显示系统状态")

    # 测试命令
    subparsers.add_parser("test", help="运行测试")

    # 环境设置命令
    subparsers.add_parser("setup", help="设置开发环境")

    args = parser.parse_args()

    if args.command == "start":
        asyncio.run(start_server(args.host, args.port, args.workers))
    elif args.command == "health":
        asyncio.run(run_health_check())
    elif args.command == "init":
        asyncio.run(init_services())
    elif args.command == "status":
        asyncio.run(show_status())
    elif args.command == "test":
        run_tests()
    elif args.command == "setup":
        setup_environment()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()