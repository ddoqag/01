#!/usr/bin/env python3
"""
智能检测器 - Hook自动触发机制
智能识别开发场景，自动推荐或启动3-6-3工作流
"""

import sys
import os
import json
import re
from pathlib import Path
from datetime import datetime

# 添加核心模块路径
sys.path.insert(0, str(Path(__file__).parent.parent / "core"))

try:
    from intelligent_engine import IntelligentEngine
except ImportError:
    print("智能引擎未找到，跳过智能检测")
    sys.exit(0)


class IntelligentDetector:
    """智能检测器"""

    def __init__(self):
        self.plugin_root = Path(__file__).parent.parent
        self.engine = IntelligentEngine(str(self.plugin_root))

        # 触发模式配置
        self.trigger_patterns = {
            "project_creation": [
                r"我想?开发",
                r"创建.*项目",
                r"新建.*应用",
                r"做一个.*网站",
                r"写个.*工具",
                r"实现.*功能",
                r"开发.*系统",
                r"构建.*平台"
            ],
            "feature_development": [
                r"添加.*功能",
                r"增加.*特性",
                r"实现.*模块",
                r"开发.*组件",
                r"写.*接口",
                r"做.*页面"
            ],
            "complex_project": [
                r"完整的.*系统",
                r"企业级.*应用",
                r"复杂的.*项目",
                r"大规模.*开发",
                r".*管理系统",
                r".*电商平台"
            ]
        }

        # 智能推荐阈值
        self.recommendation_threshold = 0.7

    def detect_and_respond(self, user_input: str) -> bool:
        """检测用户输入并智能响应"""
        if not user_input or len(user_input.strip()) < 5:
            return False

        # 分析输入内容
        analysis = self._analyze_input(user_input)

        if not analysis:
            return False

        # 获取当前项目状态
        current_status = self.engine.get_workflow_status()

        # 根据不同情况响应
        if current_status["status"] == "no_active_project":
            return self._handle_no_project(analysis, user_input)
        else:
            return self._handle_active_project(analysis, user_input, current_status)

    def _analyze_input(self, user_input: str) -> dict:
        """分析用户输入"""
        analysis = {
            "intent": None,
            "confidence": 0.0,
            "project_type": None,
            "complexity": None,
            "suggested_action": None
        }

        input_lower = user_input.lower()

        # 检测项目创建意图
        for pattern in self.trigger_patterns["project_creation"]:
            if re.search(pattern, input_lower):
                analysis["intent"] = "project_creation"
                analysis["confidence"] += 0.3
                break

        # 检测功能开发意图
        for pattern in self.trigger_patterns["feature_development"]:
            if re.search(pattern, input_lower):
                analysis["intent"] = "feature_development"
                analysis["confidence"] += 0.25
                break

        # 检测复杂项目
        for pattern in self.trigger_patterns["complex_project"]:
            if re.search(pattern, input_lower):
                analysis["complexity"] = "complex"
                analysis["confidence"] += 0.2
                break

        # 智能分析项目类型和复杂度
        if analysis["intent"]:
            project_type = self.engine.detect_project_type(user_input)
            analysis["project_type"] = project_type

            if not analysis["complexity"]:
                analysis["complexity"] = self.engine.estimate_complexity(user_input, project_type)

            # 基于置信度决定建议动作
            if analysis["confidence"] >= self.recommendation_threshold:
                analysis["suggested_action"] = "recommend_363_workflow"
            elif analysis["confidence"] >= 0.4:
                analysis["suggested_action"] = "suggest_smart_flow"

        return analysis if analysis["confidence"] > 0.1 else None

    def _handle_no_project(self, analysis: dict, user_input: str) -> bool:
        """处理无活跃项目状态"""
        if analysis["suggested_action"] == "recommend_363_workflow":
            self._show_363_recommendation(analysis, user_input)
            return True
        elif analysis["suggested_action"] == "suggest_smart_flow":
            self._show_smart_suggestion(analysis, user_input)
            return True

        return False

    def _handle_active_project(self, analysis: dict, user_input: str, status: dict) -> bool:
        """处理有活跃项目状态"""
        # 如果用户在描述新项目，可能需要重新开始
        if analysis["intent"] == "project_creation" and analysis["confidence"] > 0.6:
            print("\n⚠️ 检测到您在描述新项目")
            print(f"当前项目进度：{status['progress']*100:.0f}%")
            print("是否要：")
            print("  1. 继续当前项目")
            print("  2. 开始新项目（当前项目将保存）")
            print("  3. 查看项目状态")
            return True

        return False

    def _show_363_recommendation(self, analysis: dict, user_input: str):
        """显示3-6-3工作流推荐"""
        print("\n🧠 智能推荐：3-6-3工作流")
        print("=" * 50)

        print(f"📝 检测到项目描述：{user_input[:50]}...")
        print(f"🎯 项目类型：{analysis['project_type'].value if analysis['project_type'] else '智能识别中'}")
        print(f"📊 复杂度：{analysis['complexity'] if analysis['complexity'] else '评估中'}")
        print(f"🎯 匹配度：{analysis['confidence']*100:.0f}%")

        # 如果是学习过该类型项目，显示个性化信息
        if analysis['project_type']:
            type_key = analysis['project_type'].value
            if type_key in self.engine.profile.project_preferences:
                pref_data = self.engine.profile.project_preferences[type_key]
                if pref_data.get("frequency", 0) > 0:
                    print(f"📈 您有{pref_data['frequency']}个{type_key}项目经验")
                    if pref_data.get("avg_time"):
                        print(f"⏱️ 历史平均用时：{pref_data['avg_time']:.0f}分钟")

        # 推荐具体流程
        if analysis['complexity'] == 'complex':
            print("\n💡 推荐：完整3-6-3工作流")
            print("   包含详细的需求分析、架构设计和质量保证")
            command = "/flow 363-dev"
        else:
            print("\n💡 推荐：智能3-6-3流程")
            print("   根据项目特点自动优化的开发流程")
            command = "/flow smart " + user_input

        print(f"\n🚀 启动命令：{command}")
        print("或使用：/flow 363 查看所有选项")

    def _show_smart_suggestion(self, analysis: dict, user_input: str):
        """显示智能建议"""
        print("\n💡 智能建议")
        print("=" * 30)

        if analysis['project_type']:
            print(f"🎯 可能是{analysis['project_type'].value}类项目")

        print("🤖 使用智能Flow可以获得更好的开发体验：")
        print("   • AI自动分析项目需求")
        print("   • 个性化开发建议")
        print("   • 智能技术栈推荐")

        print(f"\n💬 尝试：/flow smart {user_input}")


def main():
    """主函数"""
    # 从环境变量获取用户输入
    user_input = os.getenv("CLAUDE_USER_PROMPT", "")

    if not user_input:
        sys.exit(0)

    detector = IntelligentDetector()

    try:
        detector.detect_and_respond(user_input)
    except Exception as e:
        # 智能检测失败不应该影响正常流程
        print(f"智能检测遇到问题：{e}")
        sys.exit(0)


if __name__ == "__main__":
    main()