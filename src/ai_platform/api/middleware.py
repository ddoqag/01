"""
中间件模块 - 展示现代 Python Web 中间件设计模式
"""

import time
import uuid
from datetime import datetime, UTC
from typing import Any, Callable

from fastapi import Request, Response
from fastapi.middleware.base import BaseHTTPMiddleware
from starlette.middleware.base import RequestResponseEndpoint
import structlog

from ..core.config import get_settings

logger = structlog.get_logger()

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """请求日志中间件"""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        """处理请求日志"""
        # 生成请求 ID
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id

        # 记录开始时间
        start_time = time.time()

        # 记录请求信息
        logger.info(
            "Request started",
            request_id=request_id,
            method=request.method,
            url=str(request.url),
            client_ip=request.client.host if request.client else "unknown",
            user_agent=request.headers.get("user-agent", "unknown"),
        )

        try:
            # 处理请求
            response = await call_next(request)

            # 计算处理时间
            process_time = time.time() - start_time

            # 记录响应信息
            logger.info(
                "Request completed",
                request_id=request_id,
                status_code=response.status_code,
                process_time_ms=int(process_time * 1000),
            )

            # 添加响应头
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Process-Time"] = f"{process_time:.3f}"

            return response

        except Exception as e:
            # 计算处理时间
            process_time = time.time() - start_time

            # 记录错误信息
            logger.error(
                "Request failed",
                request_id=request_id,
                error=str(e),
                error_type=type(e).__name__,
                process_time_ms=int(process_time * 1000),
            )

            # 重新抛出异常
            raise

class RateLimitMiddleware(BaseHTTPMiddleware):
    """速率限制中间件"""

    def __init__(self, app, max_requests: int = 100, window_seconds: int = 3600):
        super().__init__(app)
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._client_requests: dict[str, list[datetime]] = {}

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        """处理速率限制"""
        # 获取客户端 IP
        client_ip = self._get_client_ip(request)

        # 检查速率限制
        if not self._is_allowed(client_ip):
            logger.warning(
                "Rate limit exceeded",
                client_ip=client_ip,
                url=str(request.url),
            )

            return Response(
                content='{"error": "Rate limit exceeded"}',
                status_code=429,
                headers={"Retry-After": str(self.window_seconds)},
                media_type="application/json",
            )

        # 记录请求
        self._record_request(client_ip)

        # 处理请求
        return await call_next(request)

    def _get_client_ip(self, request: Request) -> str:
        """获取客户端 IP"""
        # 检查代理头
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()

        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip

        return request.client.host if request.client else "unknown"

    def _is_allowed(self, client_ip: str) -> bool:
        """检查是否允许请求"""
        now = datetime.now(UTC)
        window_start = now.replace(second=0, microsecond=0)

        # 获取客户端请求记录
        if client_ip not in self._client_requests:
            self._client_requests[client_ip] = []

        # 清理过期记录
        self._client_requests[client_ip] = [
            req_time for req_time in self._client_requests[client_ip]
            if req_time > window_start
        ]

        # 检查是否超过限制
        return len(self._client_requests[client_ip]) < self.max_requests

    def _record_request(self, client_ip: str) -> None:
        """记录请求"""
        self._client_requests[client_ip].append(datetime.now(UTC))

        # 限制内存使用
        if len(self._client_requests) > 10000:
            # 删除最旧的客户端记录
            oldest_clients = sorted(
                self._client_requests.keys(),
                key=lambda ip: min(self._client_requests[ip]) if self._client_requests[ip] else datetime.now(UTC)
            )[:1000]

            for client in oldest_clients:
                del self._client_requests[client]

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """安全头中间件"""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        """添加安全头"""
        response = await call_next(request)

        # 添加安全头
        security_headers = {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Content-Security-Policy": "default-src 'self'",
        }

        for header, value in security_headers.items():
            response.headers[header] = value

        return response

class MetricsMiddleware(BaseHTTPMiddleware):
    """指标收集中间件"""

    def __init__(self, app):
        super().__init__(app)
        self._metrics = {
            "total_requests": 0,
            "requests_by_method": {},
            "requests_by_status": {},
            "total_response_time": 0.0,
            "error_count": 0,
        }

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        """收集请求指标"""
        start_time = time.time()

        try:
            response = await call_next(request)

            # 更新指标
            self._update_metrics(request, response, start_time, False)

            return response

        except Exception as e:
            # 更新错误指标
            self._update_metrics(request, None, start_time, True)
            raise

    def _update_metrics(
        self,
        request: Request,
        response: Response | None,
        start_time: float,
        is_error: bool,
    ) -> None:
        """更新指标"""
        process_time = time.time() - start_time

        # 基础指标
        self._metrics["total_requests"] += 1
        self._metrics["total_response_time"] += process_time

        if is_error:
            self._metrics["error_count"] += 1

        # 按方法分类
        method = request.method
        self._metrics["requests_by_method"][method] = (
            self._metrics["requests_by_method"].get(method, 0) + 1
        )

        # 按状态码分类
        if response:
            status_code = response.status_code
            self._metrics["requests_by_status"][status_code] = (
                self._metrics["requests_by_status"].get(status_code, 0) + 1
            )

    def get_metrics(self) -> dict[str, Any]:
        """获取指标数据"""
        total_requests = self._metrics["total_requests"]

        return {
            **self._metrics,
            "average_response_time": (
                self._metrics["total_response_time"] / total_requests
                if total_requests > 0 else 0
            ),
            "error_rate": (
                self._metrics["error_count"] / total_requests
                if total_requests > 0 else 0
            ),
        }

class CompressionMiddleware(BaseHTTPMiddleware):
    """响应压缩中间件"""

    def __init__(self, app, minimum_size: int = 1024):
        super().__init__(app)
        self.minimum_size = minimum_size

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        """处理响应压缩"""
        response = await call_next(request)

        # 检查是否应该压缩
        if not self._should_compress(request, response):
            return response

        # 检查客户端是否支持压缩
        accept_encoding = request.headers.get("Accept-Encoding", "")
        if "gzip" not in accept_encoding.lower():
            return response

        # 这里应该实现实际的压缩逻辑
        # 为了简化，我们只添加压缩头
        response.headers["Content-Encoding"] = "gzip"

        return response

    def _should_compress(self, request: Request, response: Response) -> bool:
        """检查是否应该压缩响应"""
        # 检查内容类型
        content_type = response.headers.get("Content-Type", "")
        compressible_types = [
            "application/json",
            "text/html",
            "text/css",
            "text/javascript",
            "application/javascript",
        ]

        if not any(ct in content_type for ct in compressible_types):
            return False

        # 检查内容长度（如果可用）
        content_length = response.headers.get("Content-Length")
        if content_length and int(content_length) < self.minimum_size:
            return False

        return True

class CacheMiddleware(BaseHTTPMiddleware):
    """缓存中间件"""

    def __init__(self, app, default_ttl: int = 300):
        super().__init__(app)
        self.default_ttl = default_ttl
        self._cache: dict[str, dict[str, Any]] = {}

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        """处理缓存"""
        # 只缓存 GET 请求
        if request.method != "GET":
            return await call_next(request)

        # 生成缓存键
        cache_key = self._generate_cache_key(request)

        # 检查缓存
        cached_response = self._get_cached_response(cache_key)
        if cached_response:
            logger.debug("Cache hit", cache_key=cache_key)
            return cached_response

        # 处理请求
        response = await call_next(request)

        # 缓存响应
        if self._should_cache(request, response):
            self._cache_response(cache_key, response)
            logger.debug("Response cached", cache_key=cache_key)

        return response

    def _generate_cache_key(self, request: Request) -> str:
        """生成缓存键"""
        import hashlib
        key_parts = [
            str(request.url),
            request.headers.get("Accept", ""),
        ]
        key_string = "|".join(key_parts)
        return hashlib.md5(key_string.encode()).hexdigest()

    def _should_cache(self, request: Request, response: Response) -> bool:
        """检查是否应该缓存响应"""
        # 只缓存成功响应
        if response.status_code != 200:
            return False

        # 检查缓存控制头
        cache_control = response.headers.get("Cache-Control", "")
        if "no-cache" in cache_control or "private" in cache_control:
            return False

        return True

    def _get_cached_response(self, cache_key: str) -> Response | None:
        """获取缓存的响应"""
        if cache_key not in self._cache:
            return None

        cached_data = self._cache[cache_key]
        expires_at = cached_data["expires_at"]

        # 检查是否过期
        if datetime.now(UTC) > expires_at:
            del self._cache[cache_key]
            return None

        return cached_data["response"]

    def _cache_response(self, cache_key: str, response: Response) -> None:
        """缓存响应"""
        expires_at = datetime.now(UTC).replace(second=0, microsecond=0)
        expires_at = expires_at.replace(second=expires_at.second + self.default_ttl)

        self._cache[cache_key] = {
            "response": response,
            "expires_at": expires_at,
        }

        # 限制缓存大小
        if len(self._cache) > 1000:
            # 删除最旧的缓存条目
            oldest_key = min(
                self._cache.keys(),
                key=lambda k: self._cache[k]["expires_at"]
            )
            del self._cache[oldest_key]

def setup_middleware(app) -> None:
    """设置所有中间件"""
    settings = get_settings()

    # 添加中间件（顺序很重要）
    app.add_middleware(MetricsMiddleware)

    if settings.is_production():
        app.add_middleware(SecurityHeadersMiddleware)
        app.add_middleware(RateLimitMiddleware)

    app.add_middleware(RequestLoggingMiddleware)

    # 在生产环境中启用压缩
    if settings.is_production():
        app.add_middleware(CompressionMiddleware)

    # 缓存中间件（可选）
    # app.add_middleware(CacheMiddleware)