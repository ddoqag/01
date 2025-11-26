"""
服务工厂模式

统一创建和配置各种AI服务实例
"""

import asyncio
from typing import Dict, Any, Optional, Type
from pathlib import Path

from ..models.llm import LLMProvider, LLMConfig
from ..models.embeddings import EmbeddingProvider, VectorStore, EmbeddingConfig, VectorStoreConfig
from ..models.rag import RAGSystem, RAGConfig
from ..models.agents import Agent, MultiAgentSystem, AgentConfig
from ..models.multimodal import MultimodalProcessor, MultimodalConfig

from .llm_service import LLMServiceImpl
from .embedding_service import EmbeddingServiceImpl
from .rag_service import RAGServiceImpl
from .agent_service import AgentServiceImpl
from .multimodal_service import MultimodalServiceImpl


class ServiceFactory:
    """服务工厂类"""

    _instances: Dict[str, Any] = {}
    _configs: Dict[str, Any] = {}

    @classmethod
    async def create_llm_provider(cls, config: LLMConfig) -> LLMProvider:
        """创建LLM提供商"""
        from .providers import get_llm_provider
        return await get_llm_provider(config)

    @classmethod
    async def create_embedding_provider(cls, config: EmbeddingConfig) -> EmbeddingProvider:
        """创建嵌入提供商"""
        from .providers import get_embedding_provider
        return await get_embedding_provider(config)

    @classmethod
    async def create_vector_store(cls, config: VectorStoreConfig) -> VectorStore:
        """创建向量存储"""
        from .providers import get_vector_store
        return await get_vector_store(config)

    @classmethod
    async def create_rag_system(
        cls,
        llm_provider: LLMProvider,
        embedding_provider: EmbeddingProvider,
        vector_store: VectorStore,
        config: RAGConfig
    ) -> RAGSystem:
        """创建RAG系统"""
        rag_system = RAGSystem(llm_provider, embedding_provider, vector_store, config)
        await rag_system.initialize()
        return rag_system

    @classmethod
    async def create_agent(
        cls,
        config: AgentConfig,
        llm_provider: LLMProvider
    ) -> Agent:
        """创建Agent"""
        from .agents import create_agent
        return await create_agent(config, llm_provider)

    @classmethod
    async def create_multimodal_processor(
        cls,
        config: MultimodalConfig,
        llm_provider: LLMProvider
    ) -> MultimodalProcessor:
        """创建多模态处理器"""
        processor = MultimodalProcessor(config, llm_provider)
        await processor.initialize()
        return processor

    @classmethod
    def register_config(cls, name: str, config: Any) -> None:
        """注册配置"""
        cls._configs[name] = config

    @classmethod
    def get_config(cls, name: str) -> Optional[Any]:
        """获取配置"""
        return cls._configs.get(name)

    @classmethod
    async def get_or_create_service(
        cls,
        service_name: str,
        factory_method,
        *args,
        **kwargs
    ) -> Any:
        """获取或创建服务（单例模式）"""
        if service_name not in cls._instances:
            cls._instances[service_name] = await factory_method(*args, **kwargs)
        return cls._instances[service_name]

    @classmethod
    async def load_from_config_file(cls, config_path: Path) -> None:
        """从配置文件加载配置"""
        import yaml
        import json

        if config_path.suffix.lower() in ['.yaml', '.yml']:
            with open(config_path, 'r', encoding='utf-8') as f:
                configs = yaml.safe_load(f)
        elif config_path.suffix.lower() == '.json':
            with open(config_path, 'r', encoding='utf-8') as f:
                configs = json.load(f)
        else:
            raise ValueError(f"Unsupported config file format: {config_path.suffix}")

        # 注册所有配置
        for name, config in configs.items():
            cls.register_config(name, config)

    @classmethod
    async def create_from_config(cls, config_name: str) -> Any:
        """根据配置名称创建服务"""
        config = cls.get_config(config_name)
        if not config:
            raise ValueError(f"Config '{config_name}' not found")

        # 根据配置类型创建相应的服务
        if config.get('type') == 'llm':
            llm_config = LLMConfig(**config)
            return await cls.create_llm_provider(llm_config)
        elif config.get('type') == 'embedding':
            embedding_config = EmbeddingConfig(**config)
            return await cls.create_embedding_provider(embedding_config)
        elif config.get('type') == 'vector_store':
            vector_store_config = VectorStoreConfig(**config)
            return await cls.create_vector_store(vector_store_config)
        else:
            raise ValueError(f"Unknown config type: {config.get('type')}")

    @classmethod
    async def cleanup_all(cls) -> None:
        """清理所有服务实例"""
        for service in cls._instances.values():
            if hasattr(service, 'cleanup'):
                await service.cleanup()
        cls._instances.clear()
        cls._configs.clear()


class ServiceRegistry:
    """服务注册表"""

    def __init__(self):
        self._services: Dict[str, Any] = {}
        self._service_configs: Dict[str, Dict[str, Any]] = {}

    def register_service(
        self,
        name: str,
        service: Any,
        config: Optional[Dict[str, Any]] = None
    ) -> None:
        """注册服务"""
        self._services[name] = service
        if config:
            self._service_configs[name] = config

    def get_service(self, name: str) -> Optional[Any]:
        """获取服务"""
        return self._services.get(name)

    def get_service_config(self, name: str) -> Optional[Dict[str, Any]]:
        """获取服务配置"""
        return self._service_configs.get(name)

    def list_services(self) -> Dict[str, str]:
        """列出所有服务"""
        return {
            name: type(service).__name__
            for name, service in self._services.items()
        }

    async def start_all_services(self) -> None:
        """启动所有服务"""
        for service in self._services.values():
            if hasattr(service, 'start'):
                await service.start()

    async def stop_all_services(self) -> None:
        """停止所有服务"""
        for service in self._services.values():
            if hasattr(service, 'stop'):
                await service.stop()

    async def health_check(self) -> Dict[str, bool]:
        """健康检查"""
        health_status = {}
        for name, service in self._services.items():
            try:
                if hasattr(service, 'health_check'):
                    health_status[name] = await service.health_check()
                else:
                    health_status[name] = True  # 假设健康
            except Exception as e:
                health_status[name] = False
                print(f"Service {name} health check failed: {e}")

        return health_status


# 全局服务注册表实例
service_registry = ServiceRegistry()


def get_service_registry() -> ServiceRegistry:
    """获取全局服务注册表"""
    return service_registry