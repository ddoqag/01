"""
OpenAI GPT 集成 - 展示现代化 API 集成和异步处理
"""

import json
from datetime import datetime, UTC
from typing import Any, AsyncGenerator

import httpx

from .base import BaseAIProvider, AIRequestConfig, StreamingChunk, SupportsFunctionCalling
from ..core.models import AIRequest, AIResponse
from ..core.exceptions import AIServiceError, AIServiceTimeoutError

class OpenAIProvider(BaseAIProvider, SupportsFunctionCalling):
    """OpenAI GPT AI 服务提供商"""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._models_cache: dict[str, dict[str, Any]] = {}

    def _get_headers(self) -> dict[str, str]:
        """获取 OpenAI API 请求头"""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    async def initialize(self) -> None:
        """初始化 OpenAI 服务"""
        try:
            # 验证 API 密钥并获取模型列表
            response = await self.client.get("/models", timeout=10)
            if response.status_code != 200:
                raise AIServiceError(
                    "Failed to initialize OpenAI service",
                    provider="openai",
                    status_code=response.status_code,
                )

            # 缓存模型列表
            models_data = response.json()
            self._models_cache = {
                model["id"]: model
                for model in models_data.get("data", [])
            }

        except httpx.TimeoutException:
            raise AIServiceTimeoutError("OpenAI service initialization timeout")
        except httpx.HTTPStatusError as e:
            raise AIServiceError(
                f"OpenAI API error: {e.response.text}",
                provider="openai",
                status_code=e.response.status_code,
            )

    async def cleanup(self) -> None:
        """清理 OpenAI 资源"""
        await self.client.aclose()
        self._models_cache.clear()

    async def _make_request(
        self,
        request: AIRequest,
        config: AIRequestConfig,
    ) -> dict[str, Any]:
        """发送 OpenAI API 请求"""
        # 构建请求负载
        payload = self._build_payload(request, config)

        # 确定端点
        endpoint = "/chat/completions"

        # 发送请求
        response = await self.client.post(
            endpoint,
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
        messages = []

        # 添加系统消息
        if request.system_prompt:
            messages.append({"role": "system", "content": request.system_prompt})

        # 添加用户消息
        messages.append({"role": "user", "content": request.prompt})

        payload = {
            "model": request.model,
            "messages": messages,
            "max_tokens": config.max_tokens,
            "temperature": config.temperature,
            "stream": config.stream,
        }

        # 添加函数调用支持
        if request.functions:
            payload["functions"] = request.functions
            payload["function_call"] = "auto"

        # 添加响应格式
        if config.response_format == "json":
            payload["response_format"] = {"type": "json_object"}

        # 添加其他参数
        payload.update({
            "top_p": 1.0,
            "frequency_penalty": 0.0,
            "presence_penalty": 0.0,
        })

        return payload

    async def _parse_response(
        self,
        response_data: dict[str, Any],
        request: AIRequest,
        start_time: datetime,
    ) -> AIResponse:
        """解析 OpenAI API 响应"""
        try:
            # 计算响应时间
            response_time_ms = int((datetime.now(UTC) - start_time).total_seconds() * 1000)

            # 提取响应内容
            choice = response_data["choices"][0]
            content = choice.get("message", {}).get("content", "") or ""

            # 获取令牌使用情况
            usage = response_data.get("usage", {})
            tokens_used = usage.get("total_tokens", 0)

            # 确定结束原因
            finish_reason = choice.get("finish_reason", "stop")

            # 构建元数据
            metadata = {
                "provider": "openai",
                "raw_response": response_data if hasattr(self, "include_metadata") and self.include_metadata else None,
                "prompt_tokens": usage.get("prompt_tokens"),
                "completion_tokens": usage.get("completion_tokens"),
                "total_tokens": usage.get("total_tokens"),
            }

            # 检查是否有函数调用
            if function_call := choice.get("message", {}).get("function_call"):
                metadata["function_call"] = function_call
                content = json.dumps(function_call) if not content else content

            return AIResponse(
                content=content,
                model_used=response_data.get("model", request.model),
                tokens_used=tokens_used,
                finish_reason=finish_reason,
                response_time_ms=response_time_ms,
                metadata=metadata,
            )

        except (KeyError, IndexError, TypeError) as e:
            raise AIServiceError(
                f"Failed to parse OpenAI response: {str(e)}",
                provider="openai",
                details={"response_data": response_data},
            )

    async def _stream_response(
        self,
        response_data: dict[str, Any],
    ) -> AsyncGenerator[StreamingChunk, None]:
        """处理 OpenAI 流式响应"""
        # OpenAI 流式响应在 _make_request 中处理
        # 这里只是一个占位符
        yield ""

    async def _stream_chat_completion(
        self,
        request: AIRequest,
        config: AIRequestConfig,
    ) -> AsyncGenerator[StreamingChunk, None]:
        """处理 OpenAI 流式聊天完成"""
        payload = self._build_payload(request, config)

        async with self.client.stream(
            "POST",
            "/chat/completions",
            json=payload,
            timeout=config.timeout,
        ) as response:
            if response.status_code != 200:
                await self._handle_api_error(response)

            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    data = line[6:]  # 移除 "data: " 前缀

                    if data == "[DONE]":
                        break

                    try:
                        chunk_data = json.loads(data)
                        if choices := chunk_data.get("choices"):
                            if delta := choices[0].get("delta"):
                                if content := delta.get("content"):
                                    yield content
                    except json.JSONDecodeError:
                        continue

    async def generate_streaming_response(
        self,
        request: AIRequest,
        config: AIRequestConfig | None = None,
        *,
        chunk_callback: callable | None = None,
    ) -> AsyncGenerator[StreamingChunk, None]:
        """生成流式 AI 响应"""
        config = config or AIRequestConfig()
        config.stream = True

        async for chunk in self._stream_chat_completion(request, config):
            if chunk_callback:
                await chunk_callback(chunk)
            yield chunk

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
                    provider="openai",
                    status_code=response.status_code,
                )
            case 429:
                raise AIServiceError(
                    f"Rate limit exceeded: {error_message}",
                    provider="openai",
                    status_code=response.status_code,
                )
            case 500 | 502 | 503 | 504:
                raise AIServiceError(
                    f"OpenAI service error: {error_message}",
                    provider="openai",
                    status_code=response.status_code,
                )
            case 400:
                raise AIServiceError(
                    f"Bad request: {error_message}",
                    provider="openai",
                    status_code=response.status_code,
                )
            case _:
                raise AIServiceError(
                    f"OpenAI API error ({response.status_code}): {error_message}",
                    provider="openai",
                    status_code=response.status_code,
                    details={"error_type": error_type},
                )

    async def get_available_models(self) -> list[dict[str, Any]]:
        """获取可用模型列表"""
        if not self._models_cache:
            await self.initialize()

        return [
            {
                "id": model_id,
                "name": model_id,
                "description": f"OpenAI model: {model_id}",
                "capabilities": self._get_model_capabilities(model_id),
            }
            for model_id in self._models_cache.keys()
            if model_id.startswith(("gpt-", "text-"))
        ]

    def _get_model_capabilities(self, model_id: str) -> list[str]:
        """获取模型能力"""
        capabilities = ["text"]

        if "gpt-4" in model_id:
            capabilities.extend(["analysis", "code", "function_calling"])
        elif "gpt-3.5" in model_id:
            capabilities.extend(["code"])

        return capabilities

    async def call_function(
        self,
        function_name: str,
        arguments: dict[str, Any],
        request: AIRequest,
    ) -> Any:
        """执行函数调用"""
        # 构建函数调用请求
        function_payload = {
            "name": function_name,
            "arguments": json.dumps(arguments),
        }

        # 创建包含函数调用的请求
        function_request = AIRequest(
            prompt=f"Execute function: {function_name}",
            model=request.model,
            user_id=request.user_id,
            functions=[{
                "name": function_name,
                "description": f"Execute {function_name} function",
                "parameters": {
                    "type": "object",
                    "properties": {
                        key: {"type": "string"} for key in arguments.keys()
                    },
                    "required": list(arguments.keys()),
                },
            }],
        )

        # 发送请求
        response = await self.generate_response(function_request)

        # 解析函数调用结果
        try:
            return json.loads(response.content)
        except json.JSONDecodeError:
            return response.content

    async def count_tokens(self, text: str) -> int:
        """估算文本令牌数"""
        try:
            import tiktoken
            try:
                encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
            except KeyError:
                encoding = tiktoken.get_encoding("cl100k_base")
            return len(encoding.encode(text))
        except ImportError:
            # 如果没有 tiktoken，使用简化估算
            return len(text.split()) * 4

    async def validate_model(self, model_id: str) -> bool:
        """验证模型 ID 是否有效"""
        if not self._models_cache:
            await self.initialize()
        return model_id in self._models_cache

    def supports_streaming(self) -> bool:
        """检查是否支持流式响应"""
        return True

    def supports_function_calling(self) -> bool:
        """检查是否支持函数调用"""
        return True