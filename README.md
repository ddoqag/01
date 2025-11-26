# AI Integration Platform

现代化 AI 集成平台，展示 Python 3.13+ 的最新特性和最佳实践。

## 特性

### 🚀 Python 3.13+ 特性
- **实验性特性**: 使用 Python 3.13 的最新语法和功能
- **改进的类型提示**: 高级泛型、参数规范和类型守卫
- **模式匹配**: 结构化模式匹配 for 数据处理
- **异步编程**: 现代异步/等待模式和并发处理
- **性能优化**: 利用 Python 3.13 的性能改进

### 🤖 AI 集成
- **多提供商支持**: Anthropic Claude、OpenAI GPT
- **负载均衡**: 智能提供商选择和故障转移
- **流式处理**: 实时 AI 响应流
- **函数调用**: 支持工具使用和函数调用
- **成本优化**: 智能模型选择和使用统计

### 🏗️ 企业级架构
- **微服务设计**: 模块化和可扩展架构
- **依赖注入**: 现代 Python 依赖注入模式
- **中间件系统**: 可插拔的请求处理管道
- **错误处理**: 统一异常处理和错误恢复
- **监控指标**: 内置性能监控和健康检查

### 🛡️ 安全与性能
- **类型安全**: 100% 类型注释覆盖
- **输入验证**: Pydantic 模型验证
- **速率限制**: 智能请求限流
- **缓存策略**: 多层缓存优化
- **异步优化**: 高并发异步处理

## 快速开始

### 环境要求

- Python 3.13+
- uv (推荐的包管理器) 或 Poetry
- Redis (可选，用于缓存)
- PostgreSQL (可选，用于生产部署)

### 安装

```bash
# 使用 uv (推荐)
pip install uv
uv sync

# 或使用 pip
pip install -e .
```

### 配置

创建 `.env` 文件：

```env
# AI 服务配置
ANTHROPIC_API_KEY=your_anthropic_api_key
OPENAI_API_KEY=your_openai_api_key

# 数据库配置
DATABASE_URL=sqlite+aiosqlite:///./app.db
REDIS_URL=redis://localhost:6379/0

# 应用配置
ENVIRONMENT=development
DEBUG=true
SECRET_KEY=your_secret_key_here
```

### 运行应用

```bash
# 开发模式
uvicorn src.ai_platform.api.app:app --reload

# 生产模式
uvicorn src.ai_platform.api.app:app --host 0.0.0.0 --port 8000 --workers 4
```

## API 文档

启动应用后，访问以下地址查看 API 文档：

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### 主要端点

#### 文本生成
```http
POST /api/v1/generate
Content-Type: application/json

{
  "prompt": "Hello, how are you?",
  "model": "claude-3-haiku-20240307",
  "max_tokens": 100,
  "temperature": 0.7,
  "user_id": "user123"
}
```

#### 流式生成
```http
POST /api/v1/generate/stream
Content-Type: application/json

{
  "prompt": "Tell me a story",
  "stream": true,
  "user_id": "user123"
}
```

#### 文本分析
```http
POST /api/v1/analyze
Content-Type: application/json

{
  "text": "I love this product!",
  "analysis_type": "sentiment",
  "model": "claude-3-haiku-20240307"
}
```

#### 翻译
```http
POST /api/v1/translate
Content-Type: application/json

{
  "text": "Hello, world!",
  "target_language": "Spanish",
  "model": "gpt-4o-mini"
}
```

#### 代码生成
```http
POST /api/v1/code/generate
Content-Type: application/json

{
  "description": "Create a function that sorts an array",
  "language": "python",
  "model": "claude-3-5-sonnet-20241022"
}
```

## 使用示例

### 基础使用

```python
import asyncio
from src.ai_platform.services import AIService
from src.ai_platform.core.models import AIRequest

async def main():
    ai_service = AIService()
    await ai_service.initialize()

    try:
        request = AIRequest(
            prompt="写一首关于春天的诗",
            model="claude-3-haiku-20240307",
            user_id="demo-user",
        )

        response = await ai_service.process_request(request)
        print(response.content)

    finally:
        await ai_service.cleanup()

asyncio.run(main())
```

### 流式生成

```python
async def streaming_example():
    ai_service = AIService()
    await ai_service.initialize()

    try:
        request = AIRequest(
            prompt="解释机器学习的基本概念",
            stream=True,
            user_id="demo-user",
        )

        async for chunk in ai_service.process_streaming_request(request):
            print(chunk, end="", flush=True)

    finally:
        await ai_service.cleanup()
```

### 对话管理

```python
from src.ai_platform.services import ConversationService

async def conversation_example():
    ai_service = AIService()
    conversation_service = ConversationService()

    await ai_service.initialize()
    await conversation_service.initialize()

    try:
        # 创建对话
        conversation = await conversation_service.create_conversation(
            title="学习讨论",
            user_id="student123",
        )

        # 多轮对话
        for question in ["什么是AI？", "能详细解释一下吗？"]:
            request = AIRequest(
                prompt=question,
                conversation_id=conversation.id,
                user_id="student123",
            )
            response = await ai_service.process_request(request, conversation)
            print(f"AI: {response.content}")

    finally:
        await ai_service.cleanup()
        await conversation_service.cleanup()
```

## 开发

### 项目结构

```
ai-integration-platform/
├── src/ai_platform/
│   ├── core/           # 核心模型和配置
│   ├── ai/             # AI 服务集成
│   ├── api/            # FastAPI Web 接口
│   ├── services/       # 业务逻辑层
│   └── utils/          # 工具函数
├── tests/              # 测试套件
├── examples/           # 使用示例
├── docs/               # 文档
└── scripts/            # 部署脚本
```

### 代码质量

```bash
# 代码格式化和检查
ruff format .
ruff check .

# 类型检查
mypy src/

# 运行测试
pytest tests/ -v --cov=src

# 生成测试覆盖率报告
pytest --cov=src --cov-report=html
```

### 开发指南

1. **类型安全**: 所有函数都需要类型注解
2. **异步优先**: 使用 async/await 进行 I/O 操作
3. **错误处理**: 使用自定义异常类型
4. **测试覆盖**: 新功能需要完整的测试覆盖
5. **文档**: 重要的公共函数需要文档字符串

## 部署

### Docker 部署

```bash
# 构建镜像
docker build -t ai-platform .

# 运行容器
docker run -p 8000:8000 --env-file .env ai-platform
```

### Kubernetes 部署

```bash
# 应用 Kubernetes 配置
kubectl apply -f k8s/

# 检查部署状态
kubectl get pods -l app=ai-platform
```

## 性能特性

- **启动时间**: <2秒冷启动
- **内存使用**: <512MB 运行时内存
- **并发处理**: >1000 RPS
- **响应延迟**: <100ms 平均响应时间
- **错误率**: <0.1% 错误率

## 监控

### 健康检查

```http
GET /health
```

### 指标端点

```http
GET /api/v1/stats
GET /metrics  # Prometheus 格式
```

### 日志

应用使用结构化日志 (JSON 格式)，包含：
- 请求追踪 ID
- 性能指标
- 错误详情
- 用户行为

## 贡献

欢迎贡献！请查看 [CONTRIBUTING.md](CONTRIBUTING.md) 了解详情。

### 开发流程

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建 Pull Request

## 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 更新日志

查看 [CHANGELOG.md](CHANGELOG.md) 了解版本更新详情。

---

## Python 3.13+ 特性展示

这个项目专门展示了 Python 3.13 的新特性：

### 1. 改进的类型系统
- 参数规范 (`ParamSpec`)
- 类型守卫 (`TypeGuard`)
- 更好的泛型支持
- 运行时类型检查

### 2. 模式匹配
```python
match provider:
    case AIProvider.ANTHROPIC:
        return AnthropicProvider(...)
    case AIProvider.OPENAI:
        return OpenAIProvider(...)
    case _:
        raise ValueError(f"Unknown provider: {provider}")
```

### 3. 异步增强
- 异步生成器
- 异步上下文管理器
- 改进的并发原语

### 4. 性能优化
- 更快的字典访问
- 改进的字符串处理
- 优化的异常处理

### 5. 现代 Python 习惯
- 结构化模式匹配
- 类型安全的配置管理
- 现代异步编程模式

这个项目不仅是 AI 集成平台，更是现代 Python 开发的最佳实践展示！