"""
API 端点集成测试 - 展示现代 Web API 测试
"""

import json
import pytest
from httpx import AsyncClient

from src.ai_platform.core.models import AIRequest


class TestGenerateEndpoints:
    """生成端点测试"""

    @pytest.mark.asyncio
    async def test_generate_text_success(self, client: AsyncClient) -> None:
        """测试成功生成文本"""
        request_data = {
            "prompt": "Hello, how are you?",
            "model": "claude-3-haiku-20240307",
            "max_tokens": 100,
            "temperature": 0.7,
            "user_id": "test-user-123",
        }

        response = await client.post("/api/v1/generate", json=request_data)

        assert response.status_code == 200
        data = response.json()

        assert "content" in data
        assert "model_used" in data
        assert "tokens_used" in data
        assert "response_time_ms" in data
        assert "request_id" in data
        assert "cost" in data

        assert isinstance(data["tokens_used"], int)
        assert data["tokens_used"] >= 0
        assert isinstance(data["response_time_ms"], int)
        assert data["response_time_ms"] > 0

    @pytest.mark.asyncio
    async def test_generate_text_with_system_prompt(self, client: AsyncClient) -> None:
        """测试带系统提示的文本生成"""
        request_data = {
            "prompt": "What is the capital of France?",
            "system_prompt": "You are a helpful geography expert.",
            "model": "claude-3-haiku-20240307",
            "user_id": "test-user",
        }

        response = await client.post("/api/v1/generate", json=request_data)

        assert response.status_code == 200
        data = response.json()
        assert "content" in data
        assert len(data["content"]) > 0

    @pytest.mark.asyncio
    async def test_generate_text_validation_error(self, client: AsyncClient) -> None:
        """测试生成文本验证错误"""
        # 空提示
        request_data = {
            "prompt": "",
            "model": "claude-3-haiku-20240307",
            "user_id": "test-user",
        }

        response = await client.post("/api/v1/generate", json=request_data)

        assert response.status_code == 400
        error_data = response.json()
        assert "detail" in error_data

    @pytest.mark.asyncio
    async def test_generate_text_temperature_validation(self, client: AsyncClient) -> None:
        """测试温度参数验证"""
        request_data = {
            "prompt": "Hello",
            "temperature": 3.0,  # 超出范围
            "model": "claude-3-haiku-20240307",
            "user_id": "test-user",
        }

        response = await client.post("/api/v1/generate", json=request_data)

        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_generate_streaming_response(self, client: AsyncClient) -> None:
        """测试流式响应生成"""
        request_data = {
            "prompt": "Tell me a short story",
            "model": "claude-3-haiku-20240307",
            "stream": True,
            "user_id": "test-user",
        }

        response = await client.post("/api/v1/generate/stream", json=request_data)

        assert response.status_code == 200
        assert response.headers["content-type"] == "text/plain; charset=utf-8"

        # 读取流式响应
        content = response.text
        assert "data: " in content
        assert "[DONE]" in content

    @pytest.mark.asyncio
    async def test_batch_generate(self, client: AsyncClient) -> None:
        """测试批量生成"""
        requests = [
            {
                "prompt": "What is 2+2?",
                "model": "claude-3-haiku-20240307",
                "user_id": "test-user",
            },
            {
                "prompt": "What is the capital of Spain?",
                "model": "claude-3-haiku-20240307",
                "user_id": "test-user",
            },
        ]

        response = await client.post("/api/v1/generate/batch", json=requests)

        assert response.status_code == 200
        data = response.json()

        assert isinstance(data, list)
        assert len(data) == 2

        for item in data:
            assert "content" in item
            assert "request_id" in item
            assert "tokens_used" in item


class TestAnalysisEndpoints:
    """分析端点测试"""

    @pytest.mark.asyncio
    async def test_sentiment_analysis(self, client: AsyncClient) -> None:
        """测试情感分析"""
        request_data = {
            "text": "I love this product! It's amazing and works perfectly.",
            "analysis_type": "sentiment",
            "model": "claude-3-haiku-20240307",
        }

        response = await client.post("/api/v1/analyze", json=request_data)

        assert response.status_code == 200
        data = response.json()

        assert "analysis_type" in data
        assert "result" in data
        assert "model_used" in data

        assert data["analysis_type"] == "sentiment"

    @pytest.mark.asyncio
    async def test_entity_extraction(self, client: AsyncClient) -> None:
        """测试实体提取"""
        request_data = {
            "text": "Apple Inc. is headquartered in Cupertino, California. Tim Cook is the CEO.",
            "analysis_type": "entities",
            "model": "claude-3-haiku-20240307",
        }

        response = await client.post("/api/v1/analyze", json=request_data)

        assert response.status_code == 200
        data = response.json()

        assert "result" in data
        assert data["analysis_type"] == "entities"

    @pytest.mark.asyncio
    async def test_text_summarization(self, client: AsyncClient) -> None:
        """测试文本摘要"""
        long_text = """
        Artificial intelligence (AI) is intelligence demonstrated by machines, in contrast to the natural intelligence
        displayed by humans and animals. Leading AI textbooks define the field as the study of "intelligent agents":
        any device that perceives its environment and takes actions that maximize its chance of successfully achieving
        its goals. Colloquially, the term "artificial intelligence" is often used to describe machines that mimic
        "cognitive" functions that humans associate with the human mind, such as "learning" and "problem solving".
        """

        request_data = {
            "text": long_text,
            "analysis_type": "summary",
            "model": "claude-3-haiku-20240307",
        }

        response = await client.post("/api/v1/analyze", json=request_data)

        assert response.status_code == 200
        data = response.json()

        assert "result" in data
        assert data["analysis_type"] == "summary"

    @pytest.mark.asyncio
    async def test_invalid_analysis_type(self, client: AsyncClient) -> None:
        """测试无效分析类型"""
        request_data = {
            "text": "Test text",
            "analysis_type": "invalid_type",
            "model": "claude-3-haiku-20240307",
        }

        response = await client.post("/api/v1/analyze", json=request_data)

        assert response.status_code == 400
        error_data = response.json()
        assert "detail" in error_data


class TestTranslationEndpoints:
    """翻译端点测试"""

    @pytest.mark.asyncio
    async def test_translate_text(self, client: AsyncClient) -> None:
        """测试文本翻译"""
        request_data = {
            "text": "Hello, how are you?",
            "target_language": "Spanish",
            "source_language": "English",
            "model": "gpt-4o-mini",
        }

        response = await client.post("/api/v1/translate", json=request_data)

        assert response.status_code == 200
        data = response.json()

        assert "original_text" in data
        assert "translated_text" in data
        assert "source_language" in data
        assert "target_language" in data
        assert "model_used" in data

        assert data["original_text"] == "Hello, how are you?"
        assert data["target_language"] == "Spanish"
        assert data["source_language"] == "English"
        assert len(data["translated_text"]) > 0

    @pytest.mark.asyncio
    async def test_translate_with_auto_source(self, client: AsyncClient) -> None:
        """测试自动检测源语言翻译"""
        request_data = {
            "text": "Bonjour, comment allez-vous?",
            "target_language": "English",
            "model": "gpt-4o-mini",
        }

        response = await client.post("/api/v1/translate", json=request_data)

        assert response.status_code == 200
        data = response.json()

        assert data["source_language"] == "auto"
        assert data["target_language"] == "English"


class TestCodeGenerationEndpoints:
    """代码生成端点测试"""

    @pytest.mark.asyncio
    async def test_generate_python_code(self, client: AsyncClient) -> None:
        """测试 Python 代码生成"""
        request_data = {
            "description": "Create a function that calculates the factorial of a number recursively",
            "language": "python",
            "model": "claude-3-5-sonnet-20241022",
        }

        response = await client.post("/api/v1/code/generate", json=request_data)

        assert response.status_code == 200
        data = response.json()

        assert "description" in data
        assert "language" in data
        assert "code" in data
        assert "model_used" in data

        assert data["language"] == "python"
        assert len(data["code"]) > 0
        # 检查是否包含 Python 代码特征
        assert "def" in data["code"] or "factorial" in data["code"].lower()

    @pytest.mark.asyncio
    async def test_generate_javascript_code(self, client: AsyncClient) -> None:
        """测试 JavaScript 代码生成"""
        request_data = {
            "description": "Create a function that sorts an array of numbers in ascending order",
            "language": "javascript",
            "model": "claude-3-5-sonnet-20241022",
        }

        response = await client.post("/api/v1/code/generate", json=request_data)

        assert response.status_code == 200
        data = response.json()

        assert data["language"] == "javascript"
        assert len(data["code"]) > 0
        # 检查是否包含 JavaScript 代码特征
        assert "function" in data["code"] or "const" in data["code"]

    @pytest.mark.asyncio
    async def test_invalid_code_description(self, client: AsyncClient) -> None:
        """测试无效的代码描述"""
        request_data = {
            "description": "",  # 空描述
            "language": "python",
            "model": "claude-3-5-sonnet-20241022",
        }

        response = await client.post("/api/v1/code/generate", json=request_data)

        assert response.status_code == 422  # Validation error


class TestConversationEndpoints:
    """对话端点测试"""

    @pytest.mark.asyncio
    async def test_create_conversation(self, client: AsyncClient) -> None:
        """测试创建对话"""
        request_data = {
            "title": "Test Conversation",
            "user_id": "test-user-123",
        }

        response = await client.post("/api/v1/conversations", json=request_data)

        assert response.status_code == 200
        data = response.json()

        assert "id" in data
        assert "title" in data
        assert "user_id" in data
        assert "status" in data
        assert "message_count" in data
        assert "total_tokens" in data
        assert "created_at" in data
        assert "updated_at" in data

        assert data["title"] == "Test Conversation"
        assert data["user_id"] == "test-user-123"
        assert data["status"] == "active"
        assert data["message_count"] == 0
        assert data["total_tokens"] == 0

    @pytest.mark.asyncio
    async def test_list_conversations(self, client: AsyncClient) -> None:
        """测试列出对话"""
        # 首先创建一些对话
        for i in range(3):
            request_data = {
                "title": f"Test Conversation {i}",
                "user_id": f"test-user-{i}",
            }
            await client.post("/api/v1/conversations", json=request_data)

        # 列出对话
        response = await client.get("/api/v1/conversations")

        assert response.status_code == 200
        data = response.json()

        assert "conversations" in data
        assert "total" in data
        assert "limit" in data
        assert "offset" in data

        assert isinstance(data["conversations"], list)
        assert len(data["conversations"]) >= 0

    @pytest.mark.asyncio
    async def test_list_conversations_with_filters(self, client: AsyncClient) -> None:
        """测试带过滤器的对话列表"""
        # 创建特定用户的对话
        user_id = "filter-test-user"
        request_data = {
            "title": "Filtered Conversation",
            "user_id": user_id,
        }
        await client.post("/api/v1/conversations", json=request_data)

        # 按用户 ID 过滤
        response = await client.get(f"/api/v1/conversations?user_id={user_id}")

        assert response.status_code == 200
        data = response.json()

        # 所有返回的对话都应该属于指定用户
        for conv in data["conversations"]:
            assert conv["user_id"] == user_id

    @pytest.mark.asyncio
    async def test_get_conversation_details(self, client: AsyncClient) -> None:
        """测试获取对话详情"""
        # 创建对话
        create_request = {
            "title": "Detailed Conversation",
            "user_id": "test-user",
        }
        create_response = await client.post("/api/v1/conversations", json=create_request)
        conversation_data = create_response.json()
        conversation_id = conversation_data["id"]

        # 获取对话详情
        response = await client.get(f"/api/v1/conversations/{conversation_id}")

        assert response.status_code == 200
        data = response.json()

        assert data["id"] == conversation_id
        assert data["title"] == "Detailed Conversation"
        assert data["user_id"] == "test-user"
        assert "messages" in data
        assert isinstance(data["messages"], list)

    @pytest.mark.asyncio
    async def test_get_nonexistent_conversation(self, client: AsyncClient) -> None:
        """测试获取不存在的对话"""
        fake_id = "nonexistent-conversation-id"
        response = await client.get(f"/api/v1/conversations/{fake_id}")

        assert response.status_code == 404


class TestSystemEndpoints:
    """系统端点测试"""

    @pytest.mark.asyncio
    async def test_list_models(self, client: AsyncClient) -> None:
        """测试列出可用模型"""
        response = await client.get("/api/v1/models")

        assert response.status_code == 200
        data = response.json()

        assert "models" in data
        assert isinstance(data["models"], list)
        assert len(data["models"]) > 0

        # 检查模型数据结构
        for model in data["models"]:
            assert "id" in model
            assert "name" in model
            assert "provider" in model
            assert "description" in model
            assert "capabilities" in model
            assert isinstance(model["capabilities"], list)

    @pytest.mark.asyncio
    async def test_get_service_stats(self, client: AsyncClient) -> None:
        """测试获取服务统计"""
        response = await client.get("/api/v1/stats")

        assert response.status_code == 200
        data = response.json()

        assert "cache_size" in data
        assert "rate_limited_users" in data
        assert "ai_provider_stats" in data
        assert "timestamp" in data

    @pytest.mark.asyncio
    async def test_health_check(self, client: AsyncClient) -> None:
        """测试健康检查"""
        response = await client.get("/health")

        assert response.status_code == 200
        data = response.json()

        assert "status" in data
        assert "version" in data
        assert "services" in data
        assert "timestamp" in data

        assert data["status"] in ["healthy", "unhealthy", "degraded"]
        assert "ai_service" in data["services"]
        assert "conversation_service" in data["services"]

    @pytest.mark.asyncio
    async def test_root_endpoint(self, client: AsyncClient) -> None:
        """测试根端点"""
        response = await client.get("/")

        assert response.status_code == 200
        data = response.json()

        assert "message" in data
        assert "version" in data
        assert "environment" in data
        assert "health_url" in data


class TestErrorHandling:
    """错误处理测试"""

    @pytest.mark.asyncio
    async def test_404_endpoint(self, client: AsyncClient) -> None:
        """测试 404 错误"""
        response = await client.get("/api/v1/nonexistent")

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_invalid_json(self, client: AsyncClient) -> None:
        """测试无效 JSON"""
        response = await client.post(
            "/api/v1/generate",
            content="invalid json content",
            headers={"Content-Type": "application/json"},
        )

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_missing_required_fields(self, client: AsyncClient) -> None:
        """测试缺少必需字段"""
        # 缺少必需的 prompt 字段
        request_data = {
            "model": "claude-3-haiku-20240307",
            "user_id": "test-user",
        }

        response = await client.post("/api/v1/generate", json=request_data)

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_method_not_allowed(self, client: AsyncClient) -> None:
        """测试不允许的 HTTP 方法"""
        response = await client.delete("/api/v1/generate")

        assert response.status_code == 405


@pytest.mark.slow
class TestPerformanceEndpoints:
    """性能测试端点"""

    @pytest.mark.asyncio
    async def test_concurrent_requests(self, client: AsyncClient) -> None:
        """测试并发请求"""
        import asyncio

        request_data = {
            "prompt": "Say hello",
            "model": "claude-3-haiku-20240307",
            "user_id": "perf-test-user",
        }

        # 发送 10 个并发请求
        async def make_request():
            response = await client.post("/api/v1/generate", json=request_data)
            return response

        tasks = [make_request() for _ in range(10)]
        responses = await asyncio.gather(*tasks, return_exceptions=True)

        # 检查所有响应
        for response in responses:
            if isinstance(response, Exception):
                pytest.fail(f"Concurrent request failed: {response}")

            assert response.status_code == 200
            data = response.json()
            assert "content" in data