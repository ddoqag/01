#!/usr/bin/env python3
"""
Claude Code 智能配置管理器
自动管理Claude和MCP配置
"""

import os
import sys
import json
import shutil
import logging
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict

@dataclass
class ConfigVersion:
    """配置版本信息"""
    version: str
    timestamp: str
    description: str
    file_hash: str
    backup_path: str
    changes: List[str]

class IntelligentConfigManager:
    """智能配置管理器"""

    def __init__(self):
        self.setup_directories()
        self.setup_logging()
        self.load_metadata()

        # 配置文件路径
        self.config_files = {
            "claude_settings": {
                "path": Path.home() / ".claude" / "CLAUDE.md",
                "description": "Claude用户配置文件",
                "critical": True
            },
            "mcp_servers": {
                "path": Path.home() / ".claude" / "mcp_servers.json",
                "description": "MCP服务器配置",
                "critical": True
            },
            "claude_global": {
                "path": Path.home() / ".claude" / "claude_desktop_config.json",
                "description": "Claude桌面应用配置",
                "critical": False
            },
            "npm_config": {
                "path": Path.home() / ".npmrc",
                "description": "NPM配置文件",
                "critical": False
            },
            "git_config": {
                "path": Path.home() / ".gitconfig",
                "description": "Git全局配置",
                "critical": False
            }
        }

    def setup_directories(self):
        """设置工作目录"""
        self.base_dir = Path(__file__).parent
        self.config_backup_dir = self.base_dir / "backups" / "configs"
        self.config_template_dir = self.base_dir / "configs" / "templates"
        self.metadata_file = self.config_backup_dir / "config_metadata.json"

        # 确保目录存在
        self.config_backup_dir.mkdir(parents=True, exist_ok=True)
        self.config_template_dir.mkdir(parents=True, exist_ok=True)

    def setup_logging(self):
        """配置日志"""
        log_file = self.base_dir / "logs" / f"config_manager_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        self.logger = logging.getLogger('ConfigManager')

        if not self.logger.handlers:
            logging.basicConfig(
                level=logging.INFO,
                format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                handlers=[
                    logging.FileHandler(log_file, encoding='utf-8'),
                    logging.StreamHandler(sys.stdout)
                ]
            )

    def load_metadata(self):
        """加载配置元数据"""
        try:
            if self.metadata_file.exists():
                with open(self.metadata_file, 'r', encoding='utf-8') as f:
                    self.metadata = json.load(f)
            else:
                self.metadata = {
                    "versions": {},
                    "current_versions": {},
                    "last_update": datetime.now().isoformat()
                }
        except Exception as e:
            self.logger.error(f"加载元数据失败: {e}")
            self.metadata = {
                "versions": {},
                "current_versions": {},
                "last_update": datetime.now().isoformat()
            }

    def save_metadata(self):
        """保存配置元数据"""
        try:
            self.metadata["last_update"] = datetime.now().isoformat()
            with open(self.metadata_file, 'w', encoding='utf-8') as f:
                json.dump(self.metadata, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.logger.error(f"保存元数据失败: {e}")

    def calculate_file_hash(self, file_path: Path) -> str:
        """计算文件哈希值"""
        try:
            if not file_path.exists():
                return ""

            hasher = hashlib.sha256()
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hasher.update(chunk)
            return hasher.hexdigest()
        except Exception as e:
            self.logger.error(f"计算文件哈希失败 {file_path}: {e}")
            return ""

    def create_config_backup(self, config_name: str, description: str = "") -> bool:
        """创建配置备份"""
        try:
            if config_name not in self.config_files:
                self.logger.error(f"未知的配置文件: {config_name}")
                return False

            config_info = self.config_files[config_name]
            config_path = config_info["path"]

            if not config_path.exists():
                self.logger.warning(f"配置文件不存在: {config_path}")
                return False

            # 创建备份文件名
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"{config_name}_{timestamp}.backup"
            backup_path = self.config_backup_dir / backup_filename

            # 复制文件
            shutil.copy2(config_path, backup_path)

            # 计算文件哈希
            file_hash = self.calculate_file_hash(config_path)

            # 创建版本信息
            version_info = ConfigVersion(
                version=f"v{len(self.metadata.get('versions', {}).get(config_name, [])) + 1}",
                timestamp=datetime.now().isoformat(),
                description=description or f"自动备份 - {timestamp}",
                file_hash=file_hash,
                backup_path=str(backup_path),
                changes=[]
            )

            # 更新元数据
            if config_name not in self.metadata["versions"]:
                self.metadata["versions"][config_name] = []
            self.metadata["versions"][config_name].append(asdict(version_info))
            self.metadata["current_versions"][config_name] = version_info.version

            # 保存元数据
            self.save_metadata()

            self.logger.info(f"配置备份完成: {config_name} -> {backup_filename}")
            return True

        except Exception as e:
            self.logger.error(f"创建配置备份失败 {config_name}: {e}")
            return False

    def restore_config_version(self, config_name: str, version: str) -> bool:
        """恢复指定版本的配置"""
        try:
            if config_name not in self.metadata["versions"]:
                self.logger.error(f"没有找到配置的版本历史: {config_name}")
                return False

            # 查找指定版本
            version_data = None
            for v in self.metadata["versions"][config_name]:
                if v["version"] == version:
                    version_data = v
                    break

            if not version_data:
                self.logger.error(f"版本不存在: {config_name} v{version}")
                return False

            backup_path = Path(version_data["backup_path"])
            if not backup_path.exists():
                self.logger.error(f"备份文件不存在: {backup_path}")
                return False

            # 创建当前配置的备份
            self.create_config_backup(config_name, f"恢复前备份 - v{version}")

            # 恢复配置
            config_path = self.config_files[config_name]["path"]
            config_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(backup_path, config_path)

            self.logger.info(f"配置恢复完成: {config_name} -> {version}")
            return True

        except Exception as e:
            self.logger.error(f"恢复配置版本失败 {config_name} v{version}: {e}")
            return False

    def validate_config_syntax(self, config_path: Path) -> Dict:
        """验证配置文件语法"""
        try:
            if not config_path.exists():
                return {"valid": False, "error": "文件不存在"}

            file_extension = config_path.suffix.lower()

            if file_extension == '.json':
                try:
                    with open(config_path, 'r', encoding='utf-8') as f:
                        json.load(f)
                    return {"valid": True, "type": "JSON"}
                except json.JSONDecodeError as e:
                    return {"valid": False, "error": f"JSON语法错误: {e}"}

            elif file_extension == '.md':
                # 简单的Markdown语法检查
                try:
                    with open(config_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    # 基本检查
                    if len(content.strip()) == 0:
                        return {"valid": False, "error": "文件为空"}
                    return {"valid": True, "type": "Markdown"}
                except Exception as e:
                    return {"valid": False, "error": f"读取文件失败: {e}"}

            else:
                # 其他文件类型，检查是否可读
                try:
                    with open(config_path, 'r', encoding='utf-8') as f:
                        f.read()
                    return {"valid": True, "type": "Text"}
                except Exception as e:
                    return {"valid": False, "error": f"文件读取失败: {e}"}

        except Exception as e:
            return {"valid": False, "error": f"验证失败: {e}"}

    def auto_optimize_claude_config(self) -> Dict:
        """自动优化Claude配置"""
        results = {
            "optimized_files": [],
            "skipped_files": [],
            "errors": []
        }

        try:
            # 优化CLAUDE.md
            claude_config_path = Path.home() / ".claude" / "CLAUDE.md"
            if claude_config_path.exists():
                # 创建备份
                self.create_config_backup("claude_settings", "优化前备份")

                # 分析并优化配置
                with open(claude_config_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                # 检查常见优化点
                optimizations = []

                # 检查编码设置
                if "encoding" not in content.lower() or "utf-8" not in content.lower():
                    optimizations.append("建议添加UTF-8编码设置")

                # 检查中文设置
                if "中文" not in content and "chinese" not in content.lower():
                    optimizations.append("建议添加中文语言支持")

                # 检查Windows特定设置
                if "windows" not in content.lower():
                    optimizations.append("建议添加Windows特定优化设置")

                if optimizations:
                    self.logger.info(f"Claude配置优化建议: {'; '.join(optimizations)}")
                    results["optimized_files"].append({
                        "file": "CLAUDE.md",
                        "suggestions": optimizations
                    })
                else:
                    results["skipped_files"].append({
                        "file": "CLAUDE.md",
                        "reason": "配置已优化"
                    })

            # 优化MCP服务器配置
            mcp_config_path = Path.home() / ".claude" / "mcp_servers.json"
            if mcp_config_path.exists():
                # 创建备份
                self.create_config_backup("mcp_servers", "优化前备份")

                # 验证JSON语法
                validation = self.validate_config_syntax(mcp_config_path)
                if validation["valid"]:
                    with open(mcp_config_path, 'r', encoding='utf-8') as f:
                        mcp_config = json.load(f)

                    # 检查MCP配置优化
                    if "mcpServers" in mcp_config:
                        servers = mcp_config["mcpServers"]
                        server_count = len(servers)
                        if server_count == 0:
                            optimizations = ["建议添加有用的MCP服务器"]
                        else:
                            optimizations = [f"已配置 {server_count} 个MCP服务器"]

                        results["optimized_files"].append({
                            "file": "mcp_servers.json",
                            "suggestions": optimizations,
                            "server_count": server_count
                        })
                    else:
                        results["errors"].append({
                            "file": "mcp_servers.json",
                            "error": "缺少mcpServers配置"
                        })
                else:
                    results["errors"].append({
                        "file": "mcp_servers.json",
                        "error": f"JSON语法错误: {validation['error']}"
                    })

            return results

        except Exception as e:
            self.logger.error(f"自动优化Claude配置失败: {e}")
            results["errors"].append({
                "file": "general",
                "error": str(e)
            })
            return results

    def sync_configurations(self) -> Dict:
        """同步配置到所有相关位置"""
        results = {
            "synced_files": [],
            "skipped_files": [],
            "errors": []
        }

        try:
            # 同步Claude配置
            claude_config_path = Path.home() / ".claude" / "CLAUDE.md"
            if claude_config_path.exists():
                # 检查是否需要在项目中复制配置
                current_dir = Path.cwd()
                project_claude_path = current_dir / ".claude" / "CLAUDE.md"

                if project_claude_path.exists():
                    # 比较文件内容
                    home_hash = self.calculate_file_hash(claude_config_path)
                    project_hash = self.calculate_file_hash(project_claude_path)

                    if home_hash != project_hash:
                        # 复制更新的配置
                        shutil.copy2(claude_config_path, project_claude_path)
                        results["synced_files"].append({
                            "from": str(claude_config_path),
                            "to": str(project_claude_path),
                            "action": "更新项目配置"
                        })
                    else:
                        results["skipped_files"].append({
                            "file": str(project_claude_path),
                            "reason": "配置已是最新"
                        })

            # 同步MCP服务器配置到多个位置
            mcp_config_path = Path.home() / ".claude" / "mcp_servers.json"
            if mcp_config_path.exists():
                # 查找其他可能的MCP配置位置
                potential_paths = [
                    Path.home() / ".claude" / "claude_desktop_config.json",
                    Path.home() / ".config" / "claude" / "mcp_servers.json"
                ]

                for target_path in potential_paths:
                    try:
                        if target_path.exists():
                            # 简单的合并逻辑
                            with open(mcp_config_path, 'r', encoding='utf-8') as f:
                                source_config = json.load(f)
                            with open(target_path, 'r', encoding='utf-8') as f:
                                target_config = json.load(f)

                            # 合并MCP服务器配置
                            if "mcpServers" in source_config and "mcpServers" in target_config:
                                merged_servers = {**target_config["mcpServers"], **source_config["mcpServers"]}
                                target_config["mcpServers"] = merged_servers

                                # 写入更新后的配置
                                with open(target_path, 'w', encoding='utf-8') as f:
                                    json.dump(target_config, f, indent=2, ensure_ascii=False)

                                results["synced_files"].append({
                                    "from": str(mcp_config_path),
                                    "to": str(target_path),
                                    "action": "合并MCP服务器配置"
                                })

                    except Exception as e:
                        results["errors"].append({
                            "file": str(target_path),
                            "error": f"同步失败: {str(e)}"
                        })

            return results

        except Exception as e:
            self.logger.error(f"配置同步失败: {e}")
            results["errors"].append({
                "file": "general",
                "error": str(e)
            })
            return results

    def get_config_status(self) -> Dict:
        """获取配置状态概览"""
        status = {
            "total_configs": len(self.config_files),
            "existing_configs": 0,
            "backup_count": 0,
            "last_backup": None,
            "config_details": [],
            "recommendations": []
        }

        try:
            for config_name, config_info in self.config_files.items():
                config_path = config_info["path"]
                config_detail = {
                    "name": config_name,
                    "description": config_info["description"],
                    "critical": config_info["critical"],
                    "exists": config_path.exists(),
                    "path": str(config_path),
                    "last_modified": None,
                    "file_size": 0,
                    "backup_count": 0,
                    "current_version": None
                }

                if config_path.exists():
                    status["existing_configs"] += 1
                    config_detail["last_modified"] = datetime.fromtimestamp(
                        config_path.stat().st_mtime
                    ).isoformat()
                    config_detail["file_size"] = config_path.stat().st_size

                # 检查备份情况
                if config_name in self.metadata["versions"]:
                    config_detail["backup_count"] = len(self.metadata["versions"][config_name])
                    status["backup_count"] += len(self.metadata["versions"][config_name])
                    if config_name in self.metadata["current_versions"]:
                        config_detail["current_version"] = self.metadata["current_versions"][config_name]

                status["config_details"].append(config_detail)

            # 获取最后备份时间
            if self.metadata.get("versions"):
                latest_backup = None
                for versions in self.metadata["versions"].values():
                    for version in versions:
                        if latest_backup is None or version["timestamp"] > latest_backup:
                            latest_backup = version["timestamp"]
                status["last_backup"] = latest_backup

            # 生成建议
            if status["existing_configs"] < status["total_configs"]:
                status["recommendations"].append("某些配置文件缺失，建议创建默认配置")

            if status["backup_count"] == 0:
                status["recommendations"].append("没有配置备份，建议立即创建备份")

            critical_configs = [c for c in status["config_details"] if c["critical"] and not c["exists"]]
            if critical_configs:
                status["recommendations"].append(f"关键配置文件缺失: {', '.join(c['name'] for c in critical_configs)}")

            return status

        except Exception as e:
            self.logger.error(f"获取配置状态失败: {e}")
            status["error"] = str(e)
            return status

def main():
    """主函数"""
    try:
        manager = IntelligentConfigManager()

        # 执行配置管理任务
        tasks = [
            ("创建配置备份", lambda: manager.create_config_backup("claude_settings", "定期备份")),
            ("优化Claude配置", manager.auto_optimize_claude_config),
            ("同步配置", manager.sync_configurations),
            ("获取配置状态", manager.get_config_status)
        ]

        results = {
            "success": True,
            "message": "配置管理任务完成",
            "task_results": {}
        }

        for task_name, task_func in tasks:
            try:
                task_result = task_func()
                results["task_results"][task_name] = task_result
                manager.logger.info(f"任务完成: {task_name}")

            except Exception as e:
                manager.logger.error(f"任务失败 {task_name}: {e}")
                results["task_results"][task_name] = {"error": str(e)}
                results["success"] = False

        return results

    except Exception as e:
        logger = logging.getLogger('ConfigManager')
        logger.error(f"配置管理器执行失败: {e}")

        return {
            "success": False,
            "message": f"配置管理失败: {str(e)}",
            "task_results": None
        }

if __name__ == "__main__":
    # 设置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    result = main()
    print(json.dumps(result, indent=2, ensure_ascii=False))