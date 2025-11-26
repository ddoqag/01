"""
数据模型模块 - 展示 Python 3.13 的 Pydantic 集成和高级类型特性
"""

import asyncio
from datetime import UTC, datetime
from enum import IntEnum, StrEnum, auto
from typing import (
    Any,
    Annotated,
    AsyncGenerator,
    Literal,
    Never,
    Self,
    TypeAlias,
    TypeGuard,
    TypeVar,
    final,
)

import pydantic
from pydantic import (
    BaseModel,
    Field,
    field_validator,
    model_validator,
    ConfigDict,
    EmailStr,
    HttpUrl,
    SecretStr,
    WrapSerializer,
    AwareDatetime,
)
from pydantic_core import PydanticCustomError

# Python 3.13: 类型变量和泛型改进
T = TypeVar("T", bound=BaseModel)
MessageRole: TypeAlias = Literal["user", "assistant", "system", "tool"]
ConversationStatus: TypeAlias = Literal["active", "archived", "deleted"]

# Python 3.13: 强类型枚举
class ModelCapability(StrEnum):
    """AI 模型能力枚举"""
    TEXT_GENERATION = "text_generation"
    CODE_GENERATION = "code_generation"
    ANALYSIS = "analysis"
    TRANSLATION = "translation"
    SUMMARIZATION = "summarization"

class ModelComplexity(IntEnum):
    """模型复杂度枚举"""
    MINIMAL = 1
    BASIC = 2
    STANDARD = 3
    ADVANCED = 4
    EXPERT = 5

# Python 3.13: 使用 Protocol 和 TypeGuard
def is_valid_message_role(role: str) -> TypeGuard[MessageRole]:
    """类型守卫：验证消息角色"""
    return role in {"user", "assistant", "system", "tool"}

# Python 3.13: Final 类和不可变数据结构
@final
class AIModel(BaseModel):
    """AI 模型信息模型 - 不可变配置"""
    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        str_strip_whitespace=True,
    )

    name: Annotated[str, Field(..., min_length=1, max_length=100, description="模型名称")]
    provider: Annotated[str, Field(..., min_length=1, max_length=50, description="提供商")]
    version: Annotated[str, Field(..., min_length=1, max_length=20, description="模型版本")]
    capabilities: Annotated[set[ModelCapability], Field(default_factory=set, description="模型能力")]
    complexity: Annotated[ModelComplexity, Field(default=ModelComplexity.STANDARD, description="模型复杂度")]
    max_tokens: Annotated[int, Field(default=4096, ge=1, le=32000, description="最大令牌数")]
    cost_per_1k_tokens: Annotated[float, Field(default=0.001, ge=0, description="每千令牌成本")]
    supports_streaming: Annotated[bool, Field(default=False, description="支持流式输出")]
    supports_function_calling: Annotated[bool, Field(default=False, description="支持函数调用")]

    def get_model_id(self) -> str:
        """获取唯一模型 ID"""
        return f"{self.provider}:{self.name}:{self.version}"

    def can_handle(self, capability: ModelCapability) -> bool:
        """检查模型是否支持特定能力"""
        return capability in self.capabilities

class Message(BaseModel):
    """消息模型 - 使用 Python 3.13 的类型特性"""

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        use_enum_values=True,
    )

    id: Annotated[str, Field(default_factory=lambda: f"msg_{datetime.now(UTC).timestamp()}", description="消息 ID")]
    role: Annotated[MessageRole, Field(..., description="消息角色")]
    content: Annotated[str, Field(..., min_length=1, max_length=100000, description="消息内容")]
    timestamp: Annotated[AwareDatetime, Field(default_factory=lambda: datetime.now(UTC), description="创建时间")]
    metadata: Annotated[dict[str, Any], Field(default_factory=dict, description="元数据")]
    token_count: Annotated[int | None, Field(default=None, ge=0, description="令牌计数")]
    model_used: Annotated[str | None, Field(default=None, description="使用的模型")]

    # Python 3.13: 字段验证器
    @field_validator("role", mode="before")
    @classmethod
    def validate_role(cls, value: Any) -> MessageRole:
        """验证消息角色"""
        if isinstance(value, str) and is_valid_message_role(value):
            return value
        raise PydanticCustomError(
            "invalid_role",
            "Invalid message role: {value}. Must be one of: {expected}",
            {"value": value, "expected": ["user", "assistant", "system", "tool"]},
        )

    def is_system_message(self) -> bool:
        """检查是否为系统消息"""
        return self.role == "system"

    def is_user_message(self) -> bool:
        """检查是否为用户消息"""
        return self.role == "user"

class Conversation(BaseModel):
    """对话模型 - 展示复杂关系和验证逻辑"""

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        arbitrary_types_allowed=True,
    )

    id: Annotated[str, Field(default_factory=lambda: f"conv_{datetime.now(UTC).timestamp()}", description="对话 ID")]
    title: Annotated[str, Field(..., min_length=1, max_length=200, description="对话标题")]
    user_id: Annotated[str, Field(..., min_length=1, max_length=100, description="用户 ID")]
    status: Annotated[ConversationStatus, Field(default="active", description="对话状态")]
    messages: Annotated[list[Message], Field(default_factory=list, description="消息列表")]
    created_at: Annotated[AwareDatetime, Field(default_factory=lambda: datetime.now(UTC), description="创建时间")]
    updated_at: Annotated[AwareDatetime, Field(default_factory=lambda: datetime.now(UTC), description="更新时间")]
    metadata: Annotated[dict[str, Any], Field(default_factory=dict, description="元数据")]
    total_tokens: Annotated[int, Field(default=0, ge=0, description="总令牌数")]
    estimated_cost: Annotated[float, Field(default=0.0, ge=0, description="估算成本")]

    # Python 3.13: 模型验证器，支持复杂验证逻辑
    @model_validator(mode="after")
    def validate_conversation(self) -> Self:
        """验证对话的完整性"""
        # 确保第一个消息是用户或系统消息
        if self.messages and not (self.messages[0].is_user_message() or self.messages[0].is_system_message()):
            raise ValueError("First message must be from user or system")

        # 计算总令牌数和成本
        total_tokens = sum(msg.token_count or 0 for msg in self.messages)
        if total_tokens != self.total_tokens:
            self.total_tokens = total_tokens

        # 更新时间戳
        if self.messages:
            self.updated_at = max(msg.timestamp for msg in self.messages)

        return self

    def add_message(self, message: Message) -> None:
        """添加消息到对话"""
        self.messages.append(message)
        self.updated_at = datetime.now(UTC)

        # 更新令牌统计
        if message.token_count:
            self.total_tokens += message.token_count

    def get_last_message(self) -> Message | None:
        """获取最后一条消息"""
        return self.messages[-1] if self.messages else None

    def get_messages_by_role(self, role: MessageRole) -> list[Message]:
        """根据角色获取消息"""
        return [msg for msg in self.messages if msg.role == role]

class AIRequest(BaseModel):
    """AI 请求模型 - 展示高级类型和验证"""

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
    )

    prompt: Annotated[str, Field(..., min_length=1, max_length=50000, description="提示词")]
    conversation_id: Annotated[str | None, Field(default=None, description="对话 ID")]
    model: Annotated[str, Field(default="claude-3-haiku-20240307", description="使用的模型")]
    max_tokens: Annotated[int, Field(default=1000, ge=1, le=32000, description="最大生成令牌数")]
    temperature: Annotated[float, Field(default=0.7, ge=0.0, le=2.0, description="温度参数")]
    stream: Annotated[bool, Field(default=False, description="是否流式输出")]
    system_prompt: Annotated[str | None, Field(default=None, max_length=10000, description="系统提示词")]
    functions: Annotated[list[dict[str, Any]], Field(default_factory=list, description="可用函数列表")]
    metadata: Annotated[dict[str, Any], Field(default_factory=dict, description="请求元数据")]
    user_id: Annotated[str, Field(..., min_length=1, max_length=100, description="用户 ID")]

    @field_validator("temperature")
    @classmethod
    def validate_temperature(cls, value: float) -> float:
        """验证温度参数"""
        if not 0.0 <= value <= 2.0:
            raise ValueError("Temperature must be between 0.0 and 2.0")
        return round(value, 2)

class AIResponse(BaseModel):
    """AI 响应模型 - 展示序列化和流式处理"""

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
    )

    request_id: Annotated[str, Field(..., description="请求 ID")]
    content: Annotated[str, Field(..., min_length=1, max_length=100000, description="响应内容")]
    model_used: Annotated[str, Field(..., description="使用的模型")]
    tokens_used: Annotated[int, Field(..., ge=0, description="使用的令牌数")]
    finish_reason: Annotated[Literal["stop", "length", "tool_calls"], Field(default="stop", description="结束原因")]
    response_time_ms: Annotated[int, Field(..., ge=0, description="响应时间(毫秒)")]
    cost: Annotated[float, Field(..., ge=0, description="成本")]
    metadata: Annotated[dict[str, Any], Field(default_factory=dict, description="响应元数据")]

    # Python 3.13: 自定义序列化器
    @field_validator("cost", mode="before")
    @classmethod
    def round_cost(cls, value: float) -> float:
        """对成本进行四舍五入"""
        return round(value, 6)

class ConversationStats(BaseModel):
    """对话统计模型 - 展示聚合数据类型"""

    total_conversations: Annotated[int, Field(default=0, ge=0, description="总对话数")]
    active_conversations: Annotated[int, Field(default=0, ge=0, description="活跃对话数")]
    total_messages: Annotated[int, Field(default=0, ge=0, description="总消息数")]
    total_tokens: Annotated[int, Field(default=0, ge=0, description="总令牌数")]
    total_cost: Annotated[float, Field(default=0.0, ge=0, description="总成本")]
    average_messages_per_conversation: Annotated[float, Field(default=0.0, ge=0, description="平均每对话消息数")]
    most_used_model: Annotated[str | None, Field(default=None, description="最常用模型")]
    last_activity: Annotated[AwareDatetime | None, Field(default=None, description="最后活动时间")]

class SystemMetrics(BaseModel):
    """系统指标模型 - 展示性能监控数据"""

    cpu_usage_percent: Annotated[float, Field(default=0.0, ge=0.0, le=100.0, description="CPU 使用率")]
    memory_usage_mb: Annotated[int, Field(default=0, ge=0, description="内存使用量(MB)")]
    active_requests: Annotated[int, Field(default=0, ge=0, description="活跃请求数")]
    requests_per_minute: Annotated[float, Field(default=0.0, ge=0.0, description="每分钟请求数")]
    average_response_time_ms: Annotated[float, Field(default=0.0, ge=0.0, description="平均响应时间")]
    error_rate_percent: Annotated[float, Field(default=0.0, ge=0.0, le=100.0, description="错误率")]
    uptime_seconds: Annotated[int, Field(default=0, ge=0, description="运行时间(秒)")]
    timestamp: Annotated[AwareDatetime, Field(default_factory=lambda: datetime.now(UTC), description="指标时间戳")]

# Python 3.13: 异步生成器类型
async def stream_response(response: AIResponse) -> AsyncGenerator[str, None]:
    """流式生成响应内容"""
    words = response.content.split()
    for i, word in enumerate(words):
        yield word + (" " if i < len(words) - 1 else "")
        await asyncio.sleep(0.01)  # 模拟网络延迟

# Python 3.13: 工具函数
def create_error_response(error: Exception, request_id: str) -> AIResponse:
    """创建错误响应"""
    return AIResponse(
        request_id=request_id,
        content=f"Error: {str(error)}",
        model_used="error",
        tokens_used=0,
        finish_reason="stop",
        response_time_ms=0,
        cost=0.0,
        metadata={"error_type": type(error).__name__},
    )