# AI Engineer Framework

现代化的AI工程化框架，提供完整的大语言模型应用开发解决方案。

## 🚀 特性

### 多LLM提供商集成
- **OpenAI**: GPT-3.5, GPT-4, GPT-4 Turbo, 嵌入模型
- **Anthropic**: Claude 3 Opus, Sonnet, Haiku
- **本地模型**: 通过Ollama、Transformers支持
- **统一接口**: 无缝切换不同提供商

### RAG系统 (检索增强生成)
- **多种向量数据库**: ChromaDB, Pinecone, Weaviate, FAISS
- **智能分块**: 支持固定大小、段落、语义、混合分块策略
- **高级检索**: 相似度搜索、混合搜索、重排
- **多格式文档**: PDF, DOCX, HTML, Markdown, JSON, CSV

### Agent框架
- **多Agent协作**: 支持Agent间通信和协作
- **工具集成**: 可扩展的工具系统
- **任务调度**: 智能任务分配和执行
- **状态管理**: 完整的Agent生命周期管理

### 多模态支持
- **图像理解**: GPT-4 Vision集成
- **音频处理**: Whisper语音识别和转录
- **视频分析**: 关键帧提取和内容理解
- **统一处理**: 多模态内容的统一API

### 生产部署
- **高性能**: 异步处理，批量优化
- **监控告警**: Prometheus + Grafana集成
- **分布式**: 支持水平扩展
- **容器化**: Docker + Kubernetes就绪

### 成本优化
- **智能模型选择**: 基于任务复杂度和质量要求
- **预算控制**: 实时成本监控和预算告警
- **缓存优化**: 智能请求缓存减少重复调用
- **批处理**: 批量请求优化降低成本

## 🏗️ 架构设计

```
ai-engineer-framework/
├── src/
│   ├── models/          # 核心数据模型和接口
│   │   ├── llm.py      # LLM统一接口
│   │   ├── embeddings.py # 嵌入模型接口
│   │   ├── rag.py      # RAG系统
│   │   ├── agents.py   # Agent框架
│   │   └── multimodal.py # 多模态处理
│   ├── services/        # 服务层实现
│   │   ├── factory.py  # 服务工厂
│   │   ├── monitoring_service.py # 监控服务
│   │   └── cost_optimizer.py # 成本优化
│   ├── api/            # FastAPI路由
│   │   └── routes/     # 各模块API端点
│   └── utils/          # 工具函数
├── configs/            # 配置文件
├── scripts/            # 部署和管理脚本
└── tests/             # 测试用例
```

## 🚀 快速开始

### 环境要求

- Python 3.12+
- Docker (可选)
- Redis (可选，用于缓存)
- PostgreSQL (可选，用于生产环境)

### 安装

1. **克隆项目**
```bash
git clone https://github.com/your-org/ai-engineer-framework.git
cd ai-engineer-framework
```

2. **创建虚拟环境**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate     # Windows
```

3. **安装依赖**
```bash
pip install -r requirements/base.txt
pip install -r requirements/production.txt
```

4. **配置环境变量**
```bash
cp .env.example .env
# 编辑 .env 文件，填入你的API密钥
```

5. **启动服务**
```bash
# 开发模式
python src/main.py

# 或使用uvicorn
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

### Docker部署

1. **构建并启动所有服务**
```bash
docker-compose up -d
```

2. **查看服务状态**
```bash
docker-compose ps
```

3. **访问服务**
- API文档: http://localhost:8000/docs
- Grafana监控: http://localhost:3000
- Prometheus: http://localhost:9090
- Flower (Celery监控): http://localhost:5555

## 📖 使用示例

### 1. LLM聊天

```python
import asyncio
from ai_engineer_framework import LLMConfig, get_llm_manager

async def chat_example():
    # 配置OpenAI模型
    config = LLMConfig(
        model_name="gpt-4",
        provider="openai",
        api_key="your-api-key",
        temperature=0.7
    )

    # 注册LLM提供商
    await register_llm_provider("openai_gpt4", config, set_as_default=True)

    # 获取LLM管理器
    manager = get_llm_manager()

    # 发送消息
    response = await manager.generate([
        Message(role="user", content="你好，请介绍一下AI工程化")
    ])

    print(response.content)

asyncio.run(chat_example())
```

### 2. RAG系统

```python
from ai_engineer_framework import (
    RAGConfig, Document, DocumentType,
    get_rag_system
)

async def rag_example():
    # 创建文档
    doc = Document(
        id="doc1",
        content="AI工程化是指将人工智能技术以工程化的方法进行开发和部署...",
        doc_type=DocumentType.TEXT,
        source="knowledge_base.txt"
    )

    # 获取RAG系统
    rag_system = await get_rag_system()

    # 添加文档
    await rag_system.add_document(doc)

    # 查询
    response = await rag_system.generate_answer(
        "什么是AI工程化？"
    )

    print(f"答案: {response.answer}")
    print(f"引用: {response.citations}")

asyncio.run(rag_example())
```

### 3. Agent协作

```python
from ai_engineer_framework import (
    AgentConfig, AgentType, MultiAgentSystem
)

async def agent_example():
    # 创建多Agent系统
    system = MultiAgentSystem()

    # 创建研究Agent
    researcher_config = AgentConfig(
        name="研究专家",
        agent_type=AgentType.RESEARCHER,
        system_prompt="你是一个专业的研究专家..."
    )

    researcher = await create_agent(researcher_config, llm_provider)
    await system.add_agent(researcher)

    # 创建任务
    task_id = await system.create_task(
        description="研究最新的AI工程化趋势",
        agent_type=AgentType.RESEARCHER
    )

    # 运行系统
    await system.run()

asyncio.run(agent_example())
```

### 4. 多模态处理

```python
from ai_engineer_framework import (
    MultimodalConfig, MultimodalProcessor,
    create_media_content_from_file
)

async def multimodal_example():
    # 配置多模态处理器
    config = MultimodalConfig()
    processor = await MultimodalProcessor.create(config, llm_provider)

    # 处理图像
    image_media = create_media_content_from_file("image.jpg")
    response = await processor.generate_with_media(
        "请描述这张图片中的内容",
        [image_media]
    )

    print(response)

asyncio.run(multimodal_example())
```

## ⚙️ 配置说明

### 主配置文件 (configs/default.yaml)

```yaml
# 应用基础配置
app:
  name: "ai-engineer-framework"
  version: "0.1.0"
  host: "0.0.0.0"
  port: 8000

# LLM提供商配置
llm_providers:
  openai:
    type: "llm"
    provider: "openai"
    model_name: "gpt-4"
    api_key: "${OPENAI_API_KEY}"
    max_tokens: 2048
    temperature: 0.7

# RAG配置
rag:
  top_k: 5
  similarity_threshold: 0.7
  chunk_size: 512
  chunk_overlap: 50

# 成本优化
cost_optimization:
  daily_budget_usd: 100.0
  optimization_level: "medium"
  enable_model_switching: true

# 监控配置
monitoring:
  metrics_enabled: true
  prometheus_enabled: true
  prometheus_port: 8080
```

### 环境变量

```bash
# API密钥
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key
PINECONE_API_KEY=your_pinecone_key

# 数据库
DATABASE_URL=postgresql://user:password@localhost/db
REDIS_URL=redis://localhost:6379/0

# 监控
SENTRY_DSN=your_sentry_dsn
```

## 📊 监控和成本优化

### Prometheus指标

- `ai_engineer_requests_total`: 请求总数
- `ai_engineer_request_duration_seconds`: 请求耗时
- `ai_engineer_tokens_used_total`: 使用的token总数
- `ai_engineer_cost_usd_total`: 总成本

### 成本优化策略

1. **智能模型选择**: 根据任务复杂度自动选择性价比最高的模型
2. **请求缓存**: 缓存相同请求的响应，避免重复计算
3. **批处理**: 将多个请求合并处理
4. **预算控制**: 实时监控和预算告警

### 成本分析

```python
from ai_engineer_framework import get_cost_optimizer

optimizer = get_cost_optimizer()

# 获取成本摘要
summary = optimizer.get_cost_summary()
print(f"总成本: ${summary['total_cost']:.2f}")

# 获取优化建议
recommendations = optimizer.generate_optimization_recommendations()
for rec in recommendations:
    print(f"建议: {rec.description}")
    print(f"预期节省: ${rec.potential_savings:.2f}")
```

## 🧪 测试

### 运行测试

```bash
# 运行所有测试
pytest

# 运行特定测试
pytest tests/test_llm.py

# 生成覆盖率报告
pytest --cov=src --cov-report=html
```

### 集成测试

```bash
# 启动测试环境
docker-compose -f docker-compose.test.yml up -d

# 运行集成测试
pytest tests/integration/
```

## 🚀 生产部署

### Kubernetes部署

```yaml
# k8s-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ai-engineer-framework
spec:
  replicas: 3
  selector:
    matchLabels:
      app: ai-engineer-framework
  template:
    metadata:
      labels:
        app: ai-engineer-framework
    spec:
      containers:
      - name: app
        image: ai-engineer-framework:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: app-secrets
              key: database-url
```

### 性能优化

1. **连接池**: 配置数据库和Redis连接池
2. **缓存**: 启用多级缓存
3. **负载均衡**: 使用Nginx或云负载均衡器
4. **自动扩展**: 基于CPU和内存使用率自动扩展

### 安全配置

```yaml
# 安全配置
security:
  api_key_required: true
  rate_limit_enabled: true
  rate_limit_requests_per_minute: 60
  cors_enabled: true
  cors_origins: ["https://yourdomain.com"]
  ssl_enabled: true
```

## 🤝 贡献指南

1. Fork项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启Pull Request

### 开发规范

- 遵循PEP 8代码风格
- 编写单元测试
- 更新文档
- 使用类型提示

## 📄 许可证

本项目采用MIT许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 🙏 致谢

- [FastAPI](https://fastapi.tiangolo.com/) - 现代的Web框架
- [LangChain](https://python.langchain.com/) - LLM应用开发框架
- [ChromaDB](https://www.trychroma.com/) - 开源向量数据库
- [Prometheus](https://prometheus.io/) - 监控和告警系统

## 📞 支持

- 📧 邮箱: support@ai-engineer-framework.com
- 💬 讨论: [GitHub Discussions](https://github.com/your-org/ai-engineer-framework/discussions)
- 🐛 问题报告: [GitHub Issues](https://github.com/your-org/ai-engineer-framework/issues)
- 📚 文档: [https://docs.ai-engineer-framework.com](https://docs.ai-engineer-framework.com)

---

**AI Engineer Framework** - 让AI工程化更简单、更高效！