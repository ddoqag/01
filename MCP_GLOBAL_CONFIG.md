# Claude MCP 全局配置文档

## 📋 配置概述

本文档记录了 Claude 的 MCP (Model Context Protocol) 全局配置信息，包括已配置的服务器和可用工具。

## 🗂️ 配置文件位置

- **主配置文件**: `C:\Users\ddo\.claude.json`
- **MCP 工具目录**: `C:\Users\ddo\AppData\Roaming\npm\mcp-tools\`
- **DeepSeek MCP 服务器**: `C:\Users\ddo\AppData\Roaming\npm\deepseek_mcp_server.py`

## ⚙️ 已配置的 MCP 服务器

### 1. DeepSeek MCP 服务器 ✅ 已启用
- **名称**: `deepseek-mcp`
- **命令**: `python`
- **参数**: `["C:\\Users\\ddo\\AppData\\Roaming\\npm\\deepseek_mcp_server.py"]`
- **描述**: DeepSeek AI 集成服务器 - 提供通用提问、股票分析和市场分析功能
- **状态**: 已在 `enabledMcpjsonServers` 中启用

### 2. Sugar MCP 服务器 📦 已同步
- **名称**: `sugar-mcp`
- **命令**: `node`
- **参数**: `["C:\\Users\\ddo\\AppData\\Roaming\\npm\\mcp-tools\\sugar-mcp.js"]`
- **描述**: Sugar DevOps MCP 服务器 - 提供 DevOps 相关工具
- **状态**: 已同步到本地，需手动启用

### 3. CloudBase MCP 服务器 ☁️ 可用
- **名称**: `cloudbase`
- **命令**: `npx`
- **参数**: `["@cloudbase/cloudbase-mcp"]`
- **描述**: CloudBase MCP 服务器 - 腾讯云云开发工具
- **状态**: 已安装依赖，可随时启用

## 🛠️ 可用工具

### DeepSeek MCP 工具
- `deepseek_ask` - 向 DeepSeek AI 提出通用问题
- `deepseek_analyze_stock` - 分析指定股票代码
- `deepseek_market_analysis` - 进行市场分析

### 其他 MCP 工具（已同步配置）
- `api_debug_test` - 调试和测试 API 接口
- `knowledge_retrieve` - 检索知识库信息
- `knowledge_store` - 存储信息到知识库

## 📁 同步的文件来源

从 `/d/claude/plugins/marketplaces/claude-code-plugins-plus/plugins/mcp/` 同步的文件：

1. `conversational-api-debugger/.mcp.json`
2. `domain-memory-agent/.mcp.json`
3. `design-to-code/.mcp.json`
4. `project-health-auditor/.mcp.json`
5. `devops/sugar/mcp-server/sugar-mcp.js`

## 🔧 启用其他 MCP 服务器

要启用其他 MCP 服务器，请在 `C:\Users\ddo\.claude.json` 文件中的 `enabledMcpjsonServers` 数组中添加服务器名称：

```json
"enabledMcpjsonServers": ["deepseek-mcp", "sugar-mcp", "cloudbase"]
```

## 📝 使用说明

1. **验证配置**: 使用 `/mcp` 命令检查 MCP 服务器状态
2. **重启 Claude**: 修改配置后需要重启 Claude 应用
3. **查看工具**: 使用 `/help` 查看可用的 MCP 工具
4. **错误排查**: 检查 MCP 服务器的日志输出进行故障排除

## 🕐 同步信息

- **同步日期**: 2025-11-21
- **最后更新**: 2025-11-21 22:30
- **版本**: v1.0
- **维护者**: Claude Assistant

## 🚀 快速启动

要使用配置的 MCP 工具，只需在 Claude 中直接调用相关功能，例如：

- "使用 DeepSeek 分析股票 000042"
- "帮我调试这个 API 接口"
- "将这个信息存储到知识库"

---

*本文档由 Claude 自动生成和维护，最后更新时间: 2025-11-21*