# Python环境安装指南

## 🔍 当前问题

当前系统中的Python 3.14安装损坏，缺少关键模块（如encodings），导致无法正常运行MCP服务器。

## 🛠️ 解决方案

### 方案A: 重新安装Python（推荐）

#### 步骤1: 卸载损坏的Python
1. 打开 **控制面板** → **程序和功能**
2. 找到 **Python 3.14**
3. 右键选择 **卸载**

#### 步骤2: 下载稳定版本
访问 [Python官网](https://www.python.org/downloads/) 下载：
- **推荐**: Python 3.12.8 (LTS长期支持版本)
- **备选**: Python 3.11.9 (稳定版本)

#### 步骤3: 安装Python
1. 运行下载的安装程序
2. **重要**: 勾选以下选项：
   - ✅ **Add Python to PATH**
   - ✅ **Install for all users**
3. 点击 **Install Now**

#### 步骤4: 验证安装
打开新的命令提示符，运行：
```cmd
python --version
pip --version
```

### 方案B: 使用Microsoft Store

1. 打开 **Microsoft Store**
2. 搜索 **"Python 3.12"**
3. 点击 **获取** 或 **安装**
4. 安装完成后验证版本

### 方案C: 使用Anaconda（推荐开发者）

1. 访问 [Anaconda官网](https://www.anaconda.com/products/distribution)
2. 下载 **Anaconda Distribution**
3. 安装时选择 **Add Anaconda to PATH**
4. 提供完整的Python环境管理

## 🔧 验证Python安装

安装完成后，运行以下验证脚本：

```cmd
@echo off
echo 验证Python安装...
python --version
if %errorlevel% equ 0 (
    echo ✅ Python命令正常
) else (
    echo ❌ Python命令异常
)

python -c "import sys; print('Python路径:', sys.executable)"
python -c "import encodings; print('✅ 标准库正常')"
python -c "import json; print('✅ JSON模块正常')"
```

## 🎯 恢复MCP服务器

Python环境修复后，重新添加MCP服务器：

```cmd
# 添加deepseek-mcp
claude.cmd mcp add -s user -t stdio deepseek-mcp python "C:\Users\ddo\AppData\Roaming\npm\deepseek_mcp_server.py"

# 添加web-scraping-mcp
claude.cmd mcp add -s user -t stdio web-scraping-mcp python "C:\Users\ddo\AppData\Roaming\npm\web_scraping_simple_mcp_server.py"
```

## 📋 可用的MCP工具

Python环境修复后，您将拥有完整的8个MCP工具：

### ✅ 当前可用（5个）
- context7 - 智能上下文管理
- web-search-prime - 智谱AI网络搜索
- zai-mcp-server - Z_AI智能AI服务
- web-reader - 智谱AI网页阅读
- cloudbase - 腾讯云开发工具

### ⏳ 待恢复（3个）
- deepseek-mcp - DeepSeek AI集成
- web-scraping-mcp - 网页抓取和内容提取
- sugar-mcp - Sugar DevOps工具（需要额外安装）

## 🚨 注意事项

1. **重启系统** - Python安装后建议重启
2. **环境变量** - 确保Python在PATH中
3. **权限** - 安装时可能需要管理员权限
4. **防火墙** - 首次运行可能需要网络权限

## 📞 获取帮助

如果遇到问题，可以：
1. 查看 `setup_python_env.cmd` 脚本
2. 运行 `check_pythons.cmd` 检测安装
3. 参考Python官方文档

---
*创建时间: 2025-11-22*
*状态: 等待用户执行Python安装*