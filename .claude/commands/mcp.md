---
description: 与MCP服务器交互的统一接口
argument-hint: [server-name] [action] [arguments...]
---

# MCP服务器交互工具

您正在使用MCP（Model Context Protocol）服务器交互工具。此工具提供与配置的MCP服务器通信的统一接口。

## 当前服务器状态

### ✅ 在线服务器
- **context7**: https://mcp.context7.com/mcp - 获取最新技术文档
- **web-search-prime**: https://open.bigmodel.cn/api/mcp/web_search_prime/mcp - 网页搜索
- **web-reader**: https://open.bigmodel.cn/api/mcp/web_reader/mcp - 网页内容读取

### ❌ 离线服务器
- **zhipu-mcp**: 智谱AI集成 (基于HTTP API的新实现)
- **web-scraping-mcp**: 网页抓取 (简化版实现)
- **cloudbase**: 腾讯云开发 (需要重新配置)
- **deepseek-mcp**: DeepSeek AI集成 (需要修复API配置)

## 支持的服务器

### context7 - 技术文档获取
- **描述**: 获取最新的技术文档和代码示例
- **状态**: ✅ 正常工作
- **使用方法**: 直接询问技术库的API文档，系统会自动调用context7

### web-search-prime - 网页搜索
- **描述**: 搜索网页信息，返回包含标题、URL、摘要等结构化结果
- **状态**: ✅ 正常工作
- **工具**: `mcp__web-search-prime__webSearchPrime`

### web-reader - 网页内容读取
- **描述**: 获取网页内容并转换为适合大模型处理的格式
- **状态**: ✅ 正常工作
- **工具**: `mcp__web-reader__webReader`

### zhipu-mcp - 智谱AI集成 (新实现)
- **描述**: 基于智谱AI HTTP API的GLM模型对话和分析功能
- **状态**: 🔄 重新配置中
- **工具**:
  - `zhipu_chat`: GLM模型对话问答
  - `zhipu_analyze`: 文本分析和总结
- **配置**: 使用官方智谱AI API，需要有效的API密钥

### web-scraping-mcp - 网页抓取 (简化版)
- **描述**: 提供基本的网页内容提取功能
- **状态**: 🔄 重新配置中
- **工具**:
  - `web_check`: 检查网页可访问性
  - `web_simple_fetch`: 获取网页HTML内容
- **配置**: 简化版实现，减少外部依赖

## 使用方法

### 基本语法
```
/mcp [action] [arguments...]
```

### 可用操作

#### 1. 查看服务器状态
```
/mcp status
/mcp list
```

#### 2. 使用在线服务器

##### context7 - 技术文档查询 (自动调用)
```
# 直接询问技术文档，系统会自动调用context7
"React hooks的useEffect怎么使用？"
"Next.js 14的新特性有哪些"
```

##### web-search-prime - 网页搜索
```
/mcp search "Python异步编程最佳实践"
/mcp search "2024年前端技术趋势"
```

##### web-reader - 网页内容读取
```
/mcp read https://example.com/article
/mcp read https://docs.python.org/3/library/asyncio.html
```

#### 3. 新配置服务器使用

##### zhipu-mcp - 智谱AI对话
```
# GLM模型对话问答
"请用智谱AI分析一下当前的AI发展趋势"

# 文本分析
"使用智谱AI总结这篇文章的主要内容"
```

##### web-scraping-mcp - 网页抓取
```
# 检查网页可访问性
/mcp web-scraping check https://example.com

# 获取网页内容
/mcp web-scraping fetch https://example.com
```

#### 4. 离线服务器故障排除

##### 检查所有服务器状态
```
/mcp status          # 查看所有服务器状态
/mcp debug <server>   # 检查特定服务器详细信息
claude mcp list       # 使用原生命令查看MCP配置
claude mcp get <name> # 获取服务器详细配置
```

## 工具调用流程

1. **检查服务器状态**: 验证目标MCP服务器是否在线
2. **解析参数**: 解析用户提供的操作类型和参数
3. **调用工具**: 根据操作类型调用相应的MCP工具
4. **格式化输出**: 将结果以用户友好的格式展示

## 响应格式

工具返回的结果将包含以下信息：
- **success**: 操作是否成功
- **tool**: 使用的工具名称
- **result**: 工具执行结果
- **error**: 错误信息（如果失败）

## 故障排除

### 常见问题

#### 1. 服务器连接失败
**原因**: 多个stdio服务器连接失败
**解决方案**:
- 检查Python环境配置
- 验证npx包安装状态
- 确认API密钥有效性

#### 2. 服务器状态说明
**在线服务器** (✅):
- **context7**: 自动调用技术文档查询
- **web-search-prime**: 网页搜索功能
- **web-reader**: 网页内容读取

**重新配置中服务器** (🔄):
- **zhipu-mcp**: 新的智谱AI集成实现，基于官方HTTP API
- **web-scraping-mcp**: 简化版网页抓取实现，减少依赖

**需要修复服务器** (❌):
- **deepseek-mcp**: DeepSeek AI集成，需要修复API配置
- **cloudbase**: 腾讯云开发，需要重新配置npx包

### 调试命令
```
/mcp status          # 查看所有服务器状态
/mcp debug <server>   # 检查特定服务器详细信息
claude mcp list       # 使用原生命令查看MCP配置
claude mcp get <name> # 获取服务器详细配置
```

### 修复离线服务器

#### 测试新配置的服务器
```bash
# 测试智谱AI服务器
python3 C:\Users\ddo\AppData\Roaming\npm\zhipu_mcp_server.py --test

# 测试网页抓取服务器
python3 C:\Users\ddo\AppData\Roaming\npm\web_scraping_simple_mcp_server.py --test
```

#### 修复 DeepSeek 服务器
```bash
# 检查API密钥
echo $DEEPSEEK_API_KEY

# 重新配置服务器
claude mcp remove deepseek-mcp
claude mcp add deepseek-mcp --env DEEPSEEK_API_KEY=$DEEPSEEK_API_KEY -- python3 C:\Users\ddo\AppData\Roaming\npm\deepseek_mcp_server.py
```

#### 重新配置 cloudbase 服务器
```bash
# 检查npx包
npx @cloudbase/cloudbase-mcp --help

# 重新配置
claude mcp remove cloudbase
claude mcp add cloudbase --env TENCENT_SECRET_ID=YOUR_ID --env TENCENT_SECRET_KEY=YOUR_KEY -- npx @cloudbase/cloudbase-mcp
```

## 注意事项

- ✅ **在线服务器**: context7, web-search-prime, web-reader 可正常使用
- 🔄 **重新配置中**: zhipu-mcp (智谱AI), web-scraping-mcp (网页抓取) 新实现
- ❌ **需要修复**: deepseek-mcp, cloudbase 需要重新配置
- 🔧 **自动调用**: context7 会自动在询问技术文档时调用
- 📊 **状态监控**: 使用 `claude mcp list` 实时查看服务器状态
- 🛠️ **故障修复**: 查看本文档的修复步骤或使用 `claude mcp get <name>` 检查配置

## 更新日志

### 2025-11-25 修复更新
- ✅ 基于智谱AI官方文档重新实现了 `zhipu-mcp` 服务器
- ✅ 简化了 `web-scraping-mcp` 服务器实现，减少外部依赖
- 📚 更新了服务器使用方法和故障排除指南
- 🔧 提供了详细的修复步骤和测试方法