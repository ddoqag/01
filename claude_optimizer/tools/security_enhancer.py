#!/usr/bin/env python3
"""
Windows 安全增强模块
"""

import os
import sys
import json
import logging
import subprocess
from pathlib import Path
from typing import Dict, List

class SecurityEnhancer:
    """Windows 安全增强器"""

    def __init__(self):
        self.logger = logging.getLogger('SecurityEnhancer')

        # 安全增强设置
        self.security_settings = {
            # 用户账户控制(UAC)设置
            "uac_settings": {
                "EnableLUA": 1,
                "ConsentPromptBehaviorAdmin": 5,
                "PromptOnSecureDesktop": 1
            },

            # Windows Defender设置
            "defender_settings": {
                "DisableAntiSpyware": 0,
                "RealtimeProtection": 1,
                "BehaviorMonitoring": 1,
                "IOAVProtection": 1,
                "ScriptScanning": 1
            },

            # 网络安全设置
            "network_security": {
                "enable_firewall": True,
                "block_incoming": True,
                "stealth_mode": True
            },

            # 隐私设置
            "privacy_settings": {
                "disable_telemetry": True,
                "disable_cortana": False,
                "disable_location": True,
                "disable_advertising": True
            },

            # 系统安全设置
            "system_security": {
                "require_password_on_wakeup": True,
                "disable_autoplay": True,
                "enable_secure_boot": True,
                "disable_remote_desktop": False
            }
        }

    def backup_security_settings(self, backup_dir: Path) -> bool:
        """备份当前安全设置"""
        try:
            backup_file = backup_dir / "security_settings.txt"

            with open(backup_file, 'w', encoding='utf-8') as f:
                f.write("=== 安全设置备份 ===\n")
                f.write(f"备份时间: {subprocess.check_output('date /t', shell=True).decode().strip()}\n\n")

                # 备份UAC设置
                f.write("UAC 设置:\n")
                uac_key = "HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Policies\\System"
                cmd = f'reg query "{uac_key}"'
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                if result.returncode == 0:
                    f.write(result.stdout)
                f.write("\n")

                # 备份Windows Defender设置
                f.write("Windows Defender 设置:\n")
                defender_key = "HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Windows Defender"
                cmd = f'reg query "{defender_key}"'
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                if result.returncode == 0:
                    f.write(result.stdout)

                # 备份防火墙设置
                f.write("\n防火墙设置:\n")
                cmd = 'netsh advfirewall show allprofiles'
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                if result.returncode == 0:
                    f.write(result.stdout)

            self.logger.info(f"安全设置已备份: {backup_file}")
            return True

        except Exception as e:
            self.logger.error(f"备份安全设置失败: {e}")
            return False

    def enhance_uac_security(self) -> Dict:
        """增强UAC安全设置"""
        results = {
            "enhanced_settings": [],
            "failed_settings": []
        }

        uac_key = "HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Policies\\System"

        for setting_name, setting_value in self.security_settings["uac_settings"].items():
            try:
                cmd = f'reg add "{uac_key}" /v "{setting_name}" /t REG_DWORD /d {setting_value} /f'
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

                if result.returncode == 0:
                    results["enhanced_settings"].append(setting_name)
                    self.logger.info(f"已设置UAC参数: {setting_name} = {setting_value}")
                else:
                    results["failed_settings"].append(setting_name)
                    self.logger.error(f"设置UAC参数失败 {setting_name}: {result.stderr}")

            except Exception as e:
                results["failed_settings"].append(setting_name)
                self.logger.error(f"设置UAC参数时发生错误 {setting_name}: {e}")

        return results

    def configure_windows_defender(self) -> Dict:
        """配置Windows Defender"""
        results = {
            "configured_features": [],
            "failed_features": []
        }

        try:
            # 检查Windows Defender是否可用
            cmd = 'powershell "Get-MpComputerStatus"'
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

            if result.returncode != 0:
                return {"error": "Windows Defender不可用"}

            # 配置实时保护
            defender_settings = self.security_settings["defender_settings"]

            if defender_settings.get("RealtimeProtection"):
                cmd = 'powershell "Set-MpPreference -DisableRealtimeMonitoring $false"'
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

                if result.returncode == 0:
                    results["configured_features"].append("实时保护")
                    self.logger.info("已启用Windows Defender实时保护")
                else:
                    results["failed_features"].append("实时保护")
                    self.logger.error("启用实时保护失败")

            # 配置行为监控
            if defender_settings.get("BehaviorMonitoring"):
                cmd = 'powershell "Set-MpPreference -DisableBehaviorMonitoring $false"'
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

                if result.returncode == 0:
                    results["configured_features"].append("行为监控")
                    self.logger.info("已启用Windows Defender行为监控")
                else:
                    results["failed_features"].append("行为监控")
                    self.logger.error("启用行为监控失败")

            # 配置IOAV保护
            if defender_settings.get("IOAVProtection"):
                cmd = 'powershell "Set-MpPreference -DisableIOAVProtection $false"'
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

                if result.returncode == 0:
                    results["configured_features"].append("IOAV保护")
                    self.logger.info("已启用Windows Defender IOAV保护")
                else:
                    results["failed_features"].append("IOAV保护")
                    self.logger.error("启用IOAV保护失败")

        except Exception as e:
            self.logger.error(f"配置Windows Defender失败: {e}")
            results["error"] = str(e)

        return results

    def configure_firewall(self) -> Dict:
        """配置Windows防火墙"""
        results = {
            "configured_profiles": [],
            "failed_profiles": []
        }

        network_security = self.security_settings["network_security"]

        try:
            profiles = ["domain", "private", "public"]

            for profile in profiles:
                try:
                    # 启用防火墙
                    if network_security.get("enable_firewall"):
                        cmd = f'netsh advfirewall set {profile}profile state on'
                        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

                        if result.returncode == 0:
                            self.logger.info(f"已启用{profile}防火墙配置")
                        else:
                            results["failed_profiles"].append(f"{profile}防火墙启用")
                            continue

                    # 设置默认阻止入站连接
                    if network_security.get("block_incoming"):
                        cmd = f'netsh advfirewall set {profile}profile firewallpolicy blockinbound,allowoutbound'
                        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

                        if result.returncode == 0:
                            self.logger.info(f"已设置{profile}防火墙阻止入站连接")
                        else:
                            results["failed_profiles"].append(f"{profile}入站阻止")
                            continue

                    # 启用隐身模式
                    if network_security.get("stealth_mode"):
                        cmd = f'netsh advfirewall set {profile}profile set stealthmode enable'
                        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

                        if result.returncode == 0:
                            self.logger.info(f"已启用{profile}防火墙隐身模式")
                        else:
                            self.logger.warning(f"{profile}防火墙隐身模式设置失败")

                    results["configured_profiles"].append(profile)

                except Exception as e:
                    results["failed_profiles"].append(f"{profile}配置错误")
                    self.logger.error(f"配置{profile}防火墙时发生错误: {e}")

        except Exception as e:
            self.logger.error(f"配置防火墙失败: {e}")
            results["error"] = str(e)

        return results

    def enhance_privacy_settings(self) -> Dict:
        """增强隐私设置"""
        results = {
            "enhanced_privacy": [],
            "failed_enhancements": []
        }

        privacy_settings = self.security_settings["privacy_settings"]

        # 禁用遥测
        if privacy_settings.get("disable_telemetry"):
            try:
                telemetry_key = "HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Policies\\DataCollection"
                cmd = f'reg add "{telemetry_key}" /v "AllowTelemetry" /t REG_DWORD /d 0 /f'
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

                if result.returncode == 0:
                    results["enhanced_privacy"].append("禁用遥测")
                    self.logger.info("已禁用Windows遥测")
                else:
                    results["failed_enhancements"].append("禁用遥测")

            except Exception as e:
                results["failed_enhancements"].append("禁用遥测")
                self.logger.error(f"禁用遥测失败: {e}")

        # 禁用位置服务
        if privacy_settings.get("disable_location"):
            try:
                location_key = "HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\CapabilityAccessManager\\ConsentStore\\location"
                cmd = f'reg add "{location_key}" /v "Value" /t REG_SZ /d "Deny" /f'
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

                if result.returncode == 0:
                    results["enhanced_privacy"].append("禁用位置服务")
                    self.logger.info("已禁用位置服务")
                else:
                    results["failed_enhancements"].append("禁用位置服务")

            except Exception as e:
                results["failed_enhancements"].append("禁用位置服务")
                self.logger.error(f"禁用位置服务失败: {e}")

        # 禁用广告ID
        if privacy_settings.get("disable_advertising"):
            try:
                advertising_key = "HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\AdvertisingInfo"
                cmd = f'reg add "{advertising_key}" /v "Enabled" /t REG_DWORD /d 0 /f'
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

                if result.returncode == 0:
                    results["enhanced_privacy"].append("禁用广告ID")
                    self.logger.info("已禁用广告ID")
                else:
                    results["failed_enhancements"].append("禁用广告ID")

            except Exception as e:
                results["failed_enhancements"].append("禁用广告ID")
                self.logger.error(f"禁用广告ID失败: {e}")

        return results

    def enhance_system_security(self) -> Dict:
        """增强系统安全设置"""
        results = {
            "enhanced_features": [],
            "failed_features": []
        }

        system_security = self.security_settings["system_security"]

        # 禁用自动播放
        if system_security.get("disable_autoplay"):
            try:
                autoplay_key = "HKEY_CURRENT_USER\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\AutoplayHandlers"
                cmd = f'reg add "{autoplay_key}" /v "DisableAutoplay" /t REG_DWORD /d 1 /f'
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

                if result.returncode == 0:
                    results["enhanced_features"].append("禁用自动播放")
                    self.logger.info("已禁用自动播放")
                else:
                    results["failed_features"].append("禁用自动播放")

            except Exception as e:
                results["failed_features"].append("禁用自动播放")
                self.logger.error(f"禁用自动播放失败: {e}")

        # 设置唤醒时需要密码
        if system_security.get("require_password_on_wakeup"):
            try:
                power_key = "HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Policies\\System"
                cmd = f'reg add "{power_key}" /v "SoftwareSASGeneration" /t REG_DWORD /d 1 /f'
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

                if result.returncode == 0:
                    results["enhanced_features"].append("唤醒时密码要求")
                    self.logger.info("已设置唤醒时需要密码")
                else:
                    results["failed_features"].append("唤醒时密码要求")

            except Exception as e:
                results["failed_features"].append("唤醒时密码要求")
                self.logger.error(f"设置唤醒密码要求失败: {e}")

        return results

    def run_security_enhancement(self, backup_dir: Path = None) -> Dict:
        """运行完整的安全增强"""
        results = {
            "uac_enhancement": None,
            "defender_configuration": None,
            "firewall_configuration": None,
            "privacy_enhancement": None,
            "system_security": None,
            "backup_created": False
        }

        try:
            # 创建备份
            if backup_dir:
                results["backup_created"] = self.backup_security_settings(backup_dir)

            # UAC安全增强
            results["uac_enhancement"] = self.enhance_uac_security()

            # Windows Defender配置
            results["defender_configuration"] = self.configure_windows_defender()

            # 防火墙配置
            results["firewall_configuration"] = self.configure_firewall()

            # 隐私设置增强
            results["privacy_enhancement"] = self.enhance_privacy_settings()

            # 系统安全增强
            results["system_security"] = self.enhance_system_security()

            return results

        except Exception as e:
            self.logger.error(f"安全增强过程中发生错误: {e}")
            results["error"] = str(e)
            return results

def main():
    """主函数"""
    import tempfile

    try:
        enhancer = SecurityEnhancer()

        # 创建临时备份目录
        backup_dir = Path(tempfile.mkdtemp(prefix="sec_backup_"))

        # 执行安全增强
        enhancement_results = enhancer.run_security_enhancement(backup_dir)

        # 准备返回结果
        success = True
        message = "安全增强完成"

        # 检查增强结果
        failed_count = 0
        for key, result in enhancement_results.items():
            if isinstance(result, dict) and "failed_settings" in result:
                failed_count += len(result.get("failed_settings", []))

        if failed_count > 0:
            success = False
            message = f"安全增强部分失败 ({failed_count} 项失败)"

        # 合并结果
        combined_results = {
            "success": success,
            "message": message,
            "details": enhancement_results
        }

        # 记录摘要
        logger = logging.getLogger('SecurityEnhancer')
        if success:
            logger.info("安全增强完成")
        else:
            logger.warning("安全增强过程中遇到问题")

        return combined_results

    except Exception as e:
        logger = logging.getLogger('SecurityEnhancer')
        logger.error(f"安全增强器执行失败: {e}")

        return {
            "success": False,
            "message": f"安全增强失败: {str(e)}",
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