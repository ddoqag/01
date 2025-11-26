"""
Anthropic 提供商测试 - 展示 AI 服务集成测试
"""

import pytest
from unittest.mock import AsyncMock, MagicMock

from src.ai_platform.ai.anthropic import AnthropicProvider
from src.ai_platform.core.models import AIRequest, AIResponse
from src.ai_platform.core.exceptions import AIServiceError, AIServiceTimeoutError


class TestAnthropicProvider:
    """Anthropic 提供商测试"""

    @pytest.fixture
    def provider(self) -> AnthropicProvider:
        """创建 Anthropic 提供商实例"""
        return AnthropicProvider(
            api_key="test-anthropic-key",
            base_url="https://api.anthropic.com",
            timeout=60,
        )

    @pytest_asyncio.fixture
    async def initialized_provider(self, provider: AnthropicProvider) -> AnthropicProvider:
        """初始化的提供商实例"""
        provider.client = MagicMock()
        provider.client.get = AsyncMock(return_value=MagicMock(status_code=200))
        await provider.initialize()
        return provider

    @pytest.mark.asyncio
    async def test_initialization_success(self, provider: AnthropicProvider) -> None:
        """测试成功初始化"""
        # 模拟成功响应
        provider.client = MagicMock()
        provider.client.get = AsyncMock(return_value=MagicMock(status_code=200))

        await provider.initialize()

        assert provider.client is not None

    @pytest.mark.asyncio
    async def test_initialization_failure(self, provider: AnthropicProvider) -> None:
        """测试初始化失败"""
        provider.client = MagicMock()
        provider.client.get = AsyncMock(side_effect=Exception("Connection failed"))

        with pytest.raises(AIServiceError):
            await provider.initialize()

    @pytest.mark.asyncio
    async def test_build_payload(self, initialized_provider: AnthropicProvider) -> None:
        """测试构建请求负载"""
        from ..ai.base import AIRequestConfig

        request = AIRequest(
            prompt="Hello, world!",
            model="claude-3-haiku-20240307",
            max_tokens=100,
            temperature=0.7,
            system_prompt="You are helpful",
            user_id="test-user",
        )
        config = AIRequestConfig(
            max_tokens=100,
            temperature=0.7,
            stream=False,
        )

        payload = initialized_provider._build_payload(request, config)

        assert payload["model"] == "claude-3-haiku-20240307"
        assert payload["max_tokens"] == 100
        assert payload["temperature"] == 0.7
        assert payload["stream"] is False
        assert payload["system"] == "You are helpful"
        assert "messages" in payload
        assert len(payload["messages"]) == 1
        assert payload["messages"][0]["role"] == "user"
        assert payload["messages"][0]["content"] == "Hello, world!"

    @pytest.mark.asyncio
    async def test_parse_response(self, initialized_provider: AnthropicProvider) -> None:
        """测试解析响应"""
        from datetime import datetime, UTC

        response_data = {
            "id": "msg_123",
            "type": "message",
            "role": "assistant",
            "content": [{"type": "text", "text": "Hello! How can I help you?"}],
            "model": "claude-3-haiku-20240307",
            "stop_reason": "end_turn",
            "usage": {
                "input_tokens": 10,
                "output_tokens": 15,
            },
        }

        request = AIRequest(
            prompt="Hello",
            model="claude-3-haiku-20240307",
            user_id="test-user",
        )
        start_time = datetime.now(UTC)

        response = await initialized_provider._parse_response(response_data, request, start_time)

        assert response.content == "Hello! How can I help you?"
        assert response.model_used == "claude-3-haiku-20240307"
        assert response.tokens_used == 25  # 10 + 15
        assert response.finish_reason == "stop"

    @pytest.mark.asyncio
    async def test_parse_response_with_function_call(self, initialized_provider: AnthropicProvider) -> None:
        """测试解析带函数调用的响应"""
        response_data = {
            "id": "msg_123",
            "type": "message",
            "role": "assistant",
            "content": [
                {"type": "text", "text": "I'll help you with that."},
                {
                    "type": "tool_use",
                    "id": "tool_123",
                    "name": "calculate",
                    "input": {"expression": "2+2"}
                }
            ],
            "model": "claude-3-haiku-20240307",
            "stop_reason": "tool_use",
            "usage": {
                "input_tokens": 10,
                "output_tokens": 25,
            },
        }

        request = AIRequest(
            prompt="Calculate 2+2",
            model="claude-3-haiku-20240307",
            user_id="test-user",
        )
        start_time = datetime.now(UTC)

        response = await initialized_provider._parse_response(response_data, request, start_time)

        assert response.finish_reason == "tool_calls"

    @pytest.mark.asyncio
    async def test_parse_response_error(self, initialized_provider: AnthropicProvider) -> None:
        """测试解析响应错误"""
        invalid_response_data = {
            "invalid": "response",
            "missing": "required_fields",
        }

        request = AIRequest(
            prompt="Hello",
            model="claude-3-haiku-20240307",
            user_id="test-user",
        )
        start_time = datetime.now(UTC)

        with pytest.raises(AIServiceError):
            await initialized_provider._parse_response(invalid_response_data, request, start_time)

    @pytest.mark.asyncio
    async def test_generate_response(self, initialized_provider: AnthropicProvider) -> None:
        """测试生成响应"""
        # 模拟 API 响应
        mock_response_data = {
            "id": "msg_123",
            "type": "message",
            "role": "assistant",
            "content": [{"type": "text", "text": "Hello! How can I help you?"}],
            "model": "claude-3-haiku-20240307",
            "stop_reason": "end_turn",
            "usage": {"input_tokens": 10, "output_tokens": 15},
        }

        initialized_provider.client.post = AsyncMock(
            return_value=MagicMock(
                status_code=200,
                json=lambda: mock_response_data
            )
        )

        request = AIRequest(
            prompt="Hello",
            model="claude-3-haiku-20240307",
            user_id="test-user",
        )

        response = await initialized_provider.generate_response(request)

        assert response.content == "Hello! How can I help you?"
        assert response.model_used == "claude-3-haiku-20240307"
        assert response.tokens_used == 25

        # 验证 API 调用
        initialized_provider.client.post.assert_called_once()
        call_args = initialized_provider.client.post.call_args
        assert call_args[0][0] == "/v1/messages"  # 端点
        assert "json" in call_args[1]  # 请求数据

    @pytest.mark.asyncio
    async def test_generate_response_api_error(self, initialized_provider: AnthropicProvider) -> None:
        """测试生成响应 API 错误"""
        # 模拟 API 错误
        initialized_provider.client.post = AsyncMock(
            return_value=MagicMock(
                status_code=400,
                json=lambda: {
                    "error": {
                        "type": "invalid_request_error",
                        "message": "Invalid request"
                    }
                }
            )
        )

        request = AIRequest(
            prompt="Hello",
            model="claude-3-haiku-20240307",
            user_id="test-user",
        )

        with pytest.raises(AIServiceError):
            await initialized_provider.generate_response(request)

    @pytest.mark.asyncio
    async def test_stream_response(self, initialized_provider: AnthropicProvider) -> None:
        """测试流式响应"""
        response_data = {
            "content": [{"type": "text", "text": "Hello"}]
        }

        chunks = []
        async for chunk in initialized_provider._stream_response(response_data):
            chunks.append(chunk)

        assert len(chunks) == 1
        assert chunks[0] == "Hello"

    @pytest.mark.asyncio
    async def test_map_stop_reason(self, initialized_provider: AnthropicProvider) -> None:
        """测试映射停止原因"""
        test_cases = [
            ("end_turn", "stop"),
            ("max_tokens", "length"),
            ("tool_use", "tool_calls"),
            ("stop_sequence", "stop"),
        ]

        for anthropic_reason, expected_reason in test_cases:
            result = initialized_provider._map_stop_reason(anthropic_reason)
            assert result == expected_reason

    @pytest.mark.asyncio
    async def test_get_available_models(self, initialized_provider: AnthropicProvider) -> None:
        """测试获取可用模型"""
        models = await initialized_provider.get_available_models()

        assert isinstance(models, list)
        assert len(models) > 0

        for model in models:
            assert "id" in model
            assert "name" in model
            assert "description" in model
            assert "max_tokens" in model
            assert "capabilities" in model

        # 检查是否包含预期的模型
        model_ids = [model["id"] for model in models]
        assert "claude-3-5-sonnet-20241022" in model_ids
        assert "claude-3-5-haiku-20241022" in model_ids

    @pytest.mark.asyncio
    async def test_count_tokens(self, initialized_provider: AnthropicProvider) -> None:
        """测试令牌计数"""
        text = "Hello, how are you today? I hope you're doing well."
        token_count = await initialized_provider.count_tokens(text)

        # 令牌计数应该是一个正整数
        assert isinstance(token_count, int)
        assert token_count > 0

    @pytest.mark.asyncio
    async def test_validate_model(self, initialized_provider: AnthropicProvider) -> None:
        """测试模型验证"""
        # 有效模型
        assert await initialized_provider.validate_model("claude-3-haiku-20240307") is True

        # 无效模型
        assert await initialized_provider.validate_model("invalid-model") is False

    def test_supports_streaming(self, initialized_provider: AnthropicProvider) -> None:
        """测试流式支持"""
        assert initialized_provider.supports_streaming() is True

    def test_supports_function_calling(self, initialized_provider: AnthropicProvider) -> None:
        """测试函数调用支持"""
        assert initialized_provider.supports_function_calling() is False

    @pytest.mark.asyncio
    async def test_cleanup(self, initialized_provider: AnthropicProvider) -> None:
        """测试清理资源"""
        initialized_provider.client.aclose = AsyncMock()

        await initialized_provider.cleanup()

        initialized_provider.client.aclose.assert_called_once()
        assert len(initialized_provider._models_cache) == 0

    @pytest.mark.asyncio
    async def test_context_manager(self) -> None:
        """测试上下文管理器"""
        provider = AnthropicProvider(
            api_key="test-key",
            base_url="https://api.anthropic.com",
        )

        # 模拟客户端
        provider.client = MagicMock()
        provider.client.get = AsyncMock(return_value=MagicMock(status_code=200))
        provider.client.aclose = AsyncMock()

        async with provider as p:
            assert p is provider
            # 初始化应该被调用
            provider.client.get.assert_called()

        # 清理应该被调用
        provider.client.aclose.assert_called_once()

    @pytest.mark.asyncio
    async def test_timeout_error_handling(self, initialized_provider: AnthropicProvider) -> None:
        """测试超时错误处理"""
        import httpx

        initialized_provider.client.post = AsyncMock(
            side_effect=httpx.TimeoutException("Request timeout")
        )

        request = AIRequest(
            prompt="Hello",
            model="claude-3-haiku-20240307",
            user_id="test-user",
        )

        with pytest.raises(Exception):  # 可能被包装成其他异常类型
            await initialized_provider.generate_response(request)

    @pytest.mark.asyncio
    async def test_authentication_error(self, initialized_provider: AnthropicProvider) -> None:
        """测试认证错误"""
        initialized_provider.client.post = AsyncMock(
            return_value=MagicMock(
                status_code=401,
                json=lambda: {
                    "error": {
                        "type": "authentication_error",
                        "message": "Invalid API key"
                    }
                }
            )
        )

        request = AIRequest(
            prompt="Hello",
            model="claude-3-haiku-20240307",
            user_id="test-user",
        )

        with pytest.raises(AIServiceError) as exc_info:
            await initialized_provider.generate_response(request)

        assert "Authentication failed" in str(exc_info.value)