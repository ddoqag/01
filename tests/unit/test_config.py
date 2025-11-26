"""
配置模块测试 - 展示 Python 3.13 测试最佳实践
"""

import pytest
from pydantic import ValidationError

from src.ai_platform.core.config import Settings, AIProvider, CacheBackend, DatabaseType


class TestSettings:
    """设置类测试"""

    def test_default_settings(self, test_settings: Settings) -> None:
        """测试默认设置"""
        assert test_settings.app_name == "AI Platform Test"
        assert test_settings.environment == "testing"
        assert test_settings.debug is True
        assert test_settings.host == "127.0.0.1"
        assert test_settings.port == 8000

    def test_ai_provider_validation(self, test_settings: Settings) -> None:
        """测试 AI 提供商验证"""
        assert AIProvider.ANTHROPIC in test_settings.ai_providers
        assert AIProvider.OPENAI in test_settings.ai_providers

    def test_missing_api_key_validation(self) -> None:
        """测试缺失 API 密钥的验证"""
        with pytest.raises(ValidationError, match="Anthropic provider requires api_key"):
            Settings(
                anthropic_api_key=None,
                ai_providers=[AIProvider.ANTHROPIC],
            )

    def test_production_environment_validation(self) -> None:
        """测试生产环境验证"""
        with pytest.raises(ValidationError, match="Debug mode should not be enabled in production"):
            Settings(
                environment="production",
                debug=True,
                anthropic_api_key="test-key",
            )

    @pytest.mark.parametrize("provider", [AIProvider.ANTHROPIC, AIProvider.OPENAI])
    def test_get_ai_provider_config(self, test_settings: Settings, provider: AIProvider) -> None:
        """测试获取 AI 提供商配置"""
        config = test_settings.get_ai_provider_config(provider)

        assert "api_key" in config
        assert "base_url" in config
        assert "timeout" in config

        if provider == AIProvider.OPENAI:
            assert "model" in config

    def test_cache_backend_validation(self) -> None:
        """测试缓存后端验证"""
        with pytest.raises(ValidationError, match="Redis cache backend requires redis_url"):
            Settings(
                cache_backend=CacheBackend.REDIS,
                redis_url=None,
            )

    def test_environment_helpers(self, test_settings: Settings) -> None:
        """测试环境辅助方法"""
        assert test_settings.is_development() is False
        assert test_settings.is_production() is False

        production_settings = Settings(
            environment="production",
            anthropic_api_key="test-key",
        )
        assert production_settings.is_production() is True
        assert production_settings.is_development() is False

    def test_cors_origins_parsing(self) -> None:
        """测试 CORS 源解析"""
        settings = Settings(
            cors_origins="http://localhost:3000,https://example.com",
            anthropic_api_key="test-key",
        )

        assert "http://localhost:3000" in settings.cors_origins
        assert "https://example.com" in settings.cors_origins

    def test_ai_providers_parsing(self) -> None:
        """测试 AI 提供商解析"""
        settings = Settings(
            ai_providers="anthropic,openai",
            anthropic_api_key="test-key",
            openai_api_key="test-key",
        )

        assert AIProvider.ANTHROPIC in settings.ai_providers
        assert AIProvider.OPENAI in settings.ai_providers

    def test_secret_key_generation(self) -> None:
        """测试密钥生成"""
        settings1 = Settings(anthropic_api_key="test-key")
        settings2 = Settings(openai_api_key="test-key")

        # 密钥应该不同
        assert settings1.secret_key.get_secret_value() != settings2.secret_key.get_secret_value()

        # 密钥长度应该合理
        assert len(settings1.secret_key.get_secret_value()) >= 32

    def test_database_type_validation(self, test_settings: Settings) -> None:
        """测试数据库类型验证"""
        assert isinstance(test_settings.database_type, DatabaseType)
        assert test_settings.database_type == DatabaseType.SQLITE

    def test_url_methods(self, test_settings: Settings) -> None:
        """测试 URL 方法"""
        database_url = test_settings.get_database_url()
        redis_url = test_settings.get_redis_url()

        assert isinstance(database_url, str)
        assert isinstance(redis_url, str)

    @pytest.mark.parametrize("environment", ["development", "staging", "production"])
    def test_environment_pattern_matching(self, environment: str) -> None:
        """测试环境模式匹配"""
        settings = Settings(
            environment=environment,
            anthropic_api_key="test-key",
        )

        # 确保环境设置正确
        assert settings.environment == environment

        # 生产环境的特殊验证
        if environment == "production":
            assert not settings.debug
            assert len(settings.secret_key.get_secret_value()) >= 32

    def test_invalid_temperature_range(self) -> None:
        """测试无效温度范围"""
        with pytest.raises(ValidationError):
            Settings(
                anthropic_api_key="test-key",
                openai_temperature=3.0,  # 超出范围
            )

    def test_port_range_validation(self) -> None:
        """测试端口范围验证"""
        with pytest.raises(ValidationError):
            Settings(
                anthropic_api_key="test-key",
                port=70000,  # 超出范围
            )

    def test_model_validation_with_extra_fields(self) -> None:
        """测试额外字段验证"""
        with pytest.raises(ValidationError):
            Settings(
                anthropic_api_key="test-key",
                invalid_field="should_not_exist",
                extra="forbid",
            )