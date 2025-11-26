"""
LLM API路由

提供大语言模型相关的API端点
"""

from typing import List, Optional, Dict, Any, AsyncGenerator
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from ...models.llm import Message, MessageRole, ModelResponse, LLMConfig
from ...services.factory import get_service_registry
from ...services.cost_optimizer import get_cost_optimizer
from ...utils.cost_tracking import track_cost


router = APIRouter()


class ChatRequest(BaseModel):
    """聊天请求模型"""
    messages: List[Dict[str, str]] = Field(..., description="对话消息列表")
    model: Optional[str] = Field(None, description="指定模型，如不指定则使用默认模型")
    temperature: Optional[float] = Field(0.7, description="温度参数", ge=0.0, le=2.0)
    max_tokens: Optional[int] = Field(2048, description="最大生成令牌数")
    stream: bool = Field(False, description="是否流式输出")
    top_p: Optional[float] = Field(1.0, description="Top-p参数", ge=0.0, le=1.0)
    top_k: Optional[int] = Field(None, description="Top-k参数")
    stop: Optional[List[str]] = Field(None, description="停止词")
    presence_penalty: float = Field(0.0, description="存在惩罚", ge=-2.0, le=2.0)
    frequency_penalty: float = Field(0.0, description="频率惩罚", ge=-2.0, le=2.0)


class ChatResponse(BaseModel):
    """聊天响应模型"""
    content: str
    model: str
    usage: Dict[str, int]
    finish_reason: Optional[str] = None
    created: float


class ModelInfo(BaseModel):
    """模型信息"""
    id: str
    name: str
    provider: str
    type: str
    max_tokens: int
    context_window: int
    pricing: Dict[str, float]


class ModelSelectionRequest(BaseModel):
    """模型选择请求"""
    task_type: str = Field(..., description="任务类型")
    complexity: str = Field("medium", description="任务复杂度: low, medium, high")
    quality_requirement: float = Field(0.8, description="质量要求", ge=0.0, le=1.0)
    cost_sensitivity: float = Field(0.5, description="成本敏感度", ge=0.0, le=1.0)


def convert_messages(messages: List[Dict[str, str]]) -> List[Message]:
    """转换消息格式"""
    converted = []
    for msg in messages:
        role = MessageRole(msg.get("role", "user"))
        content = msg.get("content", "")
        name = msg.get("name")
        converted.append(Message(role=role, content=content, name=name))
    return converted


@router.post("/chat", response_model=ChatResponse)
async def chat_completion(
    request: ChatRequest,
    background_tasks: BackgroundTasks
):
    """聊天完成接口"""
    try:
        service_registry = get_service_registry()
        cost_optimizer = get_cost_optimizer()

        # 获取LLM服务
        llm_service = service_registry.get_service("llm")
        if not llm_service:
            raise HTTPException(status_code=503, detail="LLM service not available")

        # 转换消息格式
        messages = convert_messages(request.messages)

        # 选择模型
        if request.model:
            model_name = request.model
        else:
            # 使用成本优化器选择最优模型
            model_name, _ = cost_optimizer.select_optimal_model(
                service_type="llm",
                quality_requirement=request.temperature < 0.5,
                cost_sensitivity=1.0 - request.temperature
            )

        # 生成响应
        response = await llm_service.generate(
            messages=messages,
            model=model_name,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            top_p=request.top_p,
            top_k=request.top_k,
            stop=request.stop,
            presence_penalty=request.presence_penalty,
            frequency_penalty=request.frequency_penalty,
            stream=request.stream
        )

        # 记录成本（后台任务）
        background_tasks.add_task(
            cost_optimizer.record_cost,
            service_type="llm",
            model_name=model_name,
            input_tokens=response.usage.get("prompt_tokens", 0),
            output_tokens=response.usage.get("completion_tokens", 0),
            requests_count=1
        )

        return ChatResponse(
            content=response.content,
            model=response.model,
            usage=response.usage,
            finish_reason=response.finish_reason,
            created=response.created
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/chat/stream")
async def chat_completion_stream(
    request: ChatRequest,
    background_tasks: BackgroundTasks
):
    """流式聊天完成接口"""
    try:
        service_registry = get_service_registry()
        cost_optimizer = get_cost_optimizer()

        # 获取LLM服务
        llm_service = service_registry.get_service("llm")
        if not llm_service:
            raise HTTPException(status_code=503, detail="LLM service not available")

        # 转换消息格式
        messages = convert_messages(request.messages)

        # 选择模型
        model_name = request.model or "gpt-3.5-turbo"

        async def generate():
            try:
                token_count = 0
                async for chunk in llm_service.generate_stream(
                    messages=messages,
                    model=model_name,
                    temperature=request.temperature,
                    max_tokens=request.max_tokens,
                    top_p=request.top_p,
                    top_k=request.top_k,
                    stop=request.stop,
                    presence_penalty=request.presence_penalty,
                    frequency_penalty=request.frequency_penalty
                ):
                    token_count += len(chunk.split())  # 简化的token计算
                    yield f"data: {chunk}\n\n"

                # 记录成本
                background_tasks.add_task(
                    cost_optimizer.record_cost,
                    service_type="llm",
                    model_name=model_name,
                    input_tokens=sum(len(m.content.split()) for m in messages),
                    output_tokens=token_count,
                    requests_count=1
                )

                yield "data: [DONE]\n\n"

            except Exception as e:
                yield f"data: ERROR: {str(e)}\n\n"

        return StreamingResponse(
            generate(),
            media_type="text/plain",
            headers={"Cache-Control": "no-cache", "Connection": "keep-alive"}
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/models", response_model=List[ModelInfo])
async def list_models():
    """列出可用模型"""
    try:
        service_registry = get_service_registry()

        # 获取所有LLM提供商
        models = []
        llm_providers = service_registry.get_service("llm_providers")
        if llm_providers:
            for provider_name, provider in llm_providers.items():
                # 这里需要根据具体的提供商实现来获取模型信息
                models.append(ModelInfo(
                    id=provider_name,
                    name=provider_name,
                    provider=provider_name,
                    type="text_generation",
                    max_tokens=4096,
                    context_window=4096,
                    pricing={"input": 0.001, "output": 0.002}
                ))

        return models

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/models/select", response_model=Dict[str, Any])
async def select_optimal_model(request: ModelSelectionRequest):
    """选择最优模型"""
    try:
        cost_optimizer = get_cost_optimizer()

        model_name, model_tier = cost_optimizer.select_optimal_model(
            service_type="llm",
            task_complexity=request.complexity,
            quality_requirement=request.quality_requirement,
            cost_sensitivity=request.cost_sensitivity
        )

        return {
            "recommended_model": model_name,
            "model_tier": model_tier.value,
            "reasoning": f"Selected based on task type '{request.task_type}', complexity '{request.complexity}', and quality requirement {request.quality_requirement}"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/models/{model_id}")
async def get_model_info(model_id: str):
    """获取特定模型信息"""
    try:
        service_registry = get_service_registry()

        # 这里应该从服务注册表中获取模型信息
        # 简化实现
        return ModelInfo(
            id=model_id,
            name=model_id,
            provider="openai",
            type="text_generation",
            max_tokens=4096,
            context_window=4096,
            pricing={"input": 0.001, "output": 0.002}
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/models/{model_id}")
async def delete_model(model_id: str):
    """删除模型（如果支持）"""
    try:
        # 这里应该实现模型删除逻辑
        return {"message": f"Model {model_id} deleted successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/models/{model_id}/test")
async def test_model(
    model_id: str,
    test_message: str = "Hello, how are you?"
):
    """测试模型"""
    try:
        service_registry = get_service_registry()
        llm_service = service_registry.get_service("llm")
        if not llm_service:
            raise HTTPException(status_code=503, detail="LLM service not available")

        # 创建测试消息
        messages = [
            Message(role=MessageRole.USER, content=test_message)
        ]

        # 测试模型
        start_time = time.time()
        response = await llm_service.generate(messages, model=model_id)
        response_time = time.time() - start_time

        return {
            "model_id": model_id,
            "test_message": test_message,
            "response": response.content,
            "response_time": response_time,
            "usage": response.usage,
            "status": "success"
        }

    except Exception as e:
        return {
            "model_id": model_id,
            "test_message": test_message,
            "error": str(e),
            "status": "failed"
        }


@router.get("/usage")
async def get_usage_statistics():
    """获取使用统计"""
    try:
        cost_optimizer = get_cost_optimizer()
        cost_summary = cost_optimizer.get_cost_summary()

        return {
            "usage": cost_summary,
            "timestamp": time.time()
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# 导入time模块
import time