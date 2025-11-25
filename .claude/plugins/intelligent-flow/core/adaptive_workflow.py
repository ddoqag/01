#!/usr/bin/env python3
"""
自适应工作流程
基于用户学习数据动态调整的3-6-3工作流
"""

import json
import statistics
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from pathlib import Path
from dataclasses import dataclass

from intelligent_engine import IntelligentEngine, WorkflowStage, ProjectType, DeveloperProfile


@dataclass
class WorkflowStep:
    """工作流步骤"""
    name: str
    base_duration: int  # 基础持续时间（分钟）
    weight: float  # 在总流程中的权重
    adaptable: bool  # 是否可自适应调整
    dependencies: List[str]  # 依赖的前置步骤


@dataclass
class AdaptiveConfiguration:
    """自适应配置"""
    step_durations: Dict[str, int]
    step_weights: Dict[str, float]
    quality_focus_areas: List[str]
    preferred_approaches: Dict[str, str]
    risk_factors: List[str]


class AdaptiveWorkflow:
    """自适应工作流程管理器"""

    def __init__(self, engine: IntelligentEngine):
        self.engine = engine
        self.plugin_root = Path(engine.plugin_root)
        self.config_dir = self.plugin_root / "data" / "adaptive"
        self.config_dir.mkdir(parents=True, exist_ok=True)

        # 基础工作流步骤
        self.base_steps = {
            "requirement_analysis": WorkflowStep(
                name="需求拆解",
                base_duration=25,
                weight=0.25,
                adaptable=True,
                dependencies=[]
            ),
            "technical_design": WorkflowStep(
                name="技术设计",
                base_duration=15,
                weight=0.15,
                adaptable=True,
                dependencies=["requirement_analysis"]
            ),
            "core_implementation": WorkflowStep(
                name="核心实现",
                base_duration=30,
                weight=0.35,
                adaptable=True,
                dependencies=["technical_design"]
            ),
            "testing_validation": WorkflowStep(
                name="测试验收",
                base_duration=25,
                weight=0.25,
                adaptable=True,
                dependencies=["core_implementation"]
            )
        }

        # 加载自适应配置
        self.adaptive_config = self._load_adaptive_config()

    def _load_adaptive_config(self) -> AdaptiveConfiguration:
        """加载自适应配置"""
        config_file = self.config_dir / "adaptive_config.json"

        if config_file.exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                return AdaptiveConfiguration(**data)
            except Exception as e:
                print(f"加载自适应配置失败: {e}")

        # 返回默认配置
        return AdaptiveConfiguration(
            step_durations={step.name: step.base_duration for step in self.base_steps.values()},
            step_weights={step.name: step.weight for step in self.base_steps.values()},
            quality_focus_areas=[],
            preferred_approaches={},
            risk_factors=[]
        )

    def _save_adaptive_config(self):
        """保存自适应配置"""
        config_file = self.config_dir / "adaptive_config.json"
        try:
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(self.adaptive_config.__dict__, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存自适应配置失败: {e}")

    def generate_adaptive_workflow(self, project_type: ProjectType, complexity: str) -> Dict:
        """生成自适应工作流程"""
        # 基于历史数据调整配置
        self._adjust_configuration_from_history(project_type)

        # 基于用户偏好调整
        self._adjust_configuration_from_preferences()

        # 生成工作流程
        workflow = {
            "project_type": project_type.value,
            "complexity": complexity,
            "estimated_total_time": self._calculate_total_time(),
            "steps": self._generate_adaptive_steps(),
            "quality_focus": self.adaptive_config.quality_focus_areas,
            "risk_factors": self.adaptive_config.risk_factors,
            "personalization_level": self._calculate_personalization_level()
        }

        return workflow

    def _adjust_configuration_from_history(self, project_type: ProjectType):
        """基于历史数据调整配置"""
        type_key = project_type.value

        if type_key not in self.engine.profile.project_preferences:
            return

        history = self.engine.profile.project_preferences[type_key]
        if not history.get("frequency", 0) > 0:
            return

        # 调整时间预估
        avg_time = history.get("avg_time")
        if avg_time:
            current_total = sum(self.adaptive_config.step_durations.values())
            if current_total > 0:
                adjustment_factor = avg_time / current_total
                for step_name in self.adaptive_config.step_durations:
                    self.adaptive_config.step_durations[step_name] = int(
                        self.adaptive_config.step_durations[step_name] * adjustment_factor
                    )

        # 调整权重分配
        if type_key in self.engine.profile.learned_optimizations:
            optimizations = self.engine.profile.learned_optimizations[type_key]
            if "stage_weights" in optimizations:
                self.adaptive_config.step_weights.update(optimizations["stage_weights"])

    def _adjust_configuration_from_preferences(self):
        """基于用户偏好调整配置"""
        profile = self.engine.profile

        # 调整质量关注点
        if profile.quality_standards:
            quality_focus = profile.quality_standards.get("quality_focus", [])
            self.adaptive_config.quality_focus_areas = quality_focus

        # 调整偏好的方法
        if profile.work_patterns:
            patterns = profile.work_patterns

            # 根据工作时段调整
            preferred_sessions = patterns.get("preferred_work_sessions")
            if preferred_sessions:
                self._adjust_for_work_session(preferred_sessions)

            # 根据常见痛点调整
            pain_points = patterns.get("common_pain_points", [])
            if pain_points:
                self._adjust_for_pain_points(pain_points)

    def _adjust_for_work_session(self, preferred_sessions: str):
        """根据偏好的工作时段调整"""
        current_hour = datetime.now().hour

        # 根据时段调整各步骤权重
        if "morning" in preferred_sessions and 9 <= current_hour <= 11:
            # 上午适合分析和设计
            self.adaptive_config.step_weights["requirement_analysis"] *= 1.2
            self.adaptive_config.step_weights["technical_design"] *= 1.1

        elif "afternoon" in preferred_sessions and 14 <= current_hour <= 16:
            # 下午适合实现
            self.adaptive_config.step_weights["core_implementation"] *= 1.2

        elif "evening" in preferred_sessions and 19 <= current_hour <= 21:
            # 晚上适合测试和优化
            self.adaptive_config.step_weights["testing_validation"] *= 1.2

    def _adjust_for_pain_points(self, pain_points: List[str]):
        """根据常见痛点调整"""
        for pain_point in pain_points:
            if "需求" in pain_point:
                # 加强需求分析
                self.adaptive_config.step_durations["requirement_analysis"] *= 1.3
                self.adaptive_config.step_weights["requirement_analysis"] *= 1.1

            elif "测试" in pain_point or "质量" in pain_point:
                # 加强测试验收
                self.adaptive_config.step_durations["testing_validation"] *= 1.3
                self.adaptive_config.step_weights["testing_validation"] *= 1.1

            elif "架构" in pain_point or "设计" in pain_point:
                # 加强技术设计
                self.adaptive_config.step_durations["technical_design"] *= 1.3
                self.adaptive_config.step_weights["technical_design"] *= 1.1

    def _calculate_total_time(self) -> int:
        """计算总预估时间"""
        return sum(self.adaptive_config.step_durations.values())

    def _generate_adaptive_steps(self) -> List[Dict]:
        """生成自适应步骤"""
        steps = []

        for step_name, step in self.base_steps.items():
            if step_name in self.adaptive_config.step_durations:
                duration = self.adaptive_config.step_durations[step_name]
            else:
                duration = step.base_duration

            if step_name in self.adaptive_config.step_weights:
                weight = self.adaptive_config.step_weights[step_name]
            else:
                weight = step.weight

            # 生成自适应步骤描述
            step_desc = {
                "name": step.name,
                "key": step_name,
                "duration": duration,
                "weight": weight,
                "adaptable": step.adaptable,
                "dependencies": step.dependencies,
                "personalized_tips": self._generate_step_tips(step_name)
            }

            steps.append(step_desc)

        return steps

    def _generate_step_tips(self, step_name: str) -> List[str]:
        """生成步骤的个性化提示"""
        tips = []

        # 基于学习数据的提示
        if step_name == "requirement_analysis":
            if self.adaptive_config.quality_focus_areas:
                tips.append(f"重点关注：{', '.join(self.adaptive_config.quality_focus_areas[:2])}")

        elif step_name == "technical_design":
            if "security" in self.adaptive_config.quality_focus_areas:
                tips.append("优先考虑安全架构设计")
            if "performance" in self.adaptive_config.quality_focus_areas:
                tips.append("预留性能优化空间")

        elif step_name == "core_implementation":
            preferred_approaches = self.engine.profile.learned_optimizations.get("coding_style")
            if preferred_approaches:
                tips.append(f"使用您偏好的编程风格：{preferred_approaches}")

        elif step_name == "testing_validation":
            if self.adaptive_config.risk_factors:
                tips.append(f"重点测试风险点：{', '.join(self.adaptive_config.risk_factors[:2])}")

        return tips

    def _calculate_personalization_level(self) -> float:
        """计算个性化程度"""
        factors = []

        # 基于项目数量
        total_projects = sum(data.get("frequency", 0)
                           for data in self.engine.profile.project_preferences.values())
        if total_projects > 0:
            factors.append(min(total_projects / 10.0, 1.0))  # 最多10个项目达到完全个性化

        # 基于学习数据的丰富度
        learned_data = len(self.engine.profile.learned_optimizations)
        if learned_data > 0:
            factors.append(min(learned_data / 5.0, 1.0))  # 最多5个学习点达到完全个性化

        # 基于质量标准的明确度
        if self.engine.profile.quality_standards:
            quality_clarity = len(self.engine.profile.quality_standards)
            factors.append(min(quality_clarity / 3.0, 1.0))  # 最多3个标准达到完全个性化

        if not factors:
            return 0.0

        return statistics.mean(factors)

    def record_workflow_execution(self, workflow: Dict, execution_data: Dict):
        """记录工作流执行情况"""
        # 更新自适应配置
        self._update_adaptive_config_from_execution(workflow, execution_data)

        # 记录成功模式
        self._record_success_patterns(workflow, execution_data)

        # 保存更新后的配置
        self._save_adaptive_config()

    def _update_adaptive_config_from_execution(self, workflow: Dict, execution_data: Dict):
        """基于执行情况更新自适应配置"""
        actual_times = execution_data.get("step_times", {})
        satisfaction = execution_data.get("satisfaction", 3)

        # 更新步骤时间预估
        for step_key, actual_time in actual_times.items():
            if step_key in self.adaptive_config.step_durations:
                current_est = self.adaptive_config.step_durations[step_key]
                # 指数移动平均更新
                new_est = current_est * 0.7 + actual_time * 0.3

                # 根据满意度调整
                if satisfaction >= 4:  # 高满意度
                    new_est *= 0.95  # 稍微减少预估
                elif satisfaction <= 2:  # 低满意度
                    new_est *= 1.05  # 稍微增加预估

                self.adaptive_config.step_durations[step_key] = int(new_est)

    def _record_success_patterns(self, workflow: Dict, execution_data: Dict):
        """记录成功模式"""
        satisfaction = execution_data.get("satisfaction", 3)

        if satisfaction >= 4:  # 高满意度
            # 记录成功的工作流配置
            success_pattern = {
                "project_type": workflow["project_type"],
                "complexity": workflow["complexity"],
                "step_weights": workflow["steps"],
                "quality_focus": workflow["quality_focus"],
                "timestamp": datetime.now().isoformat()
            }

            # 保存成功模式
            success_file = self.config_dir / "success_patterns.json"
            patterns = []
            if success_file.exists():
                try:
                    with open(success_file, 'r', encoding='utf-8') as f:
                        patterns = json.load(f)
                except:
                    patterns = []

            patterns.append(success_pattern)

            # 保持最近20个成功模式
            if len(patterns) > 20:
                patterns = patterns[-20:]

            try:
                with open(success_file, 'w', encoding='utf-8') as f:
                    json.dump(patterns, f, ensure_ascii=False, indent=2)
            except Exception as e:
                print(f"保存成功模式失败: {e}")

    def get_adaptive_recommendations(self, project_type: ProjectType) -> List[str]:
        """获取自适应推荐"""
        recommendations = []

        # 基于历史成功模式
        success_file = self.config_dir / "success_patterns.json"
        if success_file.exists():
            try:
                with open(success_file, 'r', encoding='utf-8') as f:
                    patterns = json.load(f)

                # 找出相似项目的成功模式
                similar_patterns = [
                    p for p in patterns
                    if p["project_type"] == project_type.value
                ]

                if similar_patterns:
                    # 分析最常用的质量关注点
                    quality_focus_counts = {}
                    for pattern in similar_patterns[-5:]:  # 最近5个
                        for focus in pattern.get("quality_focus", []):
                            quality_focus_counts[focus] = quality_focus_counts.get(focus, 0) + 1

                    if quality_focus_counts:
                        most_common_focus = max(quality_focus_counts, key=quality_focus_counts.get)
                        recommendations.append(f"基于历史数据，建议重点关注：{most_common_focus}")

            except Exception as e:
                print(f"读取成功模式失败: {e}")

        # 基于用户偏好的推荐
        if self.engine.profile.quality_standards:
            user_focus = self.engine.profile.quality_standards.get("quality_focus", [])
            if user_focus:
                recommendations.append(f"根据您的偏好，建议重点关注：{', '.join(user_focus)}")

        # 基于项目类型的推荐
        type_recommendations = {
            "web_app": ["用户体验设计", "性能优化", "跨浏览器兼容"],
            "cli_tool": ["错误处理", "参数验证", "帮助文档"],
            "api_service": ["安全性", "并发处理", "API文档"],
            "mobile_app": ["内存管理", "网络优化", "用户体验"],
            "automation": ["异常恢复", "日志记录", "可维护性"]
        }

        if project_type.value in type_recommendations:
            recommendations.extend(type_recommendations[project_type.value])

        return recommendations