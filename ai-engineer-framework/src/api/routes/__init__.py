"""
API路由模块

提供所有API端点的路由定义
"""

from fastapi import APIRouter

from .llm import router as llm_router
from .embedding import router as embedding_router
from .rag import router as rag_router
from .agent import router as agent_router
from .multimodal import router as multimodal_router
from .monitoring import router as monitoring_router
from .cost import router as cost_router

# 创建主路由器
api_router = APIRouter()

# 注册各个模块的路由
api_router.include_router(llm_router, prefix="/llm", tags=["LLM"])
api_router.include_router(embedding_router, prefix="/embedding", tags=["Embedding"])
api_router.include_router(rag_router, prefix="/rag", tags=["RAG"])
api_router.include_router(agent_router, prefix="/agent", tags=["Agent"])
api_router.include_router(multimodal_router, prefix="/multimodal", tags=["Multimodal"])
api_router.include_router(monitoring_router, prefix="/monitoring", tags=["Monitoring"])
api_router.include_router(cost_router, prefix="/cost", tags=["Cost Optimization"])

# 根路径
@api_router.get("/")
async def root():
    """API根路径"""
    return {
        "message": "AI Engineer Framework API",
        "version": "0.1.0",
        "description": "现代AI工程化框架 - 集成多LLM提供商、RAG系统、Agent和多模态能力",
        "endpoints": {
            "llm": "/llm",
            "embedding": "/embedding",
            "rag": "/rag",
            "agent": "/agent",
            "multimodal": "/multimodal",
            "monitoring": "/monitoring",
            "cost": "/cost"
        },
        "docs": "/docs",
        "health": "/health"
    }