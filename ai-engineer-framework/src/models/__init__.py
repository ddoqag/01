"""
AI Engineer Framework - 核心模型模块

提供统一的LLM模型接口、嵌入模型和RAG系统抽象
"""

from .llm import LLMProvider, LLMConfig, Message, ModelResponse
from .embeddings import EmbeddingProvider, EmbeddingConfig
from .rag import RAGSystem, RAGConfig, Document, SearchResult
from .agents import Agent, AgentConfig, MultiAgentSystem
from .multimodal import MultimodalProcessor, MediaProcessor

__version__ = "0.1.0"
__all__ = [
    "LLMProvider",
    "LLMConfig",
    "Message",
    "ModelResponse",
    "EmbeddingProvider",
    "EmbeddingConfig",
    "RAGSystem",
    "RAGConfig",
    "Document",
    "SearchResult",
    "Agent",
    "AgentConfig",
    "MultiAgentSystem",
    "MultimodalProcessor",
    "MediaProcessor",
]