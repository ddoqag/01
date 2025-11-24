# DeepSeek MCP集成指南

## 🎯 概述

本指南详细说明了如何将DeepSeek AI功能集成到Claude Code中，通过MCP（Model Context Protocol）实现统一的AI工具调用接口。

## 📋 集成组件

### 1. 核心文件

- `deepseek_mcp_server.py` - MCP服务器实现
- `deepseek_mcp_integration.py` - DeepSeek API集成模块
- `.claude/claude_desktop_config.json` - MCP服务器配置
- `.claude/commands/mcp.md` - 自定义Slash命令定义
- `verify_mcp_integration.py` - 集成验证脚本

### 2. 提供的工具

| 工具名称 | 描述 | 参数 |
|---------|------|------|
| `deepseek_ask` | 通用问题回答 | `question` (字符串) |
| `deepseek_analyze_stock` | 股票分析 | `stock_code` (字符串) |
| `deepseek_market_analysis` | 市场分析 | `query` (字符串) |

## 🚀 快速开始

### 1. 环境配置

设置DeepSeek API密钥：

```bash
# Windows CMD
set DEEPSEEK_API_KEY=your_api_key_here

# Windows PowerShell
$env:DEEPSEEK_API_KEY="your_api_key_here"

# 添加到用户环境变量（永久生效）
# 控制面板 → 系统 → 高级系统设置 → 环境变量
```

### 2. 验证集成

运行验证脚本：

```bash
python verify_mcp_integration.py
```

### 3. 重启Claude Code

重启Claude Code以加载新的MCP服务器配置。

## 📖 使用方法

### 通过Slash命令

#### 1. 通用问题回答

```bash
/mcp deepseek ask "什么是Python requests库？"
/mcp deepseek ask "解释一下量化交易的基本原理"
```

#### 2. 股票分析

```bash
/mcp deepseek analyze 000042
/mcp deepseek analyze 600519
/mcp deepseek analyze "贵州茅台"
```

#### 3. 市场分析

```bash
/mcp deepseek market "今日A股市场走势分析"
/mcp deepseek market "新能源汽车板块前景"
```

### 通过对话方式

直接与Claude对话：

```
请使用deepseek MCP服务器帮我分析股票000042
```

```
请用DeepSeek分析一下当前的市场情况
```

## 🔧 技术实现

### MCP服务器架构

```
Claude Code ←→ MCP Protocol ←→ DeepSeek MCP Server ←→ DeepSeek API
```

### 通信流程

1. **初始化**: Claude Code启动MCP服务器
2. **工具发现**: Claude Code获取可用工具列表
3. **工具调用**: 用户通过命令触发工具调用
4. **结果返回**: 结果通过MCP协议返回给用户

### 数据流

```
用户输入 → Slash命令解析 → 工具参数提取 → MCP工具调用 → API请求 → 结果处理 → 格式化输出
```

## 📊 响应格式

所有工具调用返回统一的响应格式：

```json
{
  "success": true,
  "content_type": "text/html",
  "extracted_info": {
    "has_html": true,
    "found_content": false,
    "possible_answers": [],
    "debug_info": ["配置加载成功", "初始化完成"]
  }
}
```

### 成功响应示例

```json
{
  "success": true,
  "tool": "deepseek_ask",
  "question": "什么是MCP？",
  "result": "MCP（Model Context Protocol）是...",
  "extracted_info": {
    "has_answer": true,
    "question": "什么是MCP？",
    "model": "deepseek-chat"
  }
}
```

### 错误响应示例

```json
{
  "success": false,
  "error": "API密钥未设置",
  "extracted_info": {
    "has_answer": false,
    "error": "DEEPSEEK_API_KEY环境变量未设置"
  }
}
```

## 🛠️ 故障排除

### 常见问题

#### 1. MCP服务器启动失败

**症状**: 命令无响应或返回错误

**解决方案**:
```bash
# 检查Python环境
python --version

# 检查模块导入
python -c "import deepseek_mcp_integration"

# 检查配置文件
cat .claude/claude_desktop_config.json
```

#### 2. API密钥错误

**症状**: 返回认证失败错误

**解决方案**:
```bash
# 检查环境变量
echo $DEEPSEEK_API_KEY

# 重新设置环境变量
export DEEPSEEK_API_KEY="your_key_here"
```

#### 3. 工具调用失败

**症状**: 工具返回错误或无响应

**解决方案**:
```bash
# 运行验证脚本
python verify_mcp_integration.py

# 手动测试模块
python deepseek_mcp_integration.py
```

### 调试模式

启用详细日志输出：

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 🔄 更新和维护

### 更新DeepSeek API

1. 修改 `deepseek_mcp_integration.py` 中的API端点
2. 更新请求参数格式
3. 测试新的API功能

### 添加新工具

1. 在 `deepseek_mcp_integration.py` 中添加新方法
2. 在 `deepseek_mcp_server.py` 中注册工具
3. 更新工具调用逻辑
4. 更新文档

### 性能优化

1. **缓存机制**: 实现API响应缓存
2. **批量处理**: 支持批量API调用
3. **异步处理**: 使用asyncio提升并发性能

## 📈 扩展建议

### 1. 增强功能

- **多模态支持**: 支持图像分析
- **流式响应**: 实现实时响应流
- **上下文管理**: 维护对话上下文

### 2. 集成扩展

- **其他AI服务**: 集成更多AI服务提供商
- **本地模型**: 支持本地大语言模型
- **专业工具**: 添加行业专业工具

### 3. 监控和分析

- **使用统计**: 记录工具使用情况
- **性能监控**: 监控API响应时间
- **成本跟踪**: 跟踪API使用成本

## 📞 支持和反馈

如遇到问题或有改进建议，请：

1. 运行 `verify_mcp_integration.py` 获取诊断信息
2. 检查Claude Code日志文件
3. 查看MCP服务器错误输出
4. 提供详细的错误信息和复现步骤

---

*最后更新: 2025-11-21*