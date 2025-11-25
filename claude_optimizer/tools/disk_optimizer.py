#!/usr/bin/env python3
"""
Windows 磁盘优化和清理模块
"""

import os
import sys
import subprocess
import json
import logging
import tempfile
from pathlib import Path
from typing import Dict, List, Tuple

class DiskOptimizer:
    """Windows 磁盘优化器"""

    def __init__(self):
        self.logger = logging.getLogger('DiskOptimizer')

        # 临时文件和缓存目录
        self.temp_directories = [
            "%TEMP%",
            "%TMP%",
            "%WINDIR%\\Temp",
            "%LOCALAPPDATA%\\Temp",
            "%APPDATA%\\Microsoft\\Windows\\Recent",
            "%LOCALAPPDATA%\\Microsoft\\Windows\\Explorer",
            "%WINDIR%\\Prefetch",
            "%WINDIR%\\SoftwareDistribution\\Download",
            "%WINDIR%\\SoftwareDistribution\\SelfUpdate"
        ]

        # 清理选项配置
        self.cleanmgr_options = [
            "/SAGERUN:1",     # 运行设置1的清理选项
            "/VERYLOWDISK",   # 低磁盘空间模式
            "/SETUP",         # 清理安装文件
            "/AUTOCLEAN"      # 自动清理
        ]

    def get_disk_info(self, drive_letter: str = None) -> Dict:
        """获取磁盘信息"""
        try:
            if drive_letter is None:
                drive_letter = "C:"

            cmd = f'wmic logicaldisk where "DeviceID=\'{drive_letter}\'" get Size,FreeSpace,VolumeName,FileSystem /format:csv'
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

            if result.returncode != 0:
                return {"error": f"无法获取磁盘信息: {result.stderr}"}

            lines = result.stdout.strip().split('\n')
            if len(lines) < 2:
                return {"error": "磁盘信息解析失败"}

            # 跳过CSV头部，解析数据行
            data_line = lines[1]
            parts = data_line.split(',')

            if len(parts) >= 5:
                node = parts[0].strip('"')
                volume_name = parts[1].strip('"') or "无标签"
                free_space = int(parts[2].strip('"')) if parts[2].strip('"') else 0
                size = int(parts[3].strip('"')) if parts[3].strip('"') else 0
                filesystem = parts[4].strip('"')

                free_space_gb = free_space // (1024**3)
                size_gb = size // (1024**3)
                used_space_gb = size_gb - free_space_gb
                usage_percent = (used_space_gb / size_gb * 100) if size_gb > 0 else 0

                return {
                    "drive": drive_letter,
                    "volume_name": volume_name,
                    "filesystem": filesystem,
                    "total_gb": size_gb,
                    "free_gb": free_space_gb,
                    "used_gb": used_space_gb,
                    "usage_percent": round(usage_percent, 2),
                    "free_percent": round(free_space_gb / size_gb * 100, 2) if size_gb > 0 else 0
                }

            return {"error": "磁盘信息格式不正确"}

        except Exception as e:
            self.logger.error(f"获取磁盘信息失败 {drive_letter}: {e}")
            return {"error": str(e)}

    def analyze_disk_space(self) -> Dict:
        """分析磁盘空间使用情况"""
        try:
            # 获取所有驱动器信息
            drives = []
            cmd = 'wmic logicaldisk get DeviceID /format:csv'
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')[1:]  # 跳过头部
                for line in lines:
                    if line.strip():
                        drive = line.split(',')[0].strip('"')
                        if drive:
                            drives.append(drive)

            # 分析每个驱动器
            analysis = {
                "drives": [],
                "total_space_gb": 0,
                "total_free_gb": 0,
                "recommendations": []
            }

            for drive in drives:
                drive_info = self.get_disk_info(drive)
                if "error" not in drive_info:
                    analysis["drives"].append(drive_info)
                    analysis["total_space_gb"] += drive_info["total_gb"]
                    analysis["total_free_gb"] += drive_info["free_gb"]

                    # 生成建议
                    if drive_info["usage_percent"] > 90:
                        analysis["recommendations"].append(
                            f"{drive} 盘空间严重不足 ({drive_info['usage_percent']}%)，建议立即清理"
                        )
                    elif drive_info["usage_percent"] > 80:
                        analysis["recommendations"].append(
                            f"{drive} 盘空间不足 ({drive_info['usage_percent']}%)，建议清理"
                        )
                    elif drive_info["usage_percent"] > 70:
                        analysis["recommendations"].append(
                            f"{drive} 盘使用率较高 ({drive_info['usage_percent']}%)，可以考虑清理"
                        )

            # 计算总体使用率
            if analysis["total_space_gb"] > 0:
                total_usage_percent = ((analysis["total_space_gb"] - analysis["total_free_gb"]) /
                                     analysis["total_space_gb"] * 100)
                analysis["total_usage_percent"] = round(total_usage_percent, 2)

            return analysis

        except Exception as e:
            self.logger.error(f"分析磁盘空间时发生错误: {e}")
            return {"error": str(e)}

    def clean_temp_files(self) -> Dict:
        """清理临时文件"""
        results = {
            "cleaned_directories": 0,
            "skipped_directories": 0,
            "failed_directories": 0,
            "space_freed_mb": 0,
            "details": []
        }

        for temp_dir in self.temp_directories:
            try:
                # 展开环境变量
                expanded_path = os.path.expandvars(temp_dir)
                temp_path = Path(expanded_path)

                if not temp_path.exists():
                    results["skipped_directories"] += 1
                    results["details"].append({
                        "directory": temp_dir,
                        "status": "skipped",
                        "message": "目录不存在"
                    })
                    continue

                # 计算目录大小
                initial_size = 0
                try:
                    cmd = f'du -s "{temp_path}" 2>nul || echo 0'
                    size_result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                    if size_result.returncode == 0:
                        try:
                            initial_size = int(size_result.stdout.strip().split()[0]) // 1024  # 转换为MB
                        except (ValueError, IndexError):
                            pass
                except:
                    pass

                # 清理目录内容（保留目录结构）
                try:
                    for item in temp_path.iterdir():
                        if item.is_file():
                            try:
                                item.unlink()
                            except (PermissionError, FileNotFoundError):
                                pass
                        elif item.is_dir():
                            try:
                                import shutil
                                shutil.rmtree(item, ignore_errors=True)
                            except:
                                pass

                    # 计算释放的空间
                    cmd = f'du -s "{temp_path}" 2>nul || echo 0'
                    size_result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                    final_size = 0
                    if size_result.returncode == 0:
                        try:
                            final_size = int(size_result.stdout.strip().split()[0]) // 1024
                        except (ValueError, IndexError):
                            pass

                    space_freed = max(0, initial_size - final_size)
                    results["space_freed_mb"] += space_freed

                    results["cleaned_directories"] += 1
                    results["details"].append({
                        "directory": temp_dir,
                        "status": "success",
                        "space_freed_mb": space_freed,
                        "message": f"清理完成，释放 {space_freed} MB"
                    })

                except Exception as clean_error:
                    results["failed_directories"] += 1
                    results["details"].append({
                        "directory": temp_dir,
                        "status": "failed",
                        "message": f"清理失败: {str(clean_error)}"
                    })

            except Exception as e:
                self.logger.error(f"处理临时目录时发生错误 {temp_dir}: {e}")
                results["failed_directories"] += 1
                results["details"].append({
                    "directory": temp_dir,
                    "status": "error",
                    "message": f"处理错误: {str(e)}"
                })

        return results

    def run_disk_cleanup(self) -> Dict:
        """运行Windows磁盘清理工具"""
        try:
            self.logger.info("开始运行Windows磁盘清理工具...")

            # 创建SAGESET配置文件
            cmd = 'cleanmgr /sageset:1'
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

            # 这通常需要用户交互，所以我们使用自动清理选项
            for option in self.cleanmgr_options:
                cmd = f'cleanmgr {option}'
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

                if result.returncode == 0:
                    self.logger.info(f"磁盘清理选项 {option} 执行成功")
                else:
                    self.logger.warning(f"磁盘清理选项 {option} 执行失败: {result.stderr}")

            return {
                "success": True,
                "message": "Windows磁盘清理工具执行完成",
                "details": "使用自动清理选项完成系统清理"
            }

        except Exception as e:
            self.logger.error(f"运行磁盘清理工具时发生错误: {e}")
            return {
                "success": False,
                "message": f"磁盘清理失败: {str(e)}",
                "details": None
            }

    def defrag_disk(self, drive_letter: str = "C:") -> Dict:
        """碎片整理磁盘"""
        try:
            self.logger.info(f"开始碎片整理磁盘: {drive_letter}")

            # 检查是否为SSD
            cmd = f'powershell "Get-WmiObject -Class Win32_LogicalDisk | Where-Object {{$_.DeviceID -eq \'{drive_letter}\'}} | Select-Object MediaType"'
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

            is_ssd = False
            try:
                # 在Windows中，SSD通常没有MediaType或显示"Fixed hard disk media"
                if "Fixed hard disk media" in result.stdout or "SSD" in result.stdout.upper():
                    is_ssd = True
            except:
                pass

            if is_ssd:
                self.logger.info(f"检测到SSD磁盘 {drive_letter}，跳过碎片整理")
                return {
                    "success": True,
                    "message": f"{drive_letter} 是SSD，无需碎片整理",
                    "details": "SSD不需要进行碎片整理"
                }

            # 执行碎片整理
            cmd = f'defrag {drive_letter} /A /V'  # 分析模式
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

            if result.returncode == 0:
                # 提取碎片信息
                fragmentation_info = result.stdout

                # 如果碎片率较高，执行整理
                if "8%" in fragmentation_info or "fragmented" in fragmentation_info.lower():
                    cmd = f'defrag {drive_letter} /V'
                    defrag_result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

                    if defrag_result.returncode == 0:
                        return {
                            "success": True,
                            "message": f"{drive_letter} 磁盘碎片整理完成",
                            "details": defrag_result.stdout
                        }
                    else:
                        return {
                            "success": False,
                            "message": f"磁盘碎片整理失败: {defrag_result.stderr}",
                            "details": None
                        }
                else:
                    return {
                        "success": True,
                        "message": f"{drive_letter} 磁盘碎片率低，无需整理",
                        "details": fragmentation_info
                    }
            else:
                return {
                    "success": False,
                    "message": f"磁盘分析失败: {result.stderr}",
                    "details": None
                }

        except Exception as e:
            self.logger.error(f"碎片整理磁盘时发生错误 {drive_letter}: {e}")
            return {
                "success": False,
                "message": f"碎片整理失败: {str(e)}",
                "details": None
            }

    def optimize_disk(self, backup_dir: Path = None) -> Dict:
        """执行完整的磁盘优化"""
        results = {
            "initial_analysis": None,
            "temp_cleaning": None,
            "disk_cleanup": None,
            "defragmentation": None,
            "final_analysis": None,
            "total_space_freed_mb": 0
        }

        try:
            # 初始磁盘分析
            results["initial_analysis"] = self.analyze_disk_space()

            # 清理临时文件
            results["temp_cleaning"] = self.clean_temp_files()
            if results["temp_cleaning"]:
                results["total_space_freed_mb"] += results["temp_cleaning"].get("space_freed_mb", 0)

            # 运行Windows磁盘清理
            results["disk_cleanup"] = self.run_disk_cleanup()

            # 碎片整理
            results["defragmentation"] = self.defrag_disk()

            # 最终磁盘分析
            results["final_analysis"] = self.analyze_disk_space()

            # 计算总体空间节省
            if (results["initial_analysis"] and results["final_analysis"] and
                "error" not in results["initial_analysis"] and "error" not in results["final_analysis"]):

                initial_free = results["initial_analysis"]["total_free_gb"] * 1024
                final_free = results["final_analysis"]["total_free_gb"] * 1024
                additional_freed = final_free - initial_free
                results["total_space_freed_mb"] += max(0, additional_freed)

            return results

        except Exception as e:
            self.logger.error(f"磁盘优化过程中发生错误: {e}")
            results["error"] = str(e)
            return results

def main():
    """主函数"""
    import tempfile

    try:
        optimizer = DiskOptimizer()

        # 创建临时备份目录
        backup_dir = Path(tempfile.mkdtemp(prefix="disk_backup_"))

        # 执行磁盘优化
        optimization_results = optimizer.optimize_disk(backup_dir)

        # 准备返回结果
        success = True
        message = "磁盘优化完成"

        # 检查是否有错误
        error_messages = []
        for stage, result in optimization_results.items():
            if result and isinstance(result, dict) and "error" in result:
                error_messages.append(f"{stage}: {result['error']}")

        if error_messages:
            success = False
            message = f"磁盘优化部分失败: {'; '.join(error_messages)}"

        combined_results = {
            "success": success,
            "message": message,
            "details": optimization_results
        }

        # 记录摘要
        logger = logging.getLogger('DiskOptimizer')
        if success:
            total_freed_mb = optimization_results.get("total_space_freed_mb", 0)
            logger.info(f"磁盘优化完成，总计释放空间: {total_freed_mb} MB")
        else:
            logger.warning("磁盘优化过程中遇到错误")

        return combined_results

    except Exception as e:
        logger = logging.getLogger('DiskOptimizer')
        logger.error(f"磁盘优化器执行失败: {e}")

        return {
            "success": False,
            "message": f"磁盘优化失败: {str(e)}",
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