"""
模型模块测试 - 展示 Pydantic 模型测试
"""

import pytest
from datetime import datetime, UTC
from pydantic import ValidationError

from src.ai_platform.core.models import (
    AIRequest,
    AIResponse,
    Message,
    Conversation,
    AIModel,
    ModelCapability,
    ModelComplexity,
    ConversationStats,
    SystemMetrics,
)


class TestAIRequest:
    """AI 请求模型测试"""

    def test_valid_ai_request(self) -> None:
        """测试有效的 AI 请求"""
        request = AIRequest(
            prompt="Hello, how are you?",
            model="claude-3-haiku-20240307",
            max_tokens=100,
            temperature=0.7,
            user_id="test-user-123",
        )

        assert request.prompt == "Hello, how are you?"
        assert request.model == "claude-3-haiku-20240307"
        assert request.max_tokens == 100
        assert request.temperature == 0.7
        assert request.user_id == "test-user-123"
        assert request.stream is False

    def test_ai_request_with_system_prompt(self) -> None:
        """测试带系统提示的 AI 请求"""
        request = AIRequest(
            prompt="Generate a story",
            model="claude-3-sonnet-20240229",
            system_prompt="You are a creative writer.",
            user_id="test-user",
        )

        assert request.system_prompt == "You are a creative writer."

    def test_invalid_prompt_length(self) -> None:
        """测试无效的提示长度"""
        with pytest.raises(ValidationError):
            AIRequest(
                prompt="",  # 空提示
                model="claude-3-haiku-20240307",
                user_id="test-user",
            )

        with pytest.raises(ValidationError):
            AIRequest(
                prompt="a" * 50001,  # 超过最大长度
                model="claude-3-haiku-20240307",
                user_id="test-user",
            )

    def test_invalid_temperature_values(self) -> None:
        """测试无效的温度值"""
        with pytest.raises(ValidationError):
            AIRequest(
                prompt="Test",
                model="claude-3-haiku-20240307",
                temperature=-0.1,  # 小于最小值
                user_id="test-user",
            )

        with pytest.raises(ValidationError):
            AIRequest(
                prompt="Test",
                model="claude-3-haiku-20240307",
                temperature=2.1,  # 大于最大值
                user_id="test-user",
            )

    def test_temperature_rounding(self) -> None:
        """测试温度值四舍五入"""
        request = AIRequest(
            prompt="Test",
            model="claude-3-haiku-20240307",
            temperature=0.73456789,
            user_id="test-user",
        )

        # 温度应该被四舍五入
        assert request.temperature == 0.73


class TestMessage:
    """消息模型测试"""

    def test_valid_message(self) -> None:
        """测试有效的消息"""
        message = Message(
            role="user",
            content="Hello, world!",
            user_id="test-user",
        )

        assert message.role == "user"
        assert message.content == "Hello, world!"
        assert message.user_id == "test-user"
        assert isinstance(message.timestamp, datetime)
        assert message.token_count is None
        assert message.model_used is None

    def test_message_with_metadata(self) -> None:
        """测试带元数据的消息"""
        metadata = {"source": "web", "language": "en"}
        message = Message(
            role="assistant",
            content="Hello! How can I help you?",
            user_id="test-user",
            metadata=metadata,
            token_count=15,
            model_used="claude-3-haiku",
        )

        assert message.metadata == metadata
        assert message.token_count == 15
        assert message.model_used == "claude-3-haiku"

    def test_invalid_role(self) -> None:
        """测试无效的角色"""
        with pytest.raises(ValidationError):
            Message(
                role="invalid_role",  # 无效角色
                content="Test",
                user_id="test-user",
            )

    def test_message_helper_methods(self) -> None:
        """测试消息辅助方法"""
        user_message = Message(role="user", content="Hello", user_id="test")
        system_message = Message(role="system", content="System prompt", user_id="test")
        assistant_message = Message(role="assistant", content="Response", user_id="test")

        assert user_message.is_user_message() is True
        assert user_message.is_system_message() is False

        assert system_message.is_system_message() is True
        assert system_message.is_user_message() is False

        assert assistant_message.is_user_message() is False
        assert assistant_message.is_system_message() is False


class TestConversation:
    """对话模型测试"""

    def test_empty_conversation(self) -> None:
        """测试空对话"""
        conversation = Conversation(
            title="Test Conversation",
            user_id="test-user-123",
        )

        assert conversation.title == "Test Conversation"
        assert conversation.user_id == "test-user-123"
        assert conversation.status == "active"
        assert len(conversation.messages) == 0
        assert conversation.total_tokens == 0
        assert conversation.estimated_cost == 0.0
        assert isinstance(conversation.created_at, datetime)
        assert isinstance(conversation.updated_at, datetime)

    def test_conversation_with_messages(self) -> None:
        """测试带消息的对话"""
        messages = [
            Message(role="user", content="Hello", user_id="test"),
            Message(role="assistant", content="Hi there!", user_id="test", token_count=5),
            Message(role="user", content="How are you?", user_id="test", token_count=4),
        ]

        conversation = Conversation(
            title="Test Chat",
            user_id="test",
            messages=messages,
        )

        assert len(conversation.messages) == 3
        assert conversation.total_tokens == 9  # 5 + 4

    def test_add_message(self) -> None:
        """测试添加消息"""
        conversation = Conversation(
            title="Test",
            user_id="test",
        )

        initial_count = len(conversation.messages)
        new_message = Message(
            role="user",
            content="New message",
            user_id="test",
            token_count=3,
        )

        conversation.add_message(new_message)

        assert len(conversation.messages) == initial_count + 1
        assert conversation.total_tokens == 3
        assert conversation.updated_at > conversation.created_at

    def test_conversation_validation_first_message(self) -> None:
        """测试对话验证 - 第一个消息"""
        invalid_messages = [
            Message(role="assistant", content="Hello", user_id="test"),
            Message(role="tool", content="Tool result", user_id="test"),
        ]

        with pytest.raises(ValidationError, match="First message must be from user or system"):
            Conversation(
                title="Invalid",
                user_id="test",
                messages=invalid_messages,
            )

    def test_get_last_message(self) -> None:
        """测试获取最后一条消息"""
        conversation = Conversation(title="Test", user_id="test")

        assert conversation.get_last_message() is None

        message1 = Message(role="user", content="First", user_id="test")
        message2 = Message(role="assistant", content="Second", user_id="test")

        conversation.add_message(message1)
        conversation.add_message(message2)

        assert conversation.get_last_message() == message2

    def test_get_messages_by_role(self) -> None:
        """测试按角色获取消息"""
        messages = [
            Message(role="user", content="Hello", user_id="test"),
            Message(role="assistant", content="Hi", user_id="test"),
            Message(role="user", content="How are you?", user_id="test"),
            Message(role="system", content="System prompt", user_id="test"),
        ]

        conversation = Conversation(title="Test", user_id="test", messages=messages)

        user_messages = conversation.get_messages_by_role("user")
        assistant_messages = conversation.get_messages_by_role("assistant")
        system_messages = conversation.get_messages_by_role("system")

        assert len(user_messages) == 2
        assert len(assistant_messages) == 1
        assert len(system_messages) == 1

        assert all(msg.role == "user" for msg in user_messages)
        assert all(msg.role == "assistant" for msg in assistant_messages)
        assert all(msg.role == "system" for msg in system_messages)


class TestAIModel:
    """AI 模型测试"""

    def test_ai_model_creation(self) -> None:
        """测试 AI 模型创建"""
        capabilities = {ModelCapability.TEXT_GENERATION, ModelCapability.CODE_GENERATION}
        model = AIModel(
            name="claude-3-sonnet",
            provider="anthropic",
            version="20240229",
            capabilities=capabilities,
            complexity=ModelComplexity.ADVANCED,
            max_tokens=200000,
            cost_per_1k_tokens=0.015,
            supports_streaming=True,
            supports_function_calling=False,
        )

        assert model.name == "claude-3-sonnet"
        assert model.provider == "anthropic"
        assert model.version == "20240229"
        assert ModelCapability.TEXT_GENERATION in model.capabilities
        assert model.complexity == ModelComplexity.ADVANCED
        assert model.max_tokens == 200000
        assert model.supports_streaming is True
        assert model.supports_function_calling is False

    def test_get_model_id(self) -> None:
        """测试获取模型 ID"""
        model = AIModel(
            name="gpt-4",
            provider="openai",
            version="0613",
            capabilities={ModelCapability.TEXT_GENERATION},
        )

        model_id = model.get_model_id()
        assert model_id == "openai:gpt-4:0613"

    def test_can_handle_capability(self) -> None:
        """测试能力检查"""
        model = AIModel(
            name="test-model",
            provider="test",
            version="1.0",
            capabilities={
                ModelCapability.TEXT_GENERATION,
                ModelCapability.CODE_GENERATION,
            },
        )

        assert model.can_handle(ModelCapability.TEXT_GENERATION) is True
        assert model.can_handle(ModelCapability.CODE_GENERATION) is True
        assert model.can_handle(ModelCapability.TRANSLATION) is False

    def test_model_immutability(self) -> None:
        """测试模型不可变性"""
        model = AIModel(
            name="test",
            provider="test",
            version="1.0",
            capabilities={ModelCapability.TEXT_GENERATION},
        )

        # 尝试修改不可变模型应该失败
        with pytest.raises(Exception):  # 可能是 AttributeError 或其他异常
            model.name = "new_name"


class TestConversationStats:
    """对话统计测试"""

    def test_default_stats(self) -> None:
        """测试默认统计"""
        stats = ConversationStats()

        assert stats.total_conversations == 0
        assert stats.active_conversations == 0
        assert stats.total_messages == 0
        assert stats.total_tokens == 0
        assert stats.total_cost == 0.0
        assert stats.average_messages_per_conversation == 0.0
        assert stats.most_used_model is None
        assert stats.last_activity is None

    def test_stats_with_data(self) -> None:
        """测试带数据的统计"""
        now = datetime.now(UTC)
        stats = ConversationStats(
            total_conversations=100,
            active_conversations=25,
            total_messages=1500,
            total_tokens=75000,
            total_cost=15.50,
            most_used_model="claude-3-haiku",
            last_activity=now,
        )

        # 检查平均值计算
        expected_avg = 1500 / 100  # total_messages / total_conversations
        assert abs(stats.average_messages_per_conversation - expected_avg) < 0.01

        assert stats.most_used_model == "claude-3-haiku"
        assert stats.last_activity == now


class TestSystemMetrics:
    """系统指标测试"""

    def test_default_metrics(self) -> None:
        """测试默认指标"""
        metrics = SystemMetrics()

        assert metrics.cpu_usage_percent == 0.0
        assert metrics.memory_usage_mb == 0
        assert metrics.active_requests == 0
        assert metrics.requests_per_minute == 0.0
        assert metrics.average_response_time_ms == 0.0
        assert metrics.error_rate_percent == 0.0
        assert metrics.uptime_seconds == 0
        assert isinstance(metrics.timestamp, datetime)

    def test_metrics_with_values(self) -> None:
        """测试带值的指标"""
        now = datetime.now(UTC)
        metrics = SystemMetrics(
            cpu_usage_percent=45.2,
            memory_usage_mb=1024,
            active_requests=5,
            requests_per_minute=120.5,
            average_response_time_ms=850.0,
            error_rate_percent=1.2,
            uptime_seconds=86400,
            timestamp=now,
        )

        assert metrics.cpu_usage_percent == 45.2
        assert metrics.memory_usage_mb == 1024
        assert metrics.active_requests == 5
        assert metrics.requests_per_minute == 120.5
        assert metrics.average_response_time_ms == 850.0
        assert metrics.error_rate_percent == 1.2
        assert metrics.uptime_seconds == 86400
        assert metrics.timestamp == now

    def test_metric_value_bounds(self) -> None:
        """测试指标值边界"""
        with pytest.raises(ValidationError):
            SystemMetrics(cpu_usage_percent=150.0)  # 超出 0-100 范围

        with pytest.raises(ValidationError):
            SystemMetrics(memory_usage_mb=-100)  # 负值

        with pytest.raises(ValidationError):
            SystemMetrics(active_requests=-1)  # 负值

        with pytest.raises(ValidationError):
            SystemMetrics(error_rate_percent=-1.0)  # 负值

        with pytest.raises(ValidationError):
            SystemMetrics(error_rate_percent=150.0)  # 超出 0-100 范围


class TestAIResponse:
    """AI 响应测试"""

    def test_ai_response_creation(self) -> None:
        """测试 AI 响应创建"""
        response = AIResponse(
            content="Hello! How can I help you today?",
            model_used="claude-3-haiku-20240307",
            tokens_used=25,
            finish_reason="stop",
            response_time_ms=1200,
            cost=0.001,
        )

        assert response.content == "Hello! How can I help you today?"
        assert response.model_used == "claude-3-haiku-20240307"
        assert response.tokens_used == 25
        assert response.finish_reason == "stop"
        assert response.response_time_ms == 1200
        assert response.cost == 0.001
        assert response.metadata == {}

    def test_cost_rounding(self) -> None:
        """测试成本四舍五入"""
        response = AIResponse(
            content="Test",
            model_used="test-model",
            tokens_used=10,
            finish_reason="stop",
            response_time_ms=100,
            cost=0.00123456789,  # 应该被四舍五入
        )

        assert response.cost == 0.001235  # 四舍五入到 6 位小数

    def test_response_with_metadata(self) -> None:
        """测试带元数据的响应"""
        metadata = {
            "provider": "anthropic",
            "input_tokens": 10,
            "output_tokens": 15,
        }

        response = AIResponse(
            content="Test response",
            model_used="claude-3-haiku",
            tokens_used=25,
            finish_reason="stop",
            response_time_ms=1000,
            cost=0.002,
            metadata=metadata,
        )

        assert response.metadata == metadata
        assert response.metadata["provider"] == "anthropic"