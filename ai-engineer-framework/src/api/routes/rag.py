"""
RAG API路由

提供检索增强生成相关的API端点
"""

import os
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, UploadFile, File, Form, BackgroundTasks
from pydantic import BaseModel, Field

from ...models.rag import Document, DocumentType, RAGConfig
from ...services.factory import get_service_registry
from ...services.cost_optimizer import get_cost_optimizer
from ...utils.cost_tracking import track_cost


router = APIRouter()


class DocumentUploadResponse(BaseModel):
    """文档上传响应"""
    document_id: str
    filename: str
    size: int
    type: str
    chunks_created: int
    status: str


class SearchRequest(BaseModel):
    """搜索请求"""
    query: str = Field(..., description="搜索查询")
    top_k: int = Field(5, description="返回结果数量", ge=1, le=100)
    similarity_threshold: float = Field(0.7, description="相似度阈值", ge=0.0, le=1.0)
    filter: Optional[Dict[str, Any]] = Field(None, description="过滤条件")


class SearchResponse(BaseModel):
    """搜索响应"""
    query: str
    results: List[Dict[str, Any]]
    total_found: int
    search_time: float


class QueryRequest(BaseModel):
    """RAG查询请求"""
    question: str = Field(..., description="用户问题")
    top_k: int = Field(5, description="检索文档数量", ge=1, le=100)
    use_rag: bool = Field(True, description="是否使用RAG")
    context: Optional[List[str]] = Field(None, description="额外上下文")


class QueryResponse(BaseModel):
    """RAG查询响应"""
    answer: str
    sources: List[Dict[str, Any]]
    citations: List[Dict[str, Any]]
    query: str
    context_used: List[str]
    response_time: float
    token_usage: Dict[str, int]


class DocumentInfo(BaseModel):
    """文档信息"""
    id: str
    filename: str
    type: str
    size: int
    chunk_count: int
    created_at: float
    metadata: Dict[str, Any]


@router.post("/documents/upload", response_model=DocumentUploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """上传文档到RAG系统"""
    try:
        service_registry = get_service_registry()
        rag_service = service_registry.get_service("rag")
        if not rag_service:
            raise HTTPException(status_code=503, detail="RAG service not available")

        # 读取文件内容
        content = await file.read()
        file_size = len(content)

        # 检查文件大小限制
        max_size = 50 * 1024 * 1024  # 50MB
        if file_size > max_size:
            raise HTTPException(
                status_code=413,
                detail=f"File size {file_size} exceeds maximum allowed size {max_size}"
            )

        # 确定文档类型
        file_extension = os.path.splitext(file.filename)[1].lower()
        doc_type_map = {
            '.txt': DocumentType.TEXT,
            '.pdf': DocumentType.PDF,
            '.docx': DocumentType.DOCX,
            '.html': DocumentType.HTML,
            '.md': DocumentType.MARKDOWN,
            '.json': DocumentType.JSON,
            '.csv': DocumentType.CSV,
        }

        doc_type = doc_type_map.get(file_extension, DocumentType.TEXT)

        # 创建文档对象
        document = Document(
            id=f"doc_{int(time.time() * 1000)}",
            content=content.decode('utf-8', errors='ignore'),
            doc_type=doc_type,
            source=file.filename,
            metadata={
                "filename": file.filename,
                "size": file_size,
                "content_type": file.content_type
            }
        )

        # 处理文档（后台任务）
        background_tasks.add_task(
            process_document_async,
            rag_service,
            document
        )

        return DocumentUploadResponse(
            document_id=document.id,
            filename=file.filename,
            size=file_size,
            type=doc_type.value,
            chunks_created=0,  # 将在后台处理中更新
            status="processing"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def process_document_async(rag_service, document: Document) -> None:
    """异步处理文档"""
    try:
        # 添加文档到RAG系统
        chunk_ids = await rag_service.add_document(document)
        print(f"Document {document.id} processed with {len(chunk_ids)} chunks")
    except Exception as e:
        print(f"Failed to process document {document.id}: {e}")


@router.post("/documents", response_model=DocumentUploadResponse)
async def add_document_text(
    content: str = Form(...),
    filename: str = Form(...),
    doc_type: str = Form("text"),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """直接添加文本内容到RAG系统"""
    try:
        service_registry = get_service_registry()
        rag_service = service_registry.get_service("rag")
        if not rag_service:
            raise HTTPException(status_code=503, detail="RAG service not available")

        # 创建文档对象
        document = Document(
            id=f"doc_{int(time.time() * 1000)}",
            content=content,
            doc_type=DocumentType(doc_type),
            source=filename,
            metadata={
                "filename": filename,
                "size": len(content)
            }
        )

        # 处理文档
        chunk_ids = await rag_service.add_document(document)

        return DocumentUploadResponse(
            document_id=document.id,
            filename=filename,
            size=len(content),
            type=doc_type,
            chunks_created=len(chunk_ids),
            status="completed"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/search", response_model=SearchResponse)
async def search_documents(request: SearchRequest):
    """搜索文档"""
    try:
        service_registry = get_service_registry()
        rag_service = service_registry.get_service("rag")
        if not rag_service:
            raise HTTPException(status_code=503, detail="RAG service not available")

        # 执行搜索
        retrieval_result = await rag_service.retrieve(
            query=request.query,
            top_k=request.top_k,
            similarity_threshold=request.similarity_threshold
        )

        # 转换结果格式
        results = []
        for i, chunk in enumerate(retrieval_result.chunks):
            results.append({
                "chunk_id": chunk.id,
                "document_id": chunk.document_id,
                "content": chunk.content,
                "score": retrieval_result.scores[i],
                "metadata": chunk.metadata
            })

        return SearchResponse(
            query=request.query,
            results=results,
            total_found=retrieval_result.total_found,
            search_time=retrieval_result.search_time
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/query", response_model=QueryResponse)
async def rag_query(
    request: QueryRequest,
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """RAG查询接口"""
    try:
        service_registry = get_service_registry()
        rag_service = service_registry.get_service("rag")
        cost_optimizer = get_cost_optimizer()

        if not rag_service:
            raise HTTPException(status_code=503, detail="RAG service not available")

        if request.use_rag:
            # 使用RAG生成回答
            rag_response = await rag_service.generate_answer(
                query=request.question,
                context=request.context,
                top_k=request.top_k
            )

            # 记录成本（后台任务）
            background_tasks.add_task(
                cost_optimizer.record_cost,
                service_type="rag",
                model_name="rag_system",
                input_tokens=len(request.question),
                output_tokens=len(rag_response.answer),
                requests_count=1
            )

            # 转换源文档格式
            sources = []
            for chunk in rag_response.sources:
                sources.append({
                    "chunk_id": chunk.id,
                    "document_id": chunk.document_id,
                    "content": chunk.content[:500] + "..." if len(chunk.content) > 500 else chunk.content,
                    "metadata": chunk.metadata
                })

            return QueryResponse(
                answer=rag_response.answer,
                sources=sources,
                citations=rag_response.citations,
                query=rag_response.query,
                context_used=rag_response.context_used,
                response_time=rag_response.response_time,
                token_usage=rag_response.token_usage
            )

        else:
            # 直接回答（不使用RAG）
            # 这里应该调用LLM服务直接生成回答
            # 简化实现
            return QueryResponse(
                answer=f"This is a direct answer to: {request.question}",
                sources=[],
                citations=[],
                query=request.question,
                context_used=request.context or [],
                response_time=0.1,
                token_usage={"prompt_tokens": 50, "completion_tokens": 100, "total_tokens": 150}
            )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/documents", response_model=List[DocumentInfo])
async def list_documents(
    limit: int = 100,
    offset: int = 0
):
    """列出所有文档"""
    try:
        service_registry = get_service_registry()
        rag_service = service_registry.get_service("rag")
        if not rag_service:
            raise HTTPException(status_code=503, detail="RAG service not available")

        # 这里需要实现文档列表功能
        # 简化实现
        return []

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/documents/{document_id}")
async def get_document(document_id: str):
    """获取特定文档信息"""
    try:
        service_registry = get_service_registry()
        rag_service = service_registry.get_service("rag")
        if not rag_service:
            raise HTTPException(status_code=503, detail="RAG service not available")

        # 这里需要实现文档获取功能
        # 简化实现
        return {"document_id": document_id, "status": "found"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/documents/{document_id}")
async def delete_document(document_id: str):
    """删除文档"""
    try:
        service_registry = get_service_registry()
        rag_service = service_registry.get_service("rag")
        if not rag_service:
            raise HTTPException(status_code=503, detail="RAG service not available")

        # 删除文档
        success = await rag_service.delete_document(document_id)

        if success:
            return {"message": f"Document {document_id} deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail="Document not found")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats")
async def get_rag_stats():
    """获取RAG系统统计信息"""
    try:
        service_registry = get_service_registry()
        rag_service = service_registry.get_service("rag")
        if not rag_service:
            raise HTTPException(status_code=503, detail="RAG service not available")

        # 获取统计信息
        stats = await rag_service.get_document_stats()

        return {
            "statistics": stats,
            "timestamp": time.time()
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/config")
async def update_rag_config(config: RAGConfig):
    """更新RAG配置"""
    try:
        service_registry = get_service_registry()
        rag_service = service_registry.get_service("rag")
        if not rag_service:
            raise HTTPException(status_code=503, detail="RAG service not available")

        # 更新配置
        rag_service.config = config

        return {"message": "RAG configuration updated successfully", "config": config.dict()}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/config")
async def get_rag_config():
    """获取当前RAG配置"""
    try:
        service_registry = get_service_registry()
        rag_service = service_registry.get_service("rag")
        if not rag_service:
            raise HTTPException(status_code=503, detail="RAG service not available")

        return rag_service.config.dict()

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# 导入time模块
import time