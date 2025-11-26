"""
AI Agent 框架

提供智能Agent的创建、管理和协作功能
"""

import asyncio
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union, Callable, AsyncGenerator
from enum import Enum
import time
import json
from uuid import uuid4

from pydantic import BaseModel, Field, validator

from .llm import Message, ModelResponse, LLMProvider, MessageRole
from .rag import RAGSystem, RAGConfig


class AgentType(str, Enum):
    """Agent类型"""
    GENERAL = "general"
    RESEARCHER = "researcher"
    WRITER = "writer"
    CODER = "coder"
    ANALYST = "analyst"
    MANAGER = "manager"
    TOOL_AGENT = "tool_agent"
    MULTIMODAL = "multimodal"


class AgentStatus(str, Enum):
    """Agent状态"""
    IDLE = "idle"
    WORKING = "working"
    WAITING = "waiting"
    ERROR = "error"
    COMPLETED = "completed"


class TaskPriority(str, Enum):
    """任务优先级"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


@dataclass
class Tool:
    """Agent工具定义"""
    name: str
    description: str
    parameters: Dict[str, Any]
    function: Callable

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.parameters
        }


@dataclass
class Task:
    """Agent任务"""
    id: str
    description: str
    agent_id: str
    status: AgentStatus = AgentStatus.IDLE
    priority: TaskPriority = TaskPriority.MEDIUM
    input_data: Dict[str, Any] = field(default_factory=dict)
    output_data: Dict[str, Any] = field(default_factory=dict)
    error_message: Optional[str] = None
    created_at: float = field(default_factory=time.time)
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    dependencies: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "id": self.id,
            "description": self.description,
            "agent_id": self.agent_id,
            "status": self.status.value,
            "priority": self.priority.value,
            "input_data": self.input_data,
            "output_data": self.output_data,
            "error_message": self.error_message,
            "created_at": self.created_at,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "dependencies": self.dependencies,
            "metadata": self.metadata
        }


@dataclass
class AgentMessage:
    """Agent间消息"""
    id: str
    from_agent: str
    to_agent: str
    content: str
    message_type: str = "text"
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "id": self.id,
            "from_agent": self.from_agent,
            "to_agent": self.to_agent,
            "content": self.content,
            "message_type": self.message_type,
            "metadata": self.metadata,
            "timestamp": self.timestamp
        }


class AgentConfig(BaseModel):
    """Agent配置"""
    name: str = Field(..., description="Agent名称")
    agent_type: AgentType = Field(..., description="Agent类型")
    description: str = Field("", description="Agent描述")
    system_prompt: str = Field("你是一个有用的AI助手。", description="系统提示词")
    llm_model: str = Field("gpt-3.5-turbo", description="使用的LLM模型")
    temperature: float = Field(0.7, description="温度参数", ge=0.0, le=2.0)
    max_tokens: int = Field(2048, description="最大生成令牌数")
    enable_rag: bool = Field(False, description="是否启用RAG")
    rag_config: Optional[RAGConfig] = Field(None, description="RAG配置")
    tools: List[str] = Field(default_factory=list, description="可用工具列表")
    memory_limit: int = Field(10, description="记忆限制（对话轮数）")
    enable_tool_calling: bool = Field(False, description="是否启用工具调用")
    enable_multimodal: bool = Field(False, description="是否支持多模态")


class Agent(ABC):
    """Agent抽象基类"""

    def __init__(self, config: AgentConfig, llm_provider: LLMProvider):
        self.config = config
        self.llm_provider = llm_provider
        self.id = str(uuid4())
        self.status = AgentStatus.IDLE
        self.memory: List[Message] = []
        self.tools: Dict[str, Tool] = {}
        self.rag_system: Optional[RAGSystem] = None
        self.task_queue: asyncio.Queue = asyncio.Queue()
        self.message_queue: asyncio.Queue = asyncio.Queue()
        self.current_task: Optional[Task] = None
        self.statistics = {
            "tasks_completed": 0,
            "total_tokens_used": 0,
            "total_response_time": 0.0,
            "errors": 0
        }

    async def initialize(self) -> None:
        """初始化Agent"""
        await self.llm_provider.initialize()

        # 初始化RAG系统
        if self.config.enable_rag and self.config.rag_config:
            from ..services.factory import ServiceFactory
            self.rag_system = await ServiceFactory.create_rag_system(
                self.llm_provider,
                self.config.rag_config
            )

    def register_tool(self, tool: Tool) -> None:
        """注册工具"""
        self.tools[tool.name] = tool

    @abstractmethod
    async def process_task(self, task: Task) -> Dict[str, Any]:
        """处理任务的抽象方法"""
        pass

    async def add_task(self, task: Task) -> None:
        """添加任务到队列"""
        await self.task_queue.put(task)

    async def get_next_task(self) -> Optional[Task]:
        """获取下一个任务"""
        try:
            return self.task_queue.get_nowait()
        except asyncio.QueueEmpty:
            return None

    async def send_message(self, message: AgentMessage) -> None:
        """发送消息到其他Agent"""
        await self.message_queue.put(message)

    async def receive_message(self) -> Optional[AgentMessage]:
        """接收来自其他Agent的消息"""
        try:
            return self.message_queue.get_nowait()
        except asyncio.QueueEmpty:
            return None

    async def chat(
        self,
        message: str,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """与Agent对话"""
        # 添加到记忆
        user_message = Message(role=MessageRole.USER, content=message)
        self.memory.append(user_message)

        # 限制记忆长度
        if len(self.memory) > self.config.memory_limit * 2 + 1:  # +1 for system message
            # 保留系统消息和最近的对话
            if self.memory and self.memory[0].role == MessageRole.SYSTEM:
                system_msg = self.memory[0]
                user_assistant_pairs = self.memory[1:]
                recent_pairs = user_assistant_pairs[-self.config.memory_limit * 2:]
                self.memory = [system_msg] + recent_pairs
            else:
                self.memory = self.memory[-self.config.memory_limit * 2:]

        # 如果启用RAG，检索相关上下文
        context_info = ""
        if self.rag_system:
            try:
                rag_response = await self.rag_system.chat(message, self.memory[:-1])
                context_info = f"\n\n相关背景信息：\n{rag_response.answer}"
            except Exception as e:
                print(f"RAG检索失败: {e}")

        # 构建完整的用户消息
        full_message = message + context_info

        # 更新用户消息内容
        self.memory[-1].content = full_message

        # 生成响应
        start_time = time.time()
        response = await self.llm_provider.generate(self.memory)
        response_time = time.time() - start_time

        # 添加助手响应到记忆
        assistant_message = Message(
            role=MessageRole.ASSISTANT,
            content=response.content
        )
        self.memory.append(assistant_message)

        # 更新统计信息
        self.statistics["tasks_completed"] += 1
        self.statistics["total_tokens_used"] += response.usage.get("total_tokens", 0)
        self.statistics["total_response_time"] += response_time

        return response.content

    async def execute_tool(
        self,
        tool_name: str,
        parameters: Dict[str, Any]
    ) -> Any:
        """执行工具"""
        if tool_name not in self.tools:
            raise ValueError(f"Tool '{tool_name}' not found")

        tool = self.tools[tool_name]
        try:
            result = await tool.function(**parameters)
            return result
        except Exception as e:
            raise RuntimeError(f"Tool execution failed: {str(e)}")

    async def run_task(self, task: Task) -> Dict[str, Any]:
        """运行任务"""
        self.current_task = task
        self.status = AgentStatus.WORKING
        task.status = AgentStatus.WORKING
        task.started_at = time.time()

        try:
            # 处理任务
            result = await self.process_task(task)
            task.output_data = result
            task.status = AgentStatus.COMPLETED
            task.completed_at = time.time()

            self.statistics["tasks_completed"] += 1

        except Exception as e:
            task.error_message = str(e)
            task.status = AgentStatus.ERROR
            self.statistics["errors"] += 1
            raise

        finally:
            self.status = AgentStatus.IDLE
            self.current_task = None

        return task.output_data

    async def get_status(self) -> Dict[str, Any]:
        """获取Agent状态"""
        return {
            "id": self.id,
            "name": self.config.name,
            "type": self.config.agent_type.value,
            "status": self.status.value,
            "current_task": self.current_task.to_dict() if self.current_task else None,
            "queue_size": self.task_queue.qsize(),
            "message_queue_size": self.message_queue.qsize(),
            "memory_size": len(self.memory),
            "tools_count": len(self.tools),
            "statistics": self.statistics.copy()
        }

    def get_memory_summary(self) -> Dict[str, Any]:
        """获取记忆摘要"""
        return {
            "total_messages": len(self.memory),
            "user_messages": len([m for m in self.memory if m.role == MessageRole.USER]),
            "assistant_messages": len([m for m in self.memory if m.role == MessageRole.ASSISTANT]),
            "system_messages": len([m for m in self.memory if m.role == MessageRole.SYSTEM]),
            "last_message_time": self.memory[-1].to_dict().get("created_at", 0) if self.memory else 0
        }


class MultiAgentSystem:
    """多Agent系统"""

    def __init__(self):
        self.agents: Dict[str, Agent] = {}
        self.message_bus = asyncio.Queue()
        self.task_scheduler: Optional[TaskScheduler] = None
        self.running = False

    async def add_agent(self, agent: Agent) -> None:
        """添加Agent"""
        self.agents[agent.id] = agent
        await agent.initialize()

    def get_agent(self, agent_id: str) -> Optional[Agent]:
        """获取Agent"""
        return self.agents.get(agent_id)

    def get_agents_by_type(self, agent_type: AgentType) -> List[Agent]:
        """按类型获取Agent"""
        return [
            agent for agent in self.agents.values()
            if agent.config.agent_type == agent_type
        ]

    async def send_message(self, message: AgentMessage) -> None:
        """发送消息到消息总线"""
        await self.message_bus.put(message)

    async def broadcast_message(
        self,
        from_agent: str,
        content: str,
        message_type: str = "broadcast"
    ) -> None:
        """广播消息给所有Agent"""
        for agent_id in self.agents:
            if agent_id != from_agent:
                message = AgentMessage(
                    id=str(uuid4()),
                    from_agent=from_agent,
                    to_agent=agent_id,
                    content=content,
                    message_type=message_type
                )
                await self.send_message(message)

    async def process_messages(self) -> None:
        """处理消息总线中的消息"""
        while True:
            try:
                message = await asyncio.wait_for(self.message_bus.get(), timeout=1.0)

                # 获取目标Agent
                target_agent = self.get_agent(message.to_agent)
                if target_agent:
                    await target_agent.send_message(message)

                await asyncio.sleep(0.01)  # 小延迟避免CPU占用过高

            except asyncio.TimeoutError:
                continue
            except Exception as e:
                print(f"消息处理错误: {e}")

    async def create_task(
        self,
        description: str,
        agent_type: AgentType,
        priority: TaskPriority = TaskPriority.MEDIUM,
        input_data: Optional[Dict[str, Any]] = None,
        dependencies: Optional[List[str]] = None
    ) -> str:
        """创建任务"""
        # 选择合适的Agent
        available_agents = self.get_agents_by_type(agent_type)
        if not available_agents:
            raise ValueError(f"No available agents of type {agent_type}")

        # 选择最空闲的Agent
        selected_agent = min(
            available_agents,
            key=lambda a: a.task_queue.qsize()
        )

        # 创建任务
        task = Task(
            id=str(uuid4()),
            description=description,
            agent_id=selected_agent.id,
            priority=priority,
            input_data=input_data or {},
            dependencies=dependencies or []
        )

        # 添加任务到Agent队列
        await selected_agent.add_task(task)

        return task.id

    async def run(self) -> None:
        """运行多Agent系统"""
        self.running = True

        # 启动消息处理任务
        message_task = asyncio.create_task(self.process_messages())

        # 启动Agent任务处理
        agent_tasks = []
        for agent in self.agents.values():
            task = asyncio.create_task(self.run_agent(agent))
            agent_tasks.append(task)

        try:
            # 等待所有任务完成
            await asyncio.gather(message_task, *agent_tasks)
        except KeyboardInterrupt:
            print("多Agent系统停止")
        finally:
            self.running = False

    async def run_agent(self, agent: Agent) -> None:
        """运行单个Agent"""
        while self.running:
            try:
                # 获取下一个任务
                task = await agent.get_next_task()
                if task:
                    await agent.run_task(task)
                else:
                    # 检查是否有消息
                    message = await agent.receive_message()
                    if message:
                        # 处理消息
                        await self.handle_agent_message(agent, message)
                    else:
                        await asyncio.sleep(0.1)  # 短暂休眠

            except Exception as e:
                print(f"Agent {agent.id} 运行错误: {e}")
                await asyncio.sleep(1.0)

    async def handle_agent_message(self, agent: Agent, message: AgentMessage) -> None:
        """处理Agent消息"""
        # 可以根据消息类型执行不同的处理逻辑
        if message.message_type == "task_request":
            # 处理任务请求
            pass
        elif message.message_type == "collaboration":
            # 处理协作请求
            pass
        else:
            # 默认处理
            pass

    async def get_system_status(self) -> Dict[str, Any]:
        """获取系统状态"""
        agent_statuses = []
        for agent in self.agents.values():
            status = await agent.get_status()
            agent_statuses.append(status)

        total_tasks = sum(status["queue_size"] for status in agent_statuses)
        total_messages = sum(status["message_queue_size"] for status in agent_statuses)

        return {
            "running": self.running,
            "total_agents": len(self.agents),
            "agent_types": list(set(agent.config.agent_type.value for agent in self.agents.values())),
            "total_pending_tasks": total_tasks,
            "total_pending_messages": total_messages,
            "message_bus_size": self.message_bus.qsize(),
            "agents": agent_statuses
        }

    async def shutdown(self) -> None:
        """关闭多Agent系统"""
        self.running = False

        # 清理所有Agent
        for agent in self.agents.values():
            if hasattr(agent, 'cleanup'):
                await agent.cleanup()


class TaskScheduler:
    """任务调度器"""

    def __init__(self, multi_agent_system: MultiAgentSystem):
        self.multi_agent_system = multi_agent_system
        self.pending_tasks: Dict[str, Task] = {}
        self.running = False

    async def add_task(self, task: Task) -> None:
        """添加待调度任务"""
        self.pending_tasks[task.id] = task

    async def schedule_tasks(self) -> None:
        """调度任务"""
        self.running = True

        while self.running:
            try:
                # 查找可执行的任务（没有依赖或依赖已完成）
                ready_tasks = [
                    task for task in self.pending_tasks.values()
                    if self._can_execute_task(task)
                ]

                # 按优先级排序
                ready_tasks.sort(
                    key=lambda t: self._priority_value(t.priority),
                    reverse=True
                )

                # 执行任务
                for task in ready_tasks:
                    await self.multi_agent_system.create_task(
                        task.description,
                        AgentType(task.agent_id),
                        task.priority,
                        task.input_data,
                        task.dependencies
                    )

                    # 从待调度队列中移除
                    del self.pending_tasks[task.id]

                await asyncio.sleep(1.0)  # 每秒检查一次

            except Exception as e:
                print(f"任务调度错误: {e}")
                await asyncio.sleep(1.0)

    def _can_execute_task(self, task: Task) -> bool:
        """检查任务是否可以执行"""
        if not task.dependencies:
            return True

        # 检查依赖是否完成
        for dep_id in task.dependencies:
            if dep_id in self.pending_tasks:
                return False

        return True

    def _priority_value(self, priority: TaskPriority) -> int:
        """获取优先级数值"""
        priority_map = {
            TaskPriority.LOW: 1,
            TaskPriority.MEDIUM: 2,
            TaskPriority.HIGH: 3,
            TaskPriority.URGENT: 4
        }
        return priority_map.get(priority, 2)

    async def stop(self) -> None:
        """停止调度器"""
        self.running = False


# 工具函数
def create_tool(
    name: str,
    description: str,
    parameters: Dict[str, Any],
    function: Callable
) -> Tool:
    """创建工具的便捷函数"""
    return Tool(
        name=name,
        description=description,
        parameters=parameters,
        function=function
    )