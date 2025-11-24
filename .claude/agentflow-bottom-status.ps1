# AgentFlow底部状态显示脚本 - PowerShell版本
# 专为Windows环境优化，支持完整emoji显示

param(
    [ValidateSet("show","info","test","both","minimal")]
    [string]$Mode = "minimal"
)

# 设置PowerShell编码为UTF-8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

# Windows PowerShell颜色定义
$Colors = @{
    Red = "Red"
    Green = "Green"
    Yellow = "Yellow"
    Blue = "Blue"
    Purple = "Magenta"
    Cyan = "Cyan"
    White = "White"
    Gray = "Gray"
    Reset = "White"
}

# 模式配置 - 使用ASCII字符避免编码问题
$ModeConfig = @{
    "flow" = @{
        Icon = ""
        Name = "Flow"
        Color = "Cyan"
        Indicator = "[FLOW]"
        Description = "Agent direct mode"
        FallbackIcon = "[F]"
    }
    "agentflow" = @{
        Icon = ""
        Name = "AgentFlow"
        Color = "Yellow"
        Indicator = "[AGENT]"
        Description = "Multi-agent workflow"
        FallbackIcon = "[A]"
    }
    "fusion" = @{
        Icon = ""
        Name = "Fusion"
        Color = "Magenta"
        Indicator = "[FUSION]"
        Description = "Hybrid mode"
        FallbackIcon = "[X]"
    }
    "unknown" = @{
        Icon = ""
        Name = "Unknown"
        Color = "White"
        Indicator = "[???]"
        Description = "Unknown mode"
        FallbackIcon = "[?]"
    }
}

# 获取AgentFlow模式状态
function Get-CurrentMode {
    $modeLocations = @(
        "$env:USERPROFILE\.flow\.current_mode",
        "$env:USERPROFILE\flow\.current_mode",
        ".\.flow\.current_mode",
        ".\flow\.current_mode",
        "$env:USERPROFILE\.current_mode"
    )

    $currentMode = "flow"

    foreach ($modeFile in $modeLocations) {
        if (Test-Path $modeFile) {
            try {
                $content = Get-Content $modeFile -Raw -ErrorAction SilentlyContinue
                if ($content) {
                    $currentMode = $content.Trim().ToLower()
                    break
                }
            } catch {
                continue
            }
        }
    }

    return $currentMode
}

# 获取系统信息
function Get-SystemInfo {
    $user = $env:USERNAME
    $hostName = $env:COMPUTERNAME
    $currentDir = Get-Location

    if ($currentDir.Path -like "*claude*" -or $currentDir.Path -like "*AgentFlow*") {
        $displayDir = $currentDir.Path + " [WORK]"
    } elseif ($currentDir.Path.StartsWith($env:USERPROFILE)) {
        $displayDir = $currentDir.Path -replace [regex]::Escape($env:USERPROFILE), "~"
    } else {
        $displayDir = $currentDir.Path
    }

    $currentTime = Get-Date -Format "HH:mm:ss"
    $loadAvg = "0.1"

    return @{
        User = $user
        Host = $hostName
        Directory = $displayDir
        Time = $currentTime
        Load = $loadAvg
    }
}

# 获取终端宽度
function Get-TerminalWidth {
    try {
        return [Console]::WindowWidth
    } catch {
        return 80
    }
}

# 测试emoji支持
function Test-EmojiSupport {
    try {
        $original = [Console]::OutputEncoding
        [Console]::OutputEncoding = [System.Text.Encoding]::UTF8
        Write-Host "" -NoNewline
        return $false  # 默认使用fallback，确保兼容性
    } catch {
        return $false
    }
}

# 创建状态栏
function New-StatusBar {
    $sysInfo = Get-SystemInfo
    $currentMode = Get-CurrentMode
    $modeInfo = $ModeConfig[$currentMode]

    if (-not $modeInfo) {
        $modeInfo = $ModeConfig["unknown"]
    }

    $displayIcon = $modeInfo.FallbackIcon
    $termWidth = Get-TerminalWidth

    $leftText = "Alt+M: $($displayIcon) $($modeInfo.Name)"
    $middleText = "$($sysInfo.User)@$($sysInfo.Host):$($sysInfo.Directory)"
    $rightText = "$($sysInfo.Time) $($sysInfo.Load) 83A | CL$(Get-Date -Format 'HHmm')"

    $totalLen = $leftText.Length + $middleText.Length + $rightText.Length + 10
    $padding = [Math]::Max(2, $termWidth - $totalLen)
    $spaces = " " * $padding

    return "$leftText$spaces$middleText | $rightText"
}

# 显示底部状态栏
function Show-BottomStatus {
    $termWidth = Get-TerminalWidth
    $separator = "-" * $termWidth

    Write-Host ""
    Write-Host $separator -ForegroundColor Gray
    Write-Host (New-StatusBar) -ForegroundColor White
    Write-Host $separator -ForegroundColor Gray
    Write-Host ""
}

# 显示模式信息面板
function Show-ModeInfo {
    $currentMode = Get-CurrentMode
    $modeInfo = $ModeConfig[$currentMode]

    if (-not $modeInfo) {
        $modeInfo = $ModeConfig["unknown"]
    }

    $displayIcon = $modeInfo.FallbackIcon
    $panelWidth = 70
    $border = "=" * $panelWidth

    Write-Host ""
    Write-Host "+$border+" -ForegroundColor $modeInfo.Color
    Write-Host "| $($displayIcon) $($modeInfo.Name) - $($modeInfo.Description)" -ForegroundColor $modeInfo.Color
    Write-Host "+$border+" -ForegroundColor $modeInfo.Color
    Write-Host "| Hotkeys: Alt+M Switch | Alt+S Status | /mode Command" -ForegroundColor Gray
    Write-Host "+$border+" -ForegroundColor $modeInfo.Color
    Write-Host ""
}

# 显示图标测试
function Show-IconTest {
    Write-Host ""
    Write-Host "=== Mode Display Test ===" -ForegroundColor Cyan
    Write-Host "Flow mode: $($ModeConfig['flow'].FallbackIcon)" -ForegroundColor Cyan
    Write-Host "AgentFlow mode: $($ModeConfig['agentflow'].FallbackIcon)" -ForegroundColor Yellow
    Write-Host "Fusion mode: $($ModeConfig['fusion'].FallbackIcon)" -ForegroundColor Magenta

    $currentMode = Get-CurrentMode
    $modeInfo = $ModeConfig[$currentMode]
    Write-Host "Current mode: $($modeInfo.FallbackIcon) $($modeInfo.Name)" -ForegroundColor $modeInfo.Color
    Write-Host ""
}

# 主执行逻辑
switch ($Mode) {
    "show" { Show-BottomStatus }
    "info" { Show-ModeInfo }
    "test" { Show-IconTest }
    "both" {
        Show-BottomStatus
        Show-ModeInfo
    }
    "minimal" {
        $currentMode = Get-CurrentMode
        $modeInfo = $ModeConfig[$currentMode]
        if (-not $modeInfo) { $modeInfo = $ModeConfig["unknown"] }

        Write-Host " $($modeInfo.FallbackIcon)" -ForegroundColor $modeInfo.Color
    }
}