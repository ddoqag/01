"""
AI Integration Platform - 现代化 AI 集成平台

这个项目展示了 Python 3.13+ 的现代化开发特性，包括：
- 先进的类型系统和类型提示
- 异步编程模式
- AI/LLM API 集成
- 企业级架构模式
- 性能优化和安全最佳实践
"""

__version__ = "0.1.0"
__author__ = "Python Pro v3"
__email__ = "python-pro@example.com"

from .core.config import Settings, get_settings
from .core.models import (
    AIRequest,
    AIResponse,
    Conversation,
    Message,
)
from .core.exceptions import (
    AIPlatformError,
    AIServiceError,
    ValidationError,
)

__all__ = [
    "__version__",
    "__author__",
    "__email__",
    "Settings",
    "get_settings",
    "AIRequest",
    "AIResponse",
    "Conversation",
    "Message",
    "AIPlatformError",
    "AIServiceError",
    "ValidationError",
]