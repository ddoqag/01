#!/usr/bin/env python3
"""
AgentFlow-ProjectManager 协调器
实现 AgentFlow 总监与 project-manager-v2 的智能协作
"""

import json
import re
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass


@dataclass
class TaskAnalysis:
    """任务分析结果"""

    complexity_score: float  # 0-10 复杂度评分
    is_project_level: bool  # 是否需要项目管理
    required_phases: List[str]  # 必需阶段
    estimated_duration: str  # 预估时长
    team_size_needed: int  # 所需团队规模
    risk_level: str  # 风险等级
    priority: str  # 优先级


class ProjectCoordinator:
    """项目协调器 - 桥接 AgentFlow 和 project-manager-v2"""

    def __init__(self):
        self.delegation_rules = self._load_delegation_rules()
        self.active_projects = {}
        self.task_queue = []

    def _load_delegation_rules(self) -> Dict:
        """加载委托规则"""
        return {
            "project_indicators": [
                "项目",
                "开发",
                "实施",
                "部署",
                "架构",
                "系统",
                "平台",
                "多阶段",
                "全流程",
                "端到端",
                "完整",
                "整个",
            ],
            "complexity_keywords": {
                "high": ["复杂", "企业级", "大规模", "分布式", "高可用", "微服务"],
                "medium": ["集成", "优化", "重构", "升级", "迁移"],
                "low": ["修复", "调整", "配置", "文档", "分析"],
            },
            "duration_mapping": {
                "长期": ">3个月",
                "中期": "1-3个月",
                "短期": "<1个月",
                "快速": "<1周",
            },
        }

    def analyze_task(self, task_description: str) -> TaskAnalysis:
        """分析任务特征，判断是否需要委托给 project-manager-v2"""

        # 1. 复杂度评分
        complexity_score = self._calculate_complexity(task_description)

        # 2. 判断是否为项目级任务
        is_project_level = self._is_project_level_task(task_description)

        # 3. 识别必需阶段
        required_phases = self._identify_phases(task_description)

        # 4. 预估时长
        estimated_duration = self._estimate_duration(task_description, complexity_score)

        # 5. 评估团队规模
        team_size_needed = self._estimate_team_size(task_description, required_phases)

        # 6. 风险评估
        risk_level = self._assess_risk(task_description, complexity_score)

        # 7. 优先级
        priority = self._determine_priority(task_description)

        return TaskAnalysis(
            complexity_score=complexity_score,
            is_project_level=is_project_level,
            required_phases=required_phases,
            estimated_duration=estimated_duration,
            team_size_needed=team_size_needed,
            risk_level=risk_level,
            priority=priority,
        )

    def _calculate_complexity(self, description: str) -> float:
        """计算任务复杂度评分"""
        score = 0.0

        # 关键词权重
        high_keywords = self.delegation_rules["complexity_keywords"]["high"]
        medium_keywords = self.delegation_rules["complexity_keywords"]["medium"]

        for keyword in high_keywords:
            if keyword in description:
                score += 3.0

        for keyword in medium_keywords:
            if keyword in description:
                score += 2.0

        # 项目级标识符
        for indicator in self.delegation_rules["project_indicators"]:
            if indicator in description:
                score += 1.5

        # 系统复杂度指标
        if any(word in description for word in ["分布式", "微服务", "高并发"]):
            score += 2.0

        if any(word in description for word in ["集成", "接口", "API"]):
            score += 1.0

        return min(score, 10.0)

    def _is_project_level_task(self, description: str) -> bool:
        """判断是否为项目级任务"""
        project_indicators = self.delegation_rules["project_indicators"]

        # 包含项目指示词
        if any(indicator in description for indicator in project_indicators):
            return True

        # 多阶段描述
        phase_words = ["阶段", "步骤", "流程", "周期", "迭代", "版本"]
        phase_count = sum(1 for word in phase_words if word in description)
        if phase_count >= 2:
            return True

        # 涉及多个技术栈
        tech_stacks = ["前端", "后端", "数据库", "部署", "测试", "运维"]
        tech_count = sum(1 for tech in tech_stacks if tech in description)
        if tech_count >= 3:
            return True

        return False

    def _identify_phases(self, description: str) -> List[str]:
        """识别项目必需阶段"""
        phase_mapping = {
            "需求": ["需求", "分析", "设计", "规划"],
            "开发": ["开发", "编码", "实现", "构建"],
            "测试": ["测试", "验证", "质量", "QA"],
            "部署": ["部署", "上线", "发布", "运维"],
            "文档": ["文档", "说明", "手册", "培训"],
        }

        identified_phases = []
        for phase, keywords in phase_mapping.items():
            if any(keyword in description for keyword in keywords):
                identified_phases.append(phase)

        # 默认包含基础阶段
        if not identified_phases:
            identified_phases = ["需求", "开发", "测试"]

        return identified_phases

    def _estimate_duration(self, description: str, complexity: float) -> str:
        """预估项目时长"""
        if complexity >= 8.0:
            return "长期"
        elif complexity >= 6.0:
            return "中期"
        elif complexity >= 4.0:
            return "短期"
        else:
            return "快速"

    def _estimate_team_size(self, description: str, phases: List[str]) -> int:
        """估算所需团队规模"""
        base_size = len(phases)

        # 复杂度调整 - 只有复杂任务才需要额外人员
        complexity_words = ["复杂", "企业级", "大规模", "分布式", "微服务"]
        complexity_adjustment = 0
        for word in complexity_words:
            if word in description:
                complexity_adjustment = 2
                break

        # 技术栈调整 - 只有明确提到多种技术才需要更多人
        tech_keywords = ["前端", "后端", "数据库", "移动端", "算法", "安全", "API", "接口"]
        tech_count = sum(1 for tech in tech_keywords if tech in description)
        tech_adjustment = tech_count - 1 if tech_count > 1 else 0

        total_size = base_size + complexity_adjustment + tech_adjustment

        # 简单任务可能只需要1人
        if total_size <= 1 and "修复" in description or "调整" in description:
            return 1

        # 最少1人，最多10人
        return max(1, min(total_size, 10))

    def _assess_risk(self, description: str, complexity: float) -> str:
        """评估风险等级"""
        risk_indicators = {
            "高": ["新技术", "创新", "首次", "探索", "研究"],
            "中": ["集成", "迁移", "升级", "重构"],
            "低": ["优化", "维护", "修复", "改进"],
        }

        for level, keywords in risk_indicators.items():
            if any(keyword in description for keyword in keywords):
                return level

        # 基于复杂度的风险评估
        if complexity >= 8.0:
            return "高"
        elif complexity >= 5.0:
            return "中"
        else:
            return "低"

    def _determine_priority(self, description: str) -> str:
        """确定优先级"""
        urgent_keywords = ["紧急", "立即", "马上", "高优先级", "关键"]
        normal_keywords = ["常规", "普通", "标准"]
        low_keywords = ["低优先级", "后续", "暂缓"]

        if any(keyword in description for keyword in urgent_keywords):
            return "高"
        elif any(keyword in description for keyword in low_keywords):
            return "低"
        else:
            return "中"

    def should_delegate_to_pm(self, analysis: TaskAnalysis) -> Tuple[bool, str]:
        """判断是否应该委托给 project-manager-v2"""

        # 委托条件
        delegation_conditions = [
            (analysis.is_project_level, "项目级任务"),
            (
                analysis.complexity_score >= 6.0,
                f"高复杂度({analysis.complexity_score:.1f}/10)",
            ),
            (analysis.team_size_needed >= 3, f"需要多人协作({analysis.team_size_needed}人)"),
            (
                len(analysis.required_phases) >= 4,
                f"多阶段项目({len(analysis.required_phases)}个阶段)",
            ),
            (analysis.risk_level == "高", "高风险项目"),
        ]

        should_delegate = any(condition for condition, _ in delegation_conditions)
        reasons = [reason for condition, reason in delegation_conditions if condition]

        return should_delegate, "; ".join(reasons) if reasons else "常规任务"

    def create_delegation_request(
        self, task_id: str, analysis: TaskAnalysis, original_request: str
    ) -> Dict:
        """创建委托请求"""

        return {
            "task_id": task_id,
            "delegated_to": "project-manager-v2",
            "delegated_from": "agentflow-director",
            "timestamp": datetime.now().isoformat(),
            "original_request": original_request,
            "analysis": {
                "complexity_score": analysis.complexity_score,
                "required_phases": analysis.required_phases,
                "estimated_duration": analysis.estimated_duration,
                "team_size_needed": analysis.team_size_needed,
                "risk_level": analysis.risk_level,
                "priority": analysis.priority,
            },
            "expectations": ["详细项目计划制定", "团队协调和任务分配", "进度跟踪和风险管理", "质量保证和交付管理"],
            "reporting_schedule": "每周向AgentFlow总监汇报进度",
            "escalation_triggers": ["进度延迟超过2周", "预算超支超过20%", "关键风险事件发生", "团队冲突无法解决"],
        }

    def process_task(self, task_id: str, task_description: str) -> Dict:
        """处理任务，决定是否委托"""

        # 分析任务
        analysis = self.analyze_task(task_description)

        # 决定是否委托
        should_delegate, reasons = self.should_delegate_to_pm(analysis)

        result = {
            "task_id": task_id,
            "analysis": analysis,
            "decision": "delegate" if should_delegate else "handle_internally",
            "reasons": reasons,
            "timestamp": datetime.now().isoformat(),
        }

        if should_delegate:
            # 创建委托请求
            delegation_request = self.create_delegation_request(
                task_id, analysis, task_description
            )
            result["delegation_request"] = delegation_request

            # 记录活跃项目
            self.active_projects[task_id] = {
                "status": "delegated",
                "delegated_to": "project-manager-v2",
                "analysis": analysis,
                "delegation_time": datetime.now().isoformat(),
            }

        return result


# 使用示例
if __name__ == "__main__":
    coordinator = ProjectCoordinator()

    # 测试任务分析
    test_tasks = [
        "开发一个完整的电商系统，包括前端、后端、数据库和部署",
        "修复登录页面的显示问题",
        "构建企业级微服务架构，支持高并发和分布式部署",
        "写一个API文档",
    ]

    for i, task in enumerate(test_tasks):
        task_id = f"task_{i+1}"
        result = coordinator.process_task(task_id, task)

        print(f"\n=== 任务 {task_id} ===")
        print(f"描述: {task}")
        print(f"复杂度: {result['analysis'].complexity_score:.1f}/10")
        print(f"决策: {result['decision']}")
        print(f"原因: {result['reasons']}")

        if result["decision"] == "delegate":
            print(f"✅ 委托给 project-manager-v2")
        else:
            print(f"🔧 AgentFlow 内部处理")
