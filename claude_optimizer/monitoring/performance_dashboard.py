#!/usr/bin/env python3
"""
Claude Code 性能监控仪表板
实时监控系统状态和性能指标
"""

import os
import sys
import json
import time
import threading
import logging
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
import http.server
import socketserver
from urllib.parse import urlparse, parse_qs

@dataclass
class PerformanceMetric:
    """性能指标数据类"""
    timestamp: str
    cpu_usage: float
    memory_usage: float
    disk_usage: Dict[str, float]
    network_io: Dict[str, float]
    process_count: int
    response_time: float = 0.0

@dataclass
class AlertConfig:
    """警报配置"""
    metric_name: str
    threshold: float
    comparison: str  # 'gt', 'lt', 'eq'
    enabled: bool = True
    message: str = ""

class PerformanceMonitor:
    """性能监控器"""

    def __init__(self):
        self.setup_directories()
        self.setup_logging()
        self.load_configuration()

        # 监控状态
        self.monitoring_active = False
        self.metrics_history: List[PerformanceMetric] = []
        self.max_history_size = 1000  # 保留最近1000个数据点

        # 警报系统
        self.alerts = []
        self.alert_configs = self.load_alert_configs()

        # Web服务器
        self.server_thread = None
        self.http_server = None
        self.server_port = 8080

    def setup_directories(self):
        """设置工作目录"""
        self.base_dir = Path(__file__).parent.parent
        self.monitoring_dir = self.base_dir / "monitoring"
        self.logs_dir = self.monitoring_dir / "logs"
        self.data_dir = self.monitoring_dir / "data"

        # 确保目录存在
        for directory in [self.monitoring_dir, self.logs_dir, self.data_dir]:
            directory.mkdir(exist_ok=True)

    def setup_logging(self):
        """配置日志"""
        log_file = self.logs_dir / f"performance_monitor_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        self.logger = logging.getLogger('PerformanceMonitor')

        if not self.logger.handlers:
            logging.basicConfig(
                level=logging.INFO,
                format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                handlers=[
                    logging.FileHandler(log_file, encoding='utf-8'),
                    logging.StreamHandler(sys.stdout)
                ]
            )

    def load_configuration(self):
        """加载配置"""
        config_file = self.monitoring_dir / "monitoring_config.json"
        default_config = {
            "sampling_interval": 5,  # 秒
            "alert_thresholds": {
                "cpu_usage": 85.0,
                "memory_usage": 90.0,
                "disk_usage": 85.0,
                "response_time": 5000.0
            },
            "web_server": {
                "enabled": True,
                "port": 8080,
                "host": "localhost"
            },
            "data_retention_days": 7
        }

        try:
            if config_file.exists():
                with open(config_file, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
            else:
                self.config = default_config
                with open(config_file, 'w', encoding='utf-8') as f:
                    json.dump(self.config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.logger.error(f"加载配置失败: {e}")
            self.config = default_config

    def load_alert_configs(self) -> List[AlertConfig]:
        """加载警报配置"""
        configs = []
        thresholds = self.config.get("alert_thresholds", {})

        for metric, threshold in thresholds.items():
            configs.append(AlertConfig(
                metric_name=metric,
                threshold=threshold,
                comparison="gt",
                message=f"{metric} 超过阈值 {threshold}%"
            ))

        return configs

    def get_cpu_usage(self) -> float:
        """获取CPU使用率"""
        try:
            # 使用WMIC获取CPU使用率
            cmd = 'wmic cpu get loadpercentage /value'
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                for line in lines:
                    if 'LoadPercentage' in line:
                        try:
                            return float(line.split('=')[1].strip())
                        except (ValueError, IndexError):
                            pass

            # 备用方法
            cmd = 'powershell "Get-Counter \\'\\Processor(_Total)\\% Processor Time\\' -SampleInterval 1 -MaxSamples 1 | Select-Object -ExpandProperty CounterSamples | Select-Object -ExpandProperty CookedValue"'
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

            if result.returncode == 0:
                try:
                    return float(result.stdout.strip())
                except ValueError:
                    pass

            return 0.0

        except Exception as e:
            self.logger.error(f"获取CPU使用率失败: {e}")
            return 0.0

    def get_memory_usage(self) -> float:
        """获取内存使用率"""
        try:
            cmd = 'wmic OS get TotalVisibleMemorySize,FreePhysicalMemory /value'
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                total_memory = 0
                free_memory = 0

                for line in lines:
                    if 'TotalVisibleMemorySize' in line:
                        total_memory = int(line.split('=')[1].strip())
                    elif 'FreePhysicalMemory' in line:
                        free_memory = int(line.split('=')[1].strip())

                if total_memory > 0:
                    used_memory = total_memory - free_memory
                    return (used_memory / total_memory) * 100

            return 0.0

        except Exception as e:
            self.logger.error(f"获取内存使用率失败: {e}")
            return 0.0

    def get_disk_usage(self) -> Dict[str, float]:
        """获取磁盘使用率"""
        disk_usage = {}

        try:
            # 获取所有驱动器
            cmd = 'wmic logicaldisk get DeviceID /format:csv'
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')[1:]  # 跳过头部
                for line in lines:
                    if line.strip():
                        drive = line.split(',')[0].strip('"')
                        if drive:
                            # 获取驱动器详细信息
                            cmd = f'wmic logicaldisk where "DeviceID=\'{drive}\'" get Size,FreeSpace /value'
                            drive_result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

                            if drive_result.returncode == 0:
                                size = 0
                                free_space = 0
                                for line in drive_result.stdout.strip().split('\n'):
                                    if 'Size' in line and '=' in line:
                                        try:
                                            size = int(line.split('=')[1].strip())
                                        except ValueError:
                                            pass
                                    elif 'FreeSpace' in line and '=' in line:
                                        try:
                                            free_space = int(line.split('=')[1].strip())
                                        except ValueError:
                                            pass

                                if size > 0:
                                    usage_percent = ((size - free_space) / size) * 100
                                    disk_usage[drive] = round(usage_percent, 2)

        except Exception as e:
            self.logger.error(f"获取磁盘使用率失败: {e}")

        return disk_usage

    def get_network_io(self) -> Dict[str, float]:
        """获取网络I/O统计"""
        network_stats = {"bytes_sent": 0, "bytes_received": 0}

        try:
            cmd = 'powershell "Get-Counter \\'\\Network Interface(*)\\Bytes Sent/sec\\' -SampleInterval 1 -MaxSamples 1 | Select-Object -ExpandProperty CounterSamples | Select-Object -ExpandProperty CookedValue"'
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

            if result.returncode == 0 and result.stdout.strip():
                try:
                    network_stats["bytes_sent"] = float(result.stdout.strip())
                except ValueError:
                    pass

            cmd = 'powershell "Get-Counter \\'\\Network Interface(*)\\Bytes Received/sec\\' -SampleInterval 1 -MaxSamples 1 | Select-Object -ExpandProperty CounterSamples | Select-Object -ExpandProperty CookedValue"'
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

            if result.returncode == 0 and result.stdout.strip():
                try:
                    network_stats["bytes_received"] = float(result.stdout.strip())
                except ValueError:
                    pass

        except Exception as e:
            self.logger.error(f"获取网络I/O统计失败: {e}")

        return network_stats

    def get_process_count(self) -> int:
        """获取进程数量"""
        try:
            cmd = 'tasklist /fo csv | find ".exe" | find /c /v ""'
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

            if result.returncode == 0:
                try:
                    return int(result.stdout.strip())
                except ValueError:
                    pass

            # 备用方法
            cmd = 'powershell "Get-Process | Measure-Object | Select-Object -ExpandProperty Count"'
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

            if result.returncode == 0:
                try:
                    return int(result.stdout.strip())
                except ValueError:
                    pass

            return 0

        except Exception as e:
            self.logger.error(f"获取进程数量失败: {e}")
            return 0

    def collect_metrics(self) -> PerformanceMetric:
        """收集性能指标"""
        start_time = time.time()

        metric = PerformanceMetric(
            timestamp=datetime.now().isoformat(),
            cpu_usage=self.get_cpu_usage(),
            memory_usage=self.get_memory_usage(),
            disk_usage=self.get_disk_usage(),
            network_io=self.get_network_io(),
            process_count=self.get_process_count(),
            response_time=0.0
        )

        metric.response_time = (time.time() - start_time) * 1000  # 转换为毫秒

        return metric

    def check_alerts(self, metric: PerformanceMetric) -> List[AlertConfig]:
        """检查警报条件"""
        triggered_alerts = []

        for alert_config in self.alert_configs:
            if not alert_config.enabled:
                continue

            metric_value = 0.0
            if alert_config.metric_name == "cpu_usage":
                metric_value = metric.cpu_usage
            elif alert_config.metric_name == "memory_usage":
                metric_value = metric.memory_usage
            elif alert_config.metric_name == "disk_usage":
                if metric.disk_usage:
                    metric_value = max(metric.disk_usage.values())
            elif alert_config.metric_name == "response_time":
                metric_value = metric.response_time

            # 检查阈值
            if alert_config.comparison == "gt" and metric_value > alert_config.threshold:
                triggered_alerts.append(alert_config)
            elif alert_config.comparison == "lt" and metric_value < alert_config.threshold:
                triggered_alerts.append(alert_config)
            elif alert_config.comparison == "eq" and abs(metric_value - alert_config.threshold) < 0.1:
                triggered_alerts.append(alert_config)

        return triggered_alerts

    def start_monitoring(self):
        """开始监控"""
        if self.monitoring_active:
            self.logger.warning("监控已在运行中")
            return

        self.monitoring_active = True
        self.logger.info("开始性能监控...")

        def monitor_loop():
            while self.monitoring_active:
                try:
                    metric = self.collect_metrics()
                    self.metrics_history.append(metric)

                    # 限制历史记录大小
                    if len(self.metrics_history) > self.max_history_size:
                        self.metrics_history.pop(0)

                    # 检查警报
                    triggered_alerts = self.check_alerts(metric)
                    for alert in triggered_alerts:
                        self.logger.warning(f"警报触发: {alert.message}")
                        self.alerts.append({
                            "timestamp": metric.timestamp,
                            "message": alert.message,
                            "metric_value": getattr(metric, alert.metric_name, 0)
                        })

                    # 保存数据
                    self.save_metrics_data()

                    # 等待下次采样
                    time.sleep(self.config.get("sampling_interval", 5))

                except Exception as e:
                    self.logger.error(f"监控循环错误: {e}")
                    time.sleep(1)

        # 启动监控线程
        monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
        monitor_thread.start()

        # 启动Web服务器
        if self.config.get("web_server", {}).get("enabled", True):
            self.start_web_server()

    def stop_monitoring(self):
        """停止监控"""
        self.monitoring_active = False
        self.logger.info("停止性能监控")

        if self.http_server:
            self.http_server.shutdown()

    def save_metrics_data(self):
        """保存监控数据"""
        try:
            data_file = self.data_dir / f"metrics_{datetime.now().strftime('%Y%m%d')}.json"

            # 转换为可序列化的格式
            serializable_metrics = [asdict(metric) for metric in self.metrics_history[-100:]]  # 保存最近100个数据点

            data = {
                "timestamp": datetime.now().isoformat(),
                "metrics": serializable_metrics,
                "alerts": self.alerts[-50:]  # 保存最近50个警报
            }

            with open(data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

        except Exception as e:
            self.logger.error(f"保存监控数据失败: {e}")

    def start_web_server(self):
        """启动Web服务器"""
        try:
            handler = self.create_request_handler()
            self.http_server = socketserver.TCPServer(
                ("localhost", self.server_port),
                handler
            )

            def server_thread():
                self.http_server.serve_forever()

            thread = threading.Thread(target=server_thread, daemon=True)
            thread.start()

            self.logger.info(f"性能监控仪表板已启动: http://localhost:{self.server_port}")

        except Exception as e:
            self.logger.error(f"启动Web服务器失败: {e}")

    def create_request_handler(self):
        """创建HTTP请求处理器"""
        monitor = self

        class DashboardHandler(http.server.SimpleHTTPRequestHandler):
            def do_GET(self):
                if self.path == '/' or self.path == '/dashboard':
                    self.serve_dashboard()
                elif self.path == '/api/metrics':
                    self.serve_metrics_api()
                elif self.path == '/api/alerts':
                    self.serve_alerts_api()
                elif self.path == '/api/status':
                    self.serve_status_api()
                else:
                    self.send_error(404)

            def serve_dashboard(self):
                """提供仪表板HTML页面"""
                html_content = self.generate_dashboard_html()
                self.send_response(200)
                self.send_header('Content-type', 'text/html; charset=utf-8')
                self.end_headers()
                self.wfile.write(html_content.encode('utf-8'))

            def serve_metrics_api(self):
                """提供指标API"""
                if monitor.metrics_history:
                    latest_metrics = [asdict(m) for m in monitor.metrics_history[-50:]]
                    response = json.dumps({
                        "success": True,
                        "data": latest_metrics
                    }, ensure_ascii=False)
                else:
                    response = json.dumps({
                        "success": True,
                        "data": []
                    })

                self.send_response(200)
                self.send_header('Content-type', 'application/json; charset=utf-8')
                self.end_headers()
                self.wfile.write(response.encode('utf-8'))

            def serve_alerts_api(self):
                """提供警报API"""
                response = json.dumps({
                    "success": True,
                    "data": monitor.alerts[-20:]  # 最近20个警报
                }, ensure_ascii=False)

                self.send_response(200)
                self.send_header('Content-type', 'application/json; charset=utf-8')
                self.end_headers()
                self.wfile.write(response.encode('utf-8'))

            def serve_status_api(self):
                """提供状态API"""
                latest_metric = monitor.metrics_history[-1] if monitor.metrics_history else None

                status = {
                    "monitoring_active": monitor.monitoring_active,
                    "latest_metric": asdict(latest_metric) if latest_metric else None,
                    "metrics_count": len(monitor.metrics_history),
                    "alerts_count": len(monitor.alerts),
                    "uptime": datetime.now().isoformat()
                }

                response = json.dumps({
                    "success": True,
                    "data": status
                }, ensure_ascii=False)

                self.send_response(200)
                self.send_header('Content-type', 'application/json; charset=utf-8')
                self.end_headers()
                self.wfile.write(response.encode('utf-8'))

            def generate_dashboard_html(self):
                """生成仪表板HTML"""
                return f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Claude Code 性能监控仪表板</title>
    <style>
        body {{ font-family: 'Microsoft YaHei', Arial, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5; }}
        .header {{ background-color: #2c3e50; color: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; }}
        .metrics-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin-bottom: 20px; }}
        .metric-card {{ background-color: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .metric-title {{ font-size: 18px; font-weight: bold; margin-bottom: 10px; color: #2c3e50; }}
        .metric-value {{ font-size: 36px; font-weight: bold; margin: 10px 0; }}
        .metric-unit {{ font-size: 14px; color: #7f8c8d; }}
        .status-indicator {{ display: inline-block; width: 12px; height: 12px; border-radius: 50%; margin-right: 8px; }}
        .status-good {{ background-color: #27ae60; }}
        .status-warning {{ background-color: #f39c12; }}
        .status-critical {{ background-color: #e74c3c; }}
        .alerts-section {{ background-color: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .alert-item {{ padding: 10px; margin: 5px 0; border-left: 4px solid #e74c3c; background-color: #fadbd8; border-radius: 4px; }}
        .refresh-info {{ position: fixed; bottom: 20px; right: 20px; background-color: rgba(0,0,0,0.7); color: white; padding: 10px 15px; border-radius: 20px; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Claude Code 性能监控仪表板</h1>
        <p id="status-info">
            <span class="status-indicator" id="status-indicator"></span>
            <span id="status-text">正在加载...</span>
        </p>
    </div>

    <div class="metrics-grid">
        <div class="metric-card">
            <div class="metric-title">CPU 使用率</div>
            <div class="metric-value" id="cpu-value">--</div>
            <div class="metric-unit">百分比</div>
        </div>

        <div class="metric-card">
            <div class="metric-title">内存使用率</div>
            <div class="metric-value" id="memory-value">--</div>
            <div class="metric-unit">百分比</div>
        </div>

        <div class="metric-card">
            <div class="metric-title">磁盘使用率</div>
            <div class="metric-value" id="disk-value">--</div>
            <div class="metric-unit">最高驱动器百分比</div>
        </div>

        <div class="metric-card">
            <div class="metric-title">进程数量</div>
            <div class="metric-value" id="process-value">--</div>
            <div class="metric-unit">个进程</div>
        </div>

        <div class="metric-card">
            <div class="metric-title">响应时间</div>
            <div class="metric-value" id="response-value">--</div>
            <div class="metric-unit">毫秒</div>
        </div>

        <div class="metric-card">
            <div class="metric-title">网络 I/O</div>
            <div class="metric-value" id="network-value">--</div>
            <div class="metric-unit">字节/秒</div>
        </div>
    </div>

    <div class="alerts-section">
        <div class="metric-title">最近警报</div>
        <div id="alerts-container">
            <p>正在加载警报信息...</p>
        </div>
    </div>

    <div class="refresh-info">
        自动刷新: <span id="last-update">--</span>
    </div>

    <script>
        let isMonitoring = false;

        function updateStatus(statusData) {{
            const indicator = document.getElementById('status-indicator');
            const statusText = document.getElementById('status-text');

            if (statusData.monitoring_active) {{
                indicator.className = 'status-indicator status-good';
                statusText.textContent = '监控运行中';
                isMonitoring = true;
            }} else {{
                indicator.className = 'status-indicator status-critical';
                statusText.textContent = '监控已停止';
                isMonitoring = false;
            }}

            document.getElementById('last-update').textContent = new Date().toLocaleTimeString();
        }}

        function updateMetrics(metricData) {{
            if (metricData.length === 0) return;

            const latest = metricData[metricData.length - 1];

            document.getElementById('cpu-value').textContent = latest.cpu_usage.toFixed(1) + '%';
            document.getElementById('memory-value').textContent = latest.memory_usage.toFixed(1) + '%';
            document.getElementById('process-value').textContent = latest.process_count;
            document.getElementById('response-value').textContent = latest.response_time.toFixed(1);

            // 磁盘使用率（取最高值）
            if (latest.disk_usage && Object.keys(latest.disk_usage).length > 0) {{
                const maxDiskUsage = Math.max(...Object.values(latest.disk_usage));
                document.getElementById('disk-value').textContent = maxDiskUsage.toFixed(1) + '%';
            }}

            // 网络I/O
            const totalIO = (latest.network_io.bytes_sent || 0) + (latest.network_io.bytes_received || 0);
            document.getElementById('network-value').textContent = totalIO.toLocaleString();

            // 更新状态颜色
            updateMetricColor('cpu-value', latest.cpu_usage, 80, 95);
            updateMetricColor('memory-value', latest.memory_usage, 85, 95);
            updateMetricColor('response-value', latest.response_time, 2000, 5000);
        }}

        function updateMetricColor(elementId, value, warningThreshold, criticalThreshold) {{
            const element = document.getElementById(elementId);
            if (value >= criticalThreshold) {{
                element.style.color = '#e74c3c';
            }} else if (value >= warningThreshold) {{
                element.style.color = '#f39c12';
            }} else {{
                element.style.color = '#27ae60';
            }}
        }}

        function updateAlerts(alertsData) {{
            const container = document.getElementById('alerts-container');

            if (alertsData.length === 0) {{
                container.innerHTML = '<p>暂无警报</p>';
                return;
            }}

            const alertsHtml = alertsData.slice(-5).reverse().map(alert => `
                <div class="alert-item">
                    <strong>${{new Date(alert.timestamp).toLocaleString()}}</strong><br>
                    ${{alert.message}}
                    ${{alert.metric_value ? ` (当前值: ${{alert.metric_value}})` : ''}}
                </div>
            `).join('');

            container.innerHTML = alertsHtml;
        }}

        async function fetchData() {{
            try {{
                // 获取状态
                const statusResponse = await fetch('/api/status');
                const statusResult = await statusResponse.json();
                if (statusResult.success) {{
                    updateStatus(statusResult.data);
                }}

                // 获取指标
                const metricsResponse = await fetch('/api/metrics');
                const metricsResult = await metricsResponse.json();
                if (metricsResult.success) {{
                    updateMetrics(metricsResult.data);
                }}

                // 获取警报
                const alertsResponse = await fetch('/api/alerts');
                const alertsResult = await alertsResponse.json();
                if (alertsResult.success) {{
                    updateAlerts(alertsResult.data);
                }}

            }} catch (error) {{
                console.error('获取数据失败:', error);
            }}
        }}

        // 初始加载
        fetchData();

        // 定期刷新（每5秒）
        setInterval(fetchData, 5000);

        // 标题更新时间
        document.title = `Claude Code 监控仪表板 - ${{new Date().toLocaleTimeString()}}`;
        setInterval(() => {{
            document.title = `Claude Code 监控仪表板 - ${{new Date().toLocaleTimeString()}}`;
        }}, 1000);
    </script>
</body>
</html>
                """

        return DashboardHandler

def main():
    """主函数"""
    try:
        monitor = PerformanceMonitor()

        print("=== Claude Code 性能监控仪表板 ===")
        print(f"监控端口: {monitor.server_port}")
        print("正在启动监控服务...")

        # 启动监控
        monitor.start_monitoring()

        print("监控服务已启动!")
        print(f"仪表板地址: http://localhost:{monitor.server_port}")
        print("按 Ctrl+C 停止监控")

        # 保持运行
        try:
            while monitor.monitoring_active:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n正在停止监控...")
            monitor.stop_monitoring()
            print("监控已停止")

        return 0

    except Exception as e:
        print(f"性能监控启动失败: {e}")
        return 1

if __name__ == "__main__":
    # 设置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    sys.exit(main())