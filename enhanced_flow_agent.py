#!/usr/bin/env python3
"""
🎯 Enhanced FlowAgent - 增强版AgentFlow四模块主控制器
集成项目管理协调功能，支持与project-manager-v2的智能协作
"""

import time
import json
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import uuid

from agentflow_core.flow_agent import FlowAgent
from agentflow_coordinator import ProjectCoordinator, TaskAnalysis
from communication_protocol import (
    CommunicationProtocol,
    Message,
    MessageType,
    Priority,
    DelegationPayload,
    ProgressReportPayload,
)


class EnhancedFlowAgent(FlowAgent):
    """增强版FlowAgent，集成项目管理协调功能"""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        初始化增强版FlowAgent

        Args:
            config: 配置字典
        """
        super().__init__(config)

        # 初始化协调器
        self.coordinator = ProjectCoordinator()
        self.communication = CommunicationProtocol()

        # 项目管理相关状态
        self.delegated_projects = {}  # 委托给PM的项目
        self.active_coordination = {}  # 活跃的协调任务
        self.project_updates = {}  # 项目更新记录

        # 增强配置
        self.pm_integration_enabled = True
        self.auto_delegation_threshold = 6.0  # 自动委托复杂度阈值
        self.coordination_history = []

        print("🚀 Enhanced FlowAgent 四模块系统已初始化 (集成项目管理)")

    def process_request(self, user_request: str) -> Dict[str, Any]:
        """
        处理用户请求，增强版支持项目管理协调

        Args:
            user_request: 用户请求

        Returns:
            处理结果
        """
        print(f"\n📋 收到用户请求: {user_request[:100]}...")

        # 生成任务ID
        task_id = f"task_{int(time.time())}_{uuid.uuid4().hex[:8]}"

        # 步骤1: 任务分析和委托决策
        should_delegate, analysis = self._analyze_and_decide(task_id, user_request)

        if should_delegate:
            return self._delegate_to_project_manager(task_id, user_request, analysis)
        else:
            return self._process_internally(task_id, user_request, analysis)

    def _analyze_and_decide(
        self, task_id: str, user_request: str
    ) -> tuple[bool, TaskAnalysis]:
        """分析任务并决定是否委托"""

        print("🧠 正在分析任务复杂度和特征...")

        # 使用协调器分析任务
        analysis = self.coordinator.analyze_task(user_request)

        # 决定是否委托
        should_delegate, reasons = self.coordinator.should_delegate_to_pm(analysis)

        print(f"📊 分析结果:")
        print(f"   复杂度评分: {analysis.complexity_score:.1f}/10")
        print(f"   项目级任务: {'是' if analysis.is_project_level else '否'}")
        print(f"   所需阶段: {len(analysis.required_phases)}个")
        print(f"   团队规模: {analysis.team_size_needed}人")
        print(f"   风险等级: {analysis.risk_level}")
        print(
            f"   决策: {'委托给project-manager-v2' if should_delegate else 'AgentFlow内部处理'}"
        )
        print(f"   原因: {reasons}")

        return should_delegate, analysis

    def _delegate_to_project_manager(
        self, task_id: str, user_request: str, analysis: TaskAnalysis
    ) -> Dict[str, Any]:
        """委托任务给project-manager-v2"""

        print(f"🎯 委托任务 {task_id} 给 project-manager-v2")

        # 创建委托载荷
        delegation_payload = DelegationPayload(
            original_request=user_request,
            task_analysis={
                "complexity_score": analysis.complexity_score,
                "is_project_level": analysis.is_project_level,
                "required_phases": analysis.required_phases,
                "estimated_duration": analysis.estimated_duration,
                "team_size_needed": analysis.team_size_needed,
                "risk_level": analysis.risk_level,
                "priority": analysis.priority,
            },
            expectations=[
                "制定详细项目计划，包括里程碑和交付物",
                "协调所需Agent资源和工作分配",
                "监控项目进度，管理风险和变更",
                "确保质量标准和按时交付",
                "定期向AgentFlow总监汇报进展",
            ],
            reporting_schedule="每周汇报关键进展，重大风险即时通报",
            escalation_triggers=[
                "进度延迟超过计划20%",
                "关键技术难题无法解决",
                "资源不足或团队冲突",
                "需求重大变更影响项目范围",
            ],
            deadline=self._estimate_deadline(analysis),
            quality_standards=self._get_quality_standards(analysis),
        )

        # 创建委托消息
        delegation_msg = self.communication.create_delegation_request(
            sender="agentflow-director",
            receiver="project-manager-v2",
            task_id=task_id,
            delegation_data=delegation_payload,
        )

        # 发送委托请求
        self.communication.send_message(delegation_msg)

        # 记录委托项目
        self.delegated_projects[task_id] = {
            "status": "delegated",
            "delegation_time": datetime.now().isoformat(),
            "analysis": analysis,
            "delegation_message": delegation_msg,
            "expected_responses": [],
            "last_update": datetime.now().isoformat(),
        }

        # 创建协调任务
        self._create_coordination_task(task_id, analysis)

        return {
            "task_id": task_id,
            "status": "delegated",
            "action": "委托给project-manager-v2",
            "message": "✅ 任务已委托给专业项目管理Agent",
            "details": {
                "project_manager": "project-manager-v2",
                "complexity": analysis.complexity_score,
                "estimated_duration": analysis.estimated_duration,
                "phases": analysis.required_phases,
                "next_steps": [
                    "project-manager-v2 将制定详细项目计划",
                    "AgentFlow 将提供Agent资源协调支持",
                    "定期接收项目进展报告",
                ],
            },
            "support_info": {
                "coordination": "AgentFlow总监将持续协调支持",
                "reporting": "项目进展将通过协调器同步",
                "escalation": "重大风险将自动升级处理",
            },
        }

    def _process_internally(
        self, task_id: str, user_request: str, analysis: TaskAnalysis
    ) -> Dict[str, Any]:
        """在AgentFlow内部处理任务"""

        print(f"🔧 AgentFlow内部处理任务 {task_id}")

        # 使用原有的四模块处理流程
        try:
            # 调用父类处理方法
            result = super().process_request(user_request)

            # 添加分析信息到结果
            result["task_analysis"] = {
                "complexity_score": analysis.complexity_score,
                "processing_mode": "agentflow_internal",
                "modules_used": ["planner", "executor", "verifier", "generator"],
                "advantages": ["快速响应和处理", "直接调用专业Agent", "实时质量验证", "统一结果生成"],
            }

            return result

        except Exception as e:
            # 如果内部处理失败，考虑降级到项目管理
            if analysis.complexity_score >= 5.0:
                print(f"⚠️ 内部处理遇到困难，降级到项目管理模式: {e}")
                return self._delegate_to_project_manager(
                    task_id, user_request, analysis
                )
            else:
                raise e

    def _create_coordination_task(self, task_id: str, analysis: TaskAnalysis):
        """创建协调任务"""

        coordination_task = {
            "task_id": task_id,
            "coordination_type": "project_management_support",
            "status": "active",
            "created_time": datetime.now().isoformat(),
            "support_areas": ["Agent资源协调和分配", "技术难题专业支持", "质量保证和验证", "跨模块集成协调"],
            "checkpoints": [
                {"phase": "planning", "completed": False},
                {"phase": "execution", "completed": False},
                {"phase": "validation", "completed": False},
                {"phase": "delivery", "completed": False},
            ],
            "next_review": (datetime.now() + timedelta(days=7)).isoformat(),
        }

        self.active_coordination[task_id] = coordination_task

    def handle_progress_report(
        self, task_id: str, progress_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """处理project-manager-v2的进度报告"""

        print(f"📊 接收项目 {task_id} 进度报告")

        if task_id not in self.delegated_projects:
            return {"error": "未知项目ID"}

        # 更新项目状态
        self.delegated_projects[task_id]["last_update"] = datetime.now().isoformat()
        self.delegated_projects[task_id]["latest_progress"] = progress_data

        # 分析进度报告
        analysis = self._analyze_progress_report(progress_data)

        # 检查是否需要协调支持
        coordination_needs = self._assess_coordination_needs(progress_data)

        if coordination_needs:
            return self._provide_coordination_support(task_id, coordination_needs)
        else:
            return {
                "status": "received",
                "message": "✅ 进度报告已收到，项目进展良好",
                "analysis": analysis,
                "next_support_check": self.delegated_projects[task_id].get(
                    "next_review"
                ),
            }

    def _analyze_progress_report(self, progress_data: Dict[str, Any]) -> Dict[str, Any]:
        """分析进度报告"""

        analysis = {"overall_health": "good", "concerns": [], "recommendations": []}

        # 检查完成度
        completion = progress_data.get("completion_percentage", 0)
        if completion < 20:
            analysis["concerns"].append("项目初期进展较慢")
            analysis["recommendations"].append("加强项目启动阶段的资源投入")

        # 检查阻碍因素
        blockers = progress_data.get("blockers", [])
        if blockers:
            analysis["overall_health"] = "attention_needed"
            analysis["concerns"].append(f"存在{len(blockers)}个阻碍因素")
            analysis["recommendations"].append("优先解决阻碍项目进展的关键问题")

        # 检查风险
        risks = progress_data.get("risks", [])
        high_risks = [r for r in risks if r.get("severity") == "high"]
        if high_risks:
            analysis["overall_health"] = "concerning"
            analysis["concerns"].append(f"发现{len(high_risks)}个高风险项")
            analysis["recommendations"].append("立即制定风险缓解计划")

        return analysis

    def _assess_coordination_needs(self, progress_data: Dict[str, Any]) -> List[str]:
        """评估协调支持需求"""

        needs = []

        # 检查是否需要特定Agent支持
        blockers = progress_data.get("blockers", [])
        for blocker in blockers:
            if "技术" in blocker or "开发" in blocker:
                needs.append("技术专家支持")
            elif "测试" in blocker or "质量" in blocker:
                needs.append("测试质量支持")
            elif "部署" in blocker or "运维" in blocker:
                needs.append("DevOps支持")

        # 检查资源利用率
        utilization = progress_data.get("resource_utilization", {})
        for resource, rate in utilization.items():
            if rate > 0.9:
                needs.append(f"{resource}资源优化")

        return needs

    def _provide_coordination_support(
        self, task_id: str, needs: List[str]
    ) -> Dict[str, Any]:
        """提供协调支持"""

        print(f"🤝 为项目 {task_id} 提供协调支持: {needs}")

        # 创建协调支持消息
        coordination_msg = self.communication.create_coordination_request(
            sender="agentflow-director",
            receiver="project-manager-v2",
            task_id=task_id,
            coordination_type="resource_support",
            requirements={
                "support_needs": needs,
                "available_agents": self._get_available_agents(needs),
                "coordination_plan": self._create_coordination_plan(needs),
                "timeline": "立即响应，48小时内提供支持",
            },
        )

        self.communication.send_message(coordination_msg)

        return {
            "status": "coordination_initiated",
            "message": "🤝 已启动协调支持机制",
            "support_provided": needs,
            "available_agents": self._get_available_agents(needs),
            "estimated_response": "2小时内响应，24小时内提供支持",
        }

    def _get_available_agents(self, needs: List[str]) -> List[str]:
        """根据需求获取可用Agent"""

        agent_mapping = {
            "技术专家支持": ["python-pro-v2", "javascript-pro-v2", "java-pro-v2"],
            "测试质量支持": ["test-automation-engineer-v2", "qa-engineer-v2"],
            "DevOps支持": ["devops-troubleshooter-v2", "kubernetes-architect-v2"],
            "数据库支持": ["database-expert-v2", "sql-pro-v2"],
            "架构支持": ["backend-architect-v2", "cloud-architect-v2"],
        }

        available = []
        for need in needs:
            if need in agent_mapping:
                available.extend(agent_mapping[need])

        return list(set(available))  # 去重

    def _create_coordination_plan(self, needs: List[str]) -> Dict[str, Any]:
        """创建协调计划"""

        return {
            "immediate_actions": ["分析具体需求和技术要求", "匹配合适的专业Agent", "建立沟通和协作机制"],
            "coordination_frequency": "每日检查进度",
            "quality_assurance": "由Verifier模块监控质量",
            "escalation_path": "重大问题直接上报AgentFlow总监",
            "success_criteria": ["阻碍因素得到解决", "项目进度恢复正常", "质量标准得到保证"],
        }

    def _estimate_deadline(self, analysis: TaskAnalysis) -> str:
        """估算项目截止时间"""

        duration_mapping = {
            "快速": 7,  # 1周
            "短期": 30,  # 1个月
            "中期": 90,  # 3个月
            "长期": 180,  # 6个月
        }

        days = duration_mapping.get(analysis.estimated_duration, 30)
        deadline = datetime.now() + timedelta(days=days)

        return deadline.isoformat()

    def _get_quality_standards(self, analysis: TaskAnalysis) -> List[str]:
        """获取质量标准"""

        base_standards = ["代码符合行业最佳实践", "功能测试覆盖率达到80%以上", "文档完整且清晰", "性能满足预期指标"]

        if analysis.complexity_score >= 7.0:
            base_standards.extend(["安全性测试通过", "负载测试满足要求", "代码审查100%覆盖"])

        if analysis.risk_level == "高":
            base_standards.extend(["风险缓解措施全部到位", "回滚计划完备", "监控和告警系统完善"])

        return base_standards

    def get_coordination_status(self, task_id: Optional[str] = None) -> Dict[str, Any]:
        """获取协调状态"""

        if task_id:
            # 单个项目状态
            if task_id in self.delegated_projects:
                return {
                    "task_id": task_id,
                    "status": self.delegated_projects[task_id]["status"],
                    "last_update": self.delegated_projects[task_id]["last_update"],
                    "coordination_active": task_id in self.active_coordination,
                }
            else:
                return {"error": "项目不存在"}
        else:
            # 全局状态
            return {
                "total_delegated_projects": len(self.delegated_projects),
                "active_coordination_tasks": len(self.active_coordination),
                "projects": list(self.delegated_projects.keys()),
                "coordination_history_size": len(self.coordination_history),
                "communication_summary": {
                    "messages_sent": len(self.communication.message_history),
                    "pending_acknowledgments": len(
                        self.communication.pending_acknowledgments
                    ),
                },
            }


# 使用示例
if __name__ == "__main__":
    # 创建增强版FlowAgent
    enhanced_agent = EnhancedFlowAgent()

    # 测试不同类型的请求
    test_requests = [
        "修复登录页面的CSS样式问题",
        "开发一个完整的电商平台，包括用户管理、商品展示、购物车、支付和订单管理",
        "优化数据库查询性能",
        "构建企业级微服务架构，支持高并发和分布式部署",
    ]

    for request in test_requests:
        print(f"\n{'='*80}")
        print(f"测试请求: {request}")
        print("=" * 80)

        result = enhanced_agent.process_request(request)
        print(
            f"\n结果: {result['status']} - {result.get('message', result.get('action', ''))}"
        )

    # 显示协调状态
    print(f"\n{'='*80}")
    print("协调状态总览")
    print("=" * 80)
    status = enhanced_agent.get_coordination_status()
    print(f"委托项目数: {status['total_delegated_projects']}")
    print(f"活跃协调任务: {status['active_coordination_tasks']}")
