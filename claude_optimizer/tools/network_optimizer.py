#!/usr/bin/env python3
"""
Windows 网络优化模块
"""

import os
import sys
import json
import logging
import subprocess
from pathlib import Path
from typing import Dict, List

class NetworkOptimizer:
    """Windows 网络优化器"""

    def __init__(self):
        self.logger = logging.getLogger('NetworkOptimizer')

        # 网络优化设置
        self.network_settings = {
            # TCP/IP优化
            "tcpip_settings": {
                "TcpWindowSize": 65535,
                "Tcp1323Opts": 1,
                "DefaultTTL": 64,
                "EnablePMTUDiscovery": 1,
                "SackOpts": 1,
                "MaxFreeTcbs": 65535,
                "MaxHashTableSize": 65536,
                "MaxUserPort": 65534,
                "TcpTimedWaitDelay": 30,
                "KeepAliveTime": 7200000,
                "KeepAliveInterval": 1000
            },

            # DNS优化
            "dns_settings": {
                "primary_dns": "8.8.8.8",
                "secondary_dns": "8.8.4.4"
            },

            # 网络适配器优化
            "adapter_settings": {
                "disable_power_saving": True,
                "enable_jumbo_frames": False,
                "optimize_interrupt": True
            }
        }

    def backup_network_settings(self, backup_dir: Path) -> bool:
        """备份当前网络设置"""
        try:
            backup_file = backup_dir / "network_settings.txt"

            with open(backup_file, 'w', encoding='utf-8') as f:
                f.write("=== 网络设置备份 ===\n")
                f.write(f"备份时间: {subprocess.check_output('date /t', shell=True).decode().strip()}\n\n")

                # 备份TCP/IP设置
                f.write("TCP/IP 设置:\n")
                tcpip_key = "HKEY_LOCAL_MACHINE\\SYSTEM\\CurrentControlSet\\Services\\Tcpip\\Parameters"
                cmd = f'reg query "{tcpip_key}"'
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                if result.returncode == 0:
                    f.write(result.stdout)
                f.write("\n")

                # 备份DNS设置
                f.write("DNS 设置:\n")
                interfaces_key = "HKEY_LOCAL_MACHINE\\SYSTEM\\CurrentControlSet\\Services\\Tcpip\\Parameters\\Interfaces"
                cmd = f'reg query "{interfaces_key}"'
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                if result.returncode == 0:
                    f.write(result.stdout)

            self.logger.info(f"网络设置已备份: {backup_file}")
            return True

        except Exception as e:
            self.logger.error(f"备份网络设置失败: {e}")
            return False

    def optimize_tcpip_settings(self) -> Dict:
        """优化TCP/IP设置"""
        results = {
            "optimized_settings": [],
            "failed_settings": []
        }

        tcpip_key = "HKEY_LOCAL_MACHINE\\SYSTEM\\CurrentControlSet\\Services\\Tcpip\\Parameters"

        for setting_name, setting_value in self.network_settings["tcpip_settings"].items():
            try:
                cmd = f'reg add "{tcpip_key}" /v "{setting_name}" /t REG_DWORD /d {setting_value} /f'
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

                if result.returncode == 0:
                    results["optimized_settings"].append(setting_name)
                    self.logger.info(f"已优化TCP/IP设置: {setting_name} = {setting_value}")
                else:
                    results["failed_settings"].append(setting_name)
                    self.logger.error(f"优化TCP/IP设置失败 {setting_name}: {result.stderr}")

            except Exception as e:
                results["failed_settings"].append(setting_name)
                self.logger.error(f"设置TCP/IP参数时发生错误 {setting_name}: {e}")

        return results

    def optimize_dns_settings(self) -> Dict:
        """优化DNS设置"""
        results = {
            "optimized_interfaces": [],
            "failed_interfaces": []
        }

        try:
            # 获取所有网络接口
            interfaces_key = "HKEY_LOCAL_MACHINE\\SYSTEM\\CurrentControlSet\\Services\\Tcpip\\Parameters\\Interfaces"
            cmd = f'reg query "{interfaces_key}"'
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

            if result.returncode != 0:
                return {"error": "无法获取网络接口列表"}

            interfaces = []
            for line in result.stdout.split('\n'):
                if line.strip().startswith(interfaces_key) and line.strip() != interfaces_key:
                    interface_id = line.strip().split('\\')[-1]
                    interfaces.append(interface_id)

            # 为每个活动接口设置DNS
            for interface_id in interfaces:
                try:
                    interface_key = f"{interfaces_key}\\{interface_id}"

                    # 检查接口是否活动（有IP地址）
                    cmd = f'reg query "{interface_key}" /v "DhcpIPAddress"'
                    ip_result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

                    if ip_result.returncode == 0:
                        # 设置主DNS
                        primary_dns = self.network_settings["dns_settings"]["primary_dns"]
                        cmd = f'reg add "{interface_key}" /v "NameServer" /t REG_SZ /d "{primary_dns}" /f'
                        dns_result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

                        if dns_result.returncode == 0:
                            results["optimized_interfaces"].append(interface_id)
                            self.logger.info(f"已设置DNS服务器: {interface_id} -> {primary_dns}")
                        else:
                            results["failed_interfaces"].append(interface_id)
                            self.logger.error(f"设置DNS失败 {interface_id}: {dns_result.stderr}")

                except Exception as e:
                    results["failed_interfaces"].append(interface_id)
                    self.logger.error(f"优化接口DNS时发生错误 {interface_id}: {e}")

        except Exception as e:
            self.logger.error(f"优化DNS设置失败: {e}")

        return results

    def optimize_network_adapters(self) -> Dict:
        """优化网络适配器设置"""
        results = {
            "optimized_adapters": [],
            "failed_adapters": []
        }

        try:
            # 获取网络适配器列表
            cmd = 'powershell "Get-NetAdapter | Where-Object {$_.Status -eq \'Up\'} | Select-Object Name"'
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

            if result.returncode != 0:
                return {"error": "无法获取网络适配器列表"}

            # 解析适配器名称
            adapter_names = []
            lines = result.stdout.split('\n')
            for line in lines[2:]:  # 跳过头部
                if line.strip():
                    adapter_name = line.strip()
                    if adapter_name and adapter_name != "Name":
                        adapter_names.append(adapter_name)

            for adapter_name in adapter_names:
                try:
                    adapter_results = []

                    # 禁用节能模式
                    if self.network_settings["adapter_settings"]["disable_power_saving"]:
                        cmd = f'powershell "Get-NetAdapter -Name \'{adapter_name}\' | Set-NetAdapterPowerManagement -WakeOnMagicPacket $false -WakeOnPattern $false"'
                        power_result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

                        if power_result.returncode == 0:
                            adapter_results.append("节能模式优化")
                        else:
                            self.logger.warning(f"适配器节能设置失败 {adapter_name}")

                    # 优化中断设置
                    if self.network_settings["adapter_settings"]["optimize_interrupt"]:
                        cmd = f'powershell "Get-NetAdapterAdvancedProperty -Name \'{adapter_name}\' -RegistryKeyword \'*InterruptModeration\' | Set-NetAdapterAdvancedProperty -RegistryValue \'Enabled\'"'
                        interrupt_result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

                        if interrupt_result.returncode == 0:
                            adapter_results.append("中断优化")
                        else:
                            self.logger.warning(f"适配器中断优化失败 {adapter_name}")

                    if adapter_results:
                        results["optimized_adapters"].append({
                            "adapter": adapter_name,
                            "optimizations": adapter_results
                        })
                    else:
                        results["failed_adapters"].append(adapter_name)

                except Exception as e:
                    results["failed_adapters"].append(adapter_name)
                    self.logger.error(f"优化网络适配器时发生错误 {adapter_name}: {e}")

        except Exception as e:
            self.logger.error(f"优化网络适配器失败: {e}")

        return results

    def reset_network_cache(self) -> Dict:
        """重置网络缓存"""
        results = {
            "flushed_caches": [],
            "failed_operations": []
        }

        cache_operations = [
            ("DNS缓存", 'ipconfig /flushdns'),
            ("ARP缓存", 'arp -d'),
            ("NetBIOS缓存", 'nbtstat -R'),
            ("路由表", 'route -f')
        ]

        for cache_name, command in cache_operations:
            try:
                result = subprocess.run(command, shell=True, capture_output=True, text=True)

                if result.returncode == 0:
                    results["flushed_caches"].append(cache_name)
                    self.logger.info(f"已刷新{cache_name}")
                else:
                    results["failed_operations"].append(cache_name)
                    self.logger.warning(f"刷新{cache_name}失败: {result.stderr}")

            except Exception as e:
                results["failed_operations"].append(cache_name)
                self.logger.error(f"刷新{cache_name}时发生错误: {e}")

        return results

    def run_network_optimization(self, backup_dir: Path = None) -> Dict:
        """运行完整的网络优化"""
        results = {
            "tcpip_optimization": None,
            "dns_optimization": None,
            "adapter_optimization": None,
            "cache_reset": None,
            "backup_created": False
        }

        try:
            # 创建备份
            if backup_dir:
                results["backup_created"] = self.backup_network_settings(backup_dir)

            # TCP/IP优化
            results["tcpip_optimization"] = self.optimize_tcpip_settings()

            # DNS优化
            results["dns_optimization"] = self.optimize_dns_settings()

            # 网络适配器优化
            results["adapter_optimization"] = self.optimize_network_adapters()

            # 重置网络缓存
            results["cache_reset"] = self.reset_network_cache()

            return results

        except Exception as e:
            self.logger.error(f"网络优化过程中发生错误: {e}")
            results["error"] = str(e)
            return results

def main():
    """主函数"""
    import tempfile

    try:
        optimizer = NetworkOptimizer()

        # 创建临时备份目录
        backup_dir = Path(tempfile.mkdtemp(prefix="net_backup_"))

        # 执行网络优化
        optimization_results = optimizer.run_network_optimization(backup_dir)

        # 准备返回结果
        success = True
        message = "网络优化完成"

        # 检查优化结果
        if optimization_results.get("tcpip_optimization"):
            tcpip = optimization_results["tcpip_optimization"]
            if tcpip.get("failed_settings"):
                success = False
                message = "网络优化部分失败"

        # 合并结果
        combined_results = {
            "success": success,
            "message": message,
            "details": optimization_results
        }

        # 记录摘要
        logger = logging.getLogger('NetworkOptimizer')
        if success:
            logger.info("网络优化完成")
        else:
            logger.warning("网络优化过程中遇到问题")

        return combined_results

    except Exception as e:
        logger = logging.getLogger('NetworkOptimizer')
        logger.error(f"网络优化器执行失败: {e}")

        return {
            "success": False,
            "message": f"网络优化失败: {str(e)}",
            "details": None
        }

if __name__ == "__main__":
    # 设置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    result = main()
    print(json.dumps(result, indent=2, ensure_ascii=False))