"""
AI 服务基类 - 展示 Python 3.13 的抽象基类和协议特性
"""

from abc import ABC, abstractmethod
from datetime import datetime, UTC
from typing import (
    Any,
    AsyncGenerator,
    Awaitable,
    Callable,
    Literal,
    ParamSpec,
    Self,
    TypeAlias,
    TypeVar,
    override,
)

from pydantic import BaseModel, Field
import httpx

from ..core.models import AIRequest, AIResponse
from ..core.config import AIProvider

# Python 3.13: 参数规范改进
P = ParamSpec("P")
T = TypeVar("T")

# Python 3.13: 类型别名
StreamingChunk: TypeAlias = str
ResponseCallback: TypeAlias = Callable[[AIResponse], Awaitable[None]]
ErrorCallback: TypeAlias = Callable[[Exception], Awaitable[None]]

class AIRequestConfig(BaseModel):
    """AI 请求配置"""
    max_tokens: int = Field(default=1000, ge=1, le=32000)
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    stream: bool = Field(default=False)
    timeout: int = Field(default=60, ge=1, le=300)
    include_metadata: bool = Field(default=True)
    response_format: Literal["text", "json"] | None = Field(default=None)

class AIResponse(BaseModel):
    """AI 响应基类"""
    content: str
    model_used: str
    tokens_used: int
    finish_reason: Literal["stop", "length", "tool_calls"]
    response_time_ms: int
    metadata: dict[str, Any] = Field(default_factory=dict)

# Python 3.13: 抽象基类
class BaseAIProvider(ABC):
    """AI 服务提供商标准接口"""

    def __init__(
        self,
        api_key: str,
        base_url: str,
        timeout: int = 60,
        *,
        max_retries: int = 3,
        retry_delay: float = 1.0,
    ) -> None:
        self.api_key = api_key
        self.base_url = base_url
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay

        # 创建 HTTP 客户端
        self.client = httpx.AsyncClient(
            base_url=base_url,
            timeout=timeout,
            headers=self._get_headers(),
        )

    @abstractmethod
    async def initialize(self) -> None:
        """初始化 AI 服务"""
        ...

    @abstractmethod
    async def cleanup(self) -> None:
        """清理资源"""
        ...

    @abstractmethod
    def _get_headers(self) -> dict[str, str]:
        """获取请求头"""
        ...

    @abstractmethod
    async def _make_request(
        self,
        request: AIRequest,
        config: AIRequestConfig,
    ) -> dict[str, Any]:
        """发送 API 请求"""
        ...

    @abstractmethod
    async def _parse_response(
        self,
        response_data: dict[str, Any],
        request: AIRequest,
        start_time: datetime,
    ) -> AIResponse:
        """解析 API 响应"""
        ...

    @abstractmethod
    async def _stream_response(
        self,
        response_data: dict[str, Any],
    ) -> AsyncGenerator[StreamingChunk, None]:
        """流式响应处理"""
        ...

    async def generate_response(
        self,
        request: AIRequest,
        config: AIRequestConfig | None = None,
        *,
        success_callback: ResponseCallback | None = None,
        error_callback: ErrorCallback | None = None,
    ) -> AIResponse:
        """生成 AI 响应"""
        config = config or AIRequestConfig()
        start_time = datetime.now(UTC)

        try:
            # 发送请求
            response_data = await self._make_request(request, config)

            # 解析响应
            response = await self._parse_response(response_data, request, start_time)

            # 调用成功回调
            if success_callback:
                await success_callback(response)

            return response

        except Exception as e:
            # 调用错误回调
            if error_callback:
                await error_callback(e)
            raise

    async def generate_streaming_response(
        self,
        request: AIRequest,
        config: AIRequestConfig | None = None,
        *,
        chunk_callback: Callable[[StreamingChunk], Awaitable[None]] | None = None,
    ) -> AsyncGenerator[StreamingChunk, None]:
        """生成流式 AI 响应"""
        config = config or AIRequestConfig()
        config.stream = True

        try:
            response_data = await self._make_request(request, config)

            async for chunk in self._stream_response(response_data):
                if chunk_callback:
                    await chunk_callback(chunk)
                yield chunk

        except Exception as e:
            raise

    async def __aenter__(self) -> Self:
        """异步上下文管理器入口"""
        await self.initialize()
        return self

    async def __aexit__(self, exc_type: type[Exception] | None, exc_val: Exception | None, exc_tb: Any) -> None:
        """异步上下文管理器出口"""
        await self.cleanup()

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(base_url={self.base_url!r}, timeout={self.timeout})"

# Python 3.13: 协议定义
class SupportsStreaming(ABC):
    """支持流式响应的协议"""

    @abstractmethod
    async def stream_response(
        self,
        request: AIRequest,
        config: AIRequestConfig,
    ) -> AsyncGenerator[StreamingChunk, None]:
        """流式响应方法"""
        ...

class SupportsFunctionCalling(ABC):
    """支持函数调用的协议"""

    @abstractmethod
    async def call_function(
        self,
        function_name: str,
        arguments: dict[str, Any],
        request: AIRequest,
    ) -> Any:
        """函数调用方法"""
        ...

# Python 3.13: 泛型混入类
class RetryableMixin:
    """可重试混入类"""

    async def _retry_request(
        self,
        operation: Callable[P, Awaitable[T]],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> T:
        """重试请求操作"""
        import asyncio

        last_error: Exception | None = None
        max_retries = getattr(self, "max_retries", 3)
        retry_delay = getattr(self, "retry_delay", 1.0)

        for attempt in range(max_retries + 1):
            try:
                return await operation(*args, **kwargs)
            except Exception as e:
                last_error = e

                if attempt == max_retries:
                    break

                # 计算延迟时间
                delay = retry_delay * (2 ** attempt)  # 指数退避
                await asyncio.sleep(delay)

        # Python 3.13: 类型守卫确保 last_error 不为 None
        assert last_error is not None
        raise last_error

# Python 3.13: 工厂函数
def create_ai_provider(
    provider: AIProvider,
    api_key: str,
    base_url: str,
    **kwargs: Any,
) -> BaseAIProvider:
    """创建 AI 服务提供商标例"""
    match provider:
        case AIProvider.ANTHROPIC:
            from .anthropic import AnthropicProvider
            return AnthropicProvider(api_key=api_key, base_url=base_url, **kwargs)
        case AIProvider.OPENAI:
            from .openai import OpenAIProvider
            return OpenAIProvider(api_key=api_key, base_url=base_url, **kwargs)
        case _:
            raise ValueError(f"Unsupported AI provider: {provider}")

# Python 3.13: 实用工具函数
async def benchmark_provider(
    provider: BaseAIProvider,
    test_requests: list[AIRequest],
) -> dict[str, Any]:
    """基准测试 AI 提供商性能"""
    import time

    results = {
        "provider": provider.__class__.__name__,
        "total_requests": len(test_requests),
        "successful_requests": 0,
        "failed_requests": 0,
        "total_time_ms": 0,
        "average_response_time_ms": 0,
        "min_response_time_ms": float("inf"),
        "max_response_time_ms": 0,
        "errors": [],
    }

    for i, request in enumerate(test_requests):
        start_time = time.time()
        try:
            response = await provider.generate_response(request)
            response_time = (time.time() - start_time) * 1000

            results["successful_requests"] += 1
            results["total_time_ms"] += response_time
            results["min_response_time_ms"] = min(results["min_response_time_ms"], response_time)
            results["max_response_time_ms"] = max(results["max_response_time_ms"], response_time)

        except Exception as e:
            results["failed_requests"] += 1
            results["errors"].append({
                "request_index": i,
                "error_type": type(e).__name__,
                "error_message": str(e),
            })

    if results["successful_requests"] > 0:
        results["average_response_time_ms"] = results["total_time_ms"] / results["successful_requests"]

    return results