"""
异常处理模块 - 展示 Python 3.13 的异常处理和错误类型系统
"""

from __future__ import annotations

from typing import Any, Never

# Python 3.13: 自定义异常基类
class AIPlatformError(Exception):
    """AI 平台基础异常类"""

    def __init__(
        self,
        message: str,
        *,
        error_code: str | None = None,
        details: dict[str, Any] | None = None,
        cause: Exception | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.error_code = error_code or self.__class__.__name__
        self.details = details or {}
        self.cause = cause

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(message={self.message!r}, error_code={self.error_code!r})"

    def to_dict(self) -> dict[str, Any]:
        """转换为字典格式"""
        return {
            "error_type": self.__class__.__name__,
            "error_code": self.error_code,
            "message": self.message,
            "details": self.details,
        }

# Python 3.13: 异常层次结构
class ValidationError(AIPlatformError):
    """数据验证错误"""
    def __init__(self, message: str, field: str | None = None, **kwargs: Any) -> None:
        details = kwargs.pop("details", {})
        if field:
            details["field"] = field
        super().__init__(message, details=details, **kwargs)

class ConfigurationError(AIPlatformError):
    """配置错误"""
    pass

class AuthenticationError(AIPlatformError):
    """认证错误"""
    def __init__(self, message: str = "Authentication failed", **kwargs: Any) -> None:
        super().__init__(message, error_code="AUTH_FAILED", **kwargs)

class AuthorizationError(AIPlatformError):
    """授权错误"""
    def __init__(self, message: str = "Access denied", **kwargs: Any) -> None:
        super().__init__(message, error_code="ACCESS_DENIED", **kwargs)

class RateLimitError(AIPlatformError):
    """速率限制错误"""
    def __init__(
        self,
        message: str = "Rate limit exceeded",
        *,
        limit: int | None = None,
        window: int | None = None,
        retry_after: int | None = None,
        **kwargs: Any,
    ) -> None:
        details = kwargs.pop("details", {})
        if limit is not None:
            details["limit"] = limit
        if window is not None:
            details["window"] = window
        if retry_after is not None:
            details["retry_after"] = retry_after
        super().__init__(message, error_code="RATE_LIMITED", details=details, **kwargs)

class AIServiceError(AIPlatformError):
    """AI 服务错误"""
    def __init__(
        self,
        message: str,
        *,
        provider: str | None = None,
        model: str | None = None,
        status_code: int | None = None,
        **kwargs: Any,
    ) -> None:
        details = kwargs.pop("details", {})
        if provider:
            details["provider"] = provider
        if model:
            details["model"] = model
        if status_code is not None:
            details["status_code"] = status_code
        super().__init__(message, details=details, **kwargs)

class AIServiceTimeoutError(AIServiceError):
    """AI 服务超时错误"""
    def __init__(self, message: str = "AI service timeout", **kwargs: Any) -> None:
        super().__init__(message, error_code="AI_TIMEOUT", **kwargs)

class AIServiceUnavailableError(AIServiceError):
    """AI 服务不可用错误"""
    def __init__(self, message: str = "AI service unavailable", **kwargs: Any) -> None:
        super().__init__(message, error_code="AI_UNAVAILABLE", **kwargs)

class DatabaseError(AIPlatformError):
    """数据库错误"""
    def __init__(self, message: str, operation: str | None = None, **kwargs: Any) -> None:
        details = kwargs.pop("details", {})
        if operation:
            details["operation"] = operation
        super().__init__(message, details=details, **kwargs)

class CacheError(AIPlatformError):
    """缓存错误"""
    def __init__(self, message: str, operation: str | None = None, **kwargs: Any) -> None:
        details = kwargs.pop("details", {})
        if operation:
            details["operation"] = operation
        super().__init__(message, details=details, **kwargs)

# Python 3.13: 异常处理工具函数
def handle_ai_error(error: Exception) -> AIPlatformError:
    """将各种异常转换为平台异常"""
    match error:
        case ValidationError():
            return error
        case TimeoutError():
            return AIServiceTimeoutError(str(error), cause=error)
        case ConnectionError():
            return AIServiceUnavailableError(str(error), cause=error)
        case PermissionError():
            return AuthenticationError(str(error), cause=error)
        case ValueError() as e if "rate limit" in str(e).lower():
            return RateLimitError(str(error), cause=error)
        case ValueError() as e if "validation" in str(e).lower():
            return ValidationError(str(error), cause=error)
        case AIPlatformError():
            return error
        case _:
            return AIPlatformError(f"Unexpected error: {str(error)}", cause=error)

# Python 3.13: 异常上下文管理器
class ErrorContext:
    """错误上下文管理器，用于添加上下文信息"""

    def __init__(self, context: dict[str, Any]) -> None:
        self.context = context
        self.original_error: Exception | None = None

    def __enter__(self) -> None:
        return None

    def __exit__(self, exc_type: type[Exception] | None, exc_val: Exception | None, exc_tb: Any) -> bool:
        if exc_val is not None:
            self.original_error = exc_val
            # 添加上下文信息到异常
            if isinstance(exc_val, AIPlatformError):
                exc_val.details.update(self.context)
            else:
                # 转换为平台异常
                platform_error = handle_ai_error(exc_val)
                platform_error.details.update(self.context)
                raise platform_error from exc_val
        return False  # 不抑制异常

# Python 3.13: 异步异常处理工具
async def safe_execute(
    operation,
    *,
    error_handler: callable | None = None,
    context: dict[str, Any] | None = None,
) -> Any:
    """安全执行操作，处理异常"""
    try:
        if context:
            with ErrorContext(context):
                return await operation()
        else:
            return await operation()
    except Exception as e:
        if error_handler:
            return await error_handler(e)
        raise

# Python 3.13: 异常重试机制
class RetryConfig:
    """重试配置"""
    def __init__(
        self,
        max_attempts: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        exponential_base: float = 2.0,
        retryable_errors: tuple[type[Exception], ...] = (
            AIServiceTimeoutError,
            AIServiceUnavailableError,
            ConnectionError,
            TimeoutError,
        ),
    ) -> None:
        self.max_attempts = max_attempts
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.retryable_errors = retryable_errors

async def retry_async(
    operation,
    config: RetryConfig,
    context: dict[str, Any] | None = None,
) -> Any:
    """异步重试操作"""
    import asyncio
    import math

    last_error: Exception | None = None

    for attempt in range(config.max_attempts):
        try:
            if context:
                with ErrorContext({"attempt": attempt + 1, **context}):
                    return await operation()
            else:
                return await operation()
        except Exception as e:
            last_error = e

            # 检查是否为可重试错误
            if not isinstance(e, config.retryable_errors) or attempt == config.max_attempts - 1:
                raise

            # 计算延迟时间
            delay = min(
                config.base_delay * (config.exponential_base ** attempt),
                config.max_delay,
            )
            # 添加随机抖动
            jitter = delay * 0.1 * (0.5 - math.random())  # Python 3.13 可能会有更好的随机数生成
            total_delay = delay + jitter

            await asyncio.sleep(total_delay)

    # Python 3.13: 绝不会到达，但为了类型安全
    assert last_error is not None
    raise last_error