"""
配置管理模块 - 展示 Python 3.13 的类型系统和模式匹配特性
"""

import os
import secrets
from enum import StrEnum, auto
from pathlib import Path
from typing import Annotated, Any, Literal, Never, Self, TypeAlias

from pydantic import Field, SecretStr, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Python 3.13: 类型别名改进
Environment: TypeAlias = Literal["development", "staging", "production"]
LogLevel: TypeAlias = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]

# Python 3.13: 强类型的 Enum
class AIProvider(StrEnum):
    """支持的 AI 提供商枚举"""
    ANTHROPIC = "anthropic"
    OPENAI = "openai"
    OLLAMA = "ollama"

class CacheBackend(StrEnum):
    """缓存后端枚举"""
    REDIS = "redis"
    MEMORY = "memory"
    DISABLED = "disabled"

class DatabaseType(StrEnum):
    """数据库类型枚举"""
    POSTGRESQL = "postgresql"
    SQLITE = "sqlite"
    MYSQL = "mysql"

# Python 3.13: 使用 @dataclass_transform 的配置类
class Settings(BaseSettings):
    """应用配置类 - 使用 Pydantic Settings 进行类型安全的配置管理"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="forbid",
        validate_assignment=True,
    )

    # 基础应用配置
    app_name: Annotated[str, Field(default="AI Integration Platform", description="应用名称")]
    app_version: Annotated[str, Field(default="0.1.0", description="应用版本")]
    environment: Annotated[Environment, Field(default="development", description="运行环境")]
    debug: Annotated[bool, Field(default=False, description="调试模式")]

    # 服务器配置
    host: Annotated[str, Field(default="127.0.0.1", description="服务器主机")]
    port: Annotated[int, Field(default=8000, ge=1, le=65535, description="服务器端口")]
    workers: Annotated[int, Field(default=1, ge=1, description="工作进程数")]

    # 安全配置
    secret_key: Annotated[SecretStr, Field(default_factory=lambda: SecretStr(secrets.token_urlsafe(32)), description="应用密钥")]
    allowed_hosts: Annotated[list[str], Field(default=["localhost", "127.0.0.1"], description="允许的主机列表")]
    cors_origins: Annotated[list[str], Field(default=["*"], description="CORS 允许的源")]

    # AI 服务配置
    ai_providers: Annotated[list[AIProvider], Field(default=[AIProvider.ANTHROPIC, AIProvider.OPENAI], description="启用的 AI 提供商")]

    # Anthropic 配置
    anthropic_api_key: Annotated[SecretStr | None, Field(default=None, description="Anthropic API 密钥")]
    anthropic_base_url: Annotated[str, Field(default="https://api.anthropic.com", description="Anthropic API 基础 URL")]
    anthropic_timeout: Annotated[int, Field(default=60, ge=1, le=300, description="Anthropic API 超时时间(秒)")]

    # OpenAI 配置
    openai_api_key: Annotated[SecretStr | None, Field(default=None, description="OpenAI API 密钥")]
    openai_base_url: Annotated[str, Field(default="https://api.openai.com/v1", description="OpenAI API 基础 URL")]
    openai_timeout: Annotated[int, Field(default=60, ge=1, le=300, description="OpenAI API 超时时间(秒)")]
    openai_model: Annotated[str, Field(default="gpt-4o-mini", description="默认 OpenAI 模型")]

    # 数据库配置
    database_url: Annotated[SecretStr, Field(default=SecretStr("sqlite+aiosqlite:///./app.db"), description="数据库连接 URL")]
    database_type: Annotated[DatabaseType, Field(default=DatabaseType.SQLITE, description="数据库类型")]
    database_pool_size: Annotated[int, Field(default=10, ge=1, le=100, description="数据库连接池大小")]
    database_max_overflow: Annotated[int, Field(default=20, ge=0, le=100, description="数据库连接池溢出大小")]

    # Redis 配置
    redis_url: Annotated[SecretStr, Field(default=SecretStr("redis://localhost:6379/0"), description="Redis 连接 URL")]
    cache_backend: Annotated[CacheBackend, Field(default=CacheBackend.MEMORY, description="缓存后端")]
    cache_ttl: Annotated[int, Field(default=3600, ge=60, description="缓存过期时间(秒)")]

    # 日志配置
    log_level: Annotated[LogLevel, Field(default="INFO", description="日志级别")]
    log_format: Annotated[Literal["json", "console"], Field(default="console", description="日志格式")]
    log_file: Annotated[Path | None, Field(default=None, description="日志文件路径")]

    # 监控配置
    enable_metrics: Annotated[bool, Field(default=True, description="启用指标收集")]
    metrics_port: Annotated[int, Field(default=9090, ge=1, le=65535, description="指标服务端口")]

    # 速率限制配置
    rate_limit_requests: Annotated[int, Field(default=100, ge=1, description="速率限制请求数")]
    rate_limit_window: Annotated[int, Field(default=3600, ge=60, description="速率限制时间窗口(秒)")]

    # Python 3.13: 字段验证器
    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: Any) -> list[str]:
        """解析 CORS 源列表"""
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",")]
        return value

    @field_validator("ai_providers", mode="before")
    @classmethod
    def parse_ai_providers(cls, value: Any) -> list[AIProvider]:
        """解析 AI 提供商列表"""
        if isinstance(value, str):
            return [AIProvider(provider.strip().lower()) for provider in value.split(",")]
        return value

    # Python 3.13: 模型验证器，支持模式匹配
    @model_validator(mode="after")
    def validate_configuration(self) -> Self:
        """验证配置的完整性和一致性"""
        # 验证 AI 提供商配置
        if AIProvider.ANTHROPIC in self.ai_providers and not self.anthropic_api_key:
            raise ValueError("Anthropic provider requires api_key")

        if AIProvider.OPENAI in self.ai_providers and not self.openai_api_key:
            raise ValueError("OpenAI provider requires api_key")

        # 验证缓存配置
        if self.cache_backend == CacheBackend.REDIS and not self.redis_url:
            raise ValueError("Redis cache backend requires redis_url")

        # Python 3.13: 使用模式匹配验证环境配置
        match self.environment:
            case "production":
                if self.debug:
                    raise ValueError("Debug mode should not be enabled in production")
                if not self.secret_key.get_secret_value() or len(self.secret_key.get_secret_value()) < 32:
                    raise ValueError("Production requires a strong secret key")
            case "staging":
                if self.allowed_hosts == ["*"]:
                    raise ValueError("Staging should not use wildcard hosts")
            case "development":
                # 开发环境允许更宽松的配置
                pass
            case _:
                # Python 3.13: 绝不会到达的类型检查
                raise AssertionError(f"Unknown environment: {self.environment}")

        return self

    def get_ai_provider_config(self, provider: AIProvider) -> dict[str, Any]:
        """获取指定 AI 提供商的配置"""
        match provider:
            case AIProvider.ANTHROPIC:
                return {
                    "api_key": self.anthropic_api_key.get_secret_value() if self.anthropic_api_key else None,
                    "base_url": self.anthropic_base_url,
                    "timeout": self.anthropic_timeout,
                }
            case AIProvider.OPENAI:
                return {
                    "api_key": self.openai_api_key.get_secret_value() if self.openai_api_key else None,
                    "base_url": self.openai_base_url,
                    "timeout": self.openai_timeout,
                    "model": self.openai_model,
                }
            case AIProvider.OLLAMA:
                return {
                    "base_url": "http://localhost:11434",
                    "timeout": 120,
                }
            case _:
                # Python 3.13: 类型 narrowing，确保覆盖所有情况
                raise AssertionError(f"Unsupported AI provider: {provider}")

    def is_production(self) -> bool:
        """检查是否为生产环境"""
        return self.environment == "production"

    def is_development(self) -> bool:
        """检查是否为开发环境"""
        return self.environment == "development"

    def get_database_url(self) -> str:
        """获取数据库连接 URL"""
        return self.database_url.get_secret_value()

    def get_redis_url(self) -> str:
        """获取 Redis 连接 URL"""
        return self.redis_url.get_secret_value()

# Python 3.13: 全局设置实例，使用类型提示
_global_settings: Settings | None = None

def get_settings() -> Settings:
    """获取全局设置实例"""
    global _global_settings
    if _global_settings is None:
        _global_settings = Settings()
    return _global_settings

def set_settings(settings: Settings) -> None:
    """设置全局设置实例（主要用于测试）"""
    global _global_settings
    _global_settings = settings