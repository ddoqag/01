"""
pytest 配置文件 - 展示现代 Python 测试配置
"""

import asyncio
from pathlib import Path
from typing import Any, AsyncGenerator, Generator
from unittest.mock import AsyncMock, MagicMock

import pytest
import pytest_asyncio
from httpx import AsyncClient

from src.ai_platform.api.app import create_app
from src.ai_platform.core.config import Settings, set_settings
from src.ai_platform.ai.manager import AIManager
from src.ai_platform.services import AIService, ConversationService

# Python 3.13: 使用 pytest-asyncio 进行异步测试
@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """创建事件循环"""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

@pytest_asyncio.fixture
async def test_settings() -> Settings:
    """测试配置"""
    settings = Settings(
        app_name="AI Platform Test",
        environment="testing",
        debug=True,
        secret_key="test-secret-key-for-testing-only",
        database_url="sqlite+aiosqlite:///:memory:",
        redis_url="redis://localhost:6379/1",
        anthropic_api_key="test-anthropic-key",
        openai_api_key="test-openai-key",
        rate_limit_requests=1000,
        rate_limit_window=3600,
        enable_metrics=True,
    )
    set_settings(settings)
    return settings

@pytest_asyncio.fixture
async def app(test_settings: Settings) -> Any:
    """测试应用"""
    app = create_app()
    return app

@pytest_asyncio.fixture
async def client(app: Any) -> AsyncGenerator[AsyncClient, None]:
    """测试客户端"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

@pytest_asyncio.fixture
async def mock_ai_manager() -> AIManager:
    """模拟 AI 管理器"""
    manager = MagicMock(spec=AIManager)

    # 模拟异步方法
    manager.initialize = AsyncMock()
    manager.cleanup = AsyncMock()
    manager.generate_response = AsyncMock()
    manager.generate_streaming_response = AsyncMock()
    manager.get_provider_stats = AsyncMock(return_value={})
    manager.health_check = AsyncMock(return_value={"status": "healthy"})

    return manager

@pytest_asyncio.fixture
async def ai_service(mock_ai_manager: AIManager) -> AIService:
    """AI 服务实例"""
    service = AIService(ai_manager=mock_ai_manager)
    await service.initialize()
    return service

@pytest_asyncio.fixture
async def conversation_service() -> ConversationService:
    """对话服务实例"""
    service = ConversationService()
    await service.initialize()
    return service

# Python 3.13: 模拟 AI 响应数据
@pytest.fixture
def mock_ai_response_data() -> dict[str, Any]:
    """模拟 AI 响应数据"""
    return {
        "content": "This is a test response from the AI service.",
        "model_used": "claude-3-haiku-20240307",
        "tokens_used": 50,
        "finish_reason": "stop",
        "response_time_ms": 1500,
        "cost": 0.001,
        "metadata": {
            "provider": "anthropic",
            "input_tokens": 20,
            "output_tokens": 30,
        },
    }

@pytest.fixture
def sample_ai_request() -> dict[str, Any]:
    """示例 AI 请求数据"""
    return {
        "prompt": "Hello, how are you?",
        "model": "claude-3-haiku-20240307",
        "max_tokens": 100,
        "temperature": 0.7,
        "system_prompt": "You are a helpful assistant.",
        "user_id": "test-user-123",
    }

@pytest.fixture
def sample_conversation_data() -> dict[str, Any]:
    """示例对话数据"""
    return {
        "title": "Test Conversation",
        "user_id": "test-user-123",
        "status": "active",
    }

# Python 3.13: 测试工具函数
@pytest.fixture
def create_mock_response():
    """创建模拟响应的工厂函数"""
    def _create_response(content: str, status_code: int = 200, **kwargs):
        response = MagicMock()
        response.content = content
        response.status_code = status_code
        response.headers = kwargs.get("headers", {})
        response.json.return_value = kwargs.get("json_data", {})
        return response
    return _create_response

# 异步测试上下文管理器
@pytest.fixture
async def async_test_context():
    """异步测试上下文"""
    async with AsyncClient() as client:
        yield client

# 性能测试装饰器
def performance_test(max_time_ms: float = 1000.0):
    """性能测试装饰器"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            import time
            start_time = time.time()

            result = await func(*args, **kwargs)

            end_time = time.time()
            elapsed_time_ms = (end_time - start_time) * 1000

            assert elapsed_time_ms <= max_time_ms, (
                f"Function {func.__name__} took {elapsed_time_ms:.2f}ms, "
                f"expected <= {max_time_ms:.2f}ms"
            )

            return result
        return wrapper
    return decorator

# 测试数据生成器
@pytest.fixture
def generate_test_data():
    """生成测试数据的工具"""
    def _generate_data(data_type: str, **kwargs):
        if data_type == "ai_request":
            return {
                "prompt": kwargs.get("prompt", "Test prompt"),
                "model": kwargs.get("model", "claude-3-haiku-20240307"),
                "max_tokens": kwargs.get("max_tokens", 100),
                "temperature": kwargs.get("temperature", 0.7),
                "user_id": kwargs.get("user_id", "test-user"),
            }
        elif data_type == "conversation":
            return {
                "title": kwargs.get("title", "Test Conversation"),
                "user_id": kwargs.get("user_id", "test-user"),
                "status": kwargs.get("status", "active"),
            }
        else:
            raise ValueError(f"Unknown data type: {data_type}")

    return _generate_data

# 清理工具
@pytest.fixture(autouse=True)
async def cleanup_test_data():
    """自动清理测试数据"""
    yield
    # 测试后清理逻辑
    pass

# Python 3.13: 测试标记
def pytest_configure(config):
    """配置 pytest 标记"""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests"
    )
    config.addinivalue_line(
        "markers", "ai: marks tests that require AI API access"
    )

# 测试集合钩子
def pytest_collection_modifyitems(config, items):
    """修改测试集合"""
    for item in items:
        # 为异步测试添加标记
        if asyncio.iscoroutinefunction(item.function):
            item.add_marker(pytest.mark.asyncio)

# 并发测试支持
@pytest_asyncio.fixture(scope="session")
async def test_semaphore():
    """测试信号量，用于控制并发测试数量"""
    return asyncio.Semaphore(10)