#!/usr/bin/env python3
"""
会话初始化器
在会话开始时提供智能建议和状态恢复
"""

import sys
import os
import json
from pathlib import Path
from datetime import datetime, timedelta

# 添加核心模块路径
sys.path.insert(0, str(Path(__file__).parent.parent / "core"))

try:
    from intelligent_engine import IntelligentEngine
except ImportError:
    print("智能引擎未找到，跳过会话初始化")
    sys.exit(0)


class SessionInitializer:
    """会话初始化器"""

    def __init__(self):
        self.plugin_root = Path(__file__).parent.parent
        self.engine = IntelligentEngine(str(self.plugin_root))

    def initialize_session(self):
        """初始化会话"""
        try:
            # 检查是否有未完成的项目
            self._check_incomplete_projects()

            # 提供个性化建议
            self._provide_personalized_suggestions()

            # 显示智能提示
            self._show_smart_tips()

        except Exception as e:
            print(f"会话初始化遇到问题：{e}")

    def _check_incomplete_projects(self):
        """检查未完成的项目"""
        status = self.engine.get_workflow_status()

        if status["status"] == "active":
            print(f"\n🔄 检测到未完成的项目")
            print(f"📊 项目类型：{status['project_type']}")
            print(f"🎯 当前进度：{status['progress']*100:.0f}%")
            print(f"⏱️ 已用时间：{status['elapsed_time']:.0f}分钟")

            # 分析是否超时
            if status["elapsed_time"] > status["estimated_time"] * 1.2:
                print(f"⚠️ 项目已超出预估时间，建议：")
                print(f"   • 检查是否遇到技术难题")
                print(f"   • 考虑调整需求范围")
                print(f"   • 使用 /flow learn 获取优化建议")

            print(f"\n💡 继续工作：/flow resume")
            print(f"📋 查看详情：/flow status")

    def _provide_personalized_suggestions(self):
        """提供个性化建议"""
        profile = self.engine.profile

        # 统计用户偏好
        total_projects = sum(data.get("frequency", 0)
                           for data in profile.project_preferences.values())

        if total_projects == 0:
            self._show_new_user_suggestions()
        elif total_projects < 5:
            self._show_intermediate_suggestions()
        else:
            self._show_expert_suggestions()

    def _show_new_user_suggestions(self):
        """显示新用户建议"""
        print(f"\n👋 欢迎使用智能3-6-3工作流系统！")
        print(f"🎯 这是一个会学习您开发模式的AI助手")
        print(f"\n🚀 快速开始：")
        print(f"   /flow smart 开发一个[项目描述] - AI智能引导")
        print(f"   /flow 363 - 经典3-6-3工作流")
        print(f"   /flow help - 查看所有功能")

    def _show_intermediate_suggestions(self):
        """显示中级用户建议"""
        print(f"\n📈 您的开发档案正在形成中...")

        # 分析最常做的项目类型
        if self.engine.profile.project_preferences:
            most_common = max(self.engine.profile.project_preferences.items(),
                            key=lambda x: x[1].get("frequency", 0))
            if most_common[1].get("frequency", 0) > 0:
                print(f"🎯 您最擅长：{most_common[0]}类项目")

                # 提供进阶建议
                if most_common[1].get("frequency", 0) >= 3:
                    print(f"💡 建议：尝试 /flow adaptive 获得个性化流程")

        print(f"📚 查看学习进展：/flow learn")

    def _show_expert_suggestions(self):
        """显示专家用户建议"""
        print(f"\n🌟 您已经是经验丰富的用户！")

        # 展示学习成果
        profile = self.engine.profile

        if profile.quality_standards:
            quality_focus = profile.quality_standards.get("quality_focus", [])
            if quality_focus:
                print(f"🎯 您的质量关注点：{', '.join(quality_focus)}")

        if profile.learned_optimizations:
            print(f"💡 已掌握的优化：")
            for key, value in list(profile.learned_optimizations.items())[:3]:
                print(f"   • {key}: {value}")

        # 提供高级功能建议
        print(f"\n🚀 高级功能：")
        print(f"   /flow adaptive - 完全个性化的工作流")
        print(f"   /flow profile - 查看完整学习档案")

    def _show_smart_tips(self):
        """显示智能提示"""
        current_hour = datetime.now().hour

        # 基于时间的智能提示
        time_tips = {
            (9, 11): "☀️ 上午思维清晰，适合需求分析和架构设计",
            (11, 13): "🍽️ 临近午休，适合代码审查和文档编写",
            (14, 16): "⚡ 下午精力充沛，适合核心功能开发",
            (16, 18): "🔍 傍晚适合测试和优化工作",
            (19, 21): "🌙 晚上适合学习和技术调研"
        }

        for (start, end), tip in time_tips.items():
            if start <= current_hour < end:
                print(f"\n{tip}")
                break

        # 基于工作日的提示
        weekday = datetime.now().weekday()
        if weekday == 0:  # 周一
            print(f"📅 新的一周，适合规划新项目")
        elif weekday == 4:  # 周五
            print(f"📅 周末前，建议完成当前项目的重要功能")

        # 基于用户习惯的提示
        profile = self.engine.profile
        if profile.work_patterns:
            preferred_sessions = profile.work_patterns.get("preferred_work_sessions")
            if preferred_sessions:
                print(f"💭 根据您的习惯，您偏好在{preferred_sessions}时段工作")

        # 随机智能提示
        tips = [
            "💡 使用 /flow smart 让AI为您选择最佳开发流程",
            "🧠 系统会自动学习您的开发模式，越用越懂您",
            "⚠️ 工作流守护会帮助您避免常见的开发陷阱",
            "📊 您的所有项目数据都会被安全地学习和分析",
            "🎯 3-6-3工作流已经过200+次实战验证"
        ]

        import random
        if random.random() < 0.3:  # 30%概率显示额外提示
            print(f"\n{random.choice(tips)}")


def main():
    """主函数"""
    initializer = SessionInitializer()
    initializer.initialize_session()


if __name__ == "__main__":
    main()