#!/usr/bin/env python3
"""
工作流守护器 - 防止违反3-6-3原则
在用户执行代码编辑操作时，智能检查和提醒
"""

import sys
import os
import json
from pathlib import Path
from datetime import datetime

# 添加核心模块路径
sys.path.insert(0, str(Path(__file__).parent.parent / "core"))

try:
    from intelligent_engine import IntelligentEngine, WorkflowStage
except ImportError:
    print("智能引擎未找到，跳过工作流守护")
    sys.exit(0)


class WorkflowGuard:
    """工作流守护器"""

    def __init__(self):
        self.plugin_root = Path(__file__).parent.parent
        self.engine = IntelligentEngine(str(self.plugin_root))

        # 3个关键坑点的检测规则
        self.violation_patterns = {
            "scattered_changes": {
                "name": "零散修改",
                "description": "发现问题立即修复，反复往返",
                "indicators": [
                    r"修复.*bug",
                    r"fix.*issue",
                    r"改.*错误",
                    r"修.*问题"
                ]
            },
            "mixed_features": {
                "name": "功能与修复混合",
                "description": "修复bug时顺便添加新功能",
                "indicators": [
                    r"同时.*修复.*和.*添加",
                    r"顺便.*实现",
                    r"顺便.*加.*功能"
                ]
            },
            "excessive_modifications": {
                "name": "过度修改",
                "description": "同一问题反复修改，每次引入新问题",
                "indicators": []  # 通过状态跟踪检测
            }
        }

        # 工具到操作的映射
        self.tool_actions = {
            "Edit": "编辑文件",
            "Write": "写入文件",
            "MultiEdit": "批量编辑"
        }

    def guard_operation(self, tool_name: str, tool_args: dict) -> bool:
        """守护工具操作"""
        # 获取当前工作流状态
        status = self.engine.get_workflow_status()

        if status["status"] == "no_active_project":
            # 无活跃项目，记录基础信息
            return self._log_basic_operation(tool_name, tool_args)

        # 获取当前上下文
        context = self.engine.current_context
        if not context:
            return True

        # 检查工作流阶段是否合适
        if not self._check_stage_appropriate(tool_name, context):
            return self._handle_inappropriate_stage(tool_name, context)

        # 检查是否违反3个关键坑点
        violations = self._check_violations(tool_name, tool_args, context)
        if violations:
            return self._handle_violations(violations, tool_name, context)

        # 记录正常操作
        self._record_operation(tool_name, tool_args, context)
        return True

    def _check_stage_appropriate(self, tool_name: str, context) -> bool:
        """检查操作是否符合当前阶段"""
        current_stage = context.current_stage

        # 在需求拆解阶段，应该避免大量代码编辑
        if current_stage == WorkflowStage.REQUIREMENT and tool_name in ["Edit", "Write"]:
            # 除非是编辑需求文档
            if not self._is_requirement_edit(tool_name, tool_args):
                return False

        # 在验收迭代阶段，应该避免添加新功能
        if current_stage == WorkflowStage.TESTING:
            if self._is_feature_addition(tool_name, tool_args):
                return False

        return True

    def _check_violations(self, tool_name: str, tool_args: dict, context) -> list:
        """检查是否违反3个关键坑点"""
        violations = []

        # 获取操作描述
        operation_desc = self._extract_operation_description(tool_name, tool_args)

        # 检查零散修改
        if self._detect_scattered_changes(operation_desc, context):
            violations.append("scattered_changes")

        # 检查功能与修复混合
        if self._detect_mixed_features(operation_desc):
            violations.append("mixed_features")

        # 检查过度修改（通过状态分析）
        if self._detect_excessive_modifications(context):
            violations.append("excessive_modifications")

        return violations

    def _is_requirement_edit(self, tool_name: str, tool_args: dict) -> bool:
        """判断是否是需求文档编辑"""
        if tool_name != "Edit":
            return False

        file_path = tool_args.get("file_path", "")
        requirement_files = [
            "requirement", "需求", "spec", "规格", "design", "设计"
        ]

        return any(keyword in file_path.lower() for keyword in requirement_files)

    def _is_feature_addition(self, tool_name: str, tool_args: dict) -> bool:
        """判断是否是添加新功能"""
        # 通过文件路径和内容判断
        file_path = tool_args.get("file_path", "")
        new_string = tool_args.get("new_string", "")

        feature_keywords = [
            "new function", "新功能", "add feature", "添加功能",
            "implement", "实现", "create", "创建"
        ]

        return any(keyword in new_string.lower() for keyword in feature_keywords)

    def _detect_scattered_changes(self, operation_desc: str, context) -> bool:
        """检测零散修改模式"""
        # 检查最近是否有多个小的修复操作
        # 这里可以实现更复杂的逻辑

        # 简化实现：检查操作描述中的修复关键词
        scattered_indicators = [
            r"修复.*小.*问题",
            r"改.*小.*bug",
            r"修.*细节",
            r"调.*格式"
        ]

        import re
        for pattern in scattered_indicators:
            if re.search(pattern, operation_desc, re.IGNORECASE):
                return True

        return False

    def _detect_mixed_features(self, operation_desc: str) -> bool:
        """检测功能与修复混合"""
        mixed_patterns = [
            r"修复.*同时.*添加",
            r"顺便.*实现",
            r"顺便.*加",
            r"修.*bug.*顺便"
        ]

        import re
        for pattern in mixed_patterns:
            if re.search(pattern, operation_desc, re.IGNORECASE):
                return True

        return False

    def _detect_excessive_modifications(self, context) -> bool:
        """检测过度修改"""
        # 可以通过分析最近的操作历史来判断
        # 这里简化实现

        # 如果在同一阶段停留时间过长，可能存在问题
        if context.current_stage == WorkflowStage.IMPLEMENTATION:
            elapsed = (datetime.now() - context.start_time).total_seconds() / 60
            if elapsed > context.estimated_time * 1.5:
                return True

        return False

    def _extract_operation_description(self, tool_name: str, tool_args: dict) -> str:
        """提取操作描述"""
        description = f"{self.tool_actions.get(tool_name, tool_name)}"

        if tool_name == "Edit":
            file_path = tool_args.get("file_path", "")
            old_string = tool_args.get("old_string", "")
            new_string = tool_args.get("new_string", "")

            if old_string and new_string:
                # 简化描述提取
                if len(new_string) > len(old_string):
                    description += " (增加内容)"
                elif len(new_string) < len(old_string):
                    description += " (删除内容)"
                else:
                    description += " (修改内容)"

            if file_path:
                description += f" 文件: {Path(file_path).name}"

        elif tool_name == "Write":
            file_path = tool_args.get("file_path", "")
            if file_path:
                description += f" 文件: {Path(file_path).name}"

        return description

    def _handle_inappropriate_stage(self, tool_name: str, context) -> bool:
        """处理不合适的阶段操作"""
        stage = context.current_stage

        if stage == WorkflowStage.REQUIREMENT:
            print(f"\n⚠️ 工作流提醒：当前处于需求拆解阶段")
            print(f"📋 建议专注于需求分析和技术设计")
            print(f"💡 如需编辑代码，请先完成需求拆解阶段")
            print(f"🚀 使用 /flow 363-requirement 专注需求分析")

        elif stage == WorkflowStage.TESTING:
            print(f"\n⚠️ 工作流提醒：当前处于验收迭代阶段")
            print(f"🔍 建议专注于测试和问题修复")
            print(f"💡 避免在此阶段添加新功能")
            print(f"🚀 使用 /flow 363-testing 专注测试验收")

        # 询问用户是否继续
        print(f"\n是否继续{self.tool_actions.get(tool_name, tool_name)}操作？[Y/n]")
        try:
            response = input().strip().lower()
            return response in ['', 'y', 'yes']
        except:
            return True  # 无法读取输入时允许操作

    def _handle_violations(self, violations: list, tool_name: str, context) -> bool:
        """处理违规操作"""
        print(f"\n⚠️ 检测到可能违反3-6-3工作流原则的操作：")

        for violation_type in violations:
            violation = self.violation_patterns[violation_type]
            print(f"\n🚨 {violation['name']}")
            print(f"   说明：{violation['description']}")

        # 提供3-6-3工作流指导
        print(f"\n💡 3-6-3工作流建议：")

        if "scattered_changes" in violations:
            print("   • 集中记录所有问题，批量修复")
            print("   • 避免单个问题立即修复")

        if "mixed_features" in violations:
            print("   • 严格分离bug修复和功能开发")
            print("   • 一次只做一件事")

        if "excessive_modifications" in violations:
            print("   • 同一问题修改超过3次时考虑重生成")
            print("   • 避免技术债务累积")

        print(f"\n🤖 建议使用：")
        print(f"   /flow 363 - 重新启动标准工作流")
        print(f"   /flow smart - AI智能辅助")

        # 询问用户是否继续
        print(f"\n是否继续当前操作？[Y/n]")
        try:
            response = input().strip().lower()
            return response in ['', 'y', 'yes']
        except:
            return True  # 无法读取输入时允许操作

    def _record_operation(self, tool_name: str, tool_args: dict, context):
        """记录正常操作"""
        # 这里可以实现操作历史记录
        # 用于后续分析和学习
        pass

    def _log_basic_operation(self, tool_name: str, tool_args: dict) -> bool:
        """记录基础操作（无活跃项目时）"""
        # 可以提供一些通用建议
        return True


def main():
    """主函数"""
    # 从环境变量获取工具信息
    tool_name = os.getenv("CLAUDE_TOOL_NAME", "")
    tool_args_str = os.getenv("CLAUDE_TOOL_ARGS", "{}")

    if not tool_name:
        sys.exit(0)

    try:
        tool_args = json.loads(tool_args_str)
    except:
        tool_args = {}

    guard = WorkflowGuard()

    try:
        result = guard.guard_operation(tool_name, tool_args)
        sys.exit(0 if result else 2)  # 退出码2表示阻止操作
    except Exception as e:
        # 守护失败不应该影响正常流程
        print(f"工作流守护遇到问题：{e}")
        sys.exit(0)


if __name__ == "__main__":
    main()