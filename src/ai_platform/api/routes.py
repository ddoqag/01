"""
API 路由 - 展示现代 Python Web API 设计模式
"""

from datetime import datetime, UTC
from typing import Any, Dict, List, Optional
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
import structlog

from ..core.models import (
    AIRequest,
    AIResponse,
    Conversation,
    Message,
    ConversationStats,
)
from ..core.exceptions import ValidationError, RateLimitError, AIServiceError
from .app import get_service_from_state, HasState
from ..services import AIService, ConversationService

logger = structlog.get_logger()

# 创建路由器
api_router = APIRouter()

# Pydantic 模型用于 API 请求/响应
class GenerateRequest(BaseModel):
    """生成请求模型"""
    prompt: str = Field(..., min_length=1, max_length=50000, description="提示词")
    model: str = Field(default="claude-3-haiku-20240307", description="使用的模型")
    max_tokens: int = Field(default=1000, ge=1, le=32000, description="最大令牌数")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0, description="温度参数")
    system_prompt: Optional[str] = Field(default=None, max_length=10000, description="系统提示词")
    conversation_id: Optional[str] = Field(default=None, description="对话 ID")
    stream: bool = Field(default=False, description="是否流式输出")

class GenerateResponse(BaseModel):
    """生成响应模型"""
    request_id: str = Field(..., description="请求 ID")
    content: str = Field(..., description="生成的内容")
    model_used: str = Field(..., description="使用的模型")
    tokens_used: int = Field(..., description="使用的令牌数")
    response_time_ms: int = Field(..., description="响应时间(毫秒)")
    cost: float = Field(..., description="成本")

class ConversationRequest(BaseModel):
    """对话请求模型"""
    title: str = Field(..., min_length=1, max_length=200, description="对话标题")
    user_id: str = Field(..., min_length=1, max_length=100, description="用户 ID")

class ConversationResponse(BaseModel):
    """对话响应模型"""
    id: str
    title: str
    user_id: str
    status: str
    message_count: int
    total_tokens: int
    created_at: datetime
    updated_at: datetime

class AnalysisRequest(BaseModel):
    """分析请求模型"""
    text: str = Field(..., min_length=1, max_length=10000, description="要分析的文本")
    analysis_type: str = Field(
        default="sentiment",
        description="分析类型",
        examples=["sentiment", "entities", "topics", "summary", "keywords"]
    )
    model: str = Field(default="claude-3-haiku-20240307", description="使用的模型")

class TranslateRequest(BaseModel):
    """翻译请求模型"""
    text: str = Field(..., min_length=1, max_length=5000, description="要翻译的文本")
    target_language: str = Field(..., description="目标语言")
    source_language: str = Field(default="auto", description="源语言")
    model: str = Field(default="gpt-4o-mini", description="使用的模型")

class CodeGenerationRequest(BaseModel):
    """代码生成请求模型"""
    description: str = Field(..., min_length=1, max_length=2000, description="代码描述")
    language: str = Field(default="python", description="编程语言")
    model: str = Field(default="claude-3-5-sonnet-20241022", description="使用的模型")

# 依赖注入函数
async def get_ai_service(request) -> AIService:
    """获取 AI 服务依赖"""
    return get_service_from_state(request, "ai_service", AIService)

async def get_conversation_service(request) -> ConversationService:
    """获取对话服务依赖"""
    return get_service_from_state(request, "conversation_service", ConversationService)

# 生成相关端点
@api_router.post("/generate", response_model=GenerateResponse)
async def generate_text(
    request_data: GenerateRequest,
    background_tasks: BackgroundTasks,
    ai_service: AIService = Depends(get_ai_service),
    conversation_service: ConversationService = Depends(get_conversation_service),
):
    """生成文本内容"""
    try:
        # 创建 AI 请求
        ai_request = AIRequest(
            prompt=request_data.prompt,
            model=request_data.model,
            max_tokens=request_data.max_tokens,
            temperature=request_data.temperature,
            system_prompt=request_data.system_prompt,
            stream=request_data.stream,
            user_id="api_user",  # 实际应用中应该从认证中获取
        )

        # 获取对话（如果指定）
        conversation = None
        if request_data.conversation_id:
            conversation = await conversation_service.get_conversation(request_data.conversation_id)

        # 生成响应
        response = await ai_service.process_request(ai_request, conversation)

        # 后台任务：更新对话统计
        if conversation:
            background_tasks.add_task(
                conversation_service.update_conversation_stats,
                conversation.id,
            )

        return GenerateResponse(
            request_id=f"req_{uuid4().hex[:8]}",
            content=response.content,
            model_used=response.model_used,
            tokens_used=response.tokens_used,
            response_time_ms=response.response_time_ms,
            cost=response.cost,
        )

    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RateLimitError as e:
        raise HTTPException(
            status_code=429,
            detail={"error": "Rate limit exceeded", "retry_after": e.details.get("retry_after")},
        )
    except AIServiceError as e:
        raise HTTPException(status_code=502, detail=str(e))
    except Exception as e:
        logger.error("Generate text failed", error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")

@api_router.post("/generate/stream")
async def generate_text_stream(
    request_data: GenerateRequest,
    ai_service: AIService = Depends(get_ai_service),
):
    """流式生成文本内容"""
    try:
        # 创建 AI 请求
        ai_request = AIRequest(
            prompt=request_data.prompt,
            model=request_data.model,
            max_tokens=request_data.max_tokens,
            temperature=request_data.temperature,
            system_prompt=request_data.system_prompt,
            stream=True,
            user_id="api_user",
        )

        # 生成流式响应
        async def stream_generator():
            async for chunk in ai_service.process_streaming_request(ai_request):
                yield f"data: {chunk}\n\n"
            yield "data: [DONE]\n\n"

        return StreamingResponse(
            stream_generator(),
            media_type="text/plain",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
            },
        )

    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RateLimitError as e:
        raise HTTPException(
            status_code=429,
            detail={"error": "Rate limit exceeded", "retry_after": e.details.get("retry_after")},
        )
    except AIServiceError as e:
        raise HTTPException(status_code=502, detail=str(e))
    except Exception as e:
        logger.error("Stream generate text failed", error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")

# 批量生成端点
@api_router.post("/generate/batch", response_model=List[GenerateResponse])
async def generate_batch(
    requests: List[GenerateRequest],
    ai_service: AIService = Depends(get_ai_service),
):
    """批量生成文本内容"""
    try:
        if len(requests) > 10:
            raise ValidationError("Maximum 10 requests allowed per batch")

        # 创建 AI 请求列表
        ai_requests = []
        for req in requests:
            ai_requests.append(AIRequest(
                prompt=req.prompt,
                model=req.model,
                max_tokens=req.max_tokens,
                temperature=req.temperature,
                system_prompt=req.system_prompt,
                user_id="api_user",
            ))

        # 批量处理
        responses = await ai_service.batch_process(ai_requests)

        # 转换为响应模型
        generate_responses = []
        for response in responses:
            generate_responses.append(GenerateResponse(
                request_id=f"req_{uuid4().hex[:8]}",
                content=response.content,
                model_used=response.model_used,
                tokens_used=response.tokens_used,
                response_time_ms=response.response_time_ms,
                cost=response.cost,
            ))

        return generate_responses

    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except AIServiceError as e:
        raise HTTPException(status_code=502, detail=str(e))
    except Exception as e:
        logger.error("Batch generate failed", error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")

# 分析端点
@api_router.post("/analyze")
async def analyze_text(
    request_data: AnalysisRequest,
    ai_service: AIService = Depends(get_ai_service),
):
    """文本分析"""
    try:
        result = await ai_service.analyze_text(
            text=request_data.text,
            analysis_type=request_data.analysis_type,
            model=request_data.model,
        )

        return {
            "analysis_type": request_data.analysis_type,
            "result": result,
            "model_used": result.get("model_used", request_data.model),
        }

    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except AIServiceError as e:
        raise HTTPException(status_code=502, detail=str(e))
    except Exception as e:
        logger.error("Text analysis failed", error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")

# 翻译端点
@api_router.post("/translate")
async def translate_text(
    request_data: TranslateRequest,
    ai_service: AIService = Depends(get_ai_service),
):
    """文本翻译"""
    try:
        translated_text = await ai_service.translate_text(
            text=request_data.text,
            target_language=request_data.target_language,
            source_language=request_data.source_language,
            model=request_data.model,
        )

        return {
            "original_text": request_data.text,
            "translated_text": translated_text,
            "source_language": request_data.source_language,
            "target_language": request_data.target_language,
            "model_used": request_data.model,
        }

    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except AIServiceError as e:
        raise HTTPException(status_code=502, detail=str(e))
    except Exception as e:
        logger.error("Translation failed", error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")

# 代码生成端点
@api_router.post("/code/generate")
async def generate_code(
    request_data: CodeGenerationRequest,
    ai_service: AIService = Depends(get_ai_service),
):
    """代码生成"""
    try:
        code = await ai_service.generate_code(
            description=request_data.description,
            language=request_data.language,
            model=request_data.model,
        )

        return {
            "description": request_data.description,
            "language": request_data.language,
            "code": code,
            "model_used": request_data.model,
        }

    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except AIServiceError as e:
        raise HTTPException(status_code=502, detail=str(e))
    except Exception as e:
        logger.error("Code generation failed", error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")

# 对话相关端点
@api_router.post("/conversations", response_model=ConversationResponse)
async def create_conversation(
    request_data: ConversationRequest,
    conversation_service: ConversationService = Depends(get_conversation_service),
):
    """创建新对话"""
    try:
        conversation = await conversation_service.create_conversation(
            title=request_data.title,
            user_id=request_data.user_id,
        )

        return ConversationResponse(
            id=conversation.id,
            title=conversation.title,
            user_id=conversation.user_id,
            status=conversation.status,
            message_count=len(conversation.messages),
            total_tokens=conversation.total_tokens,
            created_at=conversation.created_at,
            updated_at=conversation.updated_at,
        )

    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error("Create conversation failed", error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")

@api_router.get("/conversations/{conversation_id}")
async def get_conversation(
    conversation_id: str,
    conversation_service: ConversationService = Depends(get_conversation_service),
):
    """获取对话详情"""
    try:
        conversation = await conversation_service.get_conversation(conversation_id)

        return {
            "id": conversation.id,
            "title": conversation.title,
            "user_id": conversation.user_id,
            "status": conversation.status,
            "messages": [
                {
                    "id": msg.id,
                    "role": msg.role,
                    "content": msg.content,
                    "timestamp": msg.timestamp,
                    "model_used": msg.model_used,
                    "token_count": msg.token_count,
                }
                for msg in conversation.messages
            ],
            "created_at": conversation.created_at,
            "updated_at": conversation.updated_at,
            "total_tokens": conversation.total_tokens,
            "estimated_cost": conversation.estimated_cost,
        }

    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error("Get conversation failed", error=str(e))
        raise HTTPException(status_code=404, detail="Conversation not found")

@api_router.get("/conversations")
async def list_conversations(
    user_id: Optional[str] = Query(None, description="用户 ID"),
    limit: int = Query(20, ge=1, le=100, description="返回数量限制"),
    offset: int = Query(0, ge=0, description="偏移量"),
    conversation_service: ConversationService = Depends(get_conversation_service),
):
    """列出对话"""
    try:
        conversations = await conversation_service.list_conversations(
            user_id=user_id,
            limit=limit,
            offset=offset,
        )

        return {
            "conversations": [
                {
                    "id": conv.id,
                    "title": conv.title,
                    "user_id": conv.user_id,
                    "status": conv.status,
                    "message_count": len(conv.messages),
                    "total_tokens": conv.total_tokens,
                    "created_at": conv.created_at,
                    "updated_at": conv.updated_at,
                }
                for conv in conversations
            ],
            "total": len(conversations),
            "limit": limit,
            "offset": offset,
        }

    except Exception as e:
        logger.error("List conversations failed", error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")

# 系统信息端点
@api_router.get("/models")
async def list_available_models(
    ai_service: AIService = Depends(get_ai_service),
):
    """获取可用模型列表"""
    try:
        # 这里应该从 AI 服务获取实际模型列表
        # 目前返回预定义的模型列表
        models = [
            {
                "id": "claude-3-5-sonnet-20241022",
                "name": "Claude 3.5 Sonnet",
                "provider": "anthropic",
                "description": "Most powerful model for complex tasks",
                "max_tokens": 200000,
                "capabilities": ["text", "analysis", "code"],
            },
            {
                "id": "claude-3-5-haiku-20241022",
                "name": "Claude 3.5 Haiku",
                "provider": "anthropic",
                "description": "Fast and efficient model for everyday tasks",
                "max_tokens": 200000,
                "capabilities": ["text", "analysis"],
            },
            {
                "id": "gpt-4o-mini",
                "name": "GPT-4o Mini",
                "provider": "openai",
                "description": "Fast and affordable model for most tasks",
                "max_tokens": 128000,
                "capabilities": ["text", "analysis", "code", "function_calling"],
            },
        ]

        return {"models": models}

    except Exception as e:
        logger.error("List models failed", error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")

@api_router.get("/stats")
async def get_service_stats(
    ai_service: AIService = Depends(get_ai_service),
):
    """获取服务统计信息"""
    try:
        stats = await ai_service.get_service_stats()
        return stats

    except Exception as e:
        logger.error("Get stats failed", error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")