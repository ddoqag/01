# AgentFlow Windows底部状态栏修复方案

## 问题诊断

用户反馈在Windows环境下底部状态栏没有显示图标，经过分析发现以下问题：

1. **系统兼容性问题**: `hostname -s`在Git Bash中不支持，`uptime`命令在Windows不可用
2. **图标显示问题**: emoji图标在某些Windows终端中无法正确显示
3. **编码问题**: PowerShell脚本的中文字符编码导致解析错误

## 解决方案

### 1. 优化的Shell脚本版本 (`/.claude/agentflow-bottom-status.sh`)

**特性:**
- Windows环境自动检测 (MINGW/MSYS/CYGWIN)
- 兼容的ANSI颜色代码
- Fallback图标方案: `[F]`、`[A]`、`[X]`、`[?]`
- 多种模式文件位置检测
- 改进的系统信息获取

**使用方法:**
```bash
# 测试图标显示
./.claude/agentflow-bottom-status.sh test

# 紧凑模式 (只显示图标)
./.claude/agentflow-bottom-status.sh minimal

# 完整状态栏
./.claude/agentflow-bottom-status.sh show

# 模式信息面板
./.claude/agentflow-bottom-status.sh info
```

### 2. PowerShell专用版本 (`/.claude/agentflow-bottom-status.ps1`)

**特性:**
- 纯PowerShell实现，更好的Windows集成
- UTF-8编码支持
- 优雅的颜色输出
- 简化的ASCII图标确保兼容性
- 动态终端宽度检测

**使用方法:**
```powershell
# 通过PowerShell直接运行
powershell -ExecutionPolicy Bypass -NoProfile -File ".claude\agentflow-bottom-status.ps1" minimal

# 或者通过批处理文件调用
./agentflow-status.cmd show
```

### 3. Windows批处理启动器 (`agentflow-status.cmd`)

**特性:**
- 自动检测可用的运行环境 (PowerShell优先)
- 透明的参数传递
- 错误处理和用户友好的错误信息

**使用方法:**
```cmd
# 基本用法
agentflow-status.cmd minimal

# 完整状态栏
agentflow-status.cmd show

# 信息面板
agentflow-status.cmd info

# 测试模式
agentflow-status.cmd test

# 同时显示状态栏和信息
agentflow-status.cmd both
```

## 三种模式显示效果

### Flow模式 - 专业Agent直接调用
- **图标**: `[F]` (或 🎯 在支持emoji的环境)
- **颜色**: 青色
- **指示器**: `[FLOW]`

### AgentFlow模式 - 多Agent工作流协调
- **图标**: `[A]` (或 🔗 在支持emoji的环境)
- **颜色**: 黄色
- **指示器**: `[AGENT]`

### Fusion模式 - Flow+AgentFlow智能协作
- **图标**: `[X]` (或 🚀 在支持emoji的环境)
- **颜色**: 紫色
- **指示器**: `[FUSION]`

## 状态栏显示示例

```
--------------------------------------------------------------------------------
Alt+M: [F] Flow  ddo@DDO:~\AppData\Roaming\npm | 18:26:48 0.1 83A | CL1826
--------------------------------------------------------------------------------
```

**状态栏组件说明:**
- `Alt+M`: 模式切换快捷键提示
- `[F] Flow`: 当前模式和图标
- `ddo@DDO`: 用户@主机名
- `~\AppData\Roaming\npm`: 当前目录
- `18:26:48`: 当前时间
- `0.1`: 系统负载 (Windows下模拟值)
- `83A`: Agent数量
- `CL1826`: 会话ID

## 模式信息面板示例

```
+======================================================================+
| [F] Flow - Agent direct mode
+======================================================================+
| Hotkeys: Alt+M Switch | Alt+S Status | /mode Command
+======================================================================+
```

## 故障排除

### 图标不显示
- **解决方案**: 所有脚本都包含ASCII fallback图标，确保在任何环境下都能显示
- **测试**: 运行 `agentflow-status.cmd test` 查看图标支持情况

### 颜色不显示
- **原因**: 终端不支持ANSI颜色或PowerShell执行策略限制
- **解决方案**: 使用PowerShell版本，它使用内置的 `-ForegroundColor` 参数

### 权限问题
- **PowerShell执行策略**: 使用 `-ExecutionPolicy Bypass` 参数
- **文件权限**: 确保脚本文件有执行权限

### 编码问题
- **中文显示**: PowerShell版本已优化为英文界面，避免编码问题
- **字符集**: Shell脚本版本自动设置UTF-8编码

## 集成建议

1. **快捷方式**: 可以将 `agentflow-status.cmd` 添加到系统PATH
2. **别名设置**: 在PowerShell profile中添加别名
   ```powershell
   Set-Alias -Name afs -Value "agentflow-status.cmd"
   ```
3. **自动化集成**: 可以在启动脚本中调用 `minimal` 模式显示当前状态

## 技术细节

### 兼容性矩阵

| 环境 | Shell脚本 | PowerShell脚本 | 批处理启动器 |
|------|----------|---------------|-------------|
| Windows PowerShell | ❌ | ✅ | ✅ |
| PowerShell Core | ❌ | ✅ | ✅ |
| Git Bash (MINGW) | ✅ | ❌ | ✅ |
| CMD | ❌ | ❌ | ✅ |
| WSL Linux | ✅ | ❌ | ❌ |

### 文件结构
```
C:\Users\ddo\AppData\Roaming\npm\
├── .claude\
│   └── agentflow-bottom-status.sh     # 优化的Shell脚本
│   └── agentflow-bottom-status.ps1    # PowerShell专用版本
├── agentflow-status.cmd               # Windows批处理启动器
└── WINDOWS_STATUS_FIX.md              # 本说明文档
```

通过这个修复方案，用户现在可以在Windows环境下正确显示底部状态栏，包括清晰的图标指示和颜色区分。