"""
AI 服务管理器 - 展示现代服务编排和负载均衡
"""

import asyncio
import random
from datetime import datetime, UTC
from typing import Any, AsyncGenerator, Dict, List

from ..core.config import AIProvider, get_settings
from ..core.models import AIRequest, AIResponse, AIModel
from ..core.exceptions import AIServiceError, RateLimitError
from .base import BaseAIProvider, create_ai_provider

class AIManager:
    """AI 服务管理器 - 负责多个 AI 提供商的管理和负载均衡"""

    def __init__(self) -> None:
        self.settings = get_settings()
        self._providers: Dict[AIProvider, BaseAIProvider] = {}
        self._provider_stats: Dict[AIProvider, Dict[str, Any]] = {}
        self._model_registry: Dict[str, AIModel] = {}
        self._initialized = False
        self._lock = asyncio.Lock()

    async def initialize(self) -> None:
        """初始化所有 AI 提供商"""
        async with self._lock:
            if self._initialized:
                return

            for provider in self.settings.ai_providers:
                try:
                    await self._initialize_provider(provider)
                except Exception as e:
                    # 记录错误但继续初始化其他提供商
                    self._provider_stats[provider] = {
                        "status": "error",
                        "error": str(e),
                        "last_updated": datetime.now(UTC),
                    }

            self._initialized = True

    async def _initialize_provider(self, provider: AIProvider) -> None:
        """初始化单个提供商"""
        config = self.settings.get_ai_provider_config(provider)

        if not config.get("api_key"):
            raise ValueError(f"No API key configured for provider: {provider}")

        # 创建提供商实例
        provider_instance = create_ai_provider(
            provider=provider,
            api_key=config["api_key"],
            base_url=config["base_url"],
            timeout=config["timeout"],
        )

        # 初始化提供商
        await provider_instance.initialize()

        # 存储提供商
        self._providers[provider] = provider_instance

        # 初始化统计信息
        self._provider_stats[provider] = {
            "status": "active",
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "total_response_time_ms": 0,
            "average_response_time_ms": 0.0,
            "last_request_time": None,
            "last_updated": datetime.now(UTC),
        }

    async def cleanup(self) -> None:
        """清理所有资源"""
        async with self._lock:
            for provider in self._providers.values():
                try:
                    await provider.cleanup()
                except Exception:
                    pass  # 忽略清理错误

            self._providers.clear()
            self._provider_stats.clear()
            self._model_registry.clear()
            self._initialized = False

    async def generate_response(
        self,
        request: AIRequest,
        preferred_provider: AIProvider | None = None,
    ) -> AIResponse:
        """生成 AI 响应，支持负载均衡和故障转移"""
        await self._ensure_initialized()

        # 选择提供商
        provider = await self._select_provider(request, preferred_provider)

        try:
            # 更新统计信息
            await self._update_request_stats(provider, "start")

            # 生成响应
            response = await self._providers[provider].generate_response(request)

            # 更新成功统计
            await self._update_request_stats(provider, "success", response.response_time_ms)

            return response

        except Exception as e:
            # 更新失败统计
            await self._update_request_stats(provider, "error")

            # 尝试故障转移到其他提供商
            if preferred_provider is None:
                return await self._failover_request(request, exclude_provider=provider)

            raise

    async def generate_streaming_response(
        self,
        request: AIRequest,
        preferred_provider: AIProvider | None = None,
    ) -> AsyncGenerator[str, None]:
        """生成流式 AI 响应"""
        await self._ensure_initialized()

        # 选择提供商（必须支持流式）
        provider = await self._select_provider(request, preferred_provider, streaming=True)

        try:
            await self._update_request_stats(provider, "start")

            async for chunk in self._providers[provider].generate_streaming_response(request):
                yield chunk

            await self._update_request_stats(provider, "success")

        except Exception as e:
            await self._update_request_stats(provider, "error")
            raise

    async def _select_provider(
        self,
        request: AIRequest,
        preferred_provider: AIProvider | None = None,
        streaming: bool = False,
    ) -> AIProvider:
        """选择最佳提供商"""
        available_providers = []

        # 收集可用的提供商
        for provider, instance in self._providers.items():
            if self._provider_stats[provider]["status"] != "active":
                continue

            if streaming and not instance.supports_streaming():
                continue

            # 验证模型支持
            if hasattr(instance, 'validate_model'):
                if not await instance.validate_model(request.model):
                    continue

            available_providers.append(provider)

        if not available_providers:
            raise AIServiceError("No available AI providers")

        # 如果指定了首选提供商且可用，使用它
        if preferred_provider and preferred_provider in available_providers:
            return preferred_provider

        # 使用负载均衡算法选择提供商
        return await self._load_balance_provider(available_providers)

    async def _load_balance_provider(self, providers: List[AIProvider]) -> AIProvider:
        """负载均衡选择提供商"""
        # 使用加权轮询算法，考虑响应时间和成功率
        weights = []

        for provider in providers:
            stats = self._provider_stats[provider]

            # 计算权重
            if stats["total_requests"] == 0:
                weight = 1.0
            else:
                success_rate = stats["successful_requests"] / stats["total_requests"]
                avg_response_time = stats["average_response_time_ms"]

                # 成功率权重 60%，响应时间权重 40%
                success_weight = success_rate * 0.6
                time_weight = (1000 / max(avg_response_time, 1)) * 0.4

                weight = success_weight + time_weight

            weights.append(weight)

        # 加权随机选择
        total_weight = sum(weights)
        if total_weight == 0:
            return random.choice(providers)

        rand_value = random.uniform(0, total_weight)
        current_weight = 0

        for provider, weight in zip(providers, weights):
            current_weight += weight
            if rand_value <= current_weight:
                return provider

        return providers[-1]  # fallback

    async def _failover_request(
        self,
        request: AIRequest,
        exclude_provider: AIProvider,
    ) -> AIResponse:
        """故障转移到其他提供商"""
        excluded_providers = {exclude_provider}
        max_attempts = len(self._providers) - 1

        for attempt in range(max_attempts):
            try:
                provider = await self._select_provider(
                    request,
                    preferred_provider=None,
                )

                if provider in excluded_providers:
                    continue

                return await self.generate_response(request, preferred_provider=provider)

            except Exception:
                excluded_providers.add(provider)
                continue

        raise AIServiceError("All AI providers failed")

    async def _update_request_stats(
        self,
        provider: AIProvider,
        status: str,
        response_time_ms: int = 0,
    ) -> None:
        """更新提供商统计信息"""
        stats = self._provider_stats[provider]

        match status:
            case "start":
                stats["total_requests"] += 1
                stats["last_request_time"] = datetime.now(UTC)
            case "success":
                stats["successful_requests"] += 1
                if response_time_ms > 0:
                    stats["total_response_time_ms"] += response_time_ms
                    stats["average_response_time_ms"] = (
                        stats["total_response_time_ms"] / stats["successful_requests"]
                    )
            case "error":
                stats["failed_requests"] += 1

        stats["last_updated"] = datetime.now(UTC)

    async def _ensure_initialized(self) -> None:
        """确保管理器已初始化"""
        if not self._initialized:
            await self.initialize()

    async def get_provider_stats(self) -> Dict[str, Any]:
        """获取提供商统计信息"""
        await self._ensure_initialized()

        return {
            provider.value: stats.copy()
            for provider, stats in self._provider_stats.items()
        }

    async def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        await self._ensure_initialized()

        health_status = {
            "overall_status": "healthy",
            "providers": {},
            "total_providers": len(self._providers),
            "active_providers": 0,
            "timestamp": datetime.now(UTC).isoformat(),
        }

        for provider, instance in self._providers.items():
            try:
                # 简单的健康检查 - 可以扩展为实际的健康检查请求
                stats = self._provider_stats[provider]
                is_healthy = stats["status"] == "active"

                health_status["providers"][provider.value] = {
                    "status": "healthy" if is_healthy else "unhealthy",
                    "last_request_time": stats.get("last_request_time"),
                    "success_rate": (
                        stats["successful_requests"] / stats["total_requests"]
                        if stats["total_requests"] > 0 else 0
                    ),
                }

                if is_healthy:
                    health_status["active_providers"] += 1

            except Exception:
                health_status["providers"][provider.value] = {
                    "status": "error",
                    "error": "Health check failed",
                }

        if health_status["active_providers"] == 0:
            health_status["overall_status"] = "unhealthy"
        elif health_status["active_providers"] < len(self._providers):
            health_status["overall_status"] = "degraded"

        return health_status

    # Python 3.13: 上下文管理器支持
    async def __aenter__(self) -> "AIManager":
        await self.initialize()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self.cleanup()

# 全局 AI 管理器实例
_ai_manager: AIManager | None = None

async def get_ai_manager() -> AIManager:
    """获取全局 AI 管理器实例"""
    global _ai_manager
    if _ai_manager is None:
        _ai_manager = AIManager()
        await _ai_manager.initialize()
    return _ai_manager

def set_ai_manager(manager: AIManager) -> None:
    """设置全局 AI 管理器实例（主要用于测试）"""
    global _ai_manager
    _ai_manager = manager