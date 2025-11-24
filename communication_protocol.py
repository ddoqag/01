#!/usr/bin/env python3
"""
AgentFlow 与 project-manager-v2 通信协议
定义标准化的消息格式和交互流程
"""

import json
from enum import Enum
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Dict, List, Optional, Any
import uuid


class MessageType(Enum):
    """消息类型枚举"""

    DELEGATION_REQUEST = "delegation_request"
    DELEGATION_ACCEPTED = "delegation_accepted"
    PROGRESS_REPORT = "progress_report"
    RISK_ALERT = "risk_alert"
    RESOURCE_REQUEST = "resource_request"
    ESCALATION = "escalation"
    PROJECT_COMPLETION = "project_completion"
    STATUS_QUERY = "status_query"
    COORDINATION_REQUEST = "coordination_request"


class Priority(Enum):
    """优先级枚举"""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class Message:
    """标准消息格式"""

    message_id: str
    message_type: MessageType
    sender: str
    receiver: str
    timestamp: str
    priority: Priority
    task_id: Optional[str] = None
    payload: Optional[Dict[str, Any]] = None
    correlation_id: Optional[str] = None  # 用于关联相关消息
    requires_ack: bool = True


@dataclass
class DelegationPayload:
    """委托请求载荷"""

    original_request: str
    task_analysis: Dict[str, Any]
    expectations: List[str]
    reporting_schedule: str
    escalation_triggers: List[str]
    deadline: Optional[str] = None
    budget_constraints: Optional[Dict[str, Any]] = None
    quality_standards: Optional[List[str]] = None


@dataclass
class ProgressReportPayload:
    """进度报告载荷"""

    project_phase: str
    completion_percentage: float
    milestones_achieved: List[str]
    upcoming_milestones: List[str]
    blockers: List[str]
    risks: List[Dict[str, Any]]
    resource_utilization: Dict[str, float]
    team_performance: Dict[str, str]
    next_steps: List[str]


@dataclass
class RiskAlertPayload:
    """风险警报载荷"""

    risk_type: str
    severity: str
    description: str
    impact_assessment: str
    mitigation_required: bool
    timeline_impact: str
    resources_needed: List[str]


class CommunicationProtocol:
    """通信协议处理器"""

    def __init__(self):
        self.message_history = []
        self.pending_acknowledgments = {}

    def create_delegation_request(
        self,
        sender: str,
        receiver: str,
        task_id: str,
        delegation_data: DelegationPayload,
    ) -> Message:
        """创建委托请求消息"""

        return Message(
            message_id=str(uuid.uuid4()),
            message_type=MessageType.DELEGATION_REQUEST,
            sender=sender,
            receiver=receiver,
            timestamp=datetime.now().isoformat(),
            priority=Priority.HIGH,
            task_id=task_id,
            payload=asdict(delegation_data),
            requires_ack=True,
        )

    def create_progress_report(
        self,
        sender: str,
        receiver: str,
        task_id: str,
        progress_data: ProgressReportPayload,
    ) -> Message:
        """创建进度报告消息"""

        return Message(
            message_id=str(uuid.uuid4()),
            message_type=MessageType.PROGRESS_REPORT,
            sender=sender,
            receiver=receiver,
            timestamp=datetime.now().isoformat(),
            priority=Priority.MEDIUM,
            task_id=task_id,
            payload=asdict(progress_data),
            correlation_id=f"progress_{task_id}",
            requires_ack=False,
        )

    def create_risk_alert(
        self, sender: str, receiver: str, task_id: str, risk_data: RiskAlertPayload
    ) -> Message:
        """创建风险警报消息"""

        return Message(
            message_id=str(uuid.uuid4()),
            message_type=MessageType.RISK_ALERT,
            sender=sender,
            receiver=receiver,
            timestamp=datetime.now().isoformat(),
            priority=Priority.CRITICAL,
            task_id=task_id,
            payload=asdict(risk_data),
            correlation_id=f"risk_{task_id}",
            requires_ack=True,
        )

    def create_escalation_message(
        self,
        sender: str,
        receiver: str,
        task_id: str,
        escalation_reason: str,
        escalation_details: Dict[str, Any],
    ) -> Message:
        """创建升级消息"""

        return Message(
            message_id=str(uuid.uuid4()),
            message_type=MessageType.ESCALATION,
            sender=sender,
            receiver=receiver,
            timestamp=datetime.now().isoformat(),
            priority=Priority.CRITICAL,
            task_id=task_id,
            payload={
                "escalation_reason": escalation_reason,
                "escalation_details": escalation_details,
                "immediate_action_required": True,
            },
            correlation_id=f"escalation_{task_id}",
            requires_ack=True,
        )

    def create_coordination_request(
        self,
        sender: str,
        receiver: str,
        task_id: str,
        coordination_type: str,
        requirements: Dict[str, Any],
    ) -> Message:
        """创建协调请求消息"""

        return Message(
            message_id=str(uuid.uuid4()),
            message_type=MessageType.COORDINATION_REQUEST,
            sender=sender,
            receiver=receiver,
            timestamp=datetime.now().isoformat(),
            priority=Priority.HIGH,
            task_id=task_id,
            payload={
                "coordination_type": coordination_type,
                "requirements": requirements,
                "requested_action": "coordinate",
            },
            correlation_id=f"coordination_{task_id}",
            requires_ack=True,
        )

    def serialize_message(self, message: Message) -> str:
        """序列化消息为JSON字符串"""

        # 转换枚举为字符串
        message_dict = asdict(message)
        message_dict["message_type"] = message.message_type.value
        message_dict["priority"] = message.priority.value

        return json.dumps(message_dict, ensure_ascii=False, indent=2)

    def deserialize_message(self, message_json: str) -> Message:
        """从JSON字符串反序列化消息"""

        message_dict = json.loads(message_json)

        # 转换字符串为枚举
        message_dict["message_type"] = MessageType(message_dict["message_type"])
        message_dict["priority"] = Priority(message_dict["priority"])

        return Message(**message_dict)

    def send_message(self, message: Message) -> bool:
        """发送消息（模拟）"""

        # 记录消息历史
        self.message_history.append(message)

        # 如果需要确认，记录待确认消息
        if message.requires_ack:
            self.pending_acknowledgments[message.message_id] = message

        # 模拟发送成功
        print(
            f"📤 消息已发送: {message.message_type.value} from {message.sender} to {message.receiver}"
        )
        if message.task_id:
            print(f"   任务ID: {message.task_id}")

        return True

    def receive_message(self, message_json: str) -> Optional[Message]:
        """接收消息（模拟）"""

        try:
            message = self.deserialize_message(message_json)

            # 记录消息历史
            self.message_history.append(message)

            # 处理确认
            if (
                message.correlation_id
                and message.correlation_id in self.pending_acknowledgments
            ):
                del self.pending_acknowledgments[message.correlation_id]

            print(
                f"📥 消息已接收: {message.message_type.value} from {message.sender} to {message.receiver}"
            )
            if message.task_id:
                print(f"   任务ID: {message.task_id}")

            return message

        except Exception as e:
            print(f"❌ 消息解析失败: {e}")
            return None

    def get_message_history(self, task_id: Optional[str] = None) -> List[Message]:
        """获取消息历史"""

        if task_id:
            return [msg for msg in self.message_history if msg.task_id == task_id]
        return self.message_history.copy()

    def get_pending_messages(self, receiver: str) -> List[Message]:
        """获取待处理消息"""

        return [
            msg
            for msg in self.pending_acknowledgments.values()
            if msg.receiver == receiver
        ]


# 预定义消息模板
class MessageTemplates:
    """消息模板库"""

    @staticmethod
    def delegation_request_template():
        """委托请求模板"""
        return {
            "greeting": "🎯 AgentFlow总监任务委托",
            "context": "经过任务分析，现将以下项目委托给您管理",
            "expectations": [
                "制定详细项目计划和里程碑",
                "协调团队资源和任务分配",
                "监控项目进度和质量",
                "管理风险和变更",
                "定期汇报项目状态",
            ],
            "support": "AgentFlow将提供必要的Agent资源协调和技术支持",
            "reporting": "请按约定频率汇报项目进展",
            "closing": "期待您的专业项目管理，确保项目成功交付",
        }

    @staticmethod
    def progress_report_template():
        """进度报告模板"""
        return {
            "header": "📊 项目进度报告",
            "sections": ["当前阶段和完成度", "已达成里程碑", "下一步计划", "存在的阻碍和风险", "资源使用情况"],
            "format": "请使用结构化格式，包含具体数据和量化指标",
        }

    @staticmethod
    def escalation_template():
        """升级请求模板"""
        return {
            "urgency": "🚨 项目升级请求",
            "content": ["升级原因和背景", "已采取的措施", "需要的支持", "影响评估", "建议解决方案"],
            "response_required": "请立即评估并提供支持",
        }


# 使用示例
if __name__ == "__main__":
    protocol = CommunicationProtocol()

    # 创建委托请求
    delegation_payload = DelegationPayload(
        original_request="开发企业级电商平台",
        task_analysis={
            "complexity": 8.5,
            "duration": "3个月",
            "team_size": 6,
            "phases": ["需求", "设计", "开发", "测试", "部署"],
        },
        expectations=["制定项目计划", "团队协调", "风险管理"],
        reporting_schedule="每周汇报",
        escalation_triggers=["进度延迟", "质量问题", "资源不足"],
    )

    delegation_msg = protocol.create_delegation_request(
        sender="agentflow-director",
        receiver="project-manager-v2",
        task_id="project_001",
        delegation_data=delegation_payload,
    )

    # 发送消息
    protocol.send_message(delegation_msg)

    # 创建进度报告
    progress_payload = ProgressReportPayload(
        project_phase="开发阶段",
        completion_percentage=45.0,
        milestones_achieved=["需求分析完成", "架构设计完成"],
        upcoming_milestones=["核心功能开发", "集成测试"],
        blockers=["第三方API延迟"],
        risks=[{"type": "技术风险", "description": "新技术学习曲线"}],
        resource_utilization={"开发人员": 0.8, "测试人员": 0.6},
        team_performance={"效率": "良好", "协作": "顺畅"},
        next_steps=["完成用户管理模块", "开始支付集成"],
    )

    progress_msg = protocol.create_progress_report(
        sender="project-manager-v2",
        receiver="agentflow-director",
        task_id="project_001",
        progress_data=progress_payload,
    )

    protocol.send_message(progress_msg)

    print(f"\n📋 消息历史总数: {len(protocol.message_history)}")
    print(f"⏳ 待确认消息: {len(protocol.pending_acknowledgments)}")
