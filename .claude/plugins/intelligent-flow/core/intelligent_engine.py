#!/usr/bin/env python3
"""
智能3-6-3工作流引擎
学习式AI驱动的项目开发流程核心引擎
"""

import json
import os
import time
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path
from dataclasses import dataclass, asdict
from enum import Enum


class WorkflowStage(Enum):
    """工作流阶段枚举"""
    REQUIREMENT = "requirement"
    IMPLEMENTATION = "implementation"
    TESTING = "testing"
    COMPLETED = "completed"


class ProjectType(Enum):
    """项目类型枚举"""
    WEB_APP = "web_app"
    CLI_TOOL = "cli_tool"
    API_SERVICE = "api_service"
    MOBILE_APP = "mobile_app"
    AUTOMATION = "automation"
    UNKNOWN = "unknown"


@dataclass
class DeveloperProfile:
    """开发者学习档案"""
    # 项目偏好
    project_preferences: Dict[str, Dict] = None
    # 工作模式
    work_patterns: Dict[str, Any] = None
    # 学习优化
    learned_optimizations: Dict[str, str] = None
    # 技术栈偏好
    technology_preferences: Dict[str, List[str]] = None
    # 质量标准
    quality_standards: Dict[str, Any] = None

    def __post_init__(self):
        if self.project_preferences is None:
            self.project_preferences = {}
        if self.work_patterns is None:
            self.work_patterns = {}
        if self.learned_optimizations is None:
            self.learned_optimizations = {}
        if self.technology_preferences is None:
            self.technology_preferences = {}
        if self.quality_standards is None:
            self.quality_standards = {}


@dataclass
class ProjectContext:
    """项目上下文"""
    project_type: ProjectType
    description: str
    complexity: str
    estimated_time: int
    tech_stack: List[str]
    current_stage: WorkflowStage
    start_time: datetime
    last_activity: datetime
    issues_found: List[str] = None
    user_preferences: Dict[str, Any] = None

    def __post_init__(self):
        if self.issues_found is None:
            self.issues_found = []
        if self.user_preferences is None:
            self.user_preferences = {}


class IntelligentEngine:
    """智能工作流引擎"""

    def __init__(self, plugin_root: str):
        self.plugin_root = Path(plugin_root)
        self.data_dir = self.plugin_root / "data"
        self.data_dir.mkdir(exist_ok=True)

        # 数据文件路径
        self.profile_file = self.data_dir / "developer_profile.json"
        self.projects_file = self.data_dir / "projects.json"
        self.patterns_file = self.data_dir / "patterns.json"

        # 初始化数据
        self.profile = self._load_profile()
        self.projects = self._load_projects()
        self.patterns = self._load_patterns()

        # 当前项目上下文
        self.current_context: Optional[ProjectContext] = None

    def _load_profile(self) -> DeveloperProfile:
        """加载开发者档案"""
        if self.profile_file.exists():
            try:
                with open(self.profile_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                return DeveloperProfile(**data)
            except Exception as e:
                print(f"加载档案失败: {e}")

        return DeveloperProfile()

    def _save_profile(self):
        """保存开发者档案"""
        try:
            with open(self.profile_file, 'w', encoding='utf-8') as f:
                json.dump(asdict(self.profile), f, ensure_ascii=False, indent=2, default=str)
        except Exception as e:
            print(f"保存档案失败: {e}")

    def _load_projects(self) -> List[Dict]:
        """加载项目历史"""
        if self.projects_file.exists():
            try:
                with open(self.projects_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"加载项目历史失败: {e}")

        return []

    def _save_projects(self):
        """保存项目历史"""
        try:
            with open(self.projects_file, 'w', encoding='utf-8') as f:
                json.dump(self.projects, f, ensure_ascii=False, indent=2, default=str)
        except Exception as e:
            print(f"保存项目历史失败: {e}")

    def _load_patterns(self) -> Dict:
        """加载模式数据"""
        if self.patterns_file.exists():
            try:
                with open(self.patterns_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"加载模式数据失败: {e}")

        return {
            "project_type_patterns": {},
            "technology_patterns": {},
            "time_patterns": {},
            "quality_patterns": {}
        }

    def _save_patterns(self):
        """保存模式数据"""
        try:
            with open(self.patterns_file, 'w', encoding='utf-8') as f:
                json.dump(self.patterns, f, ensure_ascii=False, indent=2, default=str)
        except Exception as e:
            print(f"保存模式数据失败: {e}")

    def detect_project_type(self, description: str) -> ProjectType:
        """智能检测项目类型"""
        description_lower = description.lower()

        # 关键词匹配
        type_keywords = {
            ProjectType.WEB_APP: ["网站", "web", "前端", "页面", "界面", "ui", "网页"],
            ProjectType.CLI_TOOL: ["命令行", "cli", "工具", "脚本", "终端", "命令"],
            ProjectType.API_SERVICE: ["api", "接口", "服务", "后端", "服务器", "接口"],
            ProjectType.MOBILE_APP: ["app", "应用", "移动", "手机", "android", "ios"],
            ProjectType.AUTOMATION: ["自动化", "批量", "定时", "流程", "工作流"]
        }

        scores = {}
        for project_type, keywords in type_keywords.items():
            score = sum(1 for keyword in keywords if keyword in description_lower)
            scores[project_type] = score

        # 返回得分最高的类型
        if max(scores.values()) == 0:
            return ProjectType.UNKNOWN

        return max(scores, key=scores.get)

    def estimate_complexity(self, description: str, project_type: ProjectType) -> str:
        """评估项目复杂度"""
        description_lower = description.lower()

        # 复杂度关键词
        complexity_keywords = {
            "simple": ["简单", "基础", "单一", "小型", "基础版", "原型"],
            "medium": ["中等", "标准", "完整", "功能", "系统"],
            "complex": ["复杂", "高级", "企业级", "大规模", "完整系统", "综合"]
        }

        for complexity, keywords in complexity_keywords.items():
            if any(keyword in description_lower for keyword in keywords):
                return complexity

        # 基于项目类型的默认复杂度
        default_complexity = {
            ProjectType.WEB_APP: "medium",
            ProjectType.CLI_TOOL: "simple",
            ProjectType.API_SERVICE: "medium",
            ProjectType.MOBILE_APP: "complex",
            ProjectType.AUTOMATION: "medium"
        }

        return default_complexity.get(project_type, "medium")

    def recommend_tech_stack(self, project_type: ProjectType, description: str) -> List[str]:
        """推荐技术栈"""
        # 基于历史偏好推荐
        type_key = project_type.value
        if type_key in self.profile.technology_preferences:
            historical_stack = self.profile.technology_preferences[type_key]
            if historical_stack:
                return historical_stack[:3]  # 返回前3个最常用的

        # 基于项目类型的默认推荐
        default_recommendations = {
            ProjectType.WEB_APP: ["React", "Node.js", "TypeScript"],
            ProjectType.CLI_TOOL: ["Node.js", "Commander.js", "JavaScript"],
            ProjectType.API_SERVICE: ["Python", "FastAPI", "PostgreSQL"],
            ProjectType.MOBILE_APP: ["React Native", "TypeScript", "Redux"],
            ProjectType.AUTOMATION: ["Python", "Selenium", "Jinja2"]
        }

        return default_recommendations.get(project_type, ["JavaScript", "Node.js"])

    def estimate_time(self, project_type: ProjectType, complexity: str) -> int:
        """估算开发时间（分钟）"""
        # 基于历史数据的估算
        type_key = project_type.value
        if type_key in self.profile.project_preferences:
            avg_time = self.profile.project_preferences[type_key].get("avg_time")
            if avg_time:
                return int(avg_time)

        # 基于复杂度的默认估算
        base_times = {
            "simple": 60,
            "medium": 120,
            "complex": 240
        }

        project_multipliers = {
            ProjectType.WEB_APP: 1.2,
            ProjectType.CLI_TOOL: 0.8,
            ProjectType.API_SERVICE: 1.0,
            ProjectType.MOBILE_APP: 1.5,
            ProjectType.AUTOMATION: 1.1
        }

        base_time = base_times.get(complexity, 120)
        multiplier = project_multipliers.get(project_type, 1.0)

        return int(base_time * multiplier)

    def predict_potential_issues(self, project_type: ProjectType, description: str) -> List[str]:
        """预测潜在问题"""
        issues = []

        # 基于历史问题预测
        type_key = project_type.value
        if type_key in self.profile.work_patterns:
            common_issues = self.profile.work_patterns.get("common_pain_points", [])
            issues.extend(common_issues[:2])  # 返回前2个最常见的问题

        # 基于项目类型的通用问题
        common_issues_by_type = {
            ProjectType.WEB_APP: ["状态管理复杂度", "性能优化时机", "浏览器兼容性"],
            ProjectType.CLI_TOOL: ["错误处理不完整", "参数验证缺失", "跨平台兼容"],
            ProjectType.API_SERVICE: ["并发处理", "数据一致性", "安全性问题"],
            ProjectType.MOBILE_APP: ["内存泄漏", "网络优化", "用户体验"],
            ProjectType.AUTOMATION: ["异常处理", "错误恢复", "日志记录"]
        }

        type_issues = common_issues_by_type.get(project_type, [])
        issues.extend(type_issues[:2])  # 添加2个类型相关问题

        return list(set(issues))  # 去重

    def start_project(self, description: str) -> ProjectContext:
        """启动新项目"""
        # 智能分析
        project_type = self.detect_project_type(description)
        complexity = self.estimate_complexity(description, project_type)
        tech_stack = self.recommend_tech_stack(project_type, description)
        estimated_time = self.estimate_time(project_type, complexity)
        potential_issues = self.predict_potential_issues(project_type, description)

        # 创建项目上下文
        context = ProjectContext(
            project_type=project_type,
            description=description,
            complexity=complexity,
            estimated_time=estimated_time,
            tech_stack=tech_stack,
            current_stage=WorkflowStage.REQUIREMENT,
            start_time=datetime.now(),
            last_activity=datetime.now(),
            issues_found=potential_issues
        )

        self.current_context = context

        # 记录项目启动
        self._record_project_start(context)

        return context

    def _record_project_start(self, context: ProjectContext):
        """记录项目启动"""
        project_record = {
            "id": hashlib.md5(f"{context.description}{context.start_time}".encode()).hexdigest()[:8],
            "description": context.description,
            "project_type": context.project_type.value,
            "complexity": context.complexity,
            "tech_stack": context.tech_stack,
            "start_time": context.start_time.isoformat(),
            "estimated_time": context.estimated_time,
            "predicted_issues": context.issues_found
        }

        self.projects.append(project_record)
        self._save_projects()

    def update_learning_data(self, context: ProjectContext, stage: WorkflowStage, feedback: Dict):
        """更新学习数据"""
        # 更新项目偏好
        type_key = context.project_type.value
        if type_key not in self.profile.project_preferences:
            self.profile.project_preferences[type_key] = {
                "frequency": 0,
                "avg_time": 0,
                "tech_stack": []
            }

        # 更新频率
        self.profile.project_preferences[type_key]["frequency"] += 1

        # 更新技术栈偏好
        current_tech = self.profile.project_preferences[type_key]["tech_stack"]
        for tech in context.tech_stack:
            if tech not in current_tech:
                current_tech.append(tech)

        # 更新平均时间（如果项目完成）
        if stage == WorkflowStage.COMPLETED:
            actual_time = (context.last_activity - context.start_time).total_seconds() / 60
            avg_time = self.profile.project_preferences[type_key]["avg_time"]
            if avg_time == 0:
                self.profile.project_preferences[type_key]["avg_time"] = actual_time
            else:
                # 指数移动平均
                self.profile.project_preferences[type_key]["avg_time"] = (
                    avg_time * 0.7 + actual_time * 0.3
                )

        # 更新工作模式
        if "satisfaction" in feedback:
            if "satisfaction_scores" not in self.profile.work_patterns:
                self.profile.work_patterns["satisfaction_scores"] = []

            self.profile.work_patterns["satisfaction_scores"].append({
                "timestamp": datetime.now().isoformat(),
                "project_type": type_key,
                "score": feedback["satisfaction"],
                "complexity": context.complexity
            })

        # 保存更新
        self._save_profile()

    def get_personalized_recommendations(self, context: ProjectContext) -> List[str]:
        """获取个性化推荐"""
        recommendations = []

        # 基于历史经验的推荐
        type_key = context.project_type.value
        if type_key in self.profile.learned_optimizations:
            optimizations = self.profile.learned_optimizations
            if "requirement_phase_duration" in optimizations:
                recommendations.append(f"建议{optimizations['requirement_phase_duration']}需求分析阶段")

            if "testing_approaches" in optimizations:
                recommendations.append(f"推荐使用{optimizations['testing_approaches']}")

        # 基于质量标准的推荐
        if self.profile.quality_standards:
            quality_focus = self.profile.quality_standards.get("quality_focus", [])
            if quality_focus:
                recommendations.append(f"重点关注：{', '.join(quality_focus)}")

        # 基于当前项目状态的推荐
        if context.issues_found:
            recommendations.append(f"提前关注可能的问题：{', '.join(context.issues_found[:2])}")

        return recommendations

    def get_workflow_status(self) -> Dict:
        """获取工作流状态"""
        if not self.current_context:
            return {"status": "no_active_project"}

        elapsed_time = (datetime.now() - self.current_context.start_time).total_seconds() / 60
        progress = self._calculate_progress()

        return {
            "status": "active",
            "project_type": self.current_context.project_type.value,
            "current_stage": self.current_context.current_stage.value,
            "elapsed_time": elapsed_time,
            "estimated_time": self.current_context.estimated_time,
            "progress": progress,
            "issues_found": len(self.current_context.issues_found)
        }

    def _calculate_progress(self) -> float:
        """计算项目进度"""
        if not self.current_context:
            return 0.0

        stage_weights = {
            WorkflowStage.REQUIREMENT: 0.25,
            WorkflowStage.IMPLEMENTATION: 0.5,
            WorkflowStage.TESTING: 0.25,
            WorkflowStage.COMPLETED: 1.0
        }

        return stage_weights.get(self.current_context.current_stage, 0.0)