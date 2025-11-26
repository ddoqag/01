"""
基础使用示例 - 展示 AI 集成平台的基本用法
"""

import asyncio
from datetime import datetime, UTC

from src.ai_platform.core.models import AIRequest, AIResponse, Conversation, Message
from src.ai_platform.ai.manager import AIManager
from src.ai_platform.services import AIService, ConversationService


async def basic_ai_generation():
    """基础 AI 文本生成示例"""
    print("=== 基础 AI 文本生成 ===")

    # 创建 AI 服务
    ai_service = AIService()
    await ai_service.initialize()

    try:
        # 创建请求
        request = AIRequest(
            prompt="写一首关于春天的简短诗",
            model="claude-3-haiku-20240307",
            max_tokens=200,
            temperature=0.8,
            user_id="demo-user",
        )

        # 生成响应
        response = await ai_service.process_request(request)

        print(f"模型: {response.model_used}")
        print(f"内容: {response.content}")
        print(f"令牌数: {response.tokens_used}")
        print(f"响应时间: {response.response_time_ms}ms")
        print(f"成本: ${response.cost:.6f}")

    finally:
        await ai_service.cleanup()


async def streaming_generation():
    """流式生成示例"""
    print("\n=== 流式生成示例 ===")

    ai_service = AIService()
    await ai_service.initialize()

    try:
        request = AIRequest(
            prompt="解释什么是机器学习，从基本概念开始",
            model="claude-3-haiku-20240307",
            stream=True,
            user_id="demo-user",
        )

        print("AI 回答（实时流式输出）:")
        print("-" * 40)

        async for chunk in ai_service.process_streaming_request(request):
            print(chunk, end="", flush=True)

        print("\n" + "-" * 40)

    finally:
        await ai_service.cleanup()


async def conversation_management():
    """对话管理示例"""
    print("\n=== 对话管理示例 ===")

    # 创建服务
    ai_service = AIService()
    conversation_service = ConversationService()

    await ai_service.initialize()
    await conversation_service.initialize()

    try:
        # 创建新对话
        conversation = await conversation_service.create_conversation(
            title="机器学习讨论",
            user_id="demo-user",
        )

        print(f"创建对话: {conversation.title} (ID: {conversation.id})")

        # 第一次对话
        request1 = AIRequest(
            prompt="什么是监督学习？",
            model="claude-3-haiku-20240307",
            user_id="demo-user",
            conversation_id=conversation.id,
        )

        response1 = await ai_service.process_request(request1, conversation)
        print(f"用户: {request1.prompt}")
        print(f"AI: {response1.content}")

        # 第二次对话（上下文相关）
        request2 = AIRequest(
            prompt="能给我一个具体的例子吗？",
            model="claude-3-haiku-20240307",
            user_id="demo-user",
            conversation_id=conversation.id,
        )

        response2 = await ai_service.process_request(request2, conversation)
        print(f"用户: {request2.prompt}")
        print(f"AI: {response2.content}")

        # 显示对话统计
        print(f"\n对话统计:")
        print(f"消息数: {len(conversation.messages)}")
        print(f"总令牌数: {conversation.total_tokens}")
        print(f"估算成本: ${conversation.estimated_cost:.6f}")

        # 保存对话
        await conversation_service.save_conversation(conversation)
        print("对话已保存")

    finally:
        await ai_service.cleanup()
        await conversation_service.cleanup()


async def text_analysis_example():
    """文本分析示例"""
    print("\n=== 文本分析示例 ===")

    ai_service = AIService()
    await ai_service.initialize()

    try:
        text = """
        我最近购买了这个产品，非常满意！质量很好，包装也很精美。
        客服服务态度很棒，物流速度很快。强烈推荐给朋友们。
        """

        print(f"分析文本: {text.strip()}")

        # 情感分析
        sentiment_result = await ai_service.analyze_text(
            text=text,
            analysis_type="sentiment",
            user_id="demo-user",
        )
        print(f"\n情感分析结果:")
        print(f"结果: {sentiment_result}")

        # 实体提取
        entities_result = await ai_service.analyze_text(
            text=text,
            analysis_type="entities",
            user_id="demo-user",
        )
        print(f"\n实体提取结果:")
        print(f"结果: {entities_result}")

        # 关键词提取
        keywords_result = await ai_service.analyze_text(
            text=text,
            analysis_type="keywords",
            user_id="demo-user",
        )
        print(f"\n关键词提取结果:")
        print(f"结果: {keywords_result}")

    finally:
        await ai_service.cleanup()


async def translation_example():
    """翻译示例"""
    print("\n=== 翻译示例 ===")

    ai_service = AIService()
    await ai_service.initialize()

    try:
        text = "Hello, how are you doing today?"
        print(f"原文 (英语): {text}")

        # 翻译为中文
        translated = await ai_service.translate_text(
            text=text,
            target_language="中文",
            source_language="English",
            user_id="demo-user",
        )
        print(f"翻译 (中文): {translated}")

        # 翻译为西班牙语
        spanish = await ai_service.translate_text(
            text=text,
            target_language="Spanish",
            source_language="English",
            user_id="demo-user",
        )
        print(f"翻译 (西班牙语): {spanish}")

    finally:
        await ai_service.cleanup()


async def code_generation_example():
    """代码生成示例"""
    print("\n=== 代码生成示例 ===")

    ai_service = AIService()
    await ai_service.initialize()

    try:
        description = "创建一个计算斐波那契数列的 Python 函数，包含文档字符串和错误处理"
        print(f"需求描述: {description}")

        code = await ai_service.generate_code(
            description=description,
            language="python",
            user_id="demo-user",
        )

        print(f"\n生成的代码:")
        print("-" * 50)
        print(code)
        print("-" * 50)

    finally:
        await ai_service.cleanup()


async def batch_processing_example():
    """批量处理示例"""
    print("\n=== 批量处理示例 ===")

    ai_service = AIService()
    await ai_service.initialize()

    try:
        # 创建多个请求
        requests = [
            AIRequest(
                prompt="什么是人工智能？",
                model="claude-3-haiku-20240307",
                max_tokens=100,
                user_id="demo-user",
            ),
            AIRequest(
                prompt="什么是机器学习？",
                model="claude-3-haiku-20240307",
                max_tokens=100,
                user_id="demo-user",
            ),
            AIRequest(
                prompt="什么是深度学习？",
                model="claude-3-haiku-20240307",
                max_tokens=100,
                user_id="demo-user",
            ),
        ]

        print(f"处理 {len(requests)} 个并发请求...")

        # 批量处理
        start_time = datetime.now(UTC)
        responses = await ai_service.batch_process(requests, max_concurrent=3)
        end_time = datetime.now(UTC)

        processing_time = (end_time - start_time).total_seconds()
        print(f"处理完成，耗时: {processing_time:.2f} 秒")

        # 显示结果
        for i, response in enumerate(responses):
            print(f"\n请求 {i+1}:")
            print(f"内容: {response.content[:100]}...")
            print(f"令牌数: {response.tokens_used}")
            print(f"响应时间: {response.response_time_ms}ms")

    finally:
        await ai_service.cleanup()


async def main():
    """主函数"""
    print("AI 集成平台基础使用示例")
    print("=" * 50)

    try:
        # 运行各种示例
        await basic_ai_generation()
        await streaming_generation()
        await conversation_management()
        await text_analysis_example()
        await translation_example()
        await code_generation_example()
        await batch_processing_example()

    except Exception as e:
        print(f"示例运行出错: {e}")
        import traceback
        traceback.print_exc()

    print("\n" + "=" * 50)
    print("所有示例运行完成！")


if __name__ == "__main__":
    # 运行示例
    asyncio.run(main())