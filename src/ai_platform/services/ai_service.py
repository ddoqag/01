"""
AI 服务 - 展示现代异步服务和依赖注入模式
"""

import asyncio
from datetime import datetime, UTC
from typing import Any, AsyncGenerator, Dict, List, Optional
from uuid import uuid4

from ..ai.manager import AIManager, get_ai_manager
from ..core.models import AIRequest, AIResponse, Conversation, Message
from ..core.config import get_settings
from ..core.exceptions import (
    AIServiceError,
    RateLimitError,
    ValidationError,
)

class AIService:
    """AI 服务 - 高级 AI 功能服务"""

    def __init__(
        self,
        ai_manager: Optional[AIManager] = None,
        settings: Optional[Any] = None,
    ) -> None:
        self.ai_manager = ai_manager
        self.settings = settings or get_settings()
        self._request_cache: Dict[str, Any] = {}
        self._rate_limit_tracker: Dict[str, List[datetime]] = {}
        self._lock = asyncio.Lock()

    async def initialize(self) -> None:
        """初始化 AI 服务"""
        if self.ai_manager is None:
            self.ai_manager = await get_ai_manager()

    async def process_request(
        self,
        request: AIRequest,
        conversation: Optional[Conversation] = None,
    ) -> AIResponse:
        """处理 AI 请求"""
        await self._ensure_initialized()

        # 验证请求
        await self._validate_request(request)

        # 检查速率限制
        await self._check_rate_limit(request.user_id)

        # 检查缓存
        cache_key = self._get_cache_key(request)
        if cached_response := await self._get_cached_response(cache_key):
            return cached_response

        try:
            # 添加用户消息到对话
            if conversation:
                user_message = Message(
                    role="user",
                    content=request.prompt,
                    user_id=request.user_id,
                )
                conversation.add_message(user_message)

            # 生成 AI 响应
            response = await self.ai_manager.generate_response(request)

            # 缓存响应
            await self._cache_response(cache_key, response)

            # 添加助手消息到对话
            if conversation:
                assistant_message = Message(
                    role="assistant",
                    content=response.content,
                    model_used=response.model_used,
                    token_count=response.tokens_used,
                    user_id=request.user_id,
                )
                conversation.add_message(assistant_message)

            return response

        except Exception as e:
            raise AIServiceError(f"Failed to process AI request: {str(e)}") from e

    async def process_streaming_request(
        self,
        request: AIRequest,
        conversation: Optional[Conversation] = None,
    ) -> AsyncGenerator[str, None]:
        """处理流式 AI 请求"""
        await self._ensure_initialized()

        # 验证请求
        await self._validate_request(request, streaming=True)

        # 检查速率限制
        await self._check_rate_limit(request.user_id)

        try:
            # 添加用户消息到对话
            if conversation:
                user_message = Message(
                    role="user",
                    content=request.prompt,
                    user_id=request.user_id,
                )
                conversation.add_message(user_message)

            # 生成流式响应
            accumulated_content = ""
            async for chunk in self.ai_manager.generate_streaming_response(request):
                accumulated_content += chunk
                yield chunk

            # 添加助手消息到对话（流式完成后）
            if conversation and accumulated_content:
                assistant_message = Message(
                    role="assistant",
                    content=accumulated_content,
                    model_used=request.model,
                    user_id=request.user_id,
                )
                conversation.add_message(assistant_message)

        except Exception as e:
            raise AIServiceError(f"Failed to process streaming AI request: {str(e)}") from e

    async def batch_process(
        self,
        requests: List[AIRequest],
        max_concurrent: int = 5,
    ) -> List[AIResponse]:
        """批量处理 AI 请求"""
        await self._ensure_initialized()

        if not requests:
            return []

        # 创建信号量控制并发数
        semaphore = asyncio.Semaphore(max_concurrent)

        async def process_single_request(request: AIRequest) -> AIResponse:
            async with semaphore:
                return await self.process_request(request)

        # 并发处理所有请求
        tasks = [process_single_request(request) for request in requests]
        responses = await asyncio.gather(*tasks, return_exceptions=True)

        # 处理异常结果
        processed_responses = []
        for i, response in enumerate(responses):
            if isinstance(response, Exception):
                # 创建错误响应
                error_response = AIResponse(
                    content=f"Error processing request {i}: {str(response)}",
                    model_used="error",
                    tokens_used=0,
                    finish_reason="stop",
                    response_time_ms=0,
                    cost=0.0,
                )
                processed_responses.append(error_response)
            else:
                processed_responses.append(response)

        return processed_responses

    async def analyze_text(
        self,
        text: str,
        analysis_type: str = "sentiment",
        model: str = "claude-3-haiku-20240307",
        user_id: str = "system",
    ) -> Dict[str, Any]:
        """文本分析功能"""
        analysis_prompts = {
            "sentiment": "Analyze the sentiment of this text and provide a score from -1 (very negative) to 1 (very positive), along with reasoning.",
            "entities": "Extract all named entities (people, organizations, locations, etc.) from this text.",
            "topics": "Identify the main topics and themes in this text.",
            "summary": "Provide a concise summary of this text in 2-3 sentences.",
            "keywords": "Extract the most important keywords from this text.",
        }

        if analysis_type not in analysis_prompts:
            raise ValidationError(f"Unsupported analysis type: {analysis_type}")

        prompt = f"{analysis_prompts[analysis_type]}\n\nText: {text}"

        request = AIRequest(
            prompt=prompt,
            model=model,
            user_id=user_id,
            max_tokens=500,
            temperature=0.1,  # 低温度以获得一致的分析结果
        )

        response = await self.process_request(request)

        # 尝试解析结构化结果
        try:
            import json
            return json.loads(response.content)
        except (json.JSONDecodeError, ValueError):
            # 如果不是 JSON 格式，返回原始文本
            return {
                "analysis_type": analysis_type,
                "result": response.content,
                "model_used": response.model_used,
                "tokens_used": response.tokens_used,
            }

    async def translate_text(
        self,
        text: str,
        target_language: str,
        source_language: str = "auto",
        model: str = "gpt-4o-mini",
        user_id: str = "system",
    ) -> str:
        """文本翻译功能"""
        prompt = f"""
        Translate the following text from {source_language} to {target_language}.
        Only provide the translated text without any additional explanation.

        Text to translate:
        {text}
        """

        request = AIRequest(
            prompt=prompt,
            model=model,
            user_id=user_id,
            max_tokens=min(len(text) * 2, 4000),  # 限制令牌数
            temperature=0.1,  # 低温度以获得准确的翻译
        )

        response = await self.process_request(request)
        return response.content.strip()

    async def generate_code(
        self,
        description: str,
        language: str = "python",
        model: str = "claude-3-5-sonnet-20241022",
        user_id: str = "system",
    ) -> str:
        """代码生成功能"""
        prompt = f"""
        Generate {language} code based on the following description:

        Description:
        {description}

        Please provide clean, well-commented code that follows best practices.
        Include necessary imports and error handling.
        """

        request = AIRequest(
            prompt=prompt,
            model=model,
            user_id=user_id,
            max_tokens=2000,
            temperature=0.2,  # 稍低温度以获得一致的代码质量
        )

        response = await self.process_request(request)
        return response.content

    async def _validate_request(self, request: AIRequest, streaming: bool = False) -> None:
        """验证 AI 请求"""
        if not request.prompt.strip():
            raise ValidationError("Prompt cannot be empty")

        if len(request.prompt) > 50000:
            raise ValidationError("Prompt too long (max 50000 characters)")

        if request.max_tokens < 1 or request.max_tokens > 32000:
            raise ValidationError("Invalid max_tokens (must be between 1 and 32000)")

        if not 0.0 <= request.temperature <= 2.0:
            raise ValidationError("Invalid temperature (must be between 0.0 and 2.0)")

        # 流式请求的特殊验证
        if streaming and not request.stream:
            raise ValidationError("Streaming requests must have stream=True")

    async def _check_rate_limit(self, user_id: str) -> None:
        """检查用户速率限制"""
        now = datetime.now(UTC)
        window_start = now.replace(second=0, microsecond=0)

        async with self._lock:
            if user_id not in self._rate_limit_tracker:
                self._rate_limit_tracker[user_id] = []

            # 清理过期的请求记录
            self._rate_limit_tracker[user_id] = [
                req_time for req_time in self._rate_limit_tracker[user_id]
                if req_time > window_start
            ]

            # 检查是否超过限制
            current_requests = len(self._rate_limit_tracker[user_id])
            if current_requests >= self.settings.rate_limit_requests:
                raise RateLimitError(
                    f"Rate limit exceeded for user {user_id}",
                    limit=self.settings.rate_limit_requests,
                    window=self.settings.rate_limit_window,
                )

            # 记录当前请求
            self._rate_limit_tracker[user_id].append(now)

    def _get_cache_key(self, request: AIRequest) -> str:
        """生成缓存键"""
        # 使用请求的哈希作为缓存键
        import hashlib
        content = f"{request.prompt}:{request.model}:{request.temperature}:{request.max_tokens}"
        return hashlib.md5(content.encode()).hexdigest()

    async def _get_cached_response(self, cache_key: str) -> Optional[AIResponse]:
        """获取缓存的响应"""
        if cache_key in self._request_cache:
            cached_data = self._request_cache[cache_key]
            # 检查缓存是否过期（1小时）
            if (datetime.now(UTC) - cached_data["timestamp"]).seconds < 3600:
                return cached_data["response"]
            else:
                # 删除过期缓存
                del self._request_cache[cache_key]
        return None

    async def _cache_response(self, cache_key: str, response: AIResponse) -> None:
        """缓存响应"""
        self._request_cache[cache_key] = {
            "response": response,
            "timestamp": datetime.now(UTC),
        }

        # 限制缓存大小
        if len(self._request_cache) > 1000:
            # 删除最旧的缓存条目
            oldest_key = min(
                self._request_cache.keys(),
                key=lambda k: self._request_cache[k]["timestamp"]
            )
            del self._request_cache[oldest_key]

    async def _ensure_initialized(self) -> None:
        """确保服务已初始化"""
        if self.ai_manager is None:
            await self.initialize()

    async def get_service_stats(self) -> Dict[str, Any]:
        """获取服务统计信息"""
        await self._ensure_initialized()

        return {
            "cache_size": len(self._request_cache),
            "rate_limited_users": len(self._rate_limit_tracker),
            "ai_provider_stats": await self.ai_manager.get_provider_stats(),
            "timestamp": datetime.now(UTC).isoformat(),
        }

    async def cleanup(self) -> None:
        """清理服务资源"""
        self._request_cache.clear()
        self._rate_limit_tracker.clear()
        if self.ai_manager:
            await self.ai_manager.cleanup()