#!/usr/bin/env python3
"""
智能Flow插件安装和初始化脚本
"""

import os
import sys
import json
import shutil
from pathlib import Path


def create_directory_structure():
    """创建必要的目录结构"""
    base_dir = Path(__file__).parent

    # 创建数据目录
    data_dirs = [
        "data",
        "data/adaptive",
        "data/predictions",
        "templates"
    ]

    for dir_name in data_dirs:
        dir_path = base_dir / dir_name
        dir_path.mkdir(parents=True, exist_ok=True)
        print(f"✅ 创建目录: {dir_path}")


def initialize_data_files():
    """初始化数据文件"""
    base_dir = Path(__file__).parent

    # 创建初始配置文件
    initial_configs = {
        "data/developer_profile.json": {
            "project_preferences": {},
            "work_patterns": {},
            "learned_optimizations": {},
            "technology_preferences": {},
            "quality_standards": {}
        },
        "data/projects.json": [],
        "data/patterns.json": {
            "project_type_patterns": {},
            "technology_patterns": {},
            "time_patterns": {},
            "quality_patterns": {}
        },
        "data/adaptive/adaptive_config.json": {
            "step_durations": {
                "需求拆解": 25,
                "技术设计": 15,
                "核心实现": 30,
                "测试验收": 25
            },
            "step_weights": {
                "需求拆解": 0.25,
                "技术设计": 0.15,
                "核心实现": 0.35,
                "测试验收": 0.25
            },
            "quality_focus_areas": [],
            "preferred_approaches": {},
            "risk_factors": []
        },
        "data/predictions/risk_patterns.json": {
            "technical_risks": {
                "scope_creep": {
                    "indicators": ["功能", "增加", "扩展", "补充"],
                    "probability_base": 0.3,
                    "mitigation": ["明确需求边界", "设置功能优先级", "分阶段实现"]
                },
                "technical_debt": {
                    "indicators": ["快速", "临时", "简单", "暂时"],
                    "probability_base": 0.4,
                    "mitigation": ["预留重构时间", "代码审查", "技术选型评估"]
                }
            },
            "timeline_risks": {
                "underestimation": {
                    "indicators": ["简单", "容易", "快速", "很快"],
                    "probability_base": 0.35,
                    "mitigation": ["详细任务分解", "缓冲时间", "里程碑检查"]
                }
            },
            "quality_risks": {
                "insufficient_testing": {
                    "indicators": ["测试", "验证", "检查"],
                    "probability_base": 0.4,
                    "mitigation": ["测试计划", "自动化测试", "代码覆盖率"]
                }
            }
        },
        "data/predictions/historical_data.json": {
            "projects": [],
            "success_patterns": {},
            "failure_patterns": {}
        }
    }

    for file_path, initial_data in initial_configs.items():
        full_path = base_dir / file_path
        if not full_path.exists():
            try:
                with open(full_path, 'w', encoding='utf-8') as f:
                    json.dump(initial_data, f, ensure_ascii=False, indent=2)
                print(f"✅ 初始化文件: {full_path}")
            except Exception as e:
                print(f"❌ 初始化文件失败 {full_path}: {e}")


def check_dependencies():
    """检查依赖项"""
    print("🔍 检查依赖项...")

    # 检查Python版本
    if sys.version_info < (3, 8):
        print("❌ 需要Python 3.8或更高版本")
        return False

    # 检查必要的模块
    required_modules = ['json', 'pathlib', 'datetime', 'statistics', 're']
    missing_modules = []

    for module in required_modules:
        try:
            __import__(module)
        except ImportError:
            missing_modules.append(module)

    if missing_modules:
        print(f"❌ 缺少依赖模块: {', '.join(missing_modules)}")
        return False

    print("✅ 所有依赖项检查通过")
    return True


def setup_permissions():
    """设置文件权限"""
    base_dir = Path(__file__).parent

    # 设置Python文件可执行权限
    python_files = [
        "core/intelligent_engine.py",
        "core/adaptive_workflow.py",
        "core/prediction_engine.py",
        "commands/flow_handler.py",
        "handlers/intelligent_detector.py",
        "handlers/workflow_guard.py",
        "handlers/session_initializer.py"
    ]

    for file_path in python_files:
        full_path = base_dir / file_path
        if full_path.exists():
            try:
                os.chmod(full_path, 0o755)
                print(f"✅ 设置权限: {full_path}")
            except Exception as e:
                print(f"⚠️ 设置权限失败 {full_path}: {e}")


def verify_installation():
    """验证安装"""
    print("🔍 验证安装...")

    base_dir = Path(__file__).parent

    # 检查关键文件
    key_files = [
        "plugin.json",
        "README.md",
        "core/intelligent_engine.py",
        "commands/flow_handler.py",
        "handlers/intelligent_detector.py",
        "handlers/workflow_guard.py",
        "handlers/session_initializer.py"
    ]

    missing_files = []
    for file_path in key_files:
        full_path = base_dir / file_path
        if not full_path.exists():
            missing_files.append(file_path)

    if missing_files:
        print(f"❌ 缺少关键文件: {', '.join(missing_files)}")
        return False

    # 检查数据目录
    data_dir = base_dir / "data"
    if not data_dir.exists():
        print("❌ 数据目录不存在")
        return False

    print("✅ 安装验证通过")
    return True


def print_usage_instructions():
    """打印使用说明"""
    print("\n🎉 智能Flow插件安装完成！")
    print("=" * 50)
    print("\n📚 快速开始：")
    print("  /flow                    # 查看所有工作流")
    print("  /flow 363                # 经典3-6-3工作流")
    print("  /flow smart 开发...       # AI智能流程")
    print("  /flow adaptive 开发...    # 个性化流程")
    print("  /flow profile            # 查看学习档案")
    print("  /flow learn              # 获取优化建议")

    print("\n🔧 智能功能：")
    print("  • 自动检测开发场景")
    print("  • 学习您的开发模式")
    print("  • 预测项目风险")
    print("  • 防止工作流违规")

    print("\n📖 详细文档：")
    print("  README.md - 完整使用指南")
    print("  templates/ - 需求模板和检查清单")

    print("\n💡 提示：系统会越用越懂您！")


def main():
    """主安装流程"""
    print("🚀 开始安装智能Flow插件...")
    print("=" * 50)

    # 检查依赖
    if not check_dependencies():
        sys.exit(1)

    # 创建目录结构
    print("\n📁 创建目录结构...")
    create_directory_structure()

    # 初始化数据文件
    print("\n📄 初始化数据文件...")
    initialize_data_files()

    # 设置权限
    print("\n🔐 设置文件权限...")
    setup_permissions()

    # 验证安装
    print("\n✅ 验证安装...")
    if not verify_installation():
        print("❌ 安装验证失败，请检查错误信息")
        sys.exit(1)

    # 打印使用说明
    print_usage_instructions()

    print("\n🎊 安装完成！开始您的智能开发之旅吧！")


if __name__ == "__main__":
    main()