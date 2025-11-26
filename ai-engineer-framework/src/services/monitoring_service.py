"""
监控和可观测性服务

提供性能监控、指标收集、日志记录等功能
"""

import asyncio
import time
import json
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union, Callable
from enum import Enum
from collections import defaultdict, deque
from datetime import datetime, timedelta
import threading

from pydantic import BaseModel, Field


class MetricType(str, Enum):
    """指标类型"""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"


class LogLevel(str, Enum):
    """日志级别"""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class AlertLevel(str, Enum):
    """告警级别"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class MetricPoint:
    """指标数据点"""
    name: str
    value: float
    labels: Dict[str, str] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "name": self.name,
            "value": self.value,
            "labels": self.labels,
            "timestamp": self.timestamp
        }


@dataclass
class LogEntry:
    """日志条目"""
    level: LogLevel
    message: str
    timestamp: float = field(default_factory=time.time)
    context: Dict[str, Any] = field(default_factory=dict)
    trace_id: Optional[str] = None
    span_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "level": self.level.value,
            "message": self.message,
            "timestamp": self.timestamp,
            "context": self.context,
            "trace_id": self.trace_id,
            "span_id": self.span_id
        }


@dataclass
class Alert:
    """告警"""
    id: str
    name: str
    level: AlertLevel
    message: str
    condition: str
    timestamp: float = field(default_factory=time.time)
    resolved: bool = False
    resolved_at: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def resolve(self) -> None:
        """解决告警"""
        self.resolved = True
        self.resolved_at = time.time()

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "id": self.id,
            "name": self.name,
            "level": self.level.value,
            "message": self.message,
            "condition": self.condition,
            "timestamp": self.timestamp,
            "resolved": self.resolved,
            "resolved_at": self.resolved_at,
            "metadata": self.metadata
        }


class MonitoringConfig(BaseModel):
    """监控配置"""
    # 指标配置
    metrics_enabled: bool = Field(True, description="是否启用指标收集")
    metrics_retention_hours: int = Field(24, description="指标保留时间（小时）")
    metrics_flush_interval: int = Field(60, description="指标刷新间隔（秒）")

    # 日志配置
    logging_enabled: bool = Field(True, description="是否启用日志记录")
    log_level: LogLevel = Field(LogLevel.INFO, description="日志级别")
    log_retention_hours: int = Field(168, description="日志保留时间（小时）")

    # 告警配置
    alerts_enabled: bool = Field(True, description="是否启用告警")
    alert_evaluation_interval: int = Field(30, description="告警评估间隔（秒）")

    # 性能监控配置
    performance_monitoring: bool = Field(True, description="是否启用性能监控")
    slow_query_threshold: float = Field(5.0, description="慢查询阈值（秒）")
    memory_usage_threshold: float = Field(0.8, description="内存使用阈值")

    # 外部集成配置
    prometheus_enabled: bool = Field(False, description="是否启用Prometheus集成")
    prometheus_port: int = Field(8080, description="Prometheus端口")

    opentelemetry_enabled: bool = Field(False, description="是否启用OpenTelemetry")
    sentry_enabled: bool = Field(False, description="是否启用Sentry错误追踪")


class MetricsCollector:
    """指标收集器"""

    def __init__(self, config: MonitoringConfig):
        self.config = config
        self._counters: Dict[str, float] = defaultdict(float)
        self._gauges: Dict[str, float] = {}
        self._histograms: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self._lock = threading.Lock()

    def increment_counter(self, name: str, value: float = 1.0, labels: Optional[Dict[str, str]] = None) -> None:
        """增加计数器"""
        if not self.config.metrics_enabled:
            return

        with self._lock:
            key = self._make_key(name, labels)
            self._counters[key] += value

    def set_gauge(self, name: str, value: float, labels: Optional[Dict[str, str]] = None) -> None:
        """设置仪表盘值"""
        if not self.config.metrics_enabled:
            return

        with self._lock:
            key = self._make_key(name, labels)
            self._gauges[key] = value

    def observe_histogram(self, name: str, value: float, labels: Optional[Dict[str, str]] = None) -> None:
        """观察直方图值"""
        if not self.config.metrics_enabled:
            return

        with self._lock:
            key = self._make_key(name, labels)
            self._histograms[key].append(value)

    def get_counter(self, name: str, labels: Optional[Dict[str, str]] = None) -> float:
        """获取计数器值"""
        key = self._make_key(name, labels)
        return self._counters.get(key, 0.0)

    def get_gauge(self, name: str, labels: Optional[Dict[str, str]] = None) -> Optional[float]:
        """获取仪表盘值"""
        key = self._make_key(name, labels)
        return self._gauges.get(key)

    def get_histogram_stats(self, name: str, labels: Optional[Dict[str, str]] = None) -> Dict[str, float]:
        """获取直方图统计信息"""
        key = self._make_key(name, labels)
        values = list(self._histograms.get(key, []))

        if not values:
            return {}

        values.sort()
        count = len(values)
        total = sum(values)

        return {
            "count": count,
            "sum": total,
            "avg": total / count,
            "min": values[0],
            "max": values[-1],
            "p50": values[int(count * 0.5)],
            "p90": values[int(count * 0.9)],
            "p95": values[int(count * 0.95)],
            "p99": values[int(count * 0.99)],
        }

    def _make_key(self, name: str, labels: Optional[Dict[str, str]] = None) -> str:
        """生成指标键"""
        if not labels:
            return name

        label_str = ",".join(f"{k}={v}" for k, v in sorted(labels.items()))
        return f"{name}{{{label_str}}}"

    def get_all_metrics(self) -> Dict[str, Any]:
        """获取所有指标"""
        with self._lock:
            result = {
                "counters": dict(self._counters),
                "gauges": dict(self._gauges),
                "histograms": {
                    key: self.get_histogram_stats_from_key(key)
                    for key in self._histograms.keys()
                }
            }
            return result

    def get_histogram_stats_from_key(self, key: str) -> Dict[str, float]:
        """从键获取直方图统计信息"""
        values = list(self._histograms.get(key, []))
        if not values:
            return {}

        values.sort()
        count = len(values)
        total = sum(values)

        return {
            "count": count,
            "sum": total,
            "avg": total / count,
            "min": values[0],
            "max": values[-1],
            "p50": values[int(count * 0.5)],
            "p90": values[int(count * 0.9)],
            "p95": values[int(count * 0.95)],
            "p99": values[int(count * 0.99)],
        }


class Logger:
    """结构化日志记录器"""

    def __init__(self, config: MonitoringConfig):
        self.config = config
        self._logs: deque = deque(maxlen=10000)
        self._lock = threading.Lock()

    def debug(self, message: str, **context) -> None:
        """记录调试日志"""
        self._log(LogLevel.DEBUG, message, **context)

    def info(self, message: str, **context) -> None:
        """记录信息日志"""
        self._log(LogLevel.INFO, message, **context)

    def warning(self, message: str, **context) -> None:
        """记录警告日志"""
        self._log(LogLevel.WARNING, message, **context)

    def error(self, message: str, **context) -> None:
        """记录错误日志"""
        self._log(LogLevel.ERROR, message, **context)

    def critical(self, message: str, **context) -> None:
        """记录严重错误日志"""
        self._log(LogLevel.CRITICAL, message, **context)

    def _log(self, level: LogLevel, message: str, **context) -> None:
        """内部日志记录方法"""
        if not self.config.logging_enabled:
            return

        # 检查日志级别
        if not self._should_log(level):
            return

        entry = LogEntry(
            level=level,
            message=message,
            context=context,
            timestamp=time.time()
        )

        with self._lock:
            self._logs.append(entry)

        # 如果启用了外部集成，发送到外部系统
        if self.config.sentry_enabled and level.value in ["error", "critical"]:
            self._send_to_sentry(entry)

    def _should_log(self, level: LogLevel) -> bool:
        """检查是否应该记录该级别的日志"""
        level_order = {
            LogLevel.DEBUG: 0,
            LogLevel.INFO: 1,
            LogLevel.WARNING: 2,
            LogLevel.ERROR: 3,
            LogLevel.CRITICAL: 4
        }

        return level_order[level] >= level_order[self.config.log_level]

    def _send_to_sentry(self, entry: LogEntry) -> None:
        """发送到Sentry"""
        try:
            import sentry_sdk
            sentry_sdk.capture_message(
                entry.message,
                level=entry.level.value,
                extra=entry.context
            )
        except ImportError:
            pass
        except Exception as e:
            print(f"Failed to send log to Sentry: {e}")

    def get_logs(
        self,
        level: Optional[LogLevel] = None,
        limit: int = 100,
        since: Optional[float] = None
    ) -> List[LogEntry]:
        """获取日志"""
        with self._lock:
            logs = list(self._logs)

        # 过滤条件
        if level:
            logs = [log for log in logs if log.level == level]

        if since:
            logs = [log for log in logs if log.timestamp >= since]

        # 排序和限制
        logs.sort(key=lambda x: x.timestamp, reverse=True)
        return logs[:limit]

    def get_log_stats(self) -> Dict[str, Any]:
        """获取日志统计"""
        with self._lock:
            logs = list(self._logs)

        if not logs:
            return {}

        level_counts = defaultdict(int)
        for log in logs:
            level_counts[log.level.value] += 1

        return {
            "total_logs": len(logs),
            "level_counts": dict(level_counts),
            "oldest_log": min(log.timestamp for log in logs),
            "newest_log": max(log.timestamp for log in logs)
        }


class AlertManager:
    """告警管理器"""

    def __init__(self, config: MonitoringConfig):
        self.config = config
        self._alerts: Dict[str, Alert] = {}
        self._rules: List[Dict[str, Any]] = []
        self._lock = threading.Lock()

    def add_alert_rule(self, name: str, condition: str, level: AlertLevel, message: str) -> None:
        """添加告警规则"""
        rule = {
            "name": name,
            "condition": condition,
            "level": level,
            "message": message
        }
        self._rules.append(rule)

    def evaluate_alerts(self, metrics: Dict[str, Any]) -> List[Alert]:
        """评估告警条件"""
        if not self.config.alerts_enabled:
            return []

        new_alerts = []

        for rule in self._rules:
            try:
                # 简化的条件评估（实际实现需要更复杂的表达式解析）
                if self._evaluate_condition(rule["condition"], metrics):
                    alert = Alert(
                        id=str(time.time()),
                        name=rule["name"],
                        level=rule["level"],
                        message=rule["message"],
                        condition=rule["condition"]
                    )

                    with self._lock:
                        # 检查是否已存在相同的活跃告警
                        existing_key = f"{rule['name']}_{rule['condition']}"
                        if existing_key not in self._alerts or self._alerts[existing_key].resolved:
                            self._alerts[existing_key] = alert
                            new_alerts.append(alert)

            except Exception as e:
                print(f"Alert evaluation error for rule {rule['name']}: {e}")

        # 检查已解决的告警
        resolved_alerts = []
        with self._lock:
            for key, alert in self._alerts.items():
                if not alert.resolved:
                    # 检查条件是否仍然满足
                    if not self._evaluate_condition(alert.condition, metrics):
                        alert.resolve()
                        resolved_alerts.append(alert)

        return new_alerts

    def _evaluate_condition(self, condition: str, metrics: Dict[str, Any]) -> bool:
        """评估告警条件"""
        # 简化的条件评估实现
        # 实际实现应该使用安全的表达式解析器
        try:
            # 替换指标引用
            safe_locals = {
                "counters": metrics.get("counters", {}),
                "gauges": metrics.get("gauges", {}),
                "histograms": metrics.get("histograms", {}),
            }

            # 简单的表达式替换
            for metric_type, metric_data in safe_locals.items():
                for metric_name, value in metric_data.items():
                    condition = condition.replace(metric_name, str(value))

            return eval(condition, {"__builtins__": {}}, safe_locals)
        except:
            return False

    def get_active_alerts(self) -> List[Alert]:
        """获取活跃告警"""
        with self._lock:
            return [alert for alert in self._alerts.values() if not alert.resolved]

    def get_all_alerts(self) -> List[Alert]:
        """获取所有告警"""
        with self._lock:
            return list(self._alerts.values())


class PerformanceMonitor:
    """性能监控器"""

    def __init__(self, config: MonitoringConfig):
        self.config = config
        self._active_operations: Dict[str, float] = {}
        self._lock = threading.Lock()

    def start_operation(self, operation_id: str) -> None:
        """开始操作计时"""
        if not self.config.performance_monitoring:
            return

        with self._lock:
            self._active_operations[operation_id] = time.time()

    def end_operation(self, operation_id: str) -> Optional[float]:
        """结束操作计时并返回耗时"""
        if not self.config.performance_monitoring:
            return None

        with self._lock:
            start_time = self._active_operations.pop(operation_id, None)
            if start_time:
                duration = time.time() - start_time
                return duration
            return None

    async def monitor_operation(self, operation_id: str, coro):
        """监控协程操作的性能"""
        self.start_operation(operation_id)
        try:
            return await coro
        finally:
            duration = self.end_operation(operation_id)
            if duration and duration > self.config.slow_query_threshold:
                print(f"Slow operation detected: {operation_id} took {duration:.2f}s")


class MonitoringService:
    """监控服务主类"""

    def __init__(self, config: MonitoringConfig):
        self.config = config
        self.metrics = MetricsCollector(config)
        self.logger = Logger(config)
        self.alert_manager = AlertManager(config)
        self.performance_monitor = PerformanceMonitor(config)
        self._running = False
        self._monitoring_task: Optional[asyncio.Task] = None

    async def start(self) -> None:
        """启动监控服务"""
        self._running = True

        # 启动后台监控任务
        self._monitoring_task = asyncio.create_task(self._monitoring_loop())

        # 初始化外部集成
        if self.config.opentelemetry_enabled:
            self._init_opentelemetry()

        if self.config.prometheus_enabled:
            self._init_prometheus()

        self.logger.info("Monitoring service started")

    async def stop(self) -> None:
        """停止监控服务"""
        self._running = False

        if self._monitoring_task:
            self._monitoring_task.cancel()
            try:
                await self._monitoring_task
            except asyncio.CancelledError:
                pass

        self.logger.info("Monitoring service stopped")

    async def _monitoring_loop(self) -> None:
        """监控循环"""
        while self._running:
            try:
                # 评估告警
                all_metrics = self.metrics.get_all_metrics()
                new_alerts = self.alert_manager.evaluate_alerts(all_metrics)

                # 处理新告警
                for alert in new_alerts:
                    await self._handle_alert(alert)

                # 清理过期数据
                self._cleanup_expired_data()

                await asyncio.sleep(self.config.alert_evaluation_interval)

            except Exception as e:
                self.logger.error(f"Monitoring loop error: {e}")
                await asyncio.sleep(5)

    async def _handle_alert(self, alert: Alert) -> None:
        """处理告警"""
        self.logger.warning(
            f"Alert triggered: {alert.name} - {alert.message}",
            alert_id=alert.id,
            alert_level=alert.level.value
        )

        # 这里可以添加更多的告警处理逻辑，比如发送邮件、短信等

    def _cleanup_expired_data(self) -> None:
        """清理过期数据"""
        current_time = time.time()
        # 实现数据清理逻辑
        pass

    def _init_opentelemetry(self) -> None:
        """初始化OpenTelemetry"""
        try:
            from opentelemetry import trace
            from opentelemetry.exporter.jaeger.thrift import JaegerExporter
            from opentelemetry.sdk.trace import TracerProvider
            from opentelemetry.sdk.trace.export import BatchSpanProcessor

            # 配置追踪器
            trace.set_tracer_provider(TracerProvider())
            tracer = trace.get_tracer(__name__)

            # 配置导出器
            jaeger_exporter = JaegerExporter(
                agent_host_name="localhost",
                agent_port=6831,
            )

            span_processor = BatchSpanProcessor(jaeger_exporter)
            trace.get_tracer_provider().add_span_processor(span_processor)

            self.logger.info("OpenTelemetry initialized")

        except ImportError:
            self.logger.warning("OpenTelemetry not available")
        except Exception as e:
            self.logger.error(f"Failed to initialize OpenTelemetry: {e}")

    def _init_prometheus(self) -> None:
        """初始化Prometheus"""
        try:
            from prometheus_client import start_http_server, Counter, Gauge, Histogram

            # 启动HTTP服务器
            start_http_server(self.config.prometheus_port)

            self.logger.info(f"Prometheus server started on port {self.config.prometheus_port}")

        except ImportError:
            self.logger.warning("Prometheus client not available")
        except Exception as e:
            self.logger.error(f"Failed to initialize Prometheus: {e}")

    async def health_check(self) -> bool:
        """健康检查"""
        try:
            # 检查各项服务状态
            return True
        except Exception as e:
            self.logger.error(f"Health check failed: {e}")
            return False

    def get_monitoring_summary(self) -> Dict[str, Any]:
        """获取监控摘要"""
        return {
            "metrics": self.metrics.get_all_metrics(),
            "logs": self.logger.get_log_stats(),
            "alerts": {
                "active": len(self.alert_manager.get_active_alerts()),
                "total": len(self.alert_manager.get_all_alerts())
            },
            "config": self.config.dict()
        }


# 装饰器
def monitor_performance(operation_name: Optional[str] = None):
    """性能监控装饰器"""
    def decorator(func):
        if asyncio.iscoroutinefunction(func):
            async def async_wrapper(*args, **kwargs):
                monitoring_service = get_monitoring_service()
                op_name = operation_name or f"{func.__module__}.{func.__name__}"
                return await monitoring_service.performance_monitor.monitor_operation(op_name, func(*args, **kwargs))
            return async_wrapper
        else:
            def sync_wrapper(*args, **kwargs):
                monitoring_service = get_monitoring_service()
                op_name = operation_name or f"{func.__module__}.{func.__name__}"
                monitoring_service.performance_monitor.start_operation(op_name)
                try:
                    result = func(*args, **kwargs)
                    return result
                finally:
                    monitoring_service.performance_monitor.end_operation(op_name)
            return sync_wrapper
    return decorator


# 全局监控服务实例
_monitoring_service: Optional[MonitoringService] = None


def get_monitoring_service() -> MonitoringService:
    """获取全局监控服务实例"""
    global _monitoring_service
    if _monitoring_service is None:
        config = MonitoringConfig()
        _monitoring_service = MonitoringService(config)
    return _monitoring_service


async def init_monitoring(config: MonitoringConfig) -> MonitoringService:
    """初始化全局监控服务"""
    global _monitoring_service
    _monitoring_service = MonitoringService(config)
    await _monitoring_service.start()
    return _monitoring_service