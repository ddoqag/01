# 🔑 DeepSeek API密钥获取和配置指南

## 📋 获取API密钥步骤

### 1. 访问DeepSeek官网
- **官网**: https://platform.deepseek.com/
- **备用**: https://www.deepseek.com/

### 2. 注册/登录账户
- 使用邮箱注册新账户
- 或使用现有账户登录

### 3. 创建API密钥
- 登录后进入 "API Keys" 页面
- 点击 "Create API Key"
- 设置密钥名称和权限
- 复制生成的API密钥 (格式: `sk-xxxxxxxxxx`)

### 4. 充值账户 (可选)
- 新用户通常有免费额度
- 充值页面: https://platform.deepseek.com/billing

## 💰 价格信息

- **输入**: 1元/百万tokens
- **输出**: 16元/百万tokens
- **缓存命中**: 0.1元/百万tokens
- **模型**: deepseek-chat (通用), deepseek-reasoner (推理)

## 🔐 配置方法

### 方法1: 更新settings.local.json
```json
{
  "deepseek": {
    "api_key": "sk-your-api-key-here",
    "base_url": "https://api.deepseek.com/v1",
    "model": "deepseek-chat",
    "token_source": "user_manual"
  }
}
```

### 方法2: 设置环境变量
```bash
# Windows
set DEEPSEEK_API_KEY=sk-your-api-key-here

# Linux/Mac
export DEEPSEEK_API_KEY=sk-your-api-key-here
```

### 方法3: 使用配置脚本
```bash
# 运行配置脚本
python setup_deepseek_api.py
```

## 🧪 测试API密钥

### 使用Python脚本测试
```bash
python test_deepseek_keys.py
```

### 使用curl测试
```bash
curl -X POST "https://api.deepseek.com/v1/chat/completions" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer sk-your-api-key-here" \
  -d '{
    "model": "deepseek-chat",
    "messages": [{"role": "user", "content": "你好"}],
    "max_tokens": 50
  }'
```

## ⚡ MCP服务器使用

配置完成后，可使用以下MCP工具:
- `deepseek_ask` - 通用问答
- `deepseek_analyze_stock` - 股票分析
- `deepseek_market_analysis` - 市场分析

### 使用示例
```bash
/mcp deepseek ask "解释一下量子计算"
/mcp deepseek analyze 000001
/mcp deepseek market "今日A股市场分析"
```

## 🚨 常见错误

### 401 Authentication Failed
- **原因**: API密钥无效或错误
- **解决**: 检查密钥是否正确，重新获取密钥

### 402 Insufficient Balance
- **原因**: 账户余额不足
- **解决**: 前往充值页面添加余额

### 429 Rate Limit Reached
- **原因**: 请求频率过高
- **解决**: 控制请求频率，考虑升级计划

## 📞 技术支持

- **官方文档**: https://api-docs.deepseek.com/
- **社区**: Discord, Twitter
- **邮箱**: support@deepseek.com

---

🎉 **配置完成后，您的DeepSeek MCP服务器将完全可用！**