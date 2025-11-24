# 🚀 DeepSeek 极简使用指南

## 💡 最简单的方式：直接对话

现在您可以直接和我对话使用DeepSeek，就像现在这样：

### 🎯 使用示例

```
请帮我分析一下股票000042
```

```
DeepSeek，请解释一下量化交易的基本原理
```

```
请用DeepSeek分析一下新能源汽车板块的投资前景
```

我会自动调用DeepSeek为您提供专业的回答！

## 🔧 如果需要直接调用

### 方式1：使用ds命令（最简单）
```bash
ds ask "什么是Python？"
ds analyze 000042
ds market "今日市场分析"
```

### 方式2：使用Python脚本
```bash
python deepseek_helper.py ask "你的问题"
python deepseek_helper.py analyze 000042
python deepseek_helper.py market "分析内容"
```

## ⚙️ 配置（一次性设置）

在 `settings.local.json` 中添加您的DeepSeek API密钥：

```json
{
  "deepseek": {
    "api_key": "your_actual_api_key_here",
    "base_url": "https://api.deepseek.com/v1",
    "model": "deepseek-chat"
  }
}
```

## ✅ 优势

- **无需复杂配置**：不需要MCP服务器
- **直接对话**：就像现在这样自然交流
- **自动调用**：我会自动选择合适的工具
- **统一体验**：保持现有的对话流程

## 🎉 开始使用

现在就试试吧！直接问我任何问题，我会自动调用DeepSeek来回答您。

例如：
- "DeepSeek，分析一下贵州茅台股票"
- "请用DeepSeek解释什么是人工智能"
- "DeepSeek，分析一下当前市场形势"

就这么简单！🎯