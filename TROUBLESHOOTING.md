# 🔧 故障排除手册

> **快速解决常见问题，让您的工具集始终保持最佳状态**

---

## 📋 快速诊断

### 🚨 5分钟快速自检

当遇到问题时，按以下顺序快速检查：

```
🔍 问题自检流程
├── 1️⃣ 网络连接检查
├── 2️⃣ 权限验证
├── 3️⃣ 配置文件检查
├── 4️⃣ 环境变量确认
└── 5️⃣ 服务状态诊断
```

### 🛠️ 一键诊断命令
```
诊断系统配置        # 全面检查系统状态
检查工具连接        # 验证外部服务连接
验证权限设置        # 确认文件和操作权限
测试基本功能        # 验证核心工具可用性
```

---

## 🚨 常见问题及解决方案

### 🔗 连接问题

#### 问题1：MCP服务器连接失败
**症状**:
```
❌ 无法连接到MCP服务器
❌ API调用超时
❌ 认证失败
```

**快速解决方案**:
```bash
# 1. 检查网络连接
ping api.deepseek.com

# 2. 验证API密钥
echo $DEEPSEEK_API_KEY  # 检查环境变量是否设置

# 3. 测试MCP服务器状态
/mcp deepseek status
```

**详细排查步骤**:

1. **网络检查**
   ```bash
   # 测试基本网络连接
   curl -I https://api.deepseek.com

   # 检查防火墙设置
   # Windows: netsh advfirewall show allprofiles
   # macOS/Linux: sudo ufw status
   ```

2. **API密钥验证**
   ```bash
   # 检查环境变量
   echo $DEEPSEEK_API_KEY

   # 重新设置API密钥
   export DEEPSEEK_API_KEY="your_new_key_here"
   ```

3. **服务器配置检查**
   ```json
   // 检查 ~/.claude/settings.json
   {
     "mcpServers": {
       "deepseek": {
         "command": "python",
         "args": ["正确的服务器路径"],
         "env": {
           "DEEPSEEK_API_KEY": "your_api_key"
         }
       }
     }
   }
   ```

#### 问题2：Git操作失败
**症状**:
```
❌ Git命令执行失败
❌ 权限被拒绝
❌ 分支不存在
```

**解决方案**:

1. **权限问题**
   ```bash
   # 检查Git配置
   git config --list

   # 重新配置用户信息
   git config --global user.name "Your Name"
   git config --global user.email "your.email@example.com"

   # 检查SSH密钥
   ssh -T git@github.com
   ```

2. **远程仓库问题**
   ```bash
   # 检查远程连接
   git remote -v
   git remote show origin

   # 重新添加远程仓库
   git remote set-url origin https://github.com/username/repo.git
   ```

#### 问题3：代码审查工具无法启动
**症状**:
```
❌ /code-review 命令无响应
❌ 代理加载失败
❌ 分析结果不完整
```

**解决方案**:

1. **检查插件安装**
   ```bash
   # 验证插件是否正确安装
   ls ~/.claude/plugins/

   # 重新安装插件
   /plugin install code-review
   ```

2. **检查代理配置**
   ```bash
   # 验证代理文件存在
   ls ~/.claude/plugins/code-review/agents/

   # 检查代理文件格式
   cat ~/.claude/plugins/code-review/agents/code-reviewer.md
   ```

### ⚡ 性能问题

#### 问题1：响应速度慢
**症状**:
```
⏳ 命令响应时间过长
⏳ 分析处理缓慢
⏳ 界面卡顿
```

**优化方案**:

1. **系统资源优化**
   ```bash
   # 检查内存使用
   # Windows: tasklist
   # macOS/Linux: top/htop

   # 清理临时文件
   # Windows: %temp%
   # macOS: /tmp
   # Linux: /tmp
   ```

2. **网络优化**
   ```bash
   # 更换DNS服务器
   # 设置为8.8.8.8 (Google DNS) 或 1.1.1.1 (Cloudflare DNS)

   # 检查网络延迟
   ping api.deepseek.com
   ```

3. **配置优化**
   ```json
   {
     "performance": {
       "timeout": 30000,
       "retries": 3,
       "concurrency": 5
     }
   }
   ```

#### 问题2：内存占用过高
**症状**:
```
💾 内存使用率持续上升
💾 系统变得卡顿
💾 其他应用受影响
```

**解决方案**:

1. **清理缓存**
   ```bash
   # 清理Claude缓存
   rm -rf ~/.claude/cache/*

   # 重启Claude应用
   ```

2. **限制并发**
   ```json
   {
     "limits": {
       "max_concurrent_requests": 3,
       "max_memory_usage": "2GB"
     }
   }
   ```

### 🔧 配置问题

#### 问题1：配置文件损坏
**症状**:
```
❌ 启动时配置错误
❌ 设置无法保存
❌ 工具配置丢失
```

**解决方案**:

1. **备份并重置配置**
   ```bash
   # 备份现有配置
   cp ~/.claude/settings.json ~/.claude/settings.json.backup

   # 重置为默认配置
   rm ~/.claude/settings.json
   # 重启Claude会生成新的默认配置
   ```

2. **验证配置格式**
   ```bash
   # 检查JSON格式
   python -m json.tool ~/.claude/settings.json

   # 修复常见JSON错误
   # - 缺少逗号
   # - 多余逗号
   # - 引号不匹配
   ```

#### 问题2：环境变量问题
**症状**:
```
❌ API密钥无法识别
❌ 路径配置错误
❌ 工具找不到依赖
```

**解决方案**:

1. **环境变量检查**
   ```bash
   # Windows (PowerShell)
   Get-ChildItem Env:

   # macOS/Linux
   env | grep -E "(API|PATH|CLAUDE)"
   ```

2. **重新设置环境变量**
   ```bash
   # 临时设置
   export DEEPSEEK_API_KEY="your_key"

   # 永久设置
   echo 'export DEEPSEEK_API_KEY="your_key"' >> ~/.bashrc
   source ~/.bashrc
   ```

---

## 🛠️ 高级故障排除

### 🔍 深度诊断

#### 系统健康检查
```
运行全面系统诊断
```

这个命令会执行以下检查：

1. **硬件资源检查**
   - CPU使用率
   - 内存可用性
   - 磁盘空间
   - 网络连接质量

2. **软件环境检查**
   - 依赖版本兼容性
   - 权限配置正确性
   - 服务运行状态

3. **配置完整性检查**
   - 配置文件格式
   - 环境变量设置
   - 插件安装状态

#### 日志分析
```bash
# 查看Claude日志
tail -f ~/.claude/logs/claude.log

# 查看MCP服务器日志
tail -f ~/.claude/logs/mcp.log

# 查看错误日志
grep "ERROR" ~/.claude/logs/*.log
```

### 🔧 高级修复技巧

#### 1. 完全重置系统
```bash
# ⚠️ 警告：这将删除所有自定义设置
# 备份重要数据
cp -r ~/.claude ~/.claude.backup

# 清理所有配置
rm -rf ~/.claude

# 重新初始化
claude --init
```

#### 2. 手动修复插件
```bash
# 重新下载插件
git clone https://github.com/claude-code/plugin-repo.git
cp -r plugin-repo/plugin-name ~/.claude/plugins/

# 修复权限
chmod -R 755 ~/.claude/plugins/
```

#### 3. 数据库修复
```bash
# 检查数据库完整性
sqlite3 ~/.claude/database.db ".schema"

# 重建数据库
mv ~/.claude/database.db ~/.claude/database.db.backup
claude --rebuild-db
```

---

## 📞 获取帮助

### 🆘 紧急支持

#### 1. 内置帮助系统
```
/help                    # 获取通用帮助
/help feature-dev        # 特定功能帮助
/status                  # 系统状态检查
/debug                   # 调试信息
```

#### 2. 诊断报告生成
```
生成诊断报告            # 获取完整的系统状态报告
```

报告包含：
- 系统配置信息
- 错误日志摘要
- 性能指标
- 建议的修复方案

#### 3. 社区支持
- **GitHub Issues**: 报告Bug和功能请求
- **用户社区**: 获取其他用户的帮助
- **官方文档**: 查看最新的文档更新

### 📚 学习资源

#### 1. 官方文档
- [完整用户手册](COMPLETE_USER_MANUAL.md)
- [快速启动指南](QUICK_START.md)
- [最佳实践建议](BEST_PRACTICES.md)

#### 2. 视频教程
- 新手入门视频
- 高级功能演示
- 故障排除实例

#### 3. 示例项目
- 参考配置文件
- 工作流模板
- 自定义插件示例

---

## 🔄 预防性维护

### 📅 定期维护任务

#### 每周检查
```
系统健康检查
清理临时文件
更新工具版本
```

#### 每月维护
```
备份配置文件
审查性能指标
清理旧日志
```

#### 季度优化
```
全面系统诊断
配置文件优化
插件更新
性能基准测试
```

### 🛡️ 最佳实践

#### 1. 备份策略
- 定期备份配置文件
- 保存重要的自定义设置
- 记录系统变更历史

#### 2. 监控指标
- 响应时间
- 成功率
- 资源使用率
- 错误频率

#### 3. 更新管理
- 关注版本更新通知
- 测试新版本的兼容性
- 及时安装安全补丁

---

## 🎯 问题分类索引

### A. 连接相关 (Connection Issues)
- [MCP服务器连接失败](#问题1mcp服务器连接失败)
- [Git远程连接问题](#问题2git操作失败)
- [API认证失败](#问题1mcp服务器连接失败)

### B. 性能相关 (Performance Issues)
- [响应速度慢](#问题1响应速度慢)
- [内存占用过高](#问题2内存占用过高)
- [系统卡顿](#问题1响应速度慢)

### C. 配置相关 (Configuration Issues)
- [配置文件损坏](#问题1配置文件损坏)
- [环境变量问题](#问题2环境变量问题)
- [插件加载失败](#问题3代码审查工具无法启动)

### D. 功能相关 (Functionality Issues)
- [命令无响应](#问题3代码审查工具无法启动)
- [分析结果错误](#问题3代码审查工具无法启动)
- [工作流中断](#问题3代码审查工具无法启动)

---

## 🚀 快速解决方案速查表

| 问题类型 | 快速命令 | 预期解决时间 |
|---------|---------|-------------|
| 网络连接 | `ping api.deepseek.com` | 1分钟 |
| 权限问题 | `git config --list` | 2分钟 |
| 配置错误 | `python -m json.tool ~/.claude/settings.json` | 3分钟 |
| 性能问题 | `清理缓存` | 5分钟 |
| 系统重置 | `生成诊断报告` | 10分钟 |

---

**📞 需要进一步帮助？**

如果问题仍未解决，请：
1. 运行 `生成诊断报告` 获取详细信息
2. 查看社区论坛的相似问题
3. 联系技术支持团队

**🔄 本文档持续更新，请定期查看最新版本**

---

*最后更新: 2025-11-25*
*版本: 1.0.0*