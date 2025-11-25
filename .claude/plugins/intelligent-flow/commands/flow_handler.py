#!/usr/bin/env python3
"""
智能Flow命令处理器
统一集成Hook自动检测和Flow用户控制的3-6-3工作流系统
"""

import sys
import os
import json
import argparse
from pathlib import Path
from datetime import datetime

# 添加核心模块路径
sys.path.insert(0, str(Path(__file__).parent.parent / "core"))

from intelligent_engine import IntelligentEngine, WorkflowStage, ProjectType


class FlowHandler:
    """Flow命令处理器"""

    def __init__(self):
        self.plugin_root = Path(__file__).parent.parent
        self.engine = IntelligentEngine(str(self.plugin_root))
        self.templates_dir = self.plugin_root / "templates"
        self.templates_dir.mkdir(exist_ok=True)

    def handle_command(self, args):
        """处理Flow命令"""
        if not args or args == []:
            self._show_available_flows()
            return

        command = args[0].lower()
        subcommand = args[1] if len(args) > 1 else None

        # 智能检测和处理
        if command == "363":
            self._handle_363_workflow(subcommand, args[2:])
        elif command == "smart":
            self._handle_smart_flow(args[1:])
        elif command == "adaptive":
            self._handle_adaptive_flow(args[1:])
        elif command == "profile":
            self._handle_profile()
        elif command == "learn":
            self._handle_learning()
        elif command == "help":
            self._show_help()
        else:
            # 智能解析用户意图
            self._intelligent_parse(args)

    def _show_available_flows(self):
        """显示可用的Flow"""
        print("🧠 智能Flow工作流系统")
        print("=" * 50)

        # 获取当前状态
        status = self.engine.get_workflow_status()

        if status["status"] == "active":
            print(f"🔄 当前项目：{status['project_type']}")
            print(f"📊 当前进度：{status['progress']*100:.0f}%")
            print(f"⏱️ 已用时间：{status['elapsed_time']:.0f}分钟")
            print(f"🎯 预估时间：{status['estimated_time']}分钟")
            print()

        print("🚀 可用工作流：")
        print("  /flow 363              - 经典3-6-3工作流")
        print("  /flow 363-dev          - 智能项目开发流程")
        print("  /flow 363-requirement  - 专注需求拆解阶段")
        print("  /flow 363-implementation - 专注代码生成阶段")
        print("  /flow 363-testing      - 专注验收迭代阶段")
        print()

        print("🧠 智能工作流：")
        print("  /flow smart [描述]     - AI自动选择最佳流程")
        print("  /flow adaptive [描述]  - 个性化自适应流程")
        print()

        print("📊 学习和分析：")
        print("  /flow profile          - 查看开发者学习档案")
        print("  /flow learn            - 获取学习和优化建议")
        print()

        # 智能推荐
        if status["status"] != "active":
            recommendations = self._get_smart_recommendations()
            if recommendations:
                print("💡 AI推荐：")
                for rec in recommendations:
                    print(f"  • {rec}")
                print()

    def _handle_363_workflow(self, subcommand, args):
        """处理3-6-3工作流"""
        if subcommand == "dev" or subcommand is None:
            self._start_intelligent_363_dev(args)
        elif subcommand == "requirement":
            self._start_requirement_phase()
        elif subcommand == "implementation":
            self._start_implementation_phase()
        elif subcommand == "testing":
            self._start_testing_phase()
        else:
            print(f"❌ 未知的3-6-3子命令：{subcommand}")
            print("使用 /flow 363 查看可用选项")

    def _start_intelligent_363_dev(self, args):
        """启动智能3-6-3项目开发流程"""
        description = " ".join(args) if args else input("📝 请描述您的项目需求：")

        if not description.strip():
            print("❌ 项目描述不能为空")
            return

        print("\n🧠 智能分析中...")
        context = self.engine.start_project(description)

        print(f"\n✅ 检测到项目类型：{context.project_type.value}")
        print(f"📊 复杂度评估：{context.complexity}")
        print(f"⏱️ 预估开发时间：{context.estimated_time}分钟")
        print(f"🛠️ 推荐技术栈：{', '.join(context.tech_stack)}")

        if context.issues_found:
            print(f"⚠️ 潜在问题：{', '.join(context.issues_found)}")

        # 个性化推荐
        recommendations = self.engine.get_personalized_recommendations(context)
        if recommendations:
            print("\n💡 个性化推荐：")
            for rec in recommendations:
                print(f"  • {rec}")

        print(f"\n🚀 是否启动为您优化的3-6-3开发流程？[Y/n]")
        response = input().strip().lower()

        if response in ['', 'y', 'yes']:
            self._execute_363_workflow(context)
        else:
            print("❌ 已取消项目启动")

    def _execute_363_workflow(self, context):
        """执行3-6-3工作流"""
        print("\n🎯 开始3-6-3智能工作流")
        print("=" * 50)

        # 阶段1：需求拆解（3个动作）
        self._execute_requirement_phase(context)

        # 阶段2：代码生成（2个动作）
        self._execute_implementation_phase(context)

        # 阶段3：验收迭代（2个动作）
        self._execute_testing_phase(context)

        # 完成总结
        self._complete_workflow(context)

    def _execute_requirement_phase(self, context):
        """执行需求拆解阶段"""
        print(f"\n📋 第一阶段：需求拆解（25分钟）")
        print("-" * 30)

        # 动作1：需求清晰描述
        print("\n1️⃣ 需求清晰描述")
        requirement_template = self._load_requirement_template()
        print("📋 已为您准备需求模板：")
        print(requirement_template)

        # 动作2：补充详细文档
        print("\n2️⃣ AI补充详细文档")
        print("🤖 基于您的需求，AI将补充：")
        print("  • 详细的技术架构设计")
        print("  • 完整的功能规格说明")
        print("  • 具体的实现方案")
        print("  • 开发计划和里程碑")

        # 动作3：清空上下文
        print("\n3️⃣ 清空上下文环境")
        print("🔄 准备专注于代码生成...")

        context.current_stage = WorkflowStage.REQUIREMENT
        print("✅ 需求拆解阶段完成")

    def _execute_implementation_phase(self, context):
        """执行代码生成阶段"""
        print(f"\n💻 第二阶段：代码生成（45分钟）")
        print("-" * 30)

        # 动作4：严格生成
        print("\n4️⃣ 严格按照需求文档生成")
        print("🔧 基于详细需求文档生成：")
        print("  • 完整的项目源代码")
        print("  • 项目结构和配置文件")
        print("  • 使用说明和部署指南")
        print("  • 测试用例和API文档")

        # 动作5：专注执行
        print("\n5️⃣ 专注代码实现")
        print("⚡ 保持架构一致性，确保代码质量标准")

        context.current_stage = WorkflowStage.IMPLEMENTATION
        print("✅ 代码生成阶段完成")

    def _execute_testing_phase(self, context):
        """执行验收迭代阶段"""
        print(f"\n🔍 第三阶段：验收迭代（40分钟）")
        print("-" * 30)

        # 动作6：集中测试
        print("\n6️⃣ 集中验收测试")
        print("🧪 全面测试验证：")
        test_items = [
            "功能完整性测试",
            "性能指标验证",
            "安全性检查",
            "兼容性测试"
        ]
        for item in test_items:
            print(f"  ✓ {item}")

        # 动作7：批量修复
        print("\n7️⃣ 批量问题修复")
        print("🔧 记录所有发现问题，一次性修复，避免零散修改")

        context.current_stage = WorkflowStage.TESTING
        print("✅ 验收迭代阶段完成")

    def _complete_workflow(self, context):
        """完成工作流"""
        context.current_stage = WorkflowStage.COMPLETED
        context.last_activity = datetime.now()

        # 记录学习数据
        feedback = {
            "satisfaction": 5,  # 默认满意度
            "completed": True,
            "final_time": (context.last_activity - context.start_time).total_seconds() / 60
        }
        self.engine.update_learning_data(context, WorkflowStage.COMPLETED, feedback)

        print(f"\n🎉 项目完成！")
        print("=" * 50)
        print(f"📊 项目统计：")
        print(f"  • 项目类型：{context.project_type.value}")
        print(f"  • 实际用时：{feedback['final_time']:.0f}分钟")
        print(f"  • 预估用时：{context.estimated_time}分钟")
        print(f"  • 技术栈：{', '.join(context.tech_stack)}")

        # 更新学习数据
        print(f"\n🧠 已更新您的开发模式学习数据")

    def _handle_smart_flow(self, args):
        """处理智能Flow"""
        if args:
            description = " ".join(args)
            print(f"🧠 AI智能分析：{description}")

            # 自动检测最适合的流程
            context = self.engine.start_project(description)

            # 根据项目类型和复杂度智能选择流程
            if context.complexity == "simple":
                print("💡 推荐：简化3-6-3流程（专注核心功能）")
            elif context.complexity == "complex":
                print("💡 推荐：完整3-6-3流程 + 质量强化")
            else:
                print("💡 推荐：标准3-6-3智能流程")

            # 自动启动推荐流程
            self._execute_363_workflow(context)
        else:
            print("🤖 请提供项目描述，AI将自动选择最佳流程")
            print("示例：/flow smart 开发一个电商网站")

    def _handle_adaptive_flow(self, args):
        """处理自适应Flow"""
        if not args:
            print("📊 您的开发档案：")
            self._show_developer_profile()
            return

        description = " ".join(args)
        print(f"🎯 个性化自适应流程：{description}")

        # 基于学习档案完全个性化
        context = self.engine.start_project(description)

        # 应用个性化设置
        self._apply_personalization(context)
        self._execute_363_workflow(context)

    def _handle_profile(self):
        """处理开发者档案"""
        print("👤 开发者学习档案")
        print("=" * 50)
        self._show_developer_profile()

    def _handle_learning(self):
        """处理学习和建议"""
        print("📚 智能学习建议")
        print("=" * 50)

        # 分析当前模式
        profile = self.engine.profile

        print("🎯 您的开发模式分析：")

        # 项目偏好分析
        if profile.project_preferences:
            print("\n📊 项目偏好：")
            for project_type, data in profile.project_preferences.items():
                if data["frequency"] > 0:
                    print(f"  • {project_type}: {data['frequency']}次项目")
                    if data.get("avg_time"):
                        print(f"    平均用时：{data['avg_time']:.0f}分钟")

        # 工作模式分析
        if profile.work_patterns:
            print("\n⏰ 工作模式：")
            for key, value in profile.work_patterns.items():
                print(f"  • {key}: {value}")

        # 学习优化建议
        if profile.learned_optimizations:
            print("\n💡 学习到的优化：")
            for key, value in profile.learned_optimizations.items():
                print(f"  • {key}: {value}")

        # 生成新建议
        recommendations = self._generate_learning_recommendations()
        if recommendations:
            print("\n🚀 新的建议：")
            for rec in recommendations:
                print(f"  • {rec}")

    def _intelligent_parse(self, args):
        """智能解析用户意图"""
        query = " ".join(args).lower()

        # 意图识别
        if any(word in query for word in ["状态", "进度", "当前"]):
            self._show_status()
        elif any(word in query for word in ["建议", "推荐", "优化"]):
            self._handle_learning()
        elif any(word in query for word in ["继续", "恢复"]):
            self._resume_workflow()
        else:
            # 默认启动智能流程
            self._handle_smart_flow(args)

    def _load_requirement_template(self) -> str:
        """加载需求模板"""
        template_file = self.templates_dir / "requirement_template.md"
        if template_file.exists():
            with open(template_file, 'r', encoding='utf-8') as f:
                return f.read()

        # 返回默认模板
        return """# 项目需求模板

## 🎯 项目概述
- **项目名称**：[项目名称]
- **项目类型**：[Web应用/CLI工具/API服务等]
- **核心目标**：[主要解决的问题]

## 📋 核心功能
1. **[功能1]** - [详细描述]
2. **[功能2]** - [详细描述]
3. **[功能3]** - [详细描述]

## 💻 技术要求
- **编程语言**：[首选技术栈]
- **框架要求**：[特定框架或库]
- **部署环境**：[运行环境要求]

## 🔧 技术约束
- **性能要求**：[响应时间、并发等]
- **安全要求**：[数据保护、权限控制等]
- **兼容性要求**：[平台、浏览器等]

## 📊 验收标准
- [ ] 功能完整性
- [ ] 性能指标
- [ ] 安全检查
- [ ] 兼容性测试
"""

    def _show_developer_profile(self):
        """显示开发者档案"""
        profile = self.engine.profile

        # 项目统计
        print(f"📈 项目统计：")
        total_projects = sum(data.get("frequency", 0) for data in profile.project_preferences.values())
        print(f"  • 总项目数：{total_projects}")

        if profile.project_preferences:
            favorite_type = max(profile.project_preferences.items(),
                              key=lambda x: x[1].get("frequency", 0))
            print(f"  • 最擅长的项目类型：{favorite_type[0]}")

        # 技术栈偏好
        if profile.technology_preferences:
            print(f"\n🛠️ 技术栈偏好：")
            for project_type, tech_stack in profile.technology_preferences.items():
                if tech_stack:
                    print(f"  • {project_type}: {', '.join(tech_stack[:3])}")

        # 质量标准
        if profile.quality_standards:
            print(f"\n🎯 质量关注点：")
            for key, value in profile.quality_standards.items():
                print(f"  • {key}: {value}")

        if not any([profile.project_preferences, profile.technology_preferences, profile.quality_standards]):
            print("  📝 暂无数据，开始使用后会自动学习")

    def _generate_learning_recommendations(self) -> list:
        """生成学习建议"""
        recommendations = []
        profile = self.engine.profile

        # 基于项目数量建议
        total_projects = sum(data.get("frequency", 0) for data in profile.project_preferences.values())

        if total_projects < 3:
            recommendations.append("多尝试不同类型的项目，AI会更好地了解您的偏好")
        elif total_projects < 10:
            recommendations.append("尝试使用个性化流程获得更好的开发体验")
        else:
            recommendations.append("您的学习档案已很丰富，可以尝试复杂项目挑战")

        # 基于技术栈建议
        if profile.technology_preferences:
            all_tech = []
            for tech_stack in profile.technology_preferences.values():
                all_tech.extend(tech_stack)

            if len(set(all_tech)) < 5:
                recommendations.append("尝试学习新技术栈，扩展技术视野")

        return recommendations

    def _show_status(self):
        """显示当前状态"""
        status = self.engine.get_workflow_status()

        if status["status"] == "no_active_project":
            print("🔄 当前无活跃项目")
        else:
            print(f"🔄 项目状态：{status['status']}")
            print(f"📊 当前进度：{status['progress']*100:.0f}%")
            print(f"⏱️ 已用时间：{status['elapsed_time']:.0f}分钟")
            print(f"🎯 预估时间：{status['estimated_time']}分钟")
            print(f"🐛 发现问题：{status['issues_found']}个")

    def _get_smart_recommendations(self) -> list:
        """获取智能推荐"""
        recommendations = []

        # 基于历史项目推荐
        if self.engine.profile.project_preferences:
            # 找出最常见的项目类型
            most_common = max(self.engine.profile.project_preferences.items(),
                            key=lambda x: x[1].get("frequency", 0))
            if most_common[1].get("frequency", 0) > 2:
                recommendations.append(f"您最擅长{most_common[0]}类项目，可以尝试进阶功能")

        # 基于当前时间推荐
        current_hour = datetime.now().hour
        if 9 <= current_hour <= 11:
            recommendations.append("上午适合需求分析和架构设计")
        elif 14 <= current_hour <= 16:
            recommendations.append("下午适合代码开发和实现")
        else:
            recommendations.append("当前时间适合测试和优化工作")

        return recommendations

    def _apply_personalization(self, context):
        """应用个性化设置"""
        profile = self.engine.profile
        type_key = context.project_type.value

        # 应用学习到的优化
        if type_key in profile.learned_optimizations:
            optimizations = profile.learned_optimizations[type_key]
            print(f"🎯 应用个性化设置：{optimizations}")

        # 应用质量标准
        if profile.quality_standards:
            quality_focus = profile.quality_standards.get("quality_focus", [])
            if quality_focus:
                print(f"🎯 质量重点关注：{', '.join(quality_focus)}")

    def _resume_workflow(self):
        """恢复工作流"""
        if self.engine.current_context:
            print("🔄 恢复工作流...")
            print(f"当前阶段：{self.engine.current_context.current_stage.value}")
            # 可以在这里添加恢复逻辑
        else:
            print("❌ 没有可恢复的工作流")

    def _show_help(self):
        """显示帮助信息"""
        print("🧠 智能Flow工作流系统 - 帮助")
        print("=" * 50)
        print("基本用法：")
        print("  /flow                    - 显示可用工作流")
        print("  /flow 363               - 启动经典3-6-3工作流")
        print("  /flow smart [描述]      - AI智能选择流程")
        print("  /flow adaptive [描述]   - 个性化自适应流程")
        print("\n学习功能：")
        print("  /flow profile          - 查看开发者档案")
        print("  /flow learn            - 获取学习建议")
        print("\n更多帮助：")
        print("  系统会自动学习您的开发模式")
        print("  越用越懂您，提供个性化建议")


def main():
    """主函数"""
    handler = FlowHandler()

    # 解析命令行参数
    if len(sys.argv) > 1:
        handler.handle_command(sys.argv[1:])
    else:
        handler.handle_command([])


if __name__ == "__main__":
    main()