"""
LLM提供商统一接口

支持OpenAI、Anthropic、本地模型等多种LLM提供商的统一接入
"""

import asyncio
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Union, AsyncGenerator
import time
from contextlib import asynccontextmanager

from pydantic import BaseModel, Field, validator


class ModelType(str, Enum):
    """模型类型枚举"""
    TEXT_GENERATION = "text_generation"
    CHAT = "chat"
    CODE_GENERATION = "code_generation"
    REASONING = "reasoning"
    MULTIMODAL = "multimodal"


class MessageRole(str, Enum):
    """消息角色枚举"""
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    FUNCTION = "function"
    TOOL = "tool"


@dataclass
class Message:
    """统一的消息格式"""
    role: MessageRole
    content: str
    name: Optional[str] = None
    function_call: Optional[Dict[str, Any]] = None
    tool_calls: Optional[List[Dict[str, Any]]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        result = {
            "role": self.role.value,
            "content": self.content,
        }
        if self.name:
            result["name"] = self.name
        if self.function_call:
            result["function_call"] = self.function_call
        if self.tool_calls:
            result["tool_calls"] = self.tool_calls
        return result


@dataclass
class ModelResponse:
    """模型响应统一格式"""
    content: str
    finish_reason: Optional[str] = None
    usage: Dict[str, int] = field(default_factory=dict)
    model: str = ""
    created: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)


class LLMConfig(BaseModel):
    """LLM配置类"""
    model_name: str = Field(..., description="模型名称")
    provider: str = Field(..., description="提供商名称")
    api_key: Optional[str] = Field(None, description="API密钥")
    api_base: Optional[str] = Field(None, description="API基础URL")
    max_tokens: Optional[int] = Field(2048, description="最大生成令牌数")
    temperature: float = Field(0.7, description="温度参数", ge=0.0, le=2.0)
    top_p: float = Field(1.0, description="Top-p参数", ge=0.0, le=1.0)
    top_k: Optional[int] = Field(None, description="Top-k参数")
    frequency_penalty: float = Field(0.0, description="频率惩罚", ge=-2.0, le=2.0)
    presence_penalty: float = Field(0.0, description="存在惩罚", ge=-2.0, le=2.0)
    stop: Optional[List[str]] = Field(None, description="停止词")
    stream: bool = Field(False, description="是否流式输出")
    timeout: int = Field(60, description="请求超时时间（秒）")
    retry_attempts: int = Field(3, description="重试次数")
    retry_delay: float = Field(1.0, description="重试延迟（秒）")

    @validator('temperature')
    def validate_temperature(cls, v):
        if not 0.0 <= v <= 2.0:
            raise ValueError('Temperature must be between 0.0 and 2.0')
        return v


class LLMProvider(ABC):
    """LLM提供商抽象基类"""

    def __init__(self, config: LLMConfig):
        self.config = config
        self._client = None
        self._initialized = False

    @abstractmethod
    async def initialize(self) -> None:
        """初始化客户端"""
        pass

    @abstractmethod
    async def generate(
        self,
        messages: List[Message],
        **kwargs
    ) -> ModelResponse:
        """生成响应"""
        pass

    @abstractmethod
    async def generate_stream(
        self,
        messages: List[Message],
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """流式生成响应"""
        pass

    @abstractmethod
    async def count_tokens(self, text: str) -> int:
        """计算令牌数"""
        pass

    @property
    def model_name(self) -> str:
        """获取模型名称"""
        return self.config.model_name

    @property
    def provider_name(self) -> str:
        """获取提供商名称"""
        return self.config.provider

    async def __aenter__(self):
        """异步上下文管理器入口"""
        if not self._initialized:
            await self.initialize()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        await self.cleanup()

    async def cleanup(self) -> None:
        """清理资源"""
        pass


class LLMManager:
    """LLM管理器 - 支持多个提供商和模型"""

    def __init__(self):
        self._providers: Dict[str, LLMProvider] = {}
        self._default_provider: Optional[str] = None

    def register_provider(
        self,
        name: str,
        provider: LLMProvider,
        set_as_default: bool = False
    ) -> None:
        """注册LLM提供商"""
        self._providers[name] = provider
        if set_as_default or not self._default_provider:
            self._default_provider = name

    def get_provider(self, name: Optional[str] = None) -> LLMProvider:
        """获取LLM提供商"""
        provider_name = name or self._default_provider
        if not provider_name:
            raise ValueError("No default provider set and no provider name specified")

        if provider_name not in self._providers:
            raise ValueError(f"Provider '{provider_name}' not found")

        return self._providers[provider_name]

    async def generate(
        self,
        messages: List[Message],
        provider: Optional[str] = None,
        **kwargs
    ) -> ModelResponse:
        """使用指定提供商生成响应"""
        llm_provider = self.get_provider(provider)
        return await llm_provider.generate(messages, **kwargs)

    async def generate_stream(
        self,
        messages: List[Message],
        provider: Optional[str] = None,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """使用指定提供商流式生成响应"""
        llm_provider = self.get_provider(provider)
        async for chunk in llm_provider.generate_stream(messages, **kwargs):
            yield chunk

    @asynccontextmanager
    async def use_provider(self, name: Optional[str] = None):
        """上下文管理器使用特定提供商"""
        provider = self.get_provider(name)
        async with provider as p:
            yield p


# 全局LLM管理器实例
llm_manager = LLMManager()


def get_llm_manager() -> LLMManager:
    """获取全局LLM管理器"""
    return llm_manager


async def register_llm_provider(
    name: str,
    config: LLMConfig,
    set_as_default: bool = False
) -> None:
    """注册LLM提供商的便捷函数"""
    from ..services.llm_factory import LLMFactory

    provider = await LLMFactory.create_provider(config)
    llm_manager.register_provider(name, provider, set_as_default)