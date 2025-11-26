"""
成本优化服务

提供智能的成本监控、预测和优化策略
"""

import asyncio
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union, Callable, Tuple
from enum import Enum
from collections import defaultdict, deque
from datetime import datetime, timedelta
import json
import threading

from pydantic import BaseModel, Field, validator


class CostOptimizationLevel(str, Enum):
    """成本优化级别"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    AGGRESSIVE = "aggressive"


class ModelTier(str, Enum):
    """模型层级"""
    BASIC = "basic"      # 基础模型，成本低
    STANDARD = "standard"  # 标准模型，性价比高
    PREMIUM = "premium"    # 高级模型，成本高
    ULTRA = "ultra"       # 顶级模型，成本最高


@dataclass
class CostRecord:
    """成本记录"""
    timestamp: float
    service_type: str  # llm, embedding, rag, agent, multimodal
    model_name: str
    model_tier: ModelTier
    tokens_used: int = 0
    requests_count: int = 0
    cost_usd: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "timestamp": self.timestamp,
            "service_type": self.service_type,
            "model_name": self.model_name,
            "model_tier": self.model_tier.value,
            "tokens_used": self.tokens_used,
            "requests_count": self.requests_count,
            "cost_usd": self.cost_usd,
            "metadata": self.metadata
        }


@dataclass
class ModelPricing:
    """模型定价"""
    model_name: str
    model_tier: ModelTier
    input_price_per_1k: float  # 每1000个输入token的价格（美元）
    output_price_per_1k: float  # 每1000个输出token的价格（美元）
    price_per_request: float = 0.0  # 每次请求的固定费用
    max_tokens: int = 4096  # 最大token数
    context_window: int = 4096  # 上下文窗口大小

    def calculate_cost(
        self,
        input_tokens: int,
        output_tokens: int,
        requests_count: int = 1
    ) -> float:
        """计算成本"""
        token_cost = (
            (input_tokens / 1000) * self.input_price_per_1k +
            (output_tokens / 1000) * self.output_price_per_1k
        )
        request_cost = requests_count * self.price_per_request
        return token_cost + request_cost


@dataclass
class OptimizationRecommendation:
    """优化建议"""
    recommendation_type: str
    description: str
    potential_savings: float  # 预估节省的成本（美元）
    confidence: float  # 建议的置信度（0-1）
    implementation_effort: str  # 实现难度：low, medium, high
    priority: str  # 优先级：low, medium, high, critical
    metadata: Dict[str, Any] = field(default_factory=dict)


class CostOptimizerConfig(BaseModel):
    """成本优化配置"""
    # 预算控制
    daily_budget_usd: float = Field(100.0, description="每日预算（美元）")
    monthly_budget_usd: float = Field(3000.0, description="月度预算（美元）")
    budget_alert_threshold: float = Field(0.8, description="预算告警阈值")

    # 优化级别
    optimization_level: CostOptimizationLevel = Field(CostOptimizationLevel.MEDIUM, description="优化级别")
    enable_model_switching: bool = Field(True, description="是否启用模型自动切换")
    enable_request_caching: bool = Field(True, description="是否启用请求缓存")
    enable_batch_processing: bool = Field(True, description="是否启用批处理优化")

    # 监控配置
    cost_tracking_enabled: bool = Field(True, description="是否启用成本跟踪")
    cost_retention_days: int = Field(90, description="成本数据保留天数")
    cost_analysis_interval: int = Field(3600, description="成本分析间隔（秒）")

    # 模型选择策略
    default_model_tier: ModelTier = Field(ModelTier.STANDARD, description="默认模型层级")
    fallback_model_tier: ModelTier = Field(ModelTier.BASIC, description="回退模型层级")
    quality_threshold: float = Field(0.8, description="质量阈值")

    @validator('daily_budget_usd')
    def validate_daily_budget(cls, v):
        if v <= 0:
            raise ValueError('Daily budget must be positive')
        return v


class ModelSelector:
    """模型选择器"""

    def __init__(self, config: CostOptimizerConfig, model_pricing: Dict[str, ModelPricing]):
        self.config = config
        self.model_pricing = model_pricing
        self._performance_history: Dict[str, List[float]] = defaultdict(list)

    def select_model(
        self,
        service_type: str,
        task_complexity: str = "medium",
        quality_requirement: float = 0.8,
        cost_sensitivity: float = 0.5
    ) -> Tuple[str, ModelTier]:
        """选择最优模型"""
        available_models = [
            (name, pricing) for name, pricing in self.model_pricing.items()
            if self._is_model_suitable(name, pricing, service_type)
        ]

        if not available_models:
            # 回退到默认模型
            return self._get_fallback_model()

        # 根据优化级别选择策略
        if self.config.optimization_level == CostOptimizationLevel.LOW:
            return self._select_by_quality(available_models, quality_requirement)
        elif self.config.optimization_level == CostOptimizationLevel.HIGH:
            return self._select_by_cost(available_models, cost_sensitivity)
        elif self.config.optimization_level == CostOptimizationLevel.AGGRESSIVE:
            return self._select_cheapest(available_models)
        else:  # MEDIUM
            return self._select_balanced(available_models, quality_requirement, cost_sensitivity)

    def _is_model_suitable(self, model_name: str, pricing: ModelPricing, service_type: str) -> bool:
        """检查模型是否适合特定服务"""
        # 这里可以添加更复杂的模型适用性逻辑
        return True

    def _select_by_quality(self, models: List[Tuple[str, ModelPricing]], quality_requirement: float) -> Tuple[str, ModelTier]:
        """按质量选择模型"""
        # 按层级排序，选择满足质量要求的高级模型
        tier_priority = [ModelTier.ULTRA, ModelTier.PREMIUM, ModelTier.STANDARD, ModelTier.BASIC]

        for tier in tier_priority:
            for name, pricing in models:
                if pricing.model_tier == tier:
                    return name, tier

        return self._get_fallback_model()

    def _select_by_cost(self, models: List[Tuple[str, ModelPricing]], cost_sensitivity: float) -> Tuple[str, ModelTier]:
        """按成本选择模型"""
        # 计算每个模型的性价比
        scored_models = []
        for name, pricing in models:
            # 简化的性价比评分
            cost_score = 1.0 / (pricing.input_price_per_1k + pricing.output_price_per_1k + 0.001)
            tier_score = self._get_tier_score(pricing.model_tier)
            combined_score = cost_sensitivity * cost_score + (1 - cost_sensitivity) * tier_score
            scored_models.append((name, pricing.model_tier, combined_score))

        # 选择评分最高的模型
        scored_models.sort(key=lambda x: x[2], reverse=True)
        return scored_models[0][0], scored_models[0][1]

    def _select_balanced(
        self,
        models: List[Tuple[str, ModelPricing]],
        quality_requirement: float,
        cost_sensitivity: float
    ) -> Tuple[str, ModelTier]:
        """平衡选择模型"""
        # 结合质量和成本的综合评分
        scored_models = []
        for name, pricing in models:
            quality_score = self._get_tier_score(pricing.model_tier)
            cost_score = 1.0 / (pricing.input_price_per_1k + pricing.output_price_per_1k + 0.001)
            combined_score = 0.5 * quality_score + 0.5 * cost_score
            scored_models.append((name, pricing.model_tier, combined_score))

        scored_models.sort(key=lambda x: x[2], reverse=True)
        return scored_models[0][0], scored_models[0][1]

    def _select_cheapest(self, models: List[Tuple[str, ModelPricing]]) -> Tuple[str, ModelTier]:
        """选择最便宜的模型"""
        cheapest = min(models, key=lambda x: x[1].input_price_per_1k + x[1].output_price_per_1k)
        return cheapest[0], cheapest[1].model_tier

    def _get_tier_score(self, tier: ModelTier) -> float:
        """获取层级评分"""
        tier_scores = {
            ModelTier.BASIC: 0.6,
            ModelTier.STANDARD: 0.8,
            ModelTier.PREMIUM: 0.9,
            ModelTier.ULTRA: 1.0
        }
        return tier_scores.get(tier, 0.7)

    def _get_fallback_model(self) -> Tuple[str, ModelTier]:
        """获取回退模型"""
        # 选择最便宜的可用模型作为回退
        available_models = list(self.model_pricing.items())
        if available_models:
            cheapest = min(
                available_models,
                key=lambda x: x[1].input_price_per_1k + x[1].output_price_per_1k
            )
            return cheapest[0], cheapest[1].model_tier

        return "gpt-3.5-turbo", ModelTier.BASIC


class RequestCache:
    """请求缓存器"""

    def __init__(self, max_size: int = 10000, ttl: int = 3600):
        self.max_size = max_size
        self.ttl = ttl
        self._cache: Dict[str, Tuple[Any, float]] = {}
        self._access_times: Dict[str, float] = {}
        self._lock = threading.Lock()

    def get(self, key: str) -> Optional[Any]:
        """获取缓存"""
        with self._lock:
            if key in self._cache:
                value, timestamp = self._cache[key]
                if time.time() - timestamp < self.ttl:
                    self._access_times[key] = time.time()
                    return value
                else:
                    # 过期，删除
                    del self._cache[key]
                    if key in self._access_times:
                        del self._access_times[key]
            return None

    def set(self, key: str, value: Any) -> None:
        """设置缓存"""
        with self._lock:
            # 如果缓存已满，删除最久未访问的项
            if len(self._cache) >= self.max_size:
                self._evict_lru()

            self._cache[key] = (value, time.time())
            self._access_times[key] = time.time()

    def _evict_lru(self) -> None:
        """删除最久未访问的项"""
        if not self._access_times:
            return

        lru_key = min(self._access_times.items(), key=lambda x: x[1])[0]
        del self._cache[lru_key]
        del self._access_times[lru_key]

    def clear(self) -> None:
        """清空缓存"""
        with self._lock:
            self._cache.clear()
            self._access_times.clear()

    def get_stats(self) -> Dict[str, Any]:
        """获取缓存统计"""
        with self._lock:
            return {
                "size": len(self._cache),
                "max_size": self.max_size,
                "hit_rate": getattr(self, '_hit_count', 0) / max(getattr(self, '_total_requests', 1), 1)
            }


class BudgetManager:
    """预算管理器"""

    def __init__(self, config: CostOptimizerConfig):
        self.config = config
        self._daily_spending: float = 0.0
        self._monthly_spending: float = 0.0
        self._last_reset_date: Optional[datetime] = None
        self._lock = threading.Lock()

    def record_cost(self, cost: float) -> bool:
        """记录成本，返回是否在预算内"""
        with self._lock:
            self._check_and_reset_periods()

            self._daily_spending += cost
            self._monthly_spending += cost

            # 检查预算
            return self._is_within_budget()

    def _check_and_reset_periods(self) -> None:
        """检查并重置计费周期"""
        now = datetime.now()

        if self._last_reset_date is None:
            self._last_reset_date = now
            return

        # 检查是否需要重置日预算
        if now.date() != self._last_reset_date.date():
            self._daily_spending = 0.0

        # 检查是否需要重置月预算
        if now.month != self._last_reset_date.month or now.year != self._last_reset_date.year:
            self._monthly_spending = 0.0

        self._last_reset_date = now

    def _is_within_budget(self) -> bool:
        """检查是否在预算内"""
        daily_ratio = self._daily_spending / self.config.daily_budget_usd
        monthly_ratio = self._monthly_spending / self.config.monthly_budget_usd

        return daily_ratio <= self.config.budget_alert_threshold and monthly_ratio <= self.config.budget_alert_threshold

    def get_budget_status(self) -> Dict[str, Any]:
        """获取预算状态"""
        with self._lock:
            self._check_and_reset_periods()

            return {
                "daily_spending": self._daily_spending,
                "daily_budget": self.config.daily_budget_usd,
                "daily_usage_ratio": self._daily_spending / self.config.daily_budget_usd,
                "monthly_spending": self._monthly_spending,
                "monthly_budget": self.config.monthly_budget_usd,
                "monthly_usage_ratio": self._monthly_spending / self.config.monthly_budget_usd,
                "within_budget": self._is_within_budget(),
                "alert_triggered": not self._is_within_budget()
            }


class CostOptimizer:
    """成本优化器主类"""

    def __init__(self, config: CostOptimizerConfig):
        self.config = config
        self.cost_history: deque = deque(maxlen=10000)
        self.model_pricing: Dict[str, ModelPricing] = {}
        self.model_selector = ModelSelector(config, self.model_pricing)
        self.request_cache = RequestCache()
        self.budget_manager = BudgetManager(config)
        self._lock = threading.Lock()

        # 初始化默认模型定价
        self._init_default_pricing()

    def _init_default_pricing(self) -> None:
        """初始化默认模型定价"""
        # OpenAI 模型定价
        self.model_pricing.update({
            "gpt-4": ModelPricing("gpt-4", ModelTier.PREMIUM, 0.03, 0.06, 0.0, 8192, 8192),
            "gpt-4-turbo": ModelPricing("gpt-4-turbo", ModelTier.PREMIUM, 0.01, 0.03, 0.0, 4096, 128000),
            "gpt-3.5-turbo": ModelPricing("gpt-3.5-turbo", ModelTier.STANDARD, 0.0015, 0.002, 0.0, 4096, 16385),
            "gpt-3.5-turbo-16k": ModelPricing("gpt-3.5-turbo-16k", ModelTier.STANDARD, 0.003, 0.004, 0.0, 4096, 16385),
        })

        # Claude 模型定价
        self.model_pricing.update({
            "claude-3-opus-20240229": ModelPricing("claude-3-opus-20240229", ModelTier.ULTRA, 0.015, 0.075, 0.0, 4096, 200000),
            "claude-3-sonnet-20240229": ModelPricing("claude-3-sonnet-20240229", ModelTier.PREMIUM, 0.003, 0.015, 0.0, 4096, 200000),
            "claude-3-haiku-20240307": ModelPricing("claude-3-haiku-20240307", ModelTier.STANDARD, 0.00025, 0.00125, 0.0, 4096, 200000),
        })

        # 嵌入模型定价
        self.model_pricing.update({
            "text-embedding-ada-002": ModelPricing("text-embedding-ada-002", ModelTier.STANDARD, 0.0001, 0.0, 0.0, 8191, 8191),
            "text-embedding-3-small": ModelPricing("text-embedding-3-small", ModelTier.BASIC, 0.00002, 0.0, 0.0, 8191, 8191),
            "text-embedding-3-large": ModelPricing("text-embedding-3-large", ModelTier.STANDARD, 0.00013, 0.0, 0.0, 8191, 8191),
        })

    def record_cost(
        self,
        service_type: str,
        model_name: str,
        input_tokens: int = 0,
        output_tokens: int = 0,
        requests_count: int = 1,
        metadata: Optional[Dict[str, Any]] = None
    ) -> float:
        """记录成本"""
        if not self.config.cost_tracking_enabled:
            return 0.0

        # 获取模型定价
        pricing = self.model_pricing.get(model_name)
        if not pricing:
            # 使用默认定价
            pricing = ModelPricing(model_name, ModelTier.STANDARD, 0.001, 0.002, 0.0)

        # 计算成本
        cost = pricing.calculate_cost(input_tokens, output_tokens, requests_count)

        # 创建成本记录
        cost_record = CostRecord(
            timestamp=time.time(),
            service_type=service_type,
            model_name=model_name,
            model_tier=pricing.model_tier,
            tokens_used=input_tokens + output_tokens,
            requests_count=requests_count,
            cost_usd=cost,
            metadata=metadata or {}
        )

        with self._lock:
            self.cost_history.append(cost_record)

        # 检查预算
        within_budget = self.budget_manager.record_cost(cost)

        if not within_budget:
            # 触发预算告警
            self._trigger_budget_alert(cost_record)

        return cost

    def _trigger_budget_alert(self, cost_record: CostRecord) -> None:
        """触发预算告警"""
        # 这里可以实现告警逻辑，如发送邮件、短信等
        print(f"Budget alert triggered! Recent cost: ${cost_record.cost_usd:.4f}")

    def select_optimal_model(
        self,
        service_type: str,
        task_complexity: str = "medium",
        quality_requirement: float = 0.8,
        cost_sensitivity: float = 0.5
    ) -> Tuple[str, ModelTier]:
        """选择最优模型"""
        return self.model_selector.select_model(
            service_type, task_complexity, quality_requirement, cost_sensitivity
        )

    def get_cached_response(self, cache_key: str) -> Optional[Any]:
        """获取缓存的响应"""
        if not self.config.enable_request_caching:
            return None
        return self.request_cache.get(cache_key)

    def cache_response(self, cache_key: str, response: Any) -> None:
        """缓存响应"""
        if self.config.enable_request_caching:
            self.request_cache.set(cache_key, response)

    def generate_optimization_recommendations(self) -> List[OptimizationRecommendation]:
        """生成优化建议"""
        recommendations = []

        # 分析成本历史
        if self.cost_history:
            recommendations.extend(self._analyze_cost_patterns())

        # 分析模型使用情况
        recommendations.extend(self._analyze_model_usage())

        # 分析缓存效率
        if self.config.enable_request_caching:
            recommendations.extend(self._analyze_cache_efficiency())

        return recommendations

    def _analyze_cost_patterns(self) -> List[OptimizationRecommendation]:
        """分析成本模式"""
        recommendations = []

        # 计算最近24小时的成本
        recent_costs = [
            record for record in self.cost_history
            if time.time() - record.timestamp <= 24 * 3600
        ]

        if recent_costs:
            daily_cost = sum(record.cost_usd for record in recent_costs)

            if daily_cost > self.config.daily_budget_usd * 0.9:
                recommendations.append(OptimizationRecommendation(
                    recommendation_type="cost_optimization",
                    description="Daily spending is approaching budget limit. Consider switching to lower-tier models.",
                    potential_savings=daily_cost * 0.3,
                    confidence=0.8,
                    implementation_effort="low",
                    priority="high"
                ))

        return recommendations

    def _analyze_model_usage(self) -> List[OptimizationRecommendation]:
        """分析模型使用情况"""
        recommendations = []

        # 统计各模型使用情况
        model_usage = defaultdict(lambda: {"cost": 0.0, "requests": 0})
        for record in self.cost_history:
            model_usage[record.model_name]["cost"] += record.cost_usd
            model_usage[record.model_name]["requests"] += record.requests_count

        # 检查是否有过度使用昂贵模型的情况
        for model_name, usage in model_usage.items():
            pricing = self.model_pricing.get(model_name)
            if pricing and pricing.model_tier in [ModelTier.PREMIUM, ModelTier.ULTRA]:
                avg_cost_per_request = usage["cost"] / max(usage["requests"], 1)
                if avg_cost_per_request > 0.1:  # 每次请求成本超过0.1美元
                    recommendations.append(OptimizationRecommendation(
                        recommendation_type="model_optimization",
                        description=f"High-cost model {model_name} usage detected. Consider switching to {self.config.default_model_tier.value} tier for non-critical tasks.",
                        potential_savings=usage["cost"] * 0.4,
                        confidence=0.7,
                        implementation_effort="medium",
                        priority="medium"
                    ))

        return recommendations

    def _analyze_cache_efficiency(self) -> List[OptimizationRecommendation]:
        """分析缓存效率"""
        recommendations = []

        cache_stats = self.request_cache.get_stats()
        hit_rate = cache_stats.get("hit_rate", 0)

        if hit_rate < 0.3:  # 命中率低于30%
            recommendations.append(OptimizationRecommendation(
                recommendation_type="cache_optimization",
                description="Low cache hit rate detected. Consider increasing cache size or TTL.",
                potential_savings=100.0,  # 估算节省
                confidence=0.6,
                implementation_effort="low",
                priority="medium"
            ))

        return recommendations

    def get_cost_summary(self) -> Dict[str, Any]:
        """获取成本摘要"""
        with self._lock:
            if not self.cost_history:
                return {
                    "total_cost": 0.0,
                    "total_tokens": 0,
                    "total_requests": 0,
                    "service_breakdown": {},
                    "model_breakdown": {},
                    "time_series": []
                }

            # 计算总成本
            total_cost = sum(record.cost_usd for record in self.cost_history)
            total_tokens = sum(record.tokens_used for record in self.cost_history)
            total_requests = sum(record.requests_count for record in self.cost_history)

            # 按服务类型分解
            service_breakdown = defaultdict(float)
            for record in self.cost_history:
                service_breakdown[record.service_type] += record.cost_usd

            # 按模型分解
            model_breakdown = defaultdict(lambda: {"cost": 0.0, "tokens": 0, "requests": 0})
            for record in self.cost_history:
                model_breakdown[record.model_name]["cost"] += record.cost_usd
                model_breakdown[record.model_name]["tokens"] += record.tokens_used
                model_breakdown[record.model_name]["requests"] += record.requests_count

            return {
                "total_cost": total_cost,
                "total_tokens": total_tokens,
                "total_requests": total_requests,
                "service_breakdown": dict(service_breakdown),
                "model_breakdown": dict(model_breakdown),
                "budget_status": self.budget_manager.get_budget_status(),
                "cache_stats": self.request_cache.get_stats() if self.config.enable_request_caching else None
            }

    def export_cost_data(self, format: str = "json") -> str:
        """导出成本数据"""
        data = {
            "summary": self.get_cost_summary(),
            "recommendations": [
                rec.to_dict() for rec in self.generate_optimization_recommendations()
            ],
            "detailed_records": [record.to_dict() for record in self.cost_history]
        }

        if format == "json":
            return json.dumps(data, indent=2)
        elif format == "csv":
            # 简化的CSV导出
            import csv
            import io

            output = io.StringIO()
            writer = csv.writer(output)
            writer.writerow(["timestamp", "service_type", "model_name", "model_tier", "tokens_used", "requests_count", "cost_usd"])

            for record in self.cost_history:
                writer.writerow([
                    record.timestamp,
                    record.service_type,
                    record.model_name,
                    record.model_tier.value,
                    record.tokens_used,
                    record.requests_count,
                    record.cost_usd
                ])

            return output.getvalue()
        else:
            raise ValueError(f"Unsupported export format: {format}")


# 全局成本优化器实例
_cost_optimizer: Optional[CostOptimizer] = None


def get_cost_optimizer() -> CostOptimizer:
    """获取全局成本优化器实例"""
    global _cost_optimizer
    if _cost_optimizer is None:
        config = CostOptimizerConfig()
        _cost_optimizer = CostOptimizer(config)
    return _cost_optimizer


async def init_cost_optimizer(config: CostOptimizerConfig) -> CostOptimizer:
    """初始化全局成本优化器"""
    global _cost_optimizer
    _cost_optimizer = CostOptimizer(config)
    return _cost_optimizer


# 装饰器
def track_cost(service_type: str, model_name: str):
    """成本跟踪装饰器"""
    def decorator(func):
        if asyncio.iscoroutinefunction(func):
            async def async_wrapper(*args, **kwargs):
                # 这里需要从函数调用中提取token使用情况
                # 简化实现，实际应用中需要更复杂的逻辑
                cost_optimizer = get_cost_optimizer()
                start_time = time.time()

                try:
                    result = await func(*args, **kwargs)

                    # 模拟token计算（实际应该从响应中获取）
                    input_tokens = 100  # 占位符
                    output_tokens = 200  # 占位符

                    cost_optimizer.record_cost(
                        service_type=service_type,
                        model_name=model_name,
                        input_tokens=input_tokens,
                        output_tokens=output_tokens
                    )

                    return result
                finally:
                    pass  # 记录执行时间等

            return async_wrapper
        else:
            def sync_wrapper(*args, **kwargs):
                cost_optimizer = get_cost_optimizer()
                # 同步版本的实现
                return func(*args, **kwargs)

            return sync_wrapper
    return decorator