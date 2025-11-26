"""
Anthropic Claude 集成 - 展示现代化 API 集成模式
"""

import json
from datetime import datetime, UTC
from typing import Any, AsyncGenerator

import httpx

from .base import BaseAIProvider, AIRequestConfig, StreamingChunk
from ..core.models import AIRequest, AIResponse
from ..core.exceptions import AIServiceError, AIServiceTimeoutError

class AnthropicProvider(BaseAIProvider):
    """Anthropic Claude AI 服务提供商"""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._models_cache: dict[str, dict[str, Any]] = {}

    def _get_headers(self) -> dict[str, str]:
        """获取 Anthropic API 请求头"""
        return {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        }

    async def initialize(self) -> None:
        """初始化 Anthropic 服务"""
        try:
            # 验证 API 密钥
            response = await self.client.get("/v1/messages", timeout=10)
            if response.status_code != 200:
                raise AIServiceError(
                    "Failed to initialize Anthropic service",
                    provider="anthropic",
                    status_code=response.status_code,
                )
        except httpx.TimeoutException:
            raise AIServiceTimeoutError("Anthropic service initialization timeout")
        except httpx.HTTPStatusError as e:
            raise AIServiceError(
                f"Anthropic API error: {e.response.text}",
                provider="anthropic",
                status_code=e.response.status_code,
            )

    async def cleanup(self) -> None:
        """清理 Anthropic 资源"""
        await self.client.aclose()
        self._models_cache.clear()

    async def _make_request(
        self,
        request: AIRequest,
        config: AIRequestConfig,
    ) -> dict[str, Any]:
        """发送 Anthropic API 请求"""
        # 构建请求负载
        payload = self._build_payload(request, config)

        # 发送请求
        response = await self.client.post(
            "/v1/messages",
            json=payload,
            timeout=config.timeout,
        )

        # 处理响应
        if response.status_code != 200:
            await self._handle_api_error(response)

        return response.json()

    def _build_payload(self, request: AIRequest, config: AIRequestConfig) -> dict[str, Any]:
        """构建 API 请求负载"""
        # 构建消息列表
        messages = [{"role": "user", "content": request.prompt}]

        payload = {
            "model": request.model,
            "max_tokens": config.max_tokens,
            "temperature": config.temperature,
            "messages": messages,
            "stream": config.stream,
        }

        # 添加系统提示
        if request.system_prompt:
            payload["system"] = request.system_prompt

        # 添加响应格式
        if config.response_format == "json":
            # Anthropic 不直接支持 JSON 响应格式，在系统提示中指定
            if "system" in payload:
                payload["system"] += "\n\nRespond in JSON format."
            else:
                payload["system"] = "Respond in JSON format."

        return payload

    async def _parse_response(
        self,
        response_data: dict[str, Any],
        request: AIRequest,
        start_time: datetime,
    ) -> AIResponse:
        """解析 Anthropic API 响应"""
        try:
            # 计算响应时间
            response_time_ms = int((datetime.now(UTC) - start_time).total_seconds() * 1000)

            # 提取响应内容
            content = response_data["content"][0]["text"]

            # 获取令牌使用情况
            usage = response_data.get("usage", {})
            tokens_used = usage.get("input_tokens", 0) + usage.get("output_tokens", 0)

            # 确定结束原因
            stop_reason = response_data.get("stop_reason", "end_turn")
            finish_reason = self._map_stop_reason(stop_reason)

            return AIResponse(
                content=content,
                model_used=response_data.get("model", request.model),
                tokens_used=tokens_used,
                finish_reason=finish_reason,
                response_time_ms=response_time_ms,
                metadata={
                    "provider": "anthropic",
                    "raw_response": response_data if hasattr(self, "include_metadata") and self.include_metadata else None,
                    "input_tokens": usage.get("input_tokens"),
                    "output_tokens": usage.get("output_tokens"),
                    "stop_reason": stop_reason,
                },
            )

        except (KeyError, IndexError, TypeError) as e:
            raise AIServiceError(
                f"Failed to parse Anthropic response: {str(e)}",
                provider="anthropic",
                details={"response_data": response_data},
            )

    async def _stream_response(
        self,
        response_data: dict[str, Any],
    ) -> AsyncGenerator[StreamingChunk, None]:
        """处理 Anthropic 流式响应"""
        # Anthropic 流式响应处理逻辑
        if "content" in response_data:
            content = response_data["content"]
            if isinstance(content, list) and content:
                text = content[0].get("text", "")
                if text:
                    yield text

    async def _handle_api_error(self, response: httpx.Response) -> Never:
        """处理 API 错误响应"""
        try:
            error_data = response.json()
            error_message = error_data.get("error", {}).get("message", "Unknown error")
            error_type = error_data.get("error", {}).get("type", "unknown")
        except (json.JSONDecodeError, KeyError):
            error_message = response.text
            error_type = "unknown"

        match response.status_code:
            case 401:
                raise AIServiceError(
                    f"Authentication failed: {error_message}",
                    provider="anthropic",
                    status_code=response.status_code,
                )
            case 429:
                raise AIServiceError(
                    f"Rate limit exceeded: {error_message}",
                    provider="anthropic",
                    status_code=response.status_code,
                )
            case 500 | 502 | 503 | 504:
                raise AIServiceError(
                    f"Anthropic service error: {error_message}",
                    provider="anthropic",
                    status_code=response.status_code,
                )
            case 400:
                raise AIServiceError(
                    f"Bad request: {error_message}",
                    provider="anthropic",
                    status_code=response.status_code,
                )
            case _:
                raise AIServiceError(
                    f"Anthropic API error ({response.status_code}): {error_message}",
                    provider="anthropic",
                    status_code=response.status_code,
                    details={"error_type": error_type},
                )

    def _map_stop_reason(self, stop_reason: str) -> str:
        """映射停止原因"""
        match stop_reason:
            case "end_turn":
                return "stop"
            case "max_tokens":
                return "length"
            case "tool_use":
                return "tool_calls"
            case "stop_sequence":
                return "stop"
            case _:
                return "stop"

    async def get_available_models(self) -> list[dict[str, Any]]:
        """获取可用模型列表（模拟实现）"""
        # Anthropic 不提供模型列表 API，返回预定义的模型
        return [
            {
                "id": "claude-3-5-sonnet-20241022",
                "name": "Claude 3.5 Sonnet",
                "description": "Most powerful model for complex tasks",
                "max_tokens": 200000,
                "capabilities": ["text", "analysis", "code"],
            },
            {
                "id": "claude-3-5-haiku-20241022",
                "name": "Claude 3.5 Haiku",
                "description": "Fast and efficient model for everyday tasks",
                "max_tokens": 200000,
                "capabilities": ["text", "analysis"],
            },
            {
                "id": "claude-3-opus-20240229",
                "name": "Claude 3 Opus",
                "description": "Previous generation model for complex reasoning",
                "max_tokens": 4096,
                "capabilities": ["text", "analysis", "code"],
            },
        ]

    async def count_tokens(self, text: str) -> int:
        """估算文本令牌数（简化实现）"""
        # 这是一个简化的令牌计数实现
        # 实际应用中应该使用 tiktoken 或类似的库
        return len(text.split()) * 4  # 粗略估算

    async def validate_model(self, model_id: str) -> bool:
        """验证模型 ID 是否有效"""
        available_models = await self.get_available_models()
        return any(model["id"] == model_id for model in available_models)

    # Python 3.13: 新特性 - async context manager 支持
    async def stream_with_callback(
        self,
        request: AIRequest,
        config: AIRequestConfig,
        callback: callable,
    ) -> None:
        """流式响应带回调函数"""
        async for chunk in self.generate_streaming_response(request, config):
            await callback(chunk)

    def supports_streaming(self) -> bool:
        """检查是否支持流式响应"""
        return True

    def supports_function_calling(self) -> bool:
        """检查是否支持函数调用"""
        return False  # Claude 在当前 API 版本中不支持传统函数调用