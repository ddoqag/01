"""
RAG (检索增强生成) 系统统一接口

提供文档处理、检索、增强生成等功能
"""

import asyncio
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union, Tuple, AsyncGenerator
from enum import Enum
import hashlib
import time
from pathlib import Path

from pydantic import BaseModel, Field, validator

from .llm import Message, ModelResponse, LLMProvider
from .embeddings import EmbeddingProvider, VectorStore, SearchResult, SearchQuery


class DocumentType(str, Enum):
    """文档类型"""
    TEXT = "text"
    PDF = "pdf"
    DOCX = "docx"
    HTML = "html"
    MARKDOWN = "markdown"
    JSON = "json"
    CSV = "csv"


class ChunkingStrategy(str, Enum):
    """分块策略"""
    FIXED_SIZE = "fixed_size"
    SENTENCE = "sentence"
    PARAGRAPH = "paragraph"
    SEMANTIC = "semantic"
    HYBRID = "hybrid"


@dataclass
class Document:
    """文档数据结构"""
    id: str
    content: str
    doc_type: DocumentType
    source: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)
    chunk_size: Optional[int] = None
    chunk_overlap: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "id": self.id,
            "content": self.content,
            "doc_type": self.doc_type.value,
            "source": self.source,
            "metadata": self.metadata,
            "created_at": self.created_at,
            "chunk_size": self.chunk_size,
            "chunk_overlap": self.chunk_overlap
        }


@dataclass
class DocumentChunk:
    """文档分块"""
    id: str
    document_id: str
    content: str
    start_index: int
    end_index: int
    metadata: Dict[str, Any] = field(default_factory=dict)
    embedding: Optional[List[float]] = None

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "id": self.id,
            "document_id": self.document_id,
            "content": self.content,
            "start_index": self.start_index,
            "end_index": self.end_index,
            "metadata": self.metadata,
            "embedding": self.embedding
        }


@dataclass
class RetrievalResult:
    """检索结果"""
    query: str
    chunks: List[DocumentChunk]
    scores: List[float]
    total_found: int
    search_time: float
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RAGResponse:
    """RAG响应"""
    answer: str
    sources: List[DocumentChunk]
    citations: List[Dict[str, Any]]
    query: str
    context_used: List[str]
    response_time: float
    token_usage: Dict[str, int] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


class RAGConfig(BaseModel):
    """RAG系统配置"""
    # 检索配置
    top_k: int = Field(5, description="检索的文档数量")
    similarity_threshold: float = Field(0.7, description="相似度阈值")
    max_context_length: int = Field(4000, description="最大上下文长度")
    include_metadata: bool = Field(True, description="是否包含元数据")

    # 分块配置
    chunk_size: int = Field(512, description="分块大小")
    chunk_overlap: int = Field(50, description="分块重叠")
    chunking_strategy: ChunkingStrategy = Field(ChunkingStrategy.FIXED_SIZE, description="分块策略")

    # 重排配置
    rerank: bool = Field(False, description="是否重排结果")
    rerank_model: Optional[str] = Field(None, description="重排模型")

    # 生成配置
    system_prompt: str = Field(
        "你是一个有用的AI助手。请基于提供的上下文信息回答用户的问题。",
        description="系统提示词"
    )
    context_template: str = Field(
        "上下文信息：\n{context}\n\n用户问题：{question}",
        description="上下文模板"
    )

    # 缓存配置
    enable_cache: bool = Field(True, description="是否启用缓存")
    cache_ttl: int = Field(3600, description="缓存过期时间（秒）")


class DocumentProcessor(ABC):
    """文档处理器抽象基类"""

    @abstractmethod
    async def process(self, file_path: Union[str, Path]) -> Document:
        """处理文档"""
        pass

    @abstractmethod
    def supports(self, file_path: Union[str, Path]) -> bool:
        """检查是否支持该文件类型"""
        pass


class Chunker:
    """文档分块器"""

    def __init__(self, strategy: ChunkingStrategy = ChunkingStrategy.FIXED_SIZE):
        self.strategy = strategy

    async def chunk_document(
        self,
        document: Document,
        chunk_size: int = 512,
        chunk_overlap: int = 50
    ) -> List[DocumentChunk]:
        """分块文档"""
        if self.strategy == ChunkingStrategy.FIXED_SIZE:
            return await self._fixed_size_chunking(document, chunk_size, chunk_overlap)
        elif self.strategy == ChunkingStrategy.PARAGRAPH:
            return await self._paragraph_chunking(document, chunk_overlap)
        elif self.strategy == ChunkingStrategy.SENTENCE:
            return await self._sentence_chunking(document, chunk_overlap)
        elif self.strategy == ChunkingStrategy.SEMANTIC:
            return await self._semantic_chunking(document, chunk_size)
        elif self.strategy == ChunkingStrategy.HYBRID:
            return await self._hybrid_chunking(document, chunk_size, chunk_overlap)
        else:
            raise ValueError(f"Unsupported chunking strategy: {self.strategy}")

    async def _fixed_size_chunking(
        self,
        document: Document,
        chunk_size: int,
        chunk_overlap: int
    ) -> List[DocumentChunk]:
        """固定大小分块"""
        chunks = []
        content = document.content
        length = len(content)

        for i in range(0, length, chunk_size - chunk_overlap):
            end = min(i + chunk_size, length)
            chunk_id = f"{document.id}_chunk_{len(chunks)}"

            chunk = DocumentChunk(
                id=chunk_id,
                document_id=document.id,
                content=content[i:end],
                start_index=i,
                end_index=end,
                metadata={
                    "chunk_index": len(chunks),
                    "chunk_strategy": self.strategy.value,
                    "document_source": document.source
                }
            )
            chunks.append(chunk)

        return chunks

    async def _paragraph_chunking(
        self,
        document: Document,
        chunk_overlap: int
    ) -> List[DocumentChunk]:
        """段落分块"""
        # 简化的段落分块实现
        paragraphs = document.content.split('\n\n')
        chunks = []

        current_content = ""
        start_index = 0

        for i, paragraph in enumerate(paragraphs):
            if not current_content:
                current_content = paragraph
                start_index = document.content.find(paragraph)
            else:
                current_content += "\n\n" + paragraph

            # 如果累积内容达到一定长度，创建分块
            if len(current_content) >= 512 or i == len(paragraphs) - 1:
                chunk_id = f"{document.id}_chunk_{len(chunks)}"
                end_index = start_index + len(current_content)

                chunk = DocumentChunk(
                    id=chunk_id,
                    document_id=document.id,
                    content=current_content,
                    start_index=start_index,
                    end_index=end_index,
                    metadata={
                        "chunk_index": len(chunks),
                        "chunk_strategy": self.strategy.value,
                        "document_source": document.source,
                        "paragraph_count": current_content.count('\n\n') + 1
                    }
                )
                chunks.append(chunk)
                current_content = ""

        return chunks

    async def _sentence_chunking(
        self,
        document: Document,
        chunk_overlap: int
    ) -> List[DocumentChunk]:
        """句子分块"""
        # 简化的句子分块实现
        import re
        sentences = re.split(r'[.!?]+', document.content)
        sentences = [s.strip() for s in sentences if s.strip()]

        chunks = []
        current_content = ""
        start_index = 0

        for i, sentence in enumerate(sentences):
            if not current_content:
                current_content = sentence
                start_index = document.content.find(sentence)
            else:
                current_content += ". " + sentence

            # 如果累积内容达到一定长度，创建分块
            if len(current_content) >= 400 or i == len(sentences) - 1:
                chunk_id = f"{document.id}_chunk_{len(chunks)}"
                end_index = start_index + len(current_content)

                chunk = DocumentChunk(
                    id=chunk_id,
                    document_id=document.id,
                    content=current_content,
                    start_index=start_index,
                    end_index=end_index,
                    metadata={
                        "chunk_index": len(chunks),
                        "chunk_strategy": self.strategy.value,
                        "document_source": document.source,
                        "sentence_count": current_content.count('.') + current_content.count('!') + current_content.count('?')
                    }
                )
                chunks.append(chunk)
                current_content = ""

        return chunks

    async def _semantic_chunking(
        self,
        document: Document,
        max_chunk_size: int
    ) -> List[DocumentChunk]:
        """语义分块 - 需要嵌入模型支持"""
        # 简化的语义分块实现
        # 实际实现需要基于语义相似度进行分块
        return await self._fixed_size_chunking(document, max_chunk_size, 50)

    async def _hybrid_chunking(
        self,
        document: Document,
        chunk_size: int,
        chunk_overlap: int
    ) -> List[DocumentChunk]:
        """混合分块策略"""
        # 结合多种分块策略
        chunks = []

        # 首先按段落分块
        paragraph_chunks = await self._paragraph_chunking(document, 0)

        # 对过长的段落进行进一步分块
        for chunk in paragraph_chunks:
            if len(chunk.content) > chunk_size:
                sub_chunks = await self._fixed_size_chunking(
                    Document(
                        id=chunk.id,
                        content=chunk.content,
                        doc_type=document.doc_type,
                        source=document.source,
                        metadata=document.metadata
                    ),
                    chunk_size,
                    chunk_overlap
                )
                chunks.extend(sub_chunks)
            else:
                chunks.append(chunk)

        return chunks


class RAGSystem:
    """RAG系统核心类"""

    def __init__(
        self,
        llm_provider: LLMProvider,
        embedding_provider: EmbeddingProvider,
        vector_store: VectorStore,
        config: RAGConfig
    ):
        self.llm_provider = llm_provider
        self.embedding_provider = embedding_provider
        self.vector_store = vector_store
        self.config = config
        self.chunker = Chunker(config.chunking_strategy)
        self._document_processors: Dict[DocumentType, DocumentProcessor] = {}
        self._cache: Dict[str, Any] = {}

    async def initialize(self) -> None:
        """初始化RAG系统"""
        await self.llm_provider.initialize()
        await self.embedding_provider.initialize()
        await self.vector_store.initialize()

    def register_processor(self, doc_type: DocumentType, processor: DocumentProcessor) -> None:
        """注册文档处理器"""
        self._document_processors[doc_type] = processor

    async def add_document(self, document: Document) -> List[str]:
        """添加文档到RAG系统"""
        # 分块文档
        chunks = await self.chunker.chunk_document(
            document,
            self.config.chunk_size,
            self.config.chunk_overlap
        )

        # 为分块生成嵌入
        chunk_texts = [chunk.content for chunk in chunks]
        embeddings = await self.embedding_provider.embed_batch(chunk_texts)

        # 添加嵌入到分块
        for chunk, embedding in zip(chunks, embeddings):
            chunk.embedding = embedding

        # 添加到向量存储
        from .embeddings import DocumentEmbedding
        doc_embeddings = [
            DocumentEmbedding(
                document_id=chunk.id,
                embedding=chunk.embedding,
                text=chunk.content,
                metadata=chunk.metadata
            )
            for chunk in chunks
        ]

        return await self.vector_store.add_documents(doc_embeddings)

    async def retrieve(
        self,
        query: str,
        top_k: Optional[int] = None,
        similarity_threshold: Optional[float] = None
    ) -> RetrievalResult:
        """检索相关文档"""
        start_time = time.time()

        # 检查缓存
        cache_key = hashlib.md5(query.encode()).hexdigest()
        if self.config.enable_cache and cache_key in self._cache:
            cached_result = self._cache[cache_key]
            if time.time() - cached_result["timestamp"] < self.config.cache_ttl:
                return cached_result["result"]

        # 生成查询嵌入
        query_embedding = await self.embedding_provider.embed_text(query)

        # 搜索向量存储
        search_query = SearchQuery(
            text=query,
            embedding=query_embedding,
            top_k=top_k or self.config.top_k,
            filter=None,
            include_metadata=self.config.include_metadata
        )

        search_results = await self.vector_store.search(search_query)
        search_time = time.time() - start_time

        # 过滤结果
        threshold = similarity_threshold or self.config.similarity_threshold
        filtered_results = [
            result for result in search_results
            if result.score >= threshold
        ]

        # 转换为文档分块
        chunks = []
        scores = []

        for result in filtered_results:
            chunk = DocumentChunk(
                id=result.document_id,
                document_id=result.metadata.get("document_id", ""),
                content=result.text,
                start_index=0,
                end_index=len(result.text),
                metadata=result.metadata,
                embedding=result.embedding
            )
            chunks.append(chunk)
            scores.append(result.score)

        retrieval_result = RetrievalResult(
            query=query,
            chunks=chunks,
            scores=scores,
            total_found=len(search_results),
            search_time=search_time,
            metadata={
                "threshold_used": threshold,
                "results_filtered": len(search_results) - len(filtered_results)
            }
        )

        # 缓存结果
        if self.config.enable_cache:
            self._cache[cache_key] = {
                "result": retrieval_result,
                "timestamp": time.time()
            }

        return retrieval_result

    async def generate_answer(
        self,
        query: str,
        context: Optional[List[str]] = None,
        **kwargs
    ) -> RAGResponse:
        """生成答案"""
        start_time = time.time()

        # 检索相关文档（如果没有提供上下文）
        if context is None:
            retrieval_result = await self.retrieve(query)
            context = [chunk.content for chunk in retrieval_result.chunks]
            source_chunks = retrieval_result.chunks
        else:
            source_chunks = []

        # 构建上下文
        context_text = "\n\n".join(context)
        context_text = context_text[:self.config.max_context_length]

        # 构建提示词
        prompt = self.config.context_template.format(
            context=context_text,
            question=query
        )

        messages = [
            Message(role=MessageRole.SYSTEM, content=self.config.system_prompt),
            Message(role=MessageRole.USER, content=prompt)
        ]

        # 生成回答
        response = await self.llm_provider.generate(messages, **kwargs)

        # 构建引用
        citations = []
        for i, chunk in enumerate(source_chunks):
            citation = {
                "chunk_id": chunk.id,
                "document_id": chunk.document_id,
                "text": chunk.content[:200] + "..." if len(chunk.content) > 200 else chunk.content,
                "score": retrieval_result.scores[i] if hasattr(retrieval_result, 'scores') else 0.0,
                "metadata": chunk.metadata
            }
            citations.append(citation)

        # 构建响应
        rag_response = RAGResponse(
            answer=response.content,
            sources=source_chunks,
            citations=citations,
            query=query,
            context_used=context,
            response_time=time.time() - start_time,
            token_usage=response.usage,
            metadata={
                "model_used": response.model,
                "chunks_used": len(source_chunks),
                "context_length": len(context_text)
            }
        )

        return rag_response

    async def chat(
        self,
        message: str,
        history: Optional[List[Message]] = None
    ) -> RAGResponse:
        """聊天模式"""
        history = history or []

        # 检索相关文档
        retrieval_result = await self.retrieve(message)
        context = [chunk.content for chunk in retrieval_result.chunks]

        # 构建上下文
        context_text = "\n\n".join(context)
        context_text = context_text[:self.config.max_context_length]

        # 构建消息历史
        messages = [
            Message(role=MessageRole.SYSTEM, content=self.config.system_prompt)
        ]
        messages.extend(history)

        # 添加用户消息（包含上下文）
        user_message = self.config.context_template.format(
            context=context_text,
            question=message
        )
        messages.append(Message(role=MessageRole.USER, content=user_message))

        # 生成回答
        response = await self.llm_provider.generate(messages)

        # 构建引用
        citations = []
        for i, chunk in enumerate(retrieval_result.chunks):
            citation = {
                "chunk_id": chunk.id,
                "document_id": chunk.document_id,
                "text": chunk.content[:200] + "..." if len(chunk.content) > 200 else chunk.content,
                "score": retrieval_result.scores[i],
                "metadata": chunk.metadata
            }
            citations.append(citation)

        return RAGResponse(
            answer=response.content,
            sources=retrieval_result.chunks,
            citations=citations,
            query=message,
            context_used=context,
            response_time=0.0,  # TODO: 实现计时
            token_usage=response.usage,
            metadata={
                "model_used": response.model,
                "chunks_used": len(retrieval_result.chunks)
            }
        )

    async def delete_document(self, document_id: str) -> bool:
        """删除文档"""
        # 获取文档的所有分块
        chunks = await self.vector_store.search(SearchQuery(
            filter={"document_id": document_id},
            top_k=1000
        ))

        # 删除所有分块
        chunk_ids = [result.document_id for result in chunks]
        if chunk_ids:
            return await self.vector_store.delete_documents(chunk_ids)

        return True

    async def get_document_stats(self) -> Dict[str, Any]:
        """获取文档统计信息"""
        total_docs = await self.vector_store.count_documents()

        return {
            "total_documents": total_docs,
            "cache_size": len(self._cache),
            "config": self.config.dict()
        }