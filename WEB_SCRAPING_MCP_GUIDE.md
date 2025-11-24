# 网页抓取MCP服务器使用指南

## 📋 概述

网页抓取MCP服务器提供了强大的网页内容提取和分析功能，无需依赖外部Python库，通过curl命令实现。

## 🚀 可用功能

### 1. 网页可访问性检查
```bash
/mcp web-scraping check "https://example.com"
```
检查网页是否可访问，并提取标题和描述信息。

### 2. 获取网页原始内容
```bash
/mcp web-scraping simple-fetch "https://example.com"
```
获取网页的原始HTML内容（可限制字符数）。

### 3. 提取页面链接
```bash
/mcp web-scraping extract-urls "https://example.com"
```
从网页中提取所有URL链接，包括链接文本和域名信息。

## 💡 使用示例

### 检查网站状态
```bash
/mcp web-scraping check "https://www.github.com"
```

### 获取新闻页面内容
```bash
/mcp web-scraping simple-fetch "https://news.example.com/article" --limit 3000
```

### 分析网站链接结构
```bash
/mcp web-scraping extract-urls "https://www.example.com"
```

## 📝 功能特性

- ✅ **无需外部依赖** - 使用系统curl命令
- ✅ **超时保护** - 30秒超时限制
- ✅ **内容限制** - 防止内容过大
- ✅ **链接去重** - 自动去除重复链接
- ✅ **域名解析** - 自动转换为绝对URL
- ✅ **文本清理** - 移除HTML标签

## ⚙️ 配置信息

- **服务器名称**: `web-scraping-mcp`
- **路径**: `C:\Users\ddo\AppData\Roaming\npm\web_scraping_simple_mcp_server.py`
- **命令**: `python`

## 🔧 技术实现

- 使用subprocess调用curl命令
- 正则表达式解析HTML内容
- urllib.parse处理URL转换
- JSON-RPC协议通信

## 📋 返回格式

所有功能返回JSON格式结果，包含：
- `tool`: 使用的工具名称
- `url`: 处理的URL
- `success`: 操作是否成功
- `error`: 错误信息（如果失败）
- 相关数据字段

## 🚨 注意事项

1. **网络限制**: 依赖curl命令，确保网络连接正常
2. **编码问题**: 自动处理常见编码格式
3. **超时设置**: 默认30秒超时，可调整
4. **内容大小**: 限制返回内容大小防止内存溢出

## 🔄 故障排除

### curl命令不可用
确保系统已安装curl命令：
```bash
curl --version
```

### 网页无法访问
检查：
- URL是否正确
- 网络连接是否正常
- 目标网站是否可访问

### 内容提取不完整
可能原因：
- 网页使用JavaScript动态加载
- 网页结构复杂
- 内容被截断（limit设置）