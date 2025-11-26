"""
嵌入模型和向量存储统一接口

支持多种嵌入提供商和向量数据库的统一接入
"""

import asyncio
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union, Tuple
import numpy as np
from enum import Enum

from pydantic import BaseModel, Field, validator


class EmbeddingProviderType(str, Enum):
    """嵌入提供商类型"""
    OPENAI = "openai"
    HUGGINGFACE = "huggingface"
    SENTENCE_TRANSFORMERS = "sentence_transformers"
    LOCAL = "local"


class VectorStoreType(str, Enum):
    """向量存储类型"""
    CHROMADB = "chromadb"
    PINECONE = "pinecone"
    WEAVIATE = "weaviate"
    FAISS = "faiss"
    QDRANT = "qdrant"


@dataclass
class DocumentEmbedding:
    """文档嵌入结果"""
    document_id: str
    embedding: List[float]
    text: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: float = field(default_factory=lambda: __import__('time').time())


@dataclass
class SearchQuery:
    """搜索查询"""
    text: Optional[str] = None
    embedding: Optional[List[float]] = None
    top_k: int = 10
    filter: Optional[Dict[str, Any]] = None
    include_metadata: bool = True


@dataclass
class SearchResult:
    """搜索结果"""
    document_id: str
    text: str
    score: float
    metadata: Dict[str, Any] = field(default_factory=dict)
    embedding: Optional[List[float]] = None


class EmbeddingConfig(BaseModel):
    """嵌入模型配置"""
    provider: EmbeddingProviderType
    model_name: str
    api_key: Optional[str] = None
    api_base: Optional[str] = None
    embedding_dimension: Optional[int] = None
    batch_size: int = Field(32, description="批处理大小")
    max_tokens: Optional[int] = Field(8192, description="最大令牌数")
    normalize_embeddings: bool = Field(True, description="是否归一化嵌入")
    timeout: int = Field(30, description="请求超时时间（秒）")


class VectorStoreConfig(BaseModel):
    """向量存储配置"""
    store_type: VectorStoreType
    collection_name: str = "default"
    embedding_dimension: Optional[int] = None
    api_key: Optional[str] = None
    api_base: Optional[str] = None
    host: Optional[str] = None
    port: Optional[int] = None
    index_type: str = "HNSW"
    metric: str = "cosine"
    batch_size: int = Field(100, description="批处理大小")
    timeout: int = Field(30, description="请求超时时间（秒）")


class EmbeddingProvider(ABC):
    """嵌入提供商抽象基类"""

    def __init__(self, config: EmbeddingConfig):
        self.config = config
        self._initialized = False

    @abstractmethod
    async def initialize(self) -> None:
        """初始化嵌入模型"""
        pass

    @abstractmethod
    async def embed_text(self, text: str) -> List[float]:
        """嵌入单个文本"""
        pass

    @abstractmethod
    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """批量嵌入文本"""
        pass

    @abstractmethod
    async def count_tokens(self, text: str) -> int:
        """计算令牌数"""
        pass

    @property
    def embedding_dimension(self) -> int:
        """获取嵌入维度"""
        if self.config.embedding_dimension:
            return self.config.embedding_dimension
        raise NotImplementedError("Embedding dimension not specified")

    async def embed_documents(
        self,
        documents: List[Tuple[str, str]],
        metadata: Optional[List[Dict[str, Any]]] = None
    ) -> List[DocumentEmbedding]:
        """嵌入文档"""
        texts = [doc[1] for doc in documents]
        embeddings = await self.embed_batch(texts)

        result = []
        for i, (doc_id, text) in enumerate(documents):
            doc_embedding = DocumentEmbedding(
                document_id=doc_id,
                embedding=embeddings[i],
                text=text,
                metadata=metadata[i] if metadata else {}
            )
            result.append(doc_embedding)

        return result

    async def cleanup(self) -> None:
        """清理资源"""
        pass


class VectorStore(ABC):
    """向量存储抽象基类"""

    def __init__(self, config: VectorStoreConfig):
        self.config = config
        self._initialized = False

    @abstractmethod
    async def initialize(self) -> None:
        """初始化向量存储"""
        pass

    @abstractmethod
    async def add_documents(
        self,
        embeddings: List[DocumentEmbedding]
    ) -> List[str]:
        """添加文档嵌入"""
        pass

    @abstractmethod
    async def search(
        self,
        query: SearchQuery
    ) -> List[SearchResult]:
        """搜索相似文档"""
        pass

    @abstractmethod
    async def delete_documents(self, document_ids: List[str]) -> bool:
        """删除文档"""
        pass

    @abstractmethod
    async def update_document(
        self,
        document_id: str,
        embedding: DocumentEmbedding
    ) -> bool:
        """更新文档"""
        pass

    @abstractmethod
    async def get_document(
        self,
        document_id: str
    ) -> Optional[DocumentEmbedding]:
        """获取文档"""
        pass

    @abstractmethod
    async def list_documents(
        self,
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> List[str]:
        """列出文档ID"""
        pass

    @abstractmethod
    async def count_documents(self) -> int:
        """统计文档数量"""
        pass

    async def search_by_text(
        self,
        text: str,
        embedding_provider: EmbeddingProvider,
        top_k: int = 10,
        **kwargs
    ) -> List[SearchResult]:
        """通过文本搜索"""
        embedding = await embedding_provider.embed_text(text)
        query = SearchQuery(
            text=text,
            embedding=embedding,
            top_k=top_k,
            **kwargs
        )
        return await self.search(query)

    async def cleanup(self) -> None:
        """清理资源"""
        pass


class EmbeddingManager:
    """嵌入管理器 - 统一管理嵌入提供商和向量存储"""

    def __init__(self):
        self._embedding_providers: Dict[str, EmbeddingProvider] = {}
        self._vector_stores: Dict[str, VectorStore] = {}
        self._default_provider: Optional[str] = None
        self._default_store: Optional[str] = None

    def register_embedding_provider(
        self,
        name: str,
        provider: EmbeddingProvider,
        set_as_default: bool = False
    ) -> None:
        """注册嵌入提供商"""
        self._embedding_providers[name] = provider
        if set_as_default or not self._default_provider:
            self._default_provider = name

    def register_vector_store(
        self,
        name: str,
        store: VectorStore,
        set_as_default: bool = False
    ) -> None:
        """注册向量存储"""
        self._vector_stores[name] = store
        if set_as_default or not self._default_store:
            self._default_store = name

    def get_embedding_provider(self, name: Optional[str] = None) -> EmbeddingProvider:
        """获取嵌入提供商"""
        provider_name = name or self._default_provider
        if not provider_name:
            raise ValueError("No default embedding provider set")

        if provider_name not in self._embedding_providers:
            raise ValueError(f"Embedding provider '{provider_name}' not found")

        return self._embedding_providers[provider_name]

    def get_vector_store(self, name: Optional[str] = None) -> VectorStore:
        """获取向量存储"""
        store_name = name or self._default_store
        if not store_name:
            raise ValueError("No default vector store set")

        if store_name not in self._vector_stores:
            raise ValueError(f"Vector store '{store_name}' not found")

        return self._vector_stores[store_name]

    async def index_documents(
        self,
        documents: List[Tuple[str, str]],
        embedding_provider: Optional[str] = None,
        vector_store: Optional[str] = None,
        metadata: Optional[List[Dict[str, Any]]] = None
    ) -> List[str]:
        """索引文档到向量存储"""
        provider = self.get_embedding_provider(embedding_provider)
        store = self.get_vector_store(vector_store)

        # 生成嵌入
        embeddings = await provider.embed_documents(documents, metadata)

        # 添加到向量存储
        return await store.add_documents(embeddings)

    async def search_documents(
        self,
        query_text: str,
        top_k: int = 10,
        embedding_provider: Optional[str] = None,
        vector_store: Optional[str] = None,
        **kwargs
    ) -> List[SearchResult]:
        """搜索文档"""
        provider = self.get_embedding_provider(embedding_provider)
        store = self.get_vector_store(vector_store)

        return await store.search_by_text(
            text=query_text,
            embedding_provider=provider,
            top_k=top_k,
            **kwargs
        )


# 全局嵌入管理器实例
embedding_manager = EmbeddingManager()


def get_embedding_manager() -> EmbeddingManager:
    """获取全局嵌入管理器"""
    return embedding_manager


# 工具函数
def cosine_similarity(a: List[float], b: List[float]) -> float:
    """计算余弦相似度"""
    a_np = np.array(a)
    b_np = np.array(b)
    return np.dot(a_np, b_np) / (np.linalg.norm(a_np) * np.linalg.norm(b_np))


def normalize_embedding(embedding: List[float]) -> List[float]:
    """归一化嵌入向量"""
    embedding_np = np.array(embedding)
    normalized = embedding_np / np.linalg.norm(embedding_np)
    return normalized.tolist()