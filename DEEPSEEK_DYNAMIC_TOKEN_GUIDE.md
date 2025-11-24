# 🚀 DeepSeek 动态Token集成指南

## ⚡ 极简开始

### 🎯 最佳方式：直接对话
现在您可以直接对话使用DeepSeek：
```
请用DeepSeek分析一下股票000042
DeepSeek，解释一下量化交易原理
```

### 🔧 Token配置（只需一次）

#### 方法1: 自动配置（推荐）
```bash
dt auto
```

#### 方法2: 环境变量设置
```bash
# 一次性设置
setup_deepseek_env.cmd

# 或手动设置
setx DEEPSEEK_CURRENT_TOKEN your_token_here
```

#### 方法3: 实时Token管理
```bash
dt status    # 查看Token状态
dt get       # 获取当前Token
dt test      # 测试Token有效性
```

## 🛠️ Token管理工具

### dt命令 - Token管理器
```bash
dt status              # 📊 查看所有Token来源状态
dt auto                # 🔄 自动配置最佳Token
dt get                 # 🔑 获取当前有效Token
dt update [token]      # ⚙️  手动更新Token
dt test                # 🧪 测试Token是否可用
```

### ds命令 - DeepSeek调用
```bash
ds ask "你的问题"       # 💬 通用问答
ds analyze 000042      # 📈 股票分析
ds market "分析内容"    # 📊 市场分析
```

## 🎯 Token来源优先级

系统会按以下优先级自动获取Token：

1. **🥇 DZH系统(直接读取)** - 从 `D:/dzh365(64)/token_config.json`
2. **🥈 DZH系统(脚本调用)** - 通过Python脚本动态获取
3. **🥉 环境变量** - `DEEPSEEK_CURRENT_TOKEN` 或 `DEEPSEEK_API_KEY`
4. **🏅 配置文件** - `settings.local.json` 中的静态配置
5. **🆓 本地缓存** - 1小时内有效的Token缓存

## 📋 Token配置文件结构

### DZH系统Token格式
```json
{
  "production_api": {
    "token": "MTc2MzYxNTIyNTphYzkzZDllNWQ0YzVkMWQyMTkwYTk4YmM0NGNjNTFjMGVkMjJkODM5MDY4ZDQwOTMyZjhiZTQ5MmZmNjdiNGJl",
    "user_id": "prod_user_001",
    "is_active": true,
    "expires_at": "2026-11-20T13:07:05.876093"
  }
}
```

### 本地配置格式
```json
{
  "deepseek": {
    "api_key": "your_token_here",
    "base_url": "https://api.deepseek.com/v1",
    "model": "deepseek-chat",
    "token_source": "dynamic_integration",
    "updated_at": "2025-11-21T22:30:00"
  }
}
```

## 🔍 故障排除

### 常见问题及解决

#### ❌ "未找到有效的API Token"
```bash
# 解决方案1: 自动配置
dt auto

# 解决方案2: 检查状态
dt status

# 解决方案3: 手动设置环境变量
setx DEEPSEEK_CURRENT_TOKEN your_token_here
```

#### ❌ "DZH系统读取失败"
```bash
# 检查DZH路径是否正确
dir "D:\dzh365(64)\token_config.json"

# 测试Python脚本
python -c "
import sys
sys.path.append('D:/dzh365(64)')
from token_config import DZHTokenManager
tm = DZHTokenManager()
print('Token:', tm.get_token('production_api'))
"
```

#### ❌ "Token已过期"
```bash
# 刷新DZH Token
python -c "
import sys
sys.path.append('D:/dzh365(64)')
from token_config import DZHTokenManager
tm = DZHTokenManager()
tm.refresh_token('production_api')
"

# 重新配置
dt auto
```

### 调试模式
```bash
# 查看详细日志
python deepseek_helper.py ask "test" 2>&1 | more

# 检查Token详情
python deepseek_token_manager.py status
```

## 🎉 成功案例

### 配置完成后可以这样使用：

#### 🗣️ 对话方式
```
请用DeepSeek分析一下今天的市场行情

用户: DeepSeek，帮我分析一下贵州茅台股票
AI: ✅ 正在调用DeepSeek分析...
   [返回详细分析结果]
```

#### 💻 命令行方式
```bash
# 快速问答
ds ask "什么是量化交易？"

# 股票分析
ds analyze 600519

# 市场分析
ds market "新能源汽车板块前景"

# Token管理
dt status    # 查看状态
dt auto      # 自动配置
dt test      # 测试功能
```

## 🔒 安全提示

1. **Token保密**: 不要在代码或日志中暴露完整Token
2. **定期更新**: 定期刷新Token确保安全性
3. **环境隔离**: 不同环境使用不同Token
4. **缓存清理**: 定期清理本地Token缓存

## 📞 技术支持

如遇问题，请按以下顺序排查：

1. 运行 `dt status` 查看Token状态
2. 运行 `dt auto` 自动配置
3. 运行 `dt test` 测试功能
4. 检查DZH系统是否正常运行
5. 查看网络连接是否正常

---

**🎯 现在就开始使用吧！直接对话或运行 `dt auto` 配置Token。**