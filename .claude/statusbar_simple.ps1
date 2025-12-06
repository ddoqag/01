# Claude Code Status Bar Script
# 显示当前工作目录和快捷键信息

$pwd = (Get-Location).Path
$homeDir = $env:USERPROFILE

# 如果在用户目录下，显示相对路径
if ($pwd.StartsWith($homeDir)) {
    $displayPath = $pwd.Replace($homeDir, "~")
} else {
    $displayPath = $pwd
}

# 输出状态栏信息
Write-Output "⏵⏵ accept edits on (shift+tab to cycle) $displayPath cd"