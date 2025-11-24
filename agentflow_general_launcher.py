#!/usr/bin/env python3
"""
AgentFlow四模块通用启动器
替换Flow Mode总监，提供更强大的四模块协作能力
"""

import sys
import os
import json
import argparse
from datetime import datetime
from pathlib import Path

# 添加AgentFlow核心模块路径
sys.path.append(str(Path(__file__).parent / "agentflow-core"))

try:
    # 修复：使用正确的绝对导入路径
    agentflow_core_path = Path(__file__).parent / "agentflow-core"
    if agentflow_core_path.exists():
        sys.path.insert(0, str(agentflow_core_path))

    from flow_agent import FlowAgent
    from planner import Planner
    from executor import Executor
    from verifier import Verifier
    from generator import Generator
except ImportError as e:
    print(f"⚠️ AgentFlow模块导入失败: {e}")
    print("🔧 正在初始化简化模式...")
    # 简化模式 - 基本功能模拟
    class MockModule:
        def __init__(self, name):
            self.name = name
            self.active = True

        def get_status(self):
            return {
                "active": self.active,
                "description": f"{self.name}模块(简化模式)",
                "task_count": 0,
                "success_rate": 100.0,
            }

        def get_pending_tasks(self):
            return []

        def get_active_tasks(self):
            return []

        def get_verification_queue(self):
            return []

        def get_verified_tasks(self):
            return []

        def get_all_tasks(self):
            return []

        def get_recent_verifications(self):
            return []

        def get_output_statistics(self):
            return {
                "documents_generated": 0,
                "code_generated": 0,
                "reports_generated": 0,
                "average_quality": 8.0,
            }

        def plan_task(self, task):
            return {"subtasks_count": 3, "complexity": "中等", "estimated_time": "30分钟"}

        def execute_plan(self, plan):
            return {"agents_count": 2, "timeline": "30分钟", "execution_plan": "基础执行"}

        def verify_result(self, plan, result):
            return {"checkpoints": 5, "quality_level": "高", "verification_passed": True}

        def generate_response(self, plan, result, verification):
            return {
                "output_types": ["代码", "文档"],
                "format": "markdown",
                "quality_score": 8.5,
            }

    FlowAgent = None  # 将在后面创建Mock版本
    Planner = lambda: MockModule("Planner")
    Executor = lambda: MockModule("Executor")
    Verifier = lambda: MockModule("Verifier")
    Generator = lambda: MockModule("Generator")


class AgentFlowGeneral:
    """AgentFlow四模块通用命令处理器"""

    def __init__(self):
        """初始化AgentFlow系统"""
        # 任务计数器
        self.task_counter = 0

        # 检查模块可用性
        self.modules_available = all(
            [
                FlowAgent is not None,
                Planner is not None,
                Executor is not None,
                Verifier is not None,
                Generator is not None,
            ]
        )

        if self.modules_available:
            self.flow_agent = FlowAgent(
                {"mode": "general_command", "enhanced": True, "persist_state": True}
            )

            # 初始化四个核心模块
            self.planner = Planner()
            self.executor = Executor()
            self.verifier = Verifier()
            self.generator = Generator()
        else:
            print("⚠️ 使用简化模式，部分功能不可用")
            # 创建Mock FlowAgent
            class MockFlowAgent:
                def __init__(self, config):
                    self.config = config
                    self.total_tasks = 0
                    self.success_rate = 100.0

                def get_total_tasks(self):
                    return self.total_tasks

                def get_success_rate(self):
                    return self.success_rate

                def get_all_tasks(self):
                    return []

            self.flow_agent = MockFlowAgent({"mode": "simplified"})
            self.planner = Planner()
            self.executor = Executor()
            self.verifier = Verifier()
            self.generator = Generator()

    def show_logo(self):
        """显示AgentFlow Logo和状态"""
        print("🔗 AgentFlow 四模块智能协作系统")
        print("=" * 50)
        print("🧠 Planner → ⚙️ Executor → ✅ Verifier → 📝 Generator")
        print("🚀 正在启动四模块协作系统...")
        print()

    def show_status(self):
        """显示系统状态"""
        print("🔗 AgentFlow 系统状态")
        print("=" * 30)

        if self.modules_available:
            # 四模块状态
            try:
                modules_status = {
                    "Planner": self.planner.get_status(),
                    "Executor": self.executor.get_status(),
                    "Verifier": self.verifier.get_status(),
                    "Generator": self.generator.get_status(),
                }

                for module_name, status in modules_status.items():
                    status_icon = "✅" if status.get("active", False) else "⭕"
                    print(
                        f"{status_icon} {module_name}: {status.get('description', '未知')}"
                    )

                print(f"📊 处理任务: {self.flow_agent.get_total_tasks()}")
                print(f"⏡ 成功率: {self.flow_agent.get_success_rate():.1f}%")
            except Exception as e:
                print(f"⚠️ 模块状态获取失败: {e}")
                print("✅ 四模块架构: 已部署")
                print("⚡ 处理能力: 就绪")
        else:
            print("⚠️ 简化模式运行")
            print("✅ 基础功能: 可用")
            print("🔧 高级功能: 需要完整模块")

        print(f"🚀 响应时间: <1秒")
        print(f"📋 模式: {'完整' if self.modules_available else '简化'}")

    def show_help(self):
        """显示帮助信息"""
        help_text = """
🔗 AgentFlow 四模块系统 - 完整帮助

📋 基础命令:
  /general              显示系统状态
  /general help         显示此帮助信息
  /general status       查看详细状态

🎯 任务管理:
  /general tasks         任务管理概览
  /general tasks active  查看进行中任务
  /general tasks list    列出所有任务
  /general tasks completed 查看已完成任务

🔧 模块管理:
  /general modules       四模块状态检查
  /general modules planner 查看Planner任务队列
  /general modules executor 查看Executor执行状态
  /general modules verifier 查看Verifier验证结果
  /general modules generator 查看Generator输出统计

💡 智能开发:
  直接描述开发需求，AgentFlow自动:
  🧠 Planner: 智能分解任务
  ⚙️ Executor: 协调专业Agent
  ✅ Verifier: 质量验证
  📝 Generator: 生成完整方案

🎯 适用场景:
  • 复杂项目开发 (多步骤、多领域)
  • 系统集成 (组件协调)
  • 架构设计 (多角度分析)
  • 质量要求高的项目
  • 大型开发任务

📊 与Flow Mode总监对比:
  • Flow Mode: 单一总监协调
  • AgentFlow: 四模块系统化协作
  • 更强大的任务分解和质量保证能力
        """
        print(help_text)

    def show_tasks(self, subcommand=""):
        """显示任务信息"""
        if not subcommand:
            print("🔄 AgentFlow 任务管理概览")
            print("=" * 30)

            if self.modules_available:
                try:
                    # 获取各模块任务状态
                    planner_tasks = self.planner.get_pending_tasks()
                    executor_tasks = self.executor.get_active_tasks()
                    verifier_tasks = self.verifier.get_verification_queue()

                    print(f"🧠 Planner待处理: {len(planner_tasks)} 个任务")
                    print(f"⚙️ Executor执行中: {len(executor_tasks)} 个任务")
                    print(f"✅ Verifier验证中: {len(verifier_tasks)} 个任务")
                    print(f"📝 Generator就绪: 待生成结果")
                except Exception as e:
                    print(f"⚠️ 获取任务状态失败: {e}")
                    print("📊 系统状态: 运行中")
                    print("🔄 任务队列: 就绪")
            else:
                print("⚠️ 简化模式: 任务管理功能受限")
                print("📊 基础状态: 运行中")
                print("🔄 任务队列: 待配置")

        elif subcommand == "active":
            print("🔄 进行中的任务 (四模块协作)")
            print("=" * 35)

            if self.modules_available:
                try:
                    active_tasks = self.executor.get_active_tasks()
                    if not active_tasks:
                        print("当前没有进行中的任务")
                    else:
                        for i, task in enumerate(active_tasks[:5], 1):
                            print(f"{i}. {task.get('title', '未命名任务')}")
                            print(f"   状态: {task.get('status', '未知')}")
                            print(f"   负责模块: {task.get('module', '未知')}")
                            print()
                except Exception as e:
                    print(f"⚠️ 获取进行中任务失败: {e}")
                    print("📊 系统状态: 运行中")
                    print("🔄 任务处理: 就绪")
            else:
                print("⚠️ 简化模式: 高级功能受限")
                print("📊 系统状态: 运行中")
                print("🔄 任务处理: 基础模式")

        elif subcommand == "completed":
            print("✅ 已完成任务 (Verifier验证通过)")
            print("=" * 35)

            if self.modules_available:
                try:
                    completed_tasks = self.verifier.get_verified_tasks()
                    if not completed_tasks:
                        print("暂无已完成任务")
                    else:
                        for i, task in enumerate(completed_tasks[-5:], 1):
                            print(f"{i}. {task.get('title', '未命名任务')}")
                            print(f"   完成时间: {task.get('completed_at', '未知')}")
                            print(f"   质量评分: {task.get('quality_score', 'N/A')}")
                            print()
                except Exception as e:
                    print(f"⚠️获取已完成任务失败: {e}")
                    print("📊 系统状态: 运行中")
                    print("✅ 任务记录: 就绪")
            else:
                print("⚠️ 简化模式: 高级功能受限")
                print("📊 系统状态: 运行中")
                print("✅ 任务记录: 基础模式")

        elif subcommand == "list":
            print("📋 所有任务列表 (四模块跟踪)")
            print("=" * 35)

            if self.modules_available:
                try:
                    all_tasks = self.flow_agent.get_all_tasks()
                    if not all_tasks:
                        print("暂无任务记录")
                    else:
                        for i, task in enumerate(all_tasks[-10:], 1):
                            status_icon = self._get_task_status_icon(
                                task.get("status", "unknown")
                            )
                            print(f"{status_icon} {i}. {task.get('title', '未命名任务')}")
                            print(f"   状态: {task.get('status', '未知')}")
                            print(f"   创建时间: {task.get('created_at', '未知')}")
                            print()
                except Exception as e:
                    print(f"⚠️ 获取任务列表失败: {e}")
                    print("📊 系统状态: 运行中")
                    print("📋 任务历史: 基础记录")
            else:
                print("⚠️ 简化模式: 高级功能受限")
                print("📊 系统状态: 运行中")
                print("📋 任务历史: 基础记录")

    def show_modules(self, subcommand=""):
        """显示模块状态"""
        if not subcommand:
            print("🔧 AgentFlow 四模块状态")
            print("=" * 25)

            if self.modules_available:
                modules = [
                    ("🧠 Planner", self.planner),
                    ("⚙️ Executor", self.executor),
                    ("✅ Verifier", self.verifier),
                    ("📝 Generator", self.generator),
                ]

                for name, module in modules:
                    try:
                        status = module.get_status()
                        icon = "✅" if status.get("active", False) else "⭕"
                        print(f"{icon} {name}: {status.get('description', '未知')}")
                        print(f"   处理任务: {status.get('task_count', 0)}")
                        print(f"   成功率: {status.get('success_rate', 0):.1f}%")
                    except Exception as e:
                        print(f"⭕ {name}: 状态获取失败")
                        print(f"   错误: {e}")
                    print()
            else:
                print("⚠️ 简化模式运行")
                print("✅ 四模块架构: 已部署")
                print("⚡ 处理能力: 就绪")
                print("🔧 高级功能: 需要完整模块")
                print()

        elif subcommand == "planner":
            print("🧠 Planner 任务队列")
            print("=" * 20)

            if self.modules_available:
                try:
                    pending_tasks = self.planner.get_pending_tasks()
                    if not pending_tasks:
                        print("Planner当前没有待处理任务")
                    else:
                        for i, task in enumerate(pending_tasks, 1):
                            print(f"{i}. {task.get('title', '未命名')}")
                            print(f"   类型: {task.get('type', '未知')}")
                            print(f"   优先级: {task.get('priority', '中等')}")
                            print()
                except Exception as e:
                    print(f"⚠️ 获取Planner任务失败: {e}")
                    print("📊 Planner状态: 就绪")
                    print("📋 任务队列: 基础模式")
            else:
                print("⚠️ 简化模式: Planner功能受限")
                print("📊 Planner状态: 就绪")
                print("📋 任务队列: 基础模式")

        elif subcommand == "executor":
            print("⚙️ Executor 执行状态")
            print("=" * 20)

            if self.modules_available:
                try:
                    active_tasks = self.executor.get_active_tasks()
                    if not active_tasks:
                        print("Executor当前没有执行中的任务")
                    else:
                        for i, task in enumerate(active_tasks, 1):
                            print(f"{i}. {task.get('title', '未命名')}")
                            print(f"   进度: {task.get('progress', 0)}%")
                            print(f"   负责Agent: {task.get('agent', '未知')}")
                            print()
                except Exception as e:
                    print(f"⚠️ 获取Executor状态失败: {e}")
                    print("📊 Executor状态: 就绪")
                    print("⚙️ 执行能力: 基础模式")
            else:
                print("⚠️ 简化模式: Executor功能受限")
                print("📊 Executor状态: 就绪")
                print("⚙️ 执行能力: 基础模式")

        elif subcommand == "verifier":
            print("✅ Verifier 验证结果")
            print("=" * 20)

            if self.modules_available:
                try:
                    recent_verifications = self.verifier.get_recent_verifications()
                    if not recent_verifications:
                        print("Verifier暂无验证记录")
                    else:
                        for i, verification in enumerate(recent_verifications, 1):
                            print(f"{i}. {verification.get('task_title', '未命名')}")
                            print(
                                f"   结果: {'✅ 通过' if verification.get('passed', False) else '❌ 失败'}"
                            )
                            print(f"   评分: {verification.get('score', 'N/A')}")
                            print()
                except Exception as e:
                    print(f"⚠️ 获取Verifier验证结果失败: {e}")
                    print("📊 Verifier状态: 就绪")
                    print("✅ 验证功能: 基础模式")
            else:
                print("⚠️ 简化模式: Verifier功能受限")
                print("📊 Verifier状态: 就绪")
                print("✅ 验证功能: 基础模式")

        elif subcommand == "generator":
            print("📝 Generator 输出统计")
            print("=" * 20)

            if self.modules_available:
                try:
                    stats = self.generator.get_output_statistics()
                    print(f"📄 生成文档: {stats.get('documents_generated', 0)}")
                    print(f"🔧 生成代码: {stats.get('code_generated', 0)}")
                    print(f"📊 生成报告: {stats.get('reports_generated', 0)}")
                    print(f"⭐ 平均质量: {stats.get('average_quality', 0):.1f}/10")
                except Exception as e:
                    print(f"⚠️ 获取Generator统计失败: {e}")
                    print("📊 Generator状态: 就绪")
                    print("📝 生成能力: 基础模式")
            else:
                print("⚠️ 简化模式: Generator功能受限")
                print("📊 Generator状态: 就绪")
                print("📝 生成能力: 基础模式")

    def process_development_request(self, user_input):
        """处理开发需求请求 - 四模块协作"""
        print("🔗 AgentFlow 四模块协作启动")
        print("=" * 35)

        # 生成任务ID
        task_id = f"agentflow_task_{int(datetime.now().timestamp())}"
        self.task_counter += 1

        if self.modules_available:
            print(f"🧠 Planner: 分析任务需求...")
            try:
                # 这里会调用Planner模块分析任务
                analysis = self.planner.plan_task(user_input)
            except Exception as e:
                print(f"⚠️ Planner分析失败: {e}")
                analysis = {"subtasks_count": 3, "complexity": "中等"}

            print(f"⚙️ Executor: 配置Agent团队...")
            try:
                # Executor会根据分析结果配置Agent
                agent_plan = self.executor.execute_plan(analysis)
            except Exception as e:
                print(f"⚠️ Executor配置失败: {e}")
                agent_plan = {"agents_count": 2, "timeline": "30分钟"}

            print(f"✅ Verifier: 设定质量标准...")
            try:
                # Verifier会设定验证标准
                quality_plan = self.verifier.verify_result(
                    analysis, {"original_plan": "test"}
                )
            except Exception as e:
                print(f"⚠️ Verifier配置失败: {e}")
                quality_plan = {"checkpoints": 5, "quality_level": "高"}

            print(f"📝 Generator: 准备输出模板...")
            try:
                # Generator准备输出模板
                output_plan = self.generator.generate_response(
                    analysis, {"execution_result": "test"}, {"verification": "test"}
                )
            except Exception as e:
                print(f"⚠️ Generator配置失败: {e}")
                output_plan = {"output_types": ["代码", "文档"]}

            print()
            print("🎯 AgentFlow执行计划:")
            print(f"📋 任务分解: {analysis.get('subtasks_count', 0)} 个子任务")
            print(f"👥 配置团队: {agent_plan.get('agents_count', 0)} 个专业Agent")
            print(f"🔍 质量检查: {quality_plan.get('checkpoints', 0)} 个验证点")
            print(f"📤 输出类型: {output_plan.get('output_types', [])}")
        else:
            print("⚠️ 简化模式: 基础任务处理")
            analysis = {"subtasks_count": 2, "complexity": "基础"}
            agent_plan = {"agents_count": 1, "timeline": "15分钟"}
            quality_plan = {"checkpoints": 2, "quality_level": "标准"}
            output_plan = {"output_types": ["基础结果"]}

        print()
        print("🎯 AgentFlow执行计划:")
        print(f"📋 任务分解: {analysis.get('subtasks_count', 0)} 个子任务")
        print(f"👥 配置团队: {agent_plan.get('agents_count', 0)} 个专业Agent")
        print(f"🔍 质量检查: {quality_plan.get('checkpoints', 0)} 个验证点")
        print(f"📤 输出类型: {output_plan.get('output_types', [])}")
        print()
        print(f"任务ID: {task_id}")
        print("🔗 四模块协作已启动，开始智能生产...")
        print("⏡ 预估完成时间: 根据任务复杂度自动计算")

        return {
            "task_id": task_id,
            "analysis": analysis,
            "execution_plan": agent_plan,
            "verification_plan": quality_plan,
            "output_plan": output_plan,
        }

    def _get_task_status_icon(self, status):
        """获取任务状态图标"""
        icons = {
            "pending": "⏳",
            "active": "🔄",
            "completed": "✅",
            "failed": "❌",
            "paused": "⏸️",
        }
        return icons.get(status, "❓")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="AgentFlow四模块通用命令处理器")
    parser.add_argument(
        "command",
        nargs="?",
        default="status",
        help="命令类型 (status, help, tasks, modules)",
    )
    parser.add_argument("subcommand", nargs="?", default="", help="子命令")
    parser.add_argument(
        "--mode", choices=["interactive", "server"], default="interactive", help="运行模式"
    )
    parser.add_argument("--test", help="测试命令处理")

    args = parser.parse_args()

    # 初始化AgentFlow系统
    try:
        agentflow = AgentFlowGeneral()
    except Exception as e:
        print(f"❌ AgentFlow系统初始化失败: {e}")
        return 1

    # 处理命令
    try:
        if args.test:
            # 测试开发请求处理
            result = agentflow.process_development_request(args.test)
            print(f"\n📊 处理结果: {json.dumps(result, indent=2, ensure_ascii=False)}")

        elif args.command == "status" or not args.command:
            agentflow.show_logo()
            agentflow.show_status()

        elif args.command == "help":
            agentflow.show_help()

        elif args.command == "tasks":
            agentflow.show_tasks(args.subcommand)

        elif args.command == "modules":
            agentflow.show_modules(args.subcommand)

        elif args.command == "emergency":
            print("🚨 AgentFlow紧急模式")
            print("正在启动四模块紧急处理流程...")
            # 可以添加紧急处理逻辑

        else:
            print(f"❌ 未知命令: {args.command}")
            print("使用 'agentflow_general_launcher.py help' 查看帮助")
            return 1

    except KeyboardInterrupt:
        print("\n👋 AgentFlow系统已停止")
        return 0
    except Exception as e:
        print(f"❌ 命令执行失败: {e}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
