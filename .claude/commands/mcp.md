---
description: 与MCP服务器交互的统一接口
argument-hint: [server-name] [action] [arguments...]
---

# MCP服务器交互工具

您正在使用MCP（Model Context Protocol）服务器交互工具。此工具提供与配置的MCP服务器通信的统一接口。

## 支持的服务器

### deepseek - DeepSeek AI集成
- **描述**: 提供DeepSeek AI的通用问答、股票分析和市场分析功能
- **工具列表**:
  - `deepseek_ask`: 通用问题回答
  - `deepseek_analyze_stock`: 股票分析
  - `deepseek_market_analysis`: 市场分析

## 使用方法

### 基本语法
```
/mcp [server-name] [action] [arguments...]
```

### DeepSeek服务器使用示例

#### 1. 通用问题回答
```
/mcp deepseek ask "什么是Python requests库？"
/mcp deepseek ask "解释一下量化交易的基本原理"
```

#### 2. 股票分析
```
/mcp deepseek analyze 000042
/mcp deepseek analyze 600519
/mcp deepseek analyze "贵州茅台"
```

#### 3. 市场分析
```
/mcp deepseek market "今日A股市场走势分析"
/mcp deepseek market "新能源汽车板块前景"
```

#### 4. 工具列表
```
/mcp deepseek list
```

## 工具调用流程

1. **验证服务器**: 检查指定的MCP服务器是否可用
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
1. **服务器未响应**: 检查MCP服务器配置是否正确
2. **API密钥错误**: 确保DEEPSEEK_API_KEY环境变量已设置
3. **参数错误**: 检查传递给工具的参数格式是否正确

### 调试命令
```
/mcp deepseek status  # 检查服务器状态
```

## 注意事项

- 确保已正确配置MCP服务器
- 部分功能可能需要有效的API密钥
- 股票代码请使用标准格式（如000042、600519）
- 市场分析查询请提供具体的分析方向